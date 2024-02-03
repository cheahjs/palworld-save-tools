from typing import Any, Sequence

from palworld_save_tools.archive import *

WORK_BASE_TYPES = set(
    [
        # "EPalWorkableType::Illegal",
        "EPalWorkableType::Progress",
        # "EPalWorkableType::CollectItem",
        # "EPalWorkableType::TransportItem",
        "EPalWorkableType::TransportItemInBaseCamp",
        "EPalWorkableType::ReviveCharacter",
        # "EPalWorkableType::CollectResource",
        "EPalWorkableType::LevelObject",
        "EPalWorkableType::Repair",
        "EPalWorkableType::Defense",
        "EPalWorkableType::BootUp",
        "EPalWorkableType::OnlyJoin",
        "EPalWorkableType::OnlyJoinAndWalkAround",
        "EPalWorkableType::RemoveMapObjectEffect",
        "EPalWorkableType::MonsterFarm",
    ]
)


@dataclasses.dataclass(slots=True)
class AssignLocation(SerializableBase):
    location: FVector
    facing_direction: FVector


@dataclasses.dataclass(slots=True)
class BoxSphereBounds(SerializableBase):
    origin: FVector
    box_extent: FVector
    sphere_radius: Optional[float]


@dataclasses.dataclass(slots=True)
class WorkableBounds(SerializableBase):
    location: FVector
    rotation: FQuat
    box_sphere_bounds: BoxSphereBounds


@dataclasses.dataclass(slots=True)
class WorkableBase(SerializableBase):
    id: UUID
    workable_bounds: dict[str, Any]
    base_camp_id_belong_to: UUID
    owner_map_object_model_id: UUID
    owner_map_object_concrete_model_id: UUID
    current_state: int
    assign_locations: list[AssignLocation]
    behaviour_type: int
    assign_define_data_id: str
    override_work_type: int
    assignable_fixed_type: int
    assignable_otomo: bool
    can_trigger_worker_event: bool
    can_steal_assign: bool
    transform: Optional["WorkableTransformBase"]

    def __init__(
        self,
        id: UUID,
        workable_bounds: WorkableBounds,
        base_camp_id_belong_to: UUID,
        owner_map_object_model_id: UUID,
        owner_map_object_concrete_model_id: UUID,
        current_state: int,
        assign_locations: list[AssignLocation],
        behaviour_type: int,
        assign_define_data_id: str,
        override_work_type: int,
        assignable_fixed_type: int,
        assignable_otomo: bool,
        can_trigger_worker_event: bool,
        can_steal_assign: bool,
        transform: Optional["WorkableTransformBase"] = None,
    ):
        self.id = id
        self.workable_bounds = workable_bounds
        self.base_camp_id_belong_to = base_camp_id_belong_to
        self.owner_map_object_model_id = owner_map_object_model_id
        self.owner_map_object_concrete_model_id = owner_map_object_concrete_model_id
        self.current_state = current_state
        self.assign_locations = assign_locations
        self.behaviour_type = behaviour_type
        self.assign_define_data_id = assign_define_data_id
        self.override_work_type = override_work_type
        self.assignable_fixed_type = assignable_fixed_type
        self.assignable_otomo = assignable_otomo
        self.can_trigger_worker_event = can_trigger_worker_event
        self.can_steal_assign = can_steal_assign
        self.transform = transform


@dataclasses.dataclass(slots=True)
class WorkableDefence(WorkableBase):
    defense_combat_type: int


@dataclasses.dataclass(slots=True)
class WorkableProgress(WorkableBase):
    required_work_amount: Optional[float]
    work_exp: int
    current_work_amount: Optional[float]
    auto_work_self_amount_by_sec: Optional[float]


@dataclasses.dataclass(slots=True)
class TargetIndividualId(SerializableBase):
    player_uid: UUID
    instance_id: UUID


@dataclasses.dataclass(slots=True)
class WorkableReviveCharacter(WorkableBase):
    target_individual_id: TargetIndividualId


