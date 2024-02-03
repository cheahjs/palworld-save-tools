from typing import Any, Sequence

from palworld_save_tools.archive import *


@dataclasses.dataclass(slots=True)
class FoliageModelWorldTransform(SerializableBase):
    rotator: Rotator
    location: FVector
    scale_x: Optional[float]


@dataclasses.dataclass(slots=True)
class FoliageModelInstance(SerializableBase):
    model_instance_id: UUID
    world_transform: dict[str, Any]
    hp: int


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
    parent_reader: FArchiveReader, b_bytes: Sequence[int]
) -> dict[str, Any]:
    reader = parent_reader.internal_copy(bytes(b_bytes), debug=False)
    model_instance_id = reader.guid()
    rotator = reader.compressed_short_rotator()
    x, y, z = reader.packed_vector(1)
    scale_x = reader.float()
    hp = reader.i32()
    if not reader.eof():
        raise Exception("Warning: EOF not reached")
    return FoliageModelInstance(
        model_instance_id=model_instance_id,
        world_transform=FoliageModelWorldTransform(
            rotator=rotator, location=FVector(x, y, z), scale_x=scale_x
        ),
        hp=hp,
    )


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

    writer.guid(p["model_instance_id"])
    writer.compressed_short_rotator(
        p["world_transform"]["rotator"]["pitch"],
        p["world_transform"]["rotator"]["yaw"],
        p["world_transform"]["rotator"]["roll"],
    )
    writer.packed_vector(
        1,
        p["world_transform"]["location"]["x"],
        p["world_transform"]["location"]["y"],
        p["world_transform"]["location"]["z"],
    )
    writer.float(p["world_transform"]["scale_x"])
    writer.i32(p["hp"])

    encoded_bytes = writer.bytes()
    return encoded_bytes
