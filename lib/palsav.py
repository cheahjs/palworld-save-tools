import json
import os
import subprocess
from typing import Any, Dict
import zlib

from lib.noindent import NoIndentByteDecoder


UESAVE_TYPE_MAPS = [
    ".worldSaveData.CharacterSaveParameterMap.Key=Struct",
    ".worldSaveData.FoliageGridSaveDataMap.Key=Struct",
    ".worldSaveData.FoliageGridSaveDataMap.ModelMap.InstanceDataMap.Key=Struct",
    ".worldSaveData.MapObjectSpawnerInStageSaveData.Key=Struct",
    ".worldSaveData.ItemContainerSaveData.Key=Struct",
    ".worldSaveData.CharacterContainerSaveData.Key=Struct",
]


def convert_to_json(uesave_path: str, save_path: str) -> Dict[str, Any]:
    # Open the file
    with open(save_path, "rb") as f:
        # Read the file
        data = f.read()
        uncompressed_data, _ = decompress_sav_to_gvas(data)
        if os.environ.get("DEBUG", "0") == "1":
            with open(save_path + ".gvas", "wb") as f:
                f.write(uncompressed_data)
        # Convert to json with uesave
        # Run uesave.exe with the uncompressed file piped as stdin
        # stdout will be the json string
        uesave_run = subprocess.run(
            uesave_to_json_params(uesave_path),
            input=uncompressed_data,
            capture_output=True,
        )
        print(uesave_run.stderr.decode("utf-8"))
        # Check if the command was successful
        if uesave_run.returncode != 0:
            print(uesave_run.stdout.decode("utf-8"))
            raise Exception(
                f"uesave.exe failed to convert {save_path} (return {uesave_run.returncode})"
            )
        print("Loading JSON")
        return json.loads(uesave_run.stdout.decode("utf-8"), cls=NoIndentByteDecoder)


def convert_to_sav(uesave_path: str, json_path: str, json_blob: Dict[str, Any]):
    sav_file = json_path[:-5]
    # Convert the file back to binary
    uesave_run = subprocess.run(
        uesave_from_json_params(uesave_path),
        capture_output=True,
        input=json.dumps(json_blob).encode("utf-8"),
    )
    print(uesave_run.stderr.decode("utf-8"))
    if uesave_run.returncode != 0:
        print(uesave_run.stdout.decode("utf-8"))
        raise Exception(
            f"uesave.exe failed to convert {json_path} (return {uesave_run.returncode})"
        )
    if os.environ.get("DEBUG", "0") == "1":
        with open(json_path + ".sav", "wb") as f:
            f.write(uesave_run.stdout)
    # Open the old sav file to get type
    if os.path.exists(sav_file):
        with open(sav_file, "rb") as f:
            data = f.read()
            save_type = data[11]
    # If the sav file doesn't exist, use known heuristics
    else:
        # Largest files use double compression
        if "LocalData" in sav_file or "Level" in sav_file:
            save_type = 0x32
        else:
            save_type = 0x31

    data = uesave_run.stdout
    compressed_data = compress_gvas_to_sav(data, save_type)
    with open(sav_file, "wb") as f:
        f.write(compressed_data)
    print(f"Converted {json_path} to {sav_file}")


def uesave_to_json_params(uesave_path: str) -> list[str]:
    args = [
        uesave_path,
        "to-json",
    ]
    for map_type in UESAVE_TYPE_MAPS:
        args.append("--type")
        args.append(f"{map_type}")
    return args


def uesave_from_json_params(uesave_path: str) -> list[str]:
    args = [
        uesave_path,
        "from-json",
        "--input",
        "-",
        "--output",
        "-",
    ]
    return args


def decompress_sav_to_gvas(data: bytes) -> tuple[bytes, int]:
    uncompressed_len = int.from_bytes(data[0:4], byteorder="little")
    compressed_len = int.from_bytes(data[4:8], byteorder="little")
    magic_bytes = data[8:11]
    save_type = data[11]
    # Check for magic bytes
    if magic_bytes != b"PlZ":
        raise Exception(
            f"not a compressed Palworld save, found {magic_bytes} instead of P1Z"
        )
    # Valid save types
    if save_type not in [0x30, 0x31, 0x32]:
        raise Exception(f"unknown save type: {save_type}")
    # We only have 0x31 (single zlib) and 0x32 (double zlib) saves
    if save_type not in [0x31, 0x32]:
        raise Exception(f"unhandled compression type: {save_type}")
    if save_type == 0x31:
        # Check if the compressed length is correct
        if compressed_len != len(data) - 12:
            raise Exception(f"incorrect compressed length: {compressed_len}")
    # Decompress file
    uncompressed_data = zlib.decompress(data[12:])
    if save_type == 0x32:
        # Check if the compressed length is correct
        if compressed_len != len(uncompressed_data):
            raise Exception(f"incorrect compressed length: {compressed_len}")
        # Decompress file
        uncompressed_data = zlib.decompress(uncompressed_data)
    # Check if the uncompressed length is correct
    if uncompressed_len != len(uncompressed_data):
        raise Exception(f"incorrect uncompressed length: {uncompressed_len}")

    return uncompressed_data, save_type


def compress_gvas_to_sav(data: bytes, save_type: int) -> bytes:
    uncompressed_len = len(data)
    compressed_data = zlib.compress(data)
    compressed_len = len(compressed_data)
    if save_type == 0x32:
        compressed_data = zlib.compress(compressed_data)

    # Create a byte array and append the necessary information
    result = bytearray()
    result.extend(uncompressed_len.to_bytes(4, byteorder="little"))
    result.extend(compressed_len.to_bytes(4, byteorder="little"))
    result.extend(b"PlZ")
    result.extend(bytes([save_type]))
    result.extend(compressed_data)

    return bytes(result)