@dataclasses.dataclass(slots=True)
class WorkableAssign(SerializableBase):
    handle_id: UUID
    location_index: int
    assign_type: int
    assigned_individual_id: dict[str, Any]
    state: int
    fixed: int
    transform: Optional["WorkProgressTransformBase"]

    def __init__(
        self,
        handle_id: UUID,
        location_index: int,
        assign_type: int,
        assigned_individual_id: dict[str, Any],
        state: int,
        fixed: int,
        transform: Optional["WorkProgressTransformBase"] = None,
    ):
        self.handle_id = handle_id
        self.location_index = location_index
        self.assign_type = assign_type
        self.assigned_individual_id = assigned_individual_id
        self.state = state
        self.fixed = fixed
        self.transform = transform


@dataclasses.dataclass(slots=True)
class WorkableLevelObject(WorkableAssign):
    target_map_object_model_id: UUID


@dataclasses.dataclass(slots=True)
class WorkProgressTransformBase(SerializableBase):
    type: int
    v2: int


@dataclasses.dataclass(slots=True)
class WorkProgressTransformStatic(WorkProgressTransformBase):
    location: FVector
    rotation: FQuat
    scale: FVector

    def __init__(self, type: int, location: FVector, rotation: FQuat, scale: FVector):
        self.type = type
        self.v2 = 0
        self.location = location


@dataclasses.dataclass(slots=True)
class WorkProgressTransformMapObject(WorkProgressTransformBase):
    map_object_instance_id: UUID

    def __init__(self, type: int, map_object_instance_id: UUID):
        self.type = type
        self.v2 = 0
        self.map_object_instance_id = map_object_instance_id


@dataclasses.dataclass(slots=True)
class WorkProgressTransformId(WorkProgressTransformBase):
    guid: UUID
    instance_id: UUID

    def __init__(self, type: int, guid: UUID, instance_id: UUID):
        self.type = type
        self.v2 = 0
        self.guid = guid
        self.instance_id = instance_id


@dataclasses.dataclass(slots=True)
class WorkProgressTransformUnknown(WorkProgressTransformBase):
    raw_data: list[int]

    def __init__(self, type: int, raw_data: list[int]):
        self.type = type
        self.v2 = 0
        self.raw_data = raw_data


def decode(
    reader: FArchiveReader, type_name: str, size: int, path: str
) -> dict[str, Any]:
    if type_name != "ArrayProperty":
        raise Exception(f"Expected ArrayProperty, got {type_name}")
    value = reader.property(type_name, size, path, nested_caller_path=path)
    for work_element in value["value"]["values"]:
        work_bytes = work_element["RawData"]["value"]["values"]
        work_type = work_element["WorkableType"]["value"]["value"]
        work_element["RawData"]["value"] = decode_bytes(reader, work_bytes, work_type)
        for work_assign in work_element["WorkAssignMap"]["value"]:
            work_assign_bytes = work_assign["value"]["RawData"]["value"]["values"]
            work_assign["value"]["RawData"]["value"] = decode_work_assign_bytes(
                reader, work_assign_bytes
            )
    return value


