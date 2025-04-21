from typing import Any, Sequence, Optional

from palworld_save_tools.archive import *


def decode(
    reader: FArchiveReader, type_name: str, size: int, path: str
) -> dict[str, Any]:
    if type_name != "MapProperty":
        raise Exception(f"Expected MapProperty, got {type_name}")
    value = reader.property(type_name, size, path, nested_caller_path=path)
    # Decode the raw bytes and replace the raw data
    group_map = value["value"]
    for group in group_map:
        try:
            group_type = group["value"]["GroupType"]["value"]["value"]
            group_bytes = group["value"]["RawData"]["value"]["values"]
            group["value"]["RawData"]["value"] = decode_bytes(
                reader, group_bytes, group_type
            )
        except Exception as e:
            print(f"Error decoding group of type {group.get('value', {}).get('GroupType', {}).get('value', {}).get('value', 'unknown')}: {e}")
            # Keep the raw bytes if we can't decode
            if "value" in group and "RawData" in group["value"] and "value" in group["value"]["RawData"]:
                group["value"]["RawData"]["value"] = {"values": group_bytes, "error": str(e)}
    return value


def decode_bytes(
    parent_reader: FArchiveReader, group_bytes: Sequence[int], group_type: str
) -> dict[str, Any]:
    if len(group_bytes) == 0:
        return {"values": []}

    try:
        reader = parent_reader.internal_copy(bytes(group_bytes), debug=False)
        group_data = {
            "group_type": group_type,
            "group_id": reader.guid(),
            "group_name": reader.fstring(),
            "individual_character_handle_ids": reader.tarray(instance_id_reader),
        }

        # Handle organization-type groups
        if group_type in [
            "EPalGroupType::Guild",
            "EPalGroupType::IndependentGuild",
            "EPalGroupType::Organization",
        ]:
            # Check that we have enough data before reading
            if reader.data.tell() + 1 > len(reader.data.getvalue()):
                print(f"Warning: Not enough data to read org_type for {group_type}")
                group_data["org_type"] = 0  # Default value
            else:
                group_data["org_type"] = reader.byte()

            # Check that we have enough data for the tarray header
            if reader.data.tell() + 4 > len(reader.data.getvalue()):
                print(f"Warning: Not enough data to read base_ids for {group_type}")
                group_data["base_ids"] = []  # Empty list
            else:
                group_data["base_ids"] = reader.tarray(uuid_reader)

        # Handle guild-specific data
        if group_type in ["EPalGroupType::Guild", "EPalGroupType::IndependentGuild"]:
            if reader.data.tell() + 4 > len(reader.data.getvalue()):
                print(f"Warning: Not enough data to read base_camp_level for {group_type}")
                group_data["base_camp_level"] = 0  # Default value
            else:
                group_data["base_camp_level"] = reader.i32()

            if reader.data.tell() + 4 > len(reader.data.getvalue()):
                print(f"Warning: Not enough data to read map_object_instance_ids_base_camp_points for {group_type}")
                group_data["map_object_instance_ids_base_camp_points"] = []  # Empty list
            else:
                group_data["map_object_instance_ids_base_camp_points"] = reader.tarray(uuid_reader)

            if reader.data.tell() + 4 > len(reader.data.getvalue()):
                print(f"Warning: Not enough data to read guild_name for {group_type}")
                group_data["guild_name"] = ""  # Empty string
            else:
                group_data["guild_name"] = reader.fstring()

        # Handle independent guild data
        if group_type == "EPalGroupType::IndependentGuild":
            if reader.data.tell() + 16 > len(reader.data.getvalue()):
                print(f"Warning: Not enough data to read player_uid for {group_type}")
                group_data["player_uid"] = UUID(bytes(b'\0' * 16))  # Default UUID
            else:
                group_data["player_uid"] = reader.guid()

            if reader.data.tell() + 4 > len(reader.data.getvalue()):
                print(f"Warning: Not enough data to read guild_name_2 for {group_type}")
                group_data["guild_name_2"] = ""  # Empty string
            else:
                group_data["guild_name_2"] = reader.fstring()

            if reader.data.tell() + 12 > len(reader.data.getvalue()):
                print(f"Warning: Not enough data to read player_info for {group_type}")
                group_data["player_info"] = {
                    "last_online_real_time": 0,
                    "player_name": "",
                }
            else:
                group_data["player_info"] = {
                    "last_online_real_time": reader.i64(),
                    "player_name": reader.fstring(),
                }

        # Handle guild data
        if group_type == "EPalGroupType::Guild":
            if reader.data.tell() + 16 > len(reader.data.getvalue()):
                print(f"Warning: Not enough data to read admin_player_uid for {group_type}")
                group_data["admin_player_uid"] = UUID(bytes(b'\0' * 16))  # Default UUID
            else:
                group_data["admin_player_uid"] = reader.guid()

            if reader.data.tell() + 4 > len(reader.data.getvalue()):
                print(f"Warning: Not enough data to read player_count for {group_type}")
                group_data["players"] = []  # Empty list
            else:
                player_count = reader.i32()
                group_data["players"] = []
                for _ in range(player_count):
                    if reader.data.tell() + 16 > len(reader.data.getvalue()):
                        print(f"Warning: Not enough data to read player_uid in players for {group_type}")
                        break

                    try:
                        player = {
                            "player_uid": reader.guid(),
                            "player_info": {
                                "last_online_real_time": reader.i64(),
                                "player_name": reader.fstring(),
                            },
                        }
                        group_data["players"].append(player)
                    except Exception as e:
                        print(f"Error reading player in players for {group_type}: {e}")
                        break

        # Store any trailing data
        if not reader.eof():
            group_data["trailing_unparsed_data"] = [b for b in reader.read_to_end()]

        return group_data
    except Exception as e:
        print(f"Error decoding group data of type {group_type}: {e}")
        # Return what we have with an error flag
        return {"group_type": group_type, "values": group_bytes, "error": str(e)}


