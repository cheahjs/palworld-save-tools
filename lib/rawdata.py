from typing import Any, Sequence
from lib.archive import *


def decode_group_data(
    reader: FArchiveReader, type_name: str, size: int, path: str
) -> dict[str, Any]:
    if type_name != "MapProperty":
        raise Exception(f"Expected MapProperty, got {type_name}")
    value = reader.read_property(type_name, size, path, allow_custom=False)
    # Decode the raw bytes and replace the raw data
    group_map = value["value"]
    for group in group_map:
        group_type = group["value"]["GroupType"]["value"]["value"]
        group_bytes = group["value"]["RawData"]["value"]["values"]
        group["value"]["RawData"]["value"] = decode_group_data_bytes(
            group_bytes, group_type
        )
    return value


def decode_group_data_bytes(
    group_bytes: Sequence[int], group_type: str
) -> dict[str, Any]:
    reader = FArchiveReader(bytes(group_bytes))
    group_data = {
        "group_type": group_type,
        "group_id": reader.read_uuid(),
        "group_name": reader.read_fstring(),
        "individual_character_handle_ids": reader.read_tarray(instance_id_reader),
    }
    if group_type in [
        "EPalGroupType::Guild",
        "EPalGroupType::IndependentGuild",
        "EPalGroupType::Organization",
    ]:
        org = {
            "org_type": reader.read_byte(),
            "base_ids": reader.read_tarray(uuid_reader),
        }
        group_data |= org
    if group_type in ["EPalGroupType::Guild", "EPalGroupType::IndependentGuild"]:
        guild = {
            "base_camp_level": reader.read_int32(),
            "map_object_instance_ids_base_camp_points": reader.read_tarray(uuid_reader),
            "guild_name": reader.read_fstring(),
        }
        group_data |= guild
    if group_type == "EPalGroupType::IndependentGuild":
        indie = {
            "player_uid": reader.read_uuid(),
            "guild_name_2": reader.read_fstring(),
            "player_info": {
                "last_online_real_time": reader.read_int64(),
                "player_name": reader.read_fstring(),
            },
        }
        group_data |= indie
    if group_type == "EPalGroupType::Guild":
        guild = {"admin_player_uid": reader.read_uuid(), "players": []}
        player_count = reader.read_int32()
        for _ in range(player_count):
            player = {
                "player_uid": reader.read_uuid(),
                "player_info": {
                    "last_online_real_time": reader.read_int64(),
                    "player_name": reader.read_fstring(),
                },
            }
            guild["players"].append(player)
        group_data |= guild
    if not reader.eof():
        raise Exception("Warning: EOF not reached")
    return group_data


def encode_group_data(
    writer: FArchiveWriter, property_type: str, properties: dict[str, Any]
) -> int:
    if property_type != "MapProperty":
        raise Exception(f"Expected MapProperty, got {property_type}")
    del properties["custom_type"]
    group_map = properties["value"]
    for group in group_map:
        if "values" in group["value"]["RawData"]["value"]:
            continue
        p = group["value"]["RawData"]["value"]
        encoded_bytes = encode_group_data_bytes(p)
        group["value"]["RawData"]["value"] = {"values": [b for b in encoded_bytes]}
    return writer.write_property_inner(property_type, properties)


def encode_group_data_bytes(p: dict[str, Any]) -> bytes:
    writer = FArchiveWriter()
    writer.write_uuid(p["group_id"])
    writer.write_fstring(p["group_name"])
    writer.write_tarray(instance_id_writer, p["individual_character_handle_ids"])
    if p["group_type"] in [
        "EPalGroupType::Guild",
        "EPalGroupType::IndependentGuild",
        "EPalGroupType::Organization",
    ]:
        writer.write_byte(p["org_type"])
        writer.write_tarray(uuid_writer, p["base_ids"])
    if p["group_type"] in ["EPalGroupType::Guild", "EPalGroupType::IndependentGuild"]:
        writer.write_int32(p["base_camp_level"])
        writer.write_tarray(uuid_writer, p["map_object_instance_ids_base_camp_points"])
        writer.write_fstring(p["guild_name"])
    if p["group_type"] == "EPalGroupType::IndependentGuild":
        writer.write_uuid(p["player_uid"])
        writer.write_fstring(p["guild_name_2"])
        writer.write_int64(p["player_info"]["last_online_real_time"])
        writer.write_fstring(p["player_info"]["player_name"])
    if p["group_type"] == "EPalGroupType::Guild":
        writer.write_uuid(p["admin_player_uid"])
        writer.write_int32(len(p["players"]))
        for i in range(len(p["players"])):
            writer.write_uuid(p["players"][i]["player_uid"])
            writer.write_int64(p["players"][i]["player_info"]["last_online_real_time"])
            writer.write_fstring(p["players"][i]["player_info"]["player_name"])
    encoded_bytes = writer.bytes()
    return encoded_bytes


def decode_character_data(
    reader: FArchiveReader, type_name: str, size: int, path: str
) -> dict[str, Any]:
    if type_name != "ArrayProperty":
        raise Exception(f"Expected ArrayProperty, got {type_name}")
    value = reader.read_property(type_name, size, path, allow_custom=False)
    char_bytes = value["value"]["values"]
    value["value"] = decode_character_data_bytes(char_bytes)
    return value


def decode_character_data_bytes(char_bytes: Sequence[int]) -> dict[str, Any]:
    reader = FArchiveReader(bytes(char_bytes))
    char_data = {}
    char_data["object"] = reader.read_properties_until_end()
    char_data["unknown_bytes"] = reader.read_bytes(4)
    char_data["group_id"] = reader.read_uuid()
    if not reader.eof():
        raise Exception("Warning: EOF not reached")
    return char_data


def encode_character_data(
    writer: FArchiveWriter, property_type: str, properties: dict[str, Any]
) -> int:
    if property_type != "ArrayProperty":
        raise Exception(f"Expected ArrayProperty, got {property_type}")
    del properties["custom_type"]
    encoded_bytes = encode_character_data_bytes(properties["value"])
    properties["value"] = {"values": [b for b in encoded_bytes]}
    return writer.write_property_inner(property_type, properties)


def encode_character_data_bytes(p: dict[str, Any]) -> bytes:
    writer = FArchiveWriter()
    writer.write_properties(p["object"])
    writer.write_bytes(bytes(p["unknown_bytes"]))
    writer.write_uuid(p["group_id"])
    encoded_bytes = writer.bytes()
    return encoded_bytes