def decode_bytes(
    parent_reader: FArchiveReader, b_bytes: Sequence[int], work_type: str
) -> dict[str, Any]:
    reader = parent_reader.internal_copy(bytes(b_bytes), debug=False)
    data: Union[WorkableBase, WorkableAssign]
    # Handle base serialization
    if work_type in WORK_BASE_TYPES:
        data = WorkableBase(
            id=reader.guid(),
            workable_bounds=WorkableBounds(
                location=reader.vector_dict(),
                rotation=reader.quat_dict(),
                box_sphere_bounds=BoxSphereBounds(
                    origin=reader.vector_dict(),
                    box_extent=reader.vector_dict(),
                    sphere_radius=reader.double(),
                ),
            ),
            base_camp_id_belong_to=reader.guid(),
            owner_map_object_model_id=reader.guid(),
            owner_map_object_concrete_model_id=reader.guid(),
            current_state=reader.byte(),
            assign_locations=reader.tarray(
                lambda r: AssignLocation(
                    location=r.vector_dict(),
                    facing_direction=r.vector_dict(),
                ),
            ),
            behaviour_type=reader.byte(),
            assign_define_data_id=reader.fstring(),
            override_work_type=reader.byte(),
            assignable_fixed_type=reader.byte(),
            assignable_otomo=reader.u32() > 0,
            can_trigger_worker_event=reader.u32() > 0,
            can_steal_assign=reader.u32() > 0,
        )
        if work_type == "EPalWorkableType::Defense":
            data = WorkableDefence(
                **dataclasses.asdict(data),
                defense_combat_type=reader.byte(),
            )
        elif work_type == "EPalWorkableType::Progress":
            data = WorkableProgress(
                **dataclasses.asdict(data),
                required_work_amount=reader.float(),
                work_exp=reader.i32(),
                current_work_amount=reader.float(),
                auto_work_self_amount_by_sec=reader.float(),
            )
        elif work_type == "EPalWorkableType::ReviveCharacter":
            data = WorkableReviveCharacter(
                **dataclasses.asdict(data),
                target_individual_id=TargetIndividualId(
                    player_uid=reader.guid(),
                    instance_id=reader.guid(),
                ),
            )
    # These two do not serialize base data
    elif work_type in ["EPalWorkableType::Assign", "EPalWorkableType::LevelObject"]:
        data = WorkableAssign(
            handle_id=reader.guid(),
            location_index=reader.i32(),
            assign_type=reader.byte(),
            assigned_individual_id={
                "player_uid": reader.guid(),
                "instance_id": reader.guid(),
            },
            state=reader.byte(),
            fixed=reader.u32(),
        )
        if work_type == "EPalWorkableType::LevelObject":
            data = WorkableLevelObject(
                **dataclasses.asdict(data),
                target_map_object_model_id=reader.guid(),
            )
    else:
        print(f"Warning, unable to parse {work_type}, falling back to raw bytes")
        return {"values": b_bytes}
    # UPalWorkProgressTransformBase->SerializeProperties
    transform_type = reader.byte()
    transform: WorkProgressTransformBase
    if transform_type == 1:
        transform = WorkProgressTransformStatic(
            type=transform_type,
            location=reader.vector_dict(),
            rotation=reader.quat_dict(),
            scale=reader.vector_dict(),
        )
    elif transform_type == 2:
        transform = WorkProgressTransformMapObject(
            type=transform_type,
            map_object_instance_id=reader.guid(),
        )
    elif transform_type == 3:
        transform = WorkProgressTransformId(
            type=transform_type,
            guid=reader.guid(),
            instance_id=reader.guid(),
        )
    else:
        remaining_data = reader.read_to_end()
        print(
            f"Unknown EPalWorkTransformType, please report this: {transform_type}: {work_type}: {''.join(f'{b:02x}' for b in remaining_data)}"
        )
        transform = WorkProgressTransformUnknown(
            type=transform_type,
            raw_data=[b for b in remaining_data],
        )
    data.transform = transform

    if not reader.eof():
        raise Exception(
            f"Warning: EOF not reached for {work_type}, remaining bytes: {reader.read_to_end()!r}"
        )

    return data


def decode_work_assign_bytes(
    parent_reader: FArchiveReader, b_bytes: Sequence[int]
) -> dict[str, Any]:
    reader = parent_reader.internal_copy(bytes(b_bytes), debug=False)
    data: dict[str, Any] = {}

    data["id"] = reader.guid()
    data["location_index"] = reader.i32()
    data["assign_type"] = reader.byte()
    data["assigned_individual_id"] = {
        "player_uid": reader.guid(),
        "instance_id": reader.guid(),
    }
    data["state"] = reader.byte()
    data["fixed"] = reader.u32() > 0

    if not reader.eof():
        raise Exception("Warning: EOF not reached")

    return data


def encode(
    writer: FArchiveWriter, property_type: str, properties: dict[str, Any]
) -> int:
    if property_type != "ArrayProperty":
        raise Exception(f"Expected ArrayProperty, got {property_type}")
    del properties["custom_type"]
    for work_element in properties["value"]["values"]:
        work_type = work_element["WorkableType"]["value"]["value"]
        work_element["RawData"]["value"] = {
            "values": [
                b for b in encode_bytes(work_element["RawData"]["value"], work_type)
            ]
        }
        for work_assign in work_element["WorkAssignMap"]["value"]:
            work_assign["value"]["RawData"]["value"] = {
                "values": [
                    b
                    for b in encode_work_assign_bytes(
                        work_assign["value"]["RawData"]["value"]
                    )
                ]
            }
    return writer.property_inner(property_type, properties)


