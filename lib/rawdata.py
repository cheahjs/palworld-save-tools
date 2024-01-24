import os
from lib.noindent import NoIndent
from lib.reader import *
from lib.writer import *


def decode_group_data(level_json):
    group_map = level_json["root"]["properties"]["worldSaveData"]["Struct"]["value"][
        "Struct"
    ]["GroupSaveDataMap"]["Map"]["value"]
    for group in group_map:
        group_type = group["value"]["Struct"]["Struct"]["GroupType"]["Enum"]["value"]
        group_bytes = group["value"]["Struct"]["Struct"]["RawData"]["Array"]["value"][
            "Base"
        ]["Byte"]["Byte"]
        if isinstance(group_bytes, NoIndent):
            group_bytes = group_bytes.value
        group["value"]["Struct"]["Struct"]["RawData"][
            "Parsed"
        ] = decode_group_data_bytes(group_bytes, group_type)
        if os.environ.get("DEBUG", "0") != "1":
            del group["value"]["Struct"]["Struct"]["RawData"]["Array"]["value"]["Base"][
                "Byte"
            ]["Byte"]


def decode_group_data_bytes(group_bytes, group_type):
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


def encode_group_data(level_json):
    group_map = level_json["root"]["properties"]["worldSaveData"]["Struct"]["value"][
        "Struct"
    ]["GroupSaveDataMap"]["Map"]["value"]
    for group in group_map:
        if "Parsed" not in group["value"]["Struct"]["Struct"]["RawData"]:
            continue
        p = group["value"]["Struct"]["Struct"]["RawData"]["Parsed"]
        print(
            f'Encoding group ID:{p["group_id"]} Type:{p["group_type"]} Name:{p["group_name"]}'
        )
        encoded_bytes = encode_group_data_bytes(p)
        group["value"]["Struct"]["Struct"]["RawData"]["Array"]["value"]["Base"]["Byte"][
            "Byte"
        ] = [b for b in encoded_bytes]
        if os.environ.get("DEBUG", "0") != "1":
            del group["value"]["Struct"]["Struct"]["RawData"]["Parsed"]


def encode_group_data_bytes(p):
    writer = FArchiveWriter()
    writer.write_uuid_str(p["group_id"])
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
        writer.write_uuid_str(p["player_uid"])
        writer.write_fstring(p["guild_name_2"])
        writer.write_int64(p["player_info"]["last_online_real_time"])
        writer.write_fstring(p["player_info"]["player_name"])
    if p["group_type"] == "EPalGroupType::Guild":
        writer.write_uuid_str(p["admin_player_uid"])
        writer.write_int32(len(p["players"]))
        for i in range(len(p["players"])):
            writer.write_uuid_str(p["players"][i]["player_uid"])
            writer.write_int64(p["players"][i]["player_info"]["last_online_real_time"])
            writer.write_fstring(p["players"][i]["player_info"]["player_name"])
    encoded_bytes = writer.bytes()
    return encoded_bytes


def decode_character_data(level_json):
    char_map = level_json["root"]["properties"]["worldSaveData"]["Struct"]["value"][
        "Struct"
    ]["CharacterSaveParameterMap"]["Map"]["value"]
    for char in char_map:
        char_bytes = char["value"]["Struct"]["Struct"]["RawData"]["Array"]["value"][
            "Base"
        ]["Byte"]["Byte"]
        if isinstance(char_bytes, NoIndent):
            char_bytes = char_bytes.value

        char["value"]["Struct"]["Struct"]["RawData"][
            "Parsed"
        ] = decode_character_data_bytes(char_bytes)
        if os.environ.get("DEBUG", "0") != "1":
            del char["value"]["Struct"]["Struct"]["RawData"]["Array"]["value"]["Base"][
                "Byte"
            ]["Byte"]


def decode_character_data_bytes(char_bytes):
    reader = FArchiveReader(bytes(char_bytes))
    char_data = {}
    char_data["object"] = reader.read_properties_until_end()
    char_data["unknown_bytes"] = reader.read_bytes(4)
    char_data["group_id"] = reader.read_uuid()
    if not reader.eof():
        raise Exception("Warning: EOF not reached")
    return char_data


def encode_character_data(level_json):
    char_map = level_json["root"]["properties"]["worldSaveData"]["Struct"]["value"][
        "Struct"
    ]["CharacterSaveParameterMap"]["Map"]["value"]
    for char in char_map:
        if "Parsed" not in char["value"]["Struct"]["Struct"]["RawData"]:
            continue
        p = char["value"]["Struct"]["Struct"]["RawData"]["Parsed"]
        char_uid = char["key"]["Struct"]["Struct"]["PlayerUId"]["Struct"]["value"][
            "Guid"
        ]
        char_instance_id = char["key"]["Struct"]["Struct"]["InstanceId"]["Struct"][
            "value"
        ]["Guid"]
        print(f"Encoding character PlayerUId:{char_uid} InstanceId:{char_instance_id}")
        encoded_bytes = encode_character_data_bytes(p)
        char["value"]["Struct"]["Struct"]["RawData"]["Array"]["value"]["Base"]["Byte"][
            "Byte"
        ] = [b for b in encoded_bytes]
        if os.environ.get("DEBUG", "0") != "1":
            del char["value"]["Struct"]["Struct"]["RawData"]["Parsed"]


def encode_character_data_bytes(p):
    writer = FArchiveWriter()
    writer.write_properties(p["object"])
    writer.write_bytes(bytes(p["unknown_bytes"]))
    writer.write_uuid_str(p["group_id"])
    encoded_bytes = writer.bytes()
    return encoded_bytes
