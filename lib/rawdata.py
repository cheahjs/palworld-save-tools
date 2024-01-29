from typing import Any, Sequence

from lib.archive import *


def decode_group_data(
    reader: FArchiveReader, type_name: str, size: int, path: str
) -> dict[str, Any]:
    if type_name != "MapProperty":
        raise Exception(f"Expected MapProperty, got {type_name}")
    value = reader.property(type_name, size, path, allow_custom=False)
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
        "group_id": reader.guid(),
        "group_name": reader.fstring(),
        "individual_character_handle_ids": reader.tarray(instance_id_reader),
    }
    if group_type in [
        "EPalGroupType::Guild",
        "EPalGroupType::IndependentGuild",
        "EPalGroupType::Organization",
    ]:
        org = {
            "org_type": reader.byte(),
            "base_ids": reader.tarray(uuid_reader),
        }
        group_data |= org
    if group_type in ["EPalGroupType::Guild", "EPalGroupType::IndependentGuild"]:
        guild = {
            "base_camp_level": reader.i32(),
            "map_object_instance_ids_base_camp_points": reader.tarray(uuid_reader),
            "guild_name": reader.fstring(),
        }
        group_data |= guild
    if group_type == "EPalGroupType::IndependentGuild":
        indie = {
            "player_uid": reader.guid(),
            "guild_name_2": reader.fstring(),
            "player_info": {
                "last_online_real_time": reader.i64(),
                "player_name": reader.fstring(),
            },
        }
        group_data |= indie
    if group_type == "EPalGroupType::Guild":
        guild = {"admin_player_uid": reader.guid(), "players": []}
        player_count = reader.i32()
        for _ in range(player_count):
            player = {
                "player_uid": reader.guid(),
                "player_info": {
                    "last_online_real_time": reader.i64(),
                    "player_name": reader.fstring(),
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
    return writer.property_inner(property_type, properties)


def encode_group_data_bytes(p: dict[str, Any]) -> bytes:
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
    encoded_bytes = writer.bytes()
    return encoded_bytes


def decode_character_data(
    reader: FArchiveReader, type_name: str, size: int, path: str
) -> dict[str, Any]:
    if type_name != "ArrayProperty":
        raise Exception(f"Expected ArrayProperty, got {type_name}")
    value = reader.property(type_name, size, path, allow_custom=False)
    char_bytes = value["value"]["values"]
    value["value"] = decode_character_data_bytes(char_bytes)
    return value


def decode_character_data_bytes(char_bytes: Sequence[int]) -> dict[str, Any]:
    reader = FArchiveReader(bytes(char_bytes))
    char_data = {}
    char_data["object"] = reader.properties_until_end()
    char_data["unknown_bytes"] = reader.byte_list(4)
    char_data["group_id"] = reader.guid()
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
    return writer.property_inner(property_type, properties)


def encode_character_data_bytes(p: dict[str, Any]) -> bytes:
    writer = FArchiveWriter()
    writer.properties(p["object"])
    writer.write(bytes(p["unknown_bytes"]))
    writer.guid(p["group_id"])
    encoded_bytes = writer.bytes()
    return encoded_bytes


def decode_debug(
    reader: FArchiveReader, type_name: str, size: int, path: str
) -> dict[str, Any]:
    if type_name != "ArrayProperty":
        raise Exception(f"Expected ArrayProperty, got {type_name}")
    value = reader.property(type_name, size, path, allow_custom=False)
    debug_bytes = value["value"]["values"]
    if len(debug_bytes) > 0:
        print("".join(f"{b:02x}" for b in debug_bytes))
        # print(bytes(debug_bytes))
    return value


def encode_debug(
    writer: FArchiveWriter, property_type: str, properties: dict[str, Any]
) -> int:
    if property_type != "ArrayProperty":
        raise Exception(f"Expected ArrayProperty, got {property_type}")
    del properties["custom_type"]
    return writer.property_inner(property_type, properties)


def decode_build_process(
    reader: FArchiveReader, type_name: str, size: int, path: str
) -> dict[str, Any]:
    if type_name != "ArrayProperty":
        raise Exception(f"Expected ArrayProperty, got {type_name}")
    value = reader.property(type_name, size, path, allow_custom=False)
    data_bytes = value["value"]["values"]
    value["value"] = decode_build_process_bytes(data_bytes)
    return value


def decode_build_process_bytes(b_bytes: Sequence[int]) -> dict[str, Any]:
    reader = FArchiveReader(bytes(b_bytes))
    data = {}
    data["state"] = reader.byte()
    data["id"] = reader.guid()
    if not reader.eof():
        raise Exception("Warning: EOF not reached")
    return data


def encode_build_process(
    writer: FArchiveWriter, property_type: str, properties: dict[str, Any]
) -> int:
    if property_type != "ArrayProperty":
        raise Exception(f"Expected ArrayProperty, got {property_type}")
    del properties["custom_type"]
    encoded_bytes = encode_build_process_bytes(properties["value"])
    properties["value"] = {"values": [b for b in encoded_bytes]}
    return writer.property_inner(property_type, properties)


def encode_build_process_bytes(p: dict[str, Any]) -> bytes:
    writer = FArchiveWriter()
    writer.byte(p["state"])
    writer.guid(p["id"])
    encoded_bytes = writer.bytes()
    return encoded_bytes


def decode_connector(
    reader: FArchiveReader, type_name: str, size: int, path: str
) -> dict[str, Any]:
    if type_name != "ArrayProperty":
        raise Exception(f"Expected ArrayProperty, got {type_name}")
    value = reader.property(type_name, size, path, allow_custom=False)
    data_bytes = value["value"]["values"]
    value["value"] = decode_connector_bytes(data_bytes)
    return value


def connect_info_item_reader(reader: FArchiveReader) -> dict[str, Any]:
    return {
        "connect_to_model_instance_id": reader.guid(),
        "index": reader.byte(),
    }


def connect_info_item_writer(writer: FArchiveWriter, properties: dict[str, Any]):
    writer.guid(properties["connect_to_model_instance_id"])
    writer.byte(properties["index"])


def decode_connector_bytes(c_bytes: Sequence[int]) -> dict[str, Any]:
    if len(c_bytes) == 0:
        return None
    reader = FArchiveReader(bytes(c_bytes))
    data = {}
    data["supported_level"] = reader.i32()
    data["connect"] = {
        "index": reader.byte(),
        "any_place": reader.tarray(connect_info_item_reader),
    }
    # We are guessing here, we don't have information about the type without mapping object names -> types
    # Stairs have 2 connectors (up and down),
    # Roofs have 4 connectors (front, back, right, left)
    if not reader.eof():
        data["other_connectors"] = []
        while not reader.eof():
            data["other_connectors"].append(
                {
                    "index": reader.byte(),
                    "connect": reader.tarray(connect_info_item_reader),
                }
            )
        if len(data["other_connectors"]) not in [2, 4]:
            print(
                f"Warning: unknown connector type with {len(data['other_connectors'])} connectors"
            )
    return data


def encode_connector(
    writer: FArchiveWriter, property_type: str, properties: dict[str, Any]
) -> int:
    if property_type != "ArrayProperty":
        raise Exception(f"Expected ArrayProperty, got {property_type}")
    del properties["custom_type"]
    encoded_bytes = encode_connector_bytes(properties["value"])
    properties["value"] = {"values": [b for b in encoded_bytes]}
    return writer.property_inner(property_type, properties)


def encode_connector_bytes(p: dict[str, Any]) -> bytes:
    if p is None:
        return bytes()
    writer = FArchiveWriter()
    writer.i32(p["supported_level"])
    writer.byte(p["connect"]["index"])
    writer.tarray(connect_info_item_writer, p["connect"]["any_place"])
    if "other_connectors" in p:
        for other in p["other_connectors"]:
            writer.byte(other["index"])
            writer.tarray(connect_info_item_writer, other["connect"])
    encoded_bytes = writer.bytes()
    return encoded_bytes


def decode_map_model(
    reader: FArchiveReader, type_name: str, size: int, path: str
) -> dict[str, Any]:
    if type_name != "ArrayProperty":
        raise Exception(f"Expected ArrayProperty, got {type_name}")
    value = reader.property(type_name, size, path, allow_custom=False)
    data_bytes = value["value"]["values"]
    value["value"] = decode_map_model_bytes(data_bytes)
    return value


def decode_map_model_bytes(m_bytes: Sequence[int]) -> dict[str, Any]:
    reader = FArchiveReader(bytes(m_bytes))
    data = {}
    data["instance_id"] = reader.guid()
    data["concrete_model_instance_id"] = reader.guid()
    data["base_camp_id_belong_to"] = reader.guid()
    data["group_id_belong_to"] = reader.guid()
    data["hp"] = {
        "current": reader.i32(),
        "max": reader.i32(),
    }
    data["initital_transform_cache"] = {
        "rotation": {
            "x": reader.double(),
            "y": reader.double(),
            "z": reader.double(),
            "w": reader.double(),
        },
        "translation": {
            "x": reader.double(),
            "y": reader.double(),
            "z": reader.double(),
        },
        "scale3d": {
            "x": reader.double(),
            "y": reader.double(),
            "z": reader.double(),
        },
    }
    data["repair_work_id"] = reader.guid()
    data["owner_spawner_level_object_instance_id"] = reader.guid()
    data["owner_instance_id"] = reader.guid()
    data["build_player_uid"] = reader.guid()
    data["interact_restrict_type"] = reader.byte()
    data["stage_instance_id_belong_to"] = {
        "id": reader.guid(),
        "valid": reader.u32() > 0,
    }
    data["created_at"] = reader.i64()
    if not reader.eof():
        raise Exception("Warning: EOF not reached")
    return data


def encode_map_model(
    writer: FArchiveWriter, property_type: str, properties: dict[str, Any]
) -> int:
    if property_type != "ArrayProperty":
        raise Exception(f"Expected ArrayProperty, got {property_type}")
    del properties["custom_type"]
    encoded_bytes = encode_map_model_bytes(properties["value"])
    properties["value"] = {"values": [b for b in encoded_bytes]}
    return writer.property_inner(property_type, properties)


def encode_map_model_bytes(p: dict[str, Any]) -> bytes:
    writer = FArchiveWriter()

    writer.guid(p["instance_id"])
    writer.guid(p["concrete_model_instance_id"])
    writer.guid(p["base_camp_id_belong_to"])
    writer.guid(p["group_id_belong_to"])

    writer.i32(p["hp"]["current"])
    writer.i32(p["hp"]["max"])

    writer.double(p["initital_transform_cache"]["rotation"]["x"])
    writer.double(p["initital_transform_cache"]["rotation"]["y"])
    writer.double(p["initital_transform_cache"]["rotation"]["z"])
    writer.double(p["initital_transform_cache"]["rotation"]["w"])

    writer.double(p["initital_transform_cache"]["translation"]["x"])
    writer.double(p["initital_transform_cache"]["translation"]["y"])
    writer.double(p["initital_transform_cache"]["translation"]["z"])

    writer.double(p["initital_transform_cache"]["scale3d"]["x"])
    writer.double(p["initital_transform_cache"]["scale3d"]["y"])
    writer.double(p["initital_transform_cache"]["scale3d"]["z"])

    writer.guid(p["repair_work_id"])
    writer.guid(p["owner_spawner_level_object_instance_id"])
    writer.guid(p["owner_instance_id"])
    writer.guid(p["build_player_uid"])

    writer.byte(p["interact_restrict_type"])

    writer.guid(p["stage_instance_id_belong_to"]["id"])
    writer.u32(1 if p["stage_instance_id_belong_to"]["valid"] else 0)

    writer.i64(p["created_at"])

    encoded_bytes = writer.bytes()
    return encoded_bytes


def decode_map_concrete_model(
    reader: FArchiveReader, type_name: str, size: int, path: str
) -> dict[str, Any]:
    if type_name != "StructProperty":
        raise Exception(f"Expected StructProperty, got {type_name}")
    value = reader.property(type_name, size, path, allow_custom=False)
    # Decode the raw bytes for the map object and replace the raw data
    raw_bytes = value["value"]["RawData"]["value"]["values"]
    print("".join(f"{b:02x}" for b in raw_bytes))
    # value["value"]["RawData"]["value"] = decode_map_concrete_model_bytes(raw_bytes)
    # Decode the raw bytes for the module map and replace the raw data
    # group_map = value["value"]
    # for group in group_map:
    #     group_type = group["value"]["GroupType"]["value"]["value"]
    #     group_bytes = group["value"]["RawData"]["value"]["values"]
    #     group["value"]["RawData"]["value"] = decode_map_concrete_model_bytes(
    #         group_bytes, group_type
    #     )
    # EPalMapObjectConcreteModelModuleType::None = 0,
    # EPalMapObjectConcreteModelModuleType::ItemContainer = 1,
    # EPalMapObjectConcreteModelModuleType::CharacterContainer = 2,
    # EPalMapObjectConcreteModelModuleType::Workee = 3,
    # EPalMapObjectConcreteModelModuleType::Energy = 4,
    # EPalMapObjectConcreteModelModuleType::StatusObserver = 5,
    # EPalMapObjectConcreteModelModuleType::ItemStack = 6,
    # EPalMapObjectConcreteModelModuleType::Switch = 7,
    # EPalMapObjectConcreteModelModuleType::PlayerRecord = 8,
    # EPalMapObjectConcreteModelModuleType::BaseCampPassiveEffect = 9,
    # EPalMapObjectConcreteModelModuleType::PasswordLock = 10,
    return value


def decode_map_concrete_model_bytes(m_bytes: Sequence[int]) -> dict[str, Any]:
    if len(m_bytes) == 0:
        return None
    reader = FArchiveReader(bytes(m_bytes))
    map_concrete_model = {}

    if not reader.eof():
        raise Exception("Warning: EOF not reached")
    return map_concrete_model


def encode_map_concrete_model(
    writer: FArchiveWriter, property_type: str, properties: dict[str, Any]
) -> int:
    if property_type != "MapProperty":
        raise Exception(f"Expected MapProperty, got {property_type}")
    del properties["custom_type"]
    # encoded_bytes = encode_map_concrete_model_bytes(properties["value"]["RawData"]["value"])
    # properties["value"]["RawData"]["value"] = {"values": [b for b in encoded_bytes]}
    return writer.property_inner(property_type, properties)


def encode_map_concrete_model_bytes(p: dict[str, Any]) -> bytes:
    writer = FArchiveWriter()

    encoded_bytes = writer.bytes()
    return encoded_bytes
