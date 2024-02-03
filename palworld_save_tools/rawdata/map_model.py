from typing import Any, Sequence

from palworld_save_tools.archive import *


@dataclasses.dataclass(slots=True)
class Hp(SerializableBase):
    current: int
    max: int


@dataclasses.dataclass(slots=True)
class InstanceIdBelongTo(SerializableBase):
    id: UUID
    valid: bool


@dataclasses.dataclass(slots=True)
class MapModel(SerializableBase):
    instance_id: UUID
    concrete_model_instance_id: UUID
    base_camp_id_belong_to: UUID
    group_id_belong_to: UUID
    hp: Hp
    initital_transform_cache: FTransform
    repair_work_id: UUID
    owner_spawner_level_object_instance_id: UUID
    owner_instance_id: UUID
    build_player_uid: UUID
    interact_restrict_type: int
    stage_instance_id_belong_to: InstanceIdBelongTo
    created_at: int


def decode(
    reader: FArchiveReader, type_name: str, size: int, path: str
) -> dict[str, Any]:
    if type_name != "ArrayProperty":
        raise Exception(f"Expected ArrayProperty, got {type_name}")
    value = reader.property(type_name, size, path, nested_caller_path=path)
    data_bytes = value["value"]["values"]
    value["value"] = decode_bytes(reader, data_bytes)
    return value


def decode_bytes(
    parent_reader: FArchiveReader, m_bytes: Sequence[int]
) -> dict[str, Any]:
    reader = parent_reader.internal_copy(bytes(m_bytes), debug=False)
    data = MapModel(
        instance_id=reader.guid(),
        concrete_model_instance_id=reader.guid(),
        base_camp_id_belong_to=reader.guid(),
        group_id_belong_to=reader.guid(),
        hp=Hp(
            current=reader.i32(),
            max=reader.i32(),
        ),
        initital_transform_cache=reader.ftransform(),
        repair_work_id=reader.guid(),
        owner_spawner_level_object_instance_id=reader.guid(),
        owner_instance_id=reader.guid(),
        build_player_uid=reader.guid(),
        interact_restrict_type=reader.byte(),
        stage_instance_id_belong_to=InstanceIdBelongTo(
            id=reader.guid(),
            valid=reader.u32() > 0,
        ),
        created_at=reader.i64(),
    )
    if not reader.eof():
        raise Exception("Warning: EOF not reached")
    return data


def encode(
    writer: FArchiveWriter, property_type: str, properties: dict[str, Any]
) -> int:
    if property_type != "ArrayProperty":
        raise Exception(f"Expected ArrayProperty, got {property_type}")
    del properties["custom_type"]
    encoded_bytes = encode_bytes(properties["value"])
    properties["value"] = {"values": [b for b in encoded_bytes]}
    return writer.property_inner(property_type, properties)


def encode_bytes(p: dict[str, Any]) -> bytes:
    writer = FArchiveWriter()

    writer.guid(p["instance_id"])
    writer.guid(p["concrete_model_instance_id"])
    writer.guid(p["base_camp_id_belong_to"])
    writer.guid(p["group_id_belong_to"])

    writer.i32(p["hp"]["current"])
    writer.i32(p["hp"]["max"])

    writer.ftransform(p["initital_transform_cache"])

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
