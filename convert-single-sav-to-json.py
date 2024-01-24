#!/usr/bin/env python3

import json
import os
import sys
from lib.noindent import *
from lib.palsav import *
from lib.rawdata import *


def main():
    # Check if argument exists
    if len(sys.argv) < 3:
        print(sys.argv[0] + " <path to uesave.exe> <path to .sav file>")
        exit(1)
    # Take the first argument as the path to uesave.exe
    uesave_path = sys.argv[1]
    if not os.path.exists(uesave_path):
        print(f"uesave does not exist at {uesave_path}")
        exit(1)
    # Take the second argument as a path to a save file
    save_path = sys.argv[2]
    if not os.path.exists(save_path):
        print(f"Path {save_path} does not exist")
        exit(1)
    print(f"Converting {save_path} to JSON (using {uesave_path})")
    json_blob = convert_to_json(uesave_path, save_path)
    if "worldSaveData" in json_blob["root"]["properties"]:
        print("Decoding GroupSaveDataMap")
        decode_group_data(json_blob)
        print("Decoding CharacterSaveParameterMap")
        decode_character_data(json_blob)
    output_path = save_path + ".json"
    print(f"Writing JSON to {output_path}")
    with open(output_path, "w") as f:
        json.dump(json_blob, f, indent=2, cls=CustomEncoder, ensure_ascii=False)


if __name__ == "__main__":
    main()