def encode_bytes(p: dict[str, Any], work_type: str) -> bytes:
    writer = FArchiveWriter()

    # Handle base serialization
    if work_type in WORK_BASE_TYPES:
        writer.guid(p["id"])
        writer.vector_dict(p["workable_bounds"]["location"])
        writer.quat_dict(p["workable_bounds"]["rotation"])
        writer.vector_dict(p["workable_bounds"]["box_sphere_bounds"]["origin"])
        writer.vector_dict(p["workable_bounds"]["box_sphere_bounds"]["box_extent"])
        writer.double(p["workable_bounds"]["box_sphere_bounds"]["sphere_radius"])
        writer.guid(p["base_camp_id_belong_to"])
        writer.guid(p["owner_map_object_model_id"])
        writer.guid(p["owner_map_object_concrete_model_id"])
        writer.byte(p["current_state"])
        writer.tarray(
            lambda w, l: (
                w.vector_dict(l["location"]),
                w.vector_dict(l["facing_direction"]),
                None,
            )[2],
            p["assign_locations"],
        )
        writer.byte(p["behaviour_type"])
        writer.fstring(p["assign_define_data_id"])
        writer.byte(p["override_work_type"])
        writer.byte(p["assignable_fixed_type"])
        writer.u32(1 if p["assignable_otomo"] else 0)
        writer.u32(1 if p["can_trigger_worker_event"] else 0)
        writer.u32(1 if p["can_steal_assign"] else 0)
        if work_type == "EPalWorkableType::Defense":
            writer.byte(p["defense_combat_type"])
        elif work_type == "EPalWorkableType::Progress":
            writer.float(p["required_work_amount"])
            writer.i32(p["work_exp"])
            writer.float(p["current_work_amount"])
            writer.float(p["auto_work_self_amount_by_sec"])
        elif work_type == "EPalWorkableType::ReviveCharacter":
            writer.guid(p["target_individual_id"]["player_uid"])
            writer.guid(p["target_individual_id"]["instance_id"])
    # These two do not serialize base data
    elif work_type in ["EPalWorkableType::Assign", "EPalWorkableType::LevelObject"]:
        writer.guid(p["handle_id"])
        writer.i32(p["location_index"])
        writer.byte(p["assign_type"])
        writer.guid(p["assigned_individual_id"]["player_uid"])
        writer.guid(p["assigned_individual_id"]["instance_id"])
        writer.byte(p["state"])
        writer.u32(p["fixed"])
        if work_type == "EPalWorkableType::LevelObject":
            writer.guid(p["target_map_object_model_id"])

    # UPalWorkProgressTransformBase->SerializeProperties
    transform_type = p["transform"]["type"]
    writer.byte(transform_type)
    if transform_type == 1:
        # pre-v2 the transform was deserialised in the wrong order
        if "v2" not in p["transform"]:
            writer.vector_dict(p["transform"]["location"])
            writer.quat_dict(p["transform"]["rotation"])
            writer.vector_dict(p["transform"]["scale"])
        else:
            writer.ftransform(p["transform"])
    elif transform_type == 2:
        writer.guid(p["transform"]["map_object_instance_id"])
    elif transform_type == 3:
        writer.guid(p["transform"]["guid"])
        writer.guid(p["transform"]["instance_id"])
    else:
        print(
            f"Unknown EPalWorkTransformType, please report this: {transform_type}: {work_type}"
        )
        writer.write(p["transform"]["raw_data"])

    encoded_bytes = writer.bytes()
    return encoded_bytes


def encode_work_assign_bytes(p: dict[str, Any]) -> bytes:
    writer = FArchiveWriter()

    writer.guid(p["id"])
    writer.i32(p["location_index"])
    writer.byte(p["assign_type"])
    writer.guid(p["assigned_individual_id"]["player_uid"])
    writer.guid(p["assigned_individual_id"]["instance_id"])
    writer.byte(p["state"])
    writer.u32(1 if p["fixed"] else 0)

    encoded_bytes = writer.bytes()
    return encoded_bytes
