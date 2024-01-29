from lib.rawdata import *

PALWORLD_TYPE_HINTS: dict[str, str] = {
    ".worldSaveData.CharacterContainerSaveData.Key": "StructProperty",
    ".worldSaveData.CharacterSaveParameterMap.Key": "StructProperty",
    ".worldSaveData.CharacterSaveParameterMap.Value": "StructProperty",
    ".worldSaveData.FoliageGridSaveDataMap.Key": "StructProperty",
    ".worldSaveData.FoliageGridSaveDataMap.Value.ModelMap.Value": "StructProperty",
    ".worldSaveData.FoliageGridSaveDataMap.Value.ModelMap.Value.InstanceDataMap.Key": "StructProperty",
    ".worldSaveData.FoliageGridSaveDataMap.Value.ModelMap.Value.InstanceDataMap.Value": "StructProperty",
    ".worldSaveData.FoliageGridSaveDataMap.Value": "StructProperty",
    ".worldSaveData.ItemContainerSaveData.Key": "StructProperty",
    ".worldSaveData.MapObjectSaveData.MapObjectSaveData.ConcreteModel.ModuleMap.Value": "StructProperty",
    ".worldSaveData.MapObjectSaveData.MapObjectSaveData.Model.EffectMap.Value": "StructProperty",
    ".worldSaveData.MapObjectSpawnerInStageSaveData.Key": "StructProperty",
    ".worldSaveData.MapObjectSpawnerInStageSaveData.Value": "StructProperty",
    ".worldSaveData.MapObjectSpawnerInStageSaveData.Value.SpawnerDataMapByLevelObjectInstanceId.Key": "Guid",
    ".worldSaveData.MapObjectSpawnerInStageSaveData.Value.SpawnerDataMapByLevelObjectInstanceId.Value": "StructProperty",
    ".worldSaveData.MapObjectSpawnerInStageSaveData.Value.SpawnerDataMapByLevelObjectInstanceId.Value.ItemMap.Value": "StructProperty",
    ".worldSaveData.WorkSaveData.WorkSaveData.WorkAssignMap.Value": "StructProperty",
    ".worldSaveData.BaseCampSaveData.Key": "Guid",
    ".worldSaveData.BaseCampSaveData.Value": "StructProperty",
    ".worldSaveData.BaseCampSaveData.Value.ModuleMap.Value": "StructProperty",
    ".worldSaveData.ItemContainerSaveData.Value": "StructProperty",
    ".worldSaveData.CharacterContainerSaveData.Value": "StructProperty",
    ".worldSaveData.GroupSaveDataMap.Key": "Guid",
    ".worldSaveData.GroupSaveDataMap.Value": "StructProperty",
    ".worldSaveData.EnemyCampSaveData.EnemyCampStatusMap.Value": "StructProperty",
    ".worldSaveData.DungeonSaveData.DungeonSaveData.MapObjectSaveData.MapObjectSaveData.Model.EffectMap.Value": "StructProperty",
    ".worldSaveData.DungeonSaveData.DungeonSaveData.MapObjectSaveData.MapObjectSaveData.ConcreteModel.ModuleMap.Value": "StructProperty",
}

PALWORLD_CUSTOM_PROPERTIES: dict[
    str,
    tuple[
        Callable[[FArchiveReader, str, int, str], dict[str, Any]],
        Callable[[FArchiveWriter, str, dict[str, Any]], int],
    ],
] = {
    ".worldSaveData.GroupSaveDataMap": (decode_group_data, encode_group_data),
    ".worldSaveData.CharacterSaveParameterMap.Value.RawData": (
        decode_character_data,
        encode_character_data,
    ),
    ".worldSaveData.MapObjectSaveData.MapObjectSaveData.Model.BuildProcess.RawData": (
        decode_build_process,
        encode_build_process,
    ),
    ".worldSaveData.MapObjectSaveData.MapObjectSaveData.Model.Connector.RawData": (
        decode_connector,
        encode_connector,
    ),
    ".worldSaveData.MapObjectSaveData.MapObjectSaveData.Model.RawData": (
        decode_map_model,
        encode_map_model,
    ),
    # ".worldSaveData.MapObjectSaveData.MapObjectSaveData.ConcreteModel.ModuleMap.Value.RawData": (),
    # ".worldSaveData.MapObjectSaveData.MapObjectSaveData.ConcreteModel.RawData": (),
    # ".worldSaveData.MapObjectSaveData.MapObjectSaveData.ConcreteModel": (
    #     decode_map_concrete_model,
    #     encode_map_concrete_model,
    # ),
    # ".worldSaveData.FoliageGridSaveDataMap.Value.ModelMap.Value.InstanceDataMap.Value.RawData": (),
    # ".worldSaveData.FoliageGridSaveDataMap.Value.ModelMap.Value.RawData": (),
    # ".worldSaveData.CharacterContainerSaveData.Value.RawData": (),
    # ".worldSaveData.CharacterContainerSaveData.Value.Slots.Slots.RawData": (),
    # ".worldSaveData.DynamicItemSaveData.DynamicItemSaveData.RawData": (),
    # ".worldSaveData.ItemContainerSaveData.Value.RawData": (),
    # ".worldSaveData.ItemContainerSaveData.Value.Slots.Slots.RawData": (),
}