def encode(
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
        encoded_bytes = encode_bytes(p)
        group["value"]["RawData"]["value"] = {"values": [b for b in encoded_bytes]}
    return writer.property_inner(property_type, properties)


def encode_bytes(p: dict[str, Any]) -> bytes:
    # If there's an error flag or if it's already in the correct format, return the raw bytes
    if "error" in p or "values" in p:
        if isinstance(p.get("values"), list):
            return bytes(p["values"])
        return bytes()

    writer = FArchiveWriter()
    writer.guid(p["group_id"])
    writer.fstring(p["group_name"])
    writer.tarray(instance_id_writer, p["individual_character_handle_ids"])
    if p["group_type"] in [
        "EPalGroupType::Guild",
        "EPalGroupType::IndependentGuild",
        "EPalGroupType::Organization",
    ]:
        writer.byte(p["org_type"])
        writer.tarray(uuid_writer, p["base_ids"])
    if p["group_type"] in ["EPalGroupType::Guild", "EPalGroupType::IndependentGuild"]:
        writer.i32(p["base_camp_level"])
        writer.tarray(uuid_writer, p["map_object_instance_ids_base_camp_points"])
        writer.fstring(p["guild_name"])
    if p["group_type"] == "EPalGroupType::IndependentGuild":
        writer.guid(p["player_uid"])
        writer.fstring(p["guild_name_2"])
        writer.i64(p["player_info"]["last_online_real_time"])
        writer.fstring(p["player_info"]["player_name"])
    if p["group_type"] == "EPalGroupType::Guild":
        writer.guid(p["admin_player_uid"])
        writer.i32(len(p["players"]))
        for i in range(len(p["players"])):
            writer.guid(p["players"][i]["player_uid"])
            writer.i64(p["players"][i]["player_info"]["last_online_real_time"])
            writer.fstring(p["players"][i]["player_info"]["player_name"])
    if "trailing_unparsed_data" in p:
        writer.write(bytes(p["trailing_unparsed_data"]))
    encoded_bytes = writer.bytes()
    return encoded_bytes
