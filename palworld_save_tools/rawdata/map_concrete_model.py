from typing import Any, Sequence

from palworld_save_tools.archive import *
from palworld_save_tools.rawdata.common import (
    pal_item_and_num_read,
    pal_item_and_slot_writer,
)

# Generate using extract_map_object_concrete_classes.py
MAP_OBJECT_NAME_TO_CONCRETE_MODEL_CLASS: dict[str, str] = {
    "droppedcharacter": "PalMapObjectDeathDroppedCharacterModel",
    "blastfurnace": "PalMapObjectConvertItemModel",
    "blastfurnace2": "PalMapObjectConvertItemModel",
    "blastfurnace3": "PalMapObjectConvertItemModel",
    "blastfurnace4": "PalMapObjectConvertItemModel",
    "blastfurnace5": "PalMapObjectConvertItemModel",
    "campfire": "PalMapObjectConvertItemModel",
    "characterrankup": "PalMapObjectRankUpCharacterModel",
    "commondropitem3d": "PalMapObjectDropItemModel",
    "cookingstove": "PalMapObjectConvertItemModel",
    "damagablerock_pv": "PalMapObjectItemDropOnDamagModel",
    "damagablerock0001": "PalMapObjectItemDropOnDamagModel",
    "damagablerock0002": "PalMapObjectItemDropOnDamagModel",
    "damagablerock0003": "PalMapObjectItemDropOnDamagModel",
    "damagablerock0004": "PalMapObjectItemDropOnDamagModel",
    "damagablerock0005": "PalMapObjectItemDropOnDamagModel",
    "damagablerock0017": "PalMapObjectItemDropOnDamagModel",
    "damagablerock0006": "PalMapObjectItemDropOnDamagModel",
    "damagablerock0007": "PalMapObjectItemDropOnDamagModel",
    "damagablerock0008": "PalMapObjectItemDropOnDamagModel",
    "damagablerock0009": "PalMapObjectItemDropOnDamagModel",
    "damagablerock0010": "PalMapObjectItemDropOnDamagModel",
    "damagablerock0011": "PalMapObjectItemDropOnDamagModel",
    "damagablerock0012": "PalMapObjectItemDropOnDamagModel",
    "damagablerock0013": "PalMapObjectItemDropOnDamagModel",
    "damagablerock0014": "PalMapObjectItemDropOnDamagModel",
    "damagablerock0015": "PalMapObjectItemDropOnDamagModel",
    "damagablerock0016": "PalMapObjectItemDropOnDamagModel",
    "deathpenaltychest": "PalMapObjectDeathPenaltyStorageModel",
    "defensegatlinggun": "PalMapObjectDefenseBulletLauncherModel",
    "defensemachinegun": "PalMapObjectDefenseBulletLauncherModel",
    "defenseminigun": "DEFAULT_UNKNOWN_PalMapObjectConcreteModelBase",
    "defensebowgun": "PalMapObjectDefenseBulletLauncherModel",
    "defensemissile": "PalMapObjectDefenseBulletLauncherModel",
    "defensewait": "PalMapObjectDefenseWaitModel",
    "electricgenerator": "PalMapObjectGenerateEnergyModel",
    "electricgenerator_slave": "PalMapObjectGenerateEnergyModel",
    "electricgenerator2": "PalMapObjectGenerateEnergyModel",
    "electricgenerator3": "PalMapObjectGenerateEnergyModel",
    "electrickitchen": "PalMapObjectConvertItemModel",
    "factory_comfortable_01": "PalMapObjectConvertItemModel",
    "factory_comfortable_02": "PalMapObjectConvertItemModel",
    "factory_hard_01": "PalMapObjectConvertItemModel",
    "factory_hard_02": "PalMapObjectConvertItemModel",
    "factory_hard_03": "PalMapObjectConvertItemModel",
    "farmblockv2_grade01": "PalMapObjectFarmBlockV2Model",
    "farmblockv2_grade02": "PalMapObjectFarmBlockV2Model",
    "farmblockv2_grade03": "PalMapObjectFarmBlockV2Model",
    "farmblockv2_wheet": "PalMapObjectFarmBlockV2Model",
    "farmblockv2_tomato": "PalMapObjectFarmBlockV2Model",
    "farmblockv2_lettuce": "PalMapObjectFarmBlockV2Model",
    "farmblockv2_berries": "PalMapObjectFarmBlockV2Model",
    "fasttravelpoint": "PalMapObjectFastTravelPointModel",
    "hightechkitchen": "PalMapObjectConvertItemModel",
    "itemchest": "PalMapObjectItemChestModel",
    "itemchest_02": "PalMapObjectItemChestModel",
    "itemchest_03": "PalMapObjectItemChestModel",
    "dev_itemchest": "PalMapObjectItemChestModel",
    "medicalpalbed": "PalMapObjectMedicalPalBedModel",
    "medicalpalbed_02": "PalMapObjectMedicalPalBedModel",
    "medicalpalbed_03": "PalMapObjectMedicalPalBedModel",
    "medicalpalbed_04": "PalMapObjectMedicalPalBedModel",
    "medicinefacility_01": "PalMapObjectConvertItemModel",
    "medicinefacility_02": "PalMapObjectConvertItemModel",
    "medicinefacility_03": "PalMapObjectConvertItemModel",
    "palfoodbox": "PalMapObjectPalFoodBoxModel",
    "palboxv2": "PalMapObjectBaseCampPoint",
    "displaycharacter": "PalMapObjectDisplayCharacterModel",
    "pickupitem_flint": "PalMapObjectPickupItemOnLevelModel",
    "pickupitem_log": "PalMapObjectPickupItemOnLevelModel",
    "pickupitem_redberry": "PalMapObjectPickupItemOnLevelModel",
    "pickupitem_stone": "PalMapObjectPickupItemOnLevelModel",
    "pickupitem_potato": "PalMapObjectPickupItemOnLevelModel",
    "pickupitem_poppy": "PalMapObjectPickupItemOnLevelModel",
    "playerbed": "PalMapObjectPlayerBedModel",
    "playerbed_02": "PalMapObjectPlayerBedModel",
    "playerbed_03": "PalMapObjectPlayerBedModel",
    "shippingitembox": "PalMapObjectShippingItemModel",
    "spherefactory_black_01": "PalMapObjectConvertItemModel",
    "spherefactory_black_02": "PalMapObjectConvertItemModel",
    "spherefactory_black_03": "PalMapObjectConvertItemModel",
    "spherefactory_white_01": "PalMapObjectConvertItemModel",
    "spherefactory_white_02": "PalMapObjectConvertItemModel",
    "spherefactory_white_03": "PalMapObjectConvertItemModel",
    "stonehouse1": "PalBuildObject",
    "stonepit": "PalMapObjectProductItemModel",
    "strawhouse1": "PalBuildObject",
    "weaponfactory_clean_01": "PalMapObjectConvertItemModel",
    "weaponfactory_clean_02": "PalMapObjectConvertItemModel",
    "weaponfactory_clean_03": "PalMapObjectConvertItemModel",
    "weaponfactory_dirty_01": "PalMapObjectConvertItemModel",
    "weaponfactory_dirty_02": "PalMapObjectConvertItemModel",
    "weaponfactory_dirty_03": "PalMapObjectConvertItemModel",
    "well": "PalMapObjectProductItemModel",
    "woodhouse1": "PalBuildObject",
    "workbench": "PalMapObjectConvertItemModel",
    "recoverotomo": "PalMapObjectRecoverOtomoModel",
    "palegg": "PalMapObjectPalEggModel",
    "palegg_fire": "PalMapObjectPalEggModel",
    "palegg_water": "PalMapObjectPalEggModel",
    "palegg_leaf": "PalMapObjectPalEggModel",
    "palegg_electricity": "PalMapObjectPalEggModel",
    "palegg_ice": "PalMapObjectPalEggModel",
    "palegg_earth": "PalMapObjectPalEggModel",
    "palegg_dark": "PalMapObjectPalEggModel",
    "palegg_dragon": "PalMapObjectPalEggModel",
    "hatchingpalegg": "PalMapObjectHatchingEggModel",
    "treasurebox": "PalMapObjectTreasureBoxModel",
    "treasurebox_visiblecontent": "PalMapObjectPickupItemOnLevelModel",
    "treasurebox_visiblecontent_skillfruits": "PalMapObjectPickupItemOnLevelModel",
    "stationdeforest2": "PalMapObjectProductItemModel",
    "workbench_skillunlock": "PalMapObjectConvertItemModel",
    "workbench_skillcard": "PalMapObjectConvertItemModel",
    "wooden_foundation": "PalBuildObject",
    "wooden_wall": "PalBuildObject",
    "wooden_roof": "PalBuildObject",
    "wooden_stair": "PalBuildObject",
    "wooden_doorwall": "PalMapObjectDoorModel",
    "stone_foundation": "PalBuildObject",
    "stone_wall": "PalBuildObject",
    "stone_roof": "PalBuildObject",
    "stone_stair": "PalBuildObject",
    "stone_doorwall": "PalMapObjectDoorModel",
    "metal_foundation": "PalBuildObject",
    "metal_wall": "PalBuildObject",
    "metal_roof": "PalBuildObject",
    "metal_stair": "PalBuildObject",
    "metal_doorwall": "PalMapObjectDoorModel",
    "buildablegoddessstatue": "PalMapObjectCharacterStatusOperatorModel",
    "spa": "PalMapObjectAmusementModel",
    "spa2": "PalMapObjectAmusementModel",
    "pickupitem_mushroom": "PalMapObjectPickupItemOnLevelModel",
    "defensewall_wood": "PalBuildObject",
    "defensewall": "PalBuildObject",
    "defensewall_metal": "PalBuildObject",
    "heater": "PalMapObjectHeatSourceModel",
    "electricheater": "PalMapObjectHeatSourceModel",
    "cooler": "PalMapObjectHeatSourceModel",
    "electriccooler": "PalMapObjectHeatSourceModel",
    "torch": "PalMapObjectTorchModel",
    "walltorch": "PalMapObjectTorchModel",
    "lamp": "PalMapObjectLampModel",
    "ceilinglamp": "PalMapObjectLampModel",
    "largelamp": "PalMapObjectLampModel",
    "largeceilinglamp": "PalMapObjectLampModel",
    "crusher": "PalMapObjectConvertItemModel",
    "woodcrusher": "PalMapObjectConvertItemModel",
    "flourmill": "PalMapObjectConvertItemModel",
    "trap_leghold": "DEFAULT_UNKNOWN_PalMapObjectConcreteModelBase",
    "trap_leghold_big": "DEFAULT_UNKNOWN_PalMapObjectConcreteModelBase",
    "trap_noose": "DEFAULT_UNKNOWN_PalMapObjectConcreteModelBase",
    "trap_movingpanel": "DEFAULT_UNKNOWN_PalMapObjectConcreteModelBase",
    "trap_mineelecshock": "DEFAULT_UNKNOWN_PalMapObjectConcreteModelBase",
    "trap_minefreeze": "DEFAULT_UNKNOWN_PalMapObjectConcreteModelBase",
    "trap_mineattack": "DEFAULT_UNKNOWN_PalMapObjectConcreteModelBase",
    "breedfarm": "PalMapObjectBreedFarmModel",
    "wood_gate": "PalMapObjectDoorModel",
    "stone_gate": "PalMapObjectDoorModel",
    "metal_gate": "PalMapObjectDoorModel",
    "repairbench": "PalMapObjectRepairItemModel",
    "skillfruit_test": "PalMapObjectPickupItemOnLevelModel",
    "toolboxv1": "PalMapObjectBaseCampPassiveEffectModel",
    "toolboxv2": "PalMapObjectBaseCampPassiveEffectModel",
    "fountain": "PalMapObjectBaseCampPassiveEffectModel",
    "silo": "PalMapObjectBaseCampPassiveEffectModel",
    "transmissiontower": "PalMapObjectBaseCampPassiveEffectModel",
    "flowerbed": "PalMapObjectBaseCampPassiveEffectModel",
    "stump": "PalMapObjectBaseCampPassiveEffectModel",
    "miningtool": "PalMapObjectBaseCampPassiveEffectModel",
    "cauldron": "PalMapObjectBaseCampPassiveEffectModel",
    "snowman": "PalMapObjectBaseCampPassiveEffectModel",
    "olympiccauldron": "PalMapObjectBaseCampPassiveEffectModel",
    "basecampworkhard": "PalMapObjectBaseCampPassiveWorkHardModel",
    "coolerbox": "PalMapObjectItemChest_AffectCorruption",
    "refrigerator": "PalMapObjectItemChest_AffectCorruption",
    "damagedscarecrow": "PalMapObjectDamagedScarecrowModel",
    "signboard": "PalMapObjectSignboardModel",
    "basecampbattledirector": "PalMapObjectBaseCampWorkerDirectorModel",
    "monsterfarm": "PalMapObjectMonsterFarmModel",
    "wood_windowwall": "PalBuildObject",
    "stone_windowwall": "PalBuildObject",
    "metal_windowwall": "PalBuildObject",
    "wood_trianglewall": "PalBuildObject",
    "stone_trianglewall": "PalBuildObject",
    "metal_trianglewall": "PalBuildObject",
    "wood_slantedroof": "PalBuildObject",
    "stone_slantedroof": "PalBuildObject",
    "metal_slantedroof": "PalBuildObject",
    "table1": "PalBuildObject",
    "barrel_wood": "PalMapObjectItemChestModel",
    "box_wood": "PalMapObjectItemChestModel",
    "box01_iron": "PalMapObjectItemChestModel",
    "box02_iron": "PalMapObjectItemChestModel",
    "shelf_wood": "PalMapObjectItemChestModel",
    "shelf_cask_wood": "PalMapObjectItemChestModel",
    "shelf_hang01_wood": "PalMapObjectItemChestModel",
    "shelf01_iron": "PalMapObjectItemChestModel",
    "shelf02_iron": "PalMapObjectItemChestModel",
    "shelf03_iron": "PalMapObjectItemChestModel",
    "shelf04_iron": "PalMapObjectItemChestModel",
    "shelf05_stone": "PalMapObjectItemChestModel",
    "shelf06_stone": "PalMapObjectItemChestModel",
    "shelf07_stone": "PalMapObjectItemChestModel",
    "shelf01_wall_stone": "PalMapObjectItemChestModel",
    "shelf01_wall_iron": "PalMapObjectItemChestModel",
    "shelf01_stone": "PalMapObjectItemChestModel",
    "shelf02_stone": "PalMapObjectItemChestModel",
    "shelf03_stone": "PalMapObjectItemChestModel",
    "shelf04_stone": "PalMapObjectItemChestModel",
    "container01_iron": "PalMapObjectItemChestModel",
    "tablesquare_wood": "PalBuildObject",
    "tablecircular_wood": "PalBuildObject",
    "bench_wood": "PalBuildObject",
    "stool_wood": "PalBuildObject",
    "decal_palsticker_pinkcat": "PalBuildObject",
    "stool_high_wood": "PalBuildObject",
    "counter_wood": "PalBuildObject",
    "rug_wood": "PalBuildObject",
    "shelf_hang02_wood": "PalBuildObject",
    "ivy01": "PalBuildObject",
    "ivy02": "PalBuildObject",
    "ivy03": "PalBuildObject",
    "chair01_wood": "PalBuildObject",
    "box01_stone": "PalBuildObject",
    "barrel01_iron": "PalBuildObject",
    "barrel02_iron": "PalBuildObject",
    "barrel03_iron": "PalBuildObject",
    "cablecoil01_iron": "PalBuildObject",
    "chair01_iron": "PalBuildObject",
    "chair02_iron": "PalBuildObject",
    "clock01_wall_iron": "PalBuildObject",
    "garbagebag_iron": "PalBuildObject",
    "goalsoccer_iron": "PalBuildObject",
    "machinegame01_iron": "PalBuildObject",
    "machinevending01_iron": "PalBuildObject",
    "pipeclay01_iron": "PalBuildObject",
    "signexit_ceiling_iron": "PalBuildObject",
    "signexit_wall_iron": "PalBuildObject",
    "sofa01_iron": "PalBuildObject",
    "sofa02_iron": "PalBuildObject",
    "stool01_iron": "PalBuildObject",
    "tablecircular01_iron": "PalBuildObject",
    "tableside01_iron": "PalBuildObject",
    "tablesquare01_iron": "PalBuildObject",
    "tablesquare02_iron": "PalBuildObject",
    "tire01_iron": "PalBuildObject",
    "trafficbarricade01_iron": "PalBuildObject",
    "trafficbarricade02_iron": "PalBuildObject",
    "trafficbarricade03_iron": "PalBuildObject",
    "trafficbarricade04_iron": "PalBuildObject",
    "trafficbarricade05_iron": "PalBuildObject",
    "trafficcone01_iron": "PalBuildObject",
    "trafficcone02_iron": "PalBuildObject",
    "trafficcone03_iron": "PalBuildObject",
    "trafficlight01_iron": "PalBuildObject",
    "bathtub_stone": "PalBuildObject",
    "chair01_stone": "PalBuildObject",
    "chair02_stone": "PalBuildObject",
    "clock01_stone": "PalBuildObject",
    "curtain01_wall_stone": "PalBuildObject",
    "desk01_stone": "PalBuildObject",
    "globe01_stone": "PalBuildObject",
    "mirror01_stone": "PalBuildObject",
    "mirror02_stone": "PalBuildObject",
    "mirror01_wall_stone": "PalBuildObject",
    "partition_stone": "PalBuildObject",
    "piano01_stone": "PalBuildObject",
    "piano02_stone": "PalBuildObject",
    "rug01_stone": "PalBuildObject",
    "rug02_stone": "PalBuildObject",
    "rug03_stone": "PalBuildObject",
    "rug04_stone": "PalBuildObject",
    "sofa01_stone": "PalBuildObject",
    "sofa02_stone": "PalBuildObject",
    "sofa03_stone": "PalBuildObject",
    "stool01_stone": "PalBuildObject",
    "stove01_stone": "PalBuildObject",
    "tablecircular01_stone": "PalBuildObject",
    "tabledresser01_stone": "PalBuildObject",
    "tablesink01_stone": "PalBuildObject",
    "toilet01_stone": "PalBuildObject",
    "toiletholder01_stone": "PalBuildObject",
    "towlrack01_stone": "PalBuildObject",
    "plant01_plant": "PalBuildObject",
    "plant02_plant": "PalBuildObject",
    "plant03_plant": "PalBuildObject",
    "plant04_plant": "PalBuildObject",
    "light_floorlamp01": "PalMapObjectLampModel",
    "light_floorlamp02": "PalMapObjectLampModel",
    "light_lightpole01": "PalMapObjectLampModel",
    "light_lightpole02": "PalMapObjectLampModel",
    "light_lightpole03": "PalMapObjectLampModel",
    "light_lightpole04": "PalMapObjectLampModel",
    "light_fireplace01": "PalMapObjectTorchModel",
    "light_fireplace02": "PalMapObjectTorchModel",
    "light_candlesticks_top": "PalMapObjectLampModel",
    "light_candlesticks_wall": "PalMapObjectLampModel",
    "television01_iron": "PalBuildObject",
    "desk01_iron": "PalBuildObject",
    "trafficsign01_iron": "PalBuildObject",
    "trafficsign02_iron": "PalBuildObject",
    "trafficsign03_iron": "PalBuildObject",
    "trafficsign04_iron": "PalBuildObject",
    "chair01_pal": "PalBuildObject",
}
NO_OP_TYPES = set(
    [
        "Default_PalMapObjectConcreteModelBase",
        "PalBuildObject",
        "PalMapObjectRankUpCharacterModel",
        "PalMapObjectDefenseWaitModel",
        "PalMapObjectItemChestModel",
        "PalMapObjectMedicalPalBedModel",
        "PalMapObjectPalFoodBoxModel",
        "PalMapObjectPlayerBedModel",
        "PalMapObjectDisplayCharacterModel",
        "PalMapObjectDoorModel",
        "PalMapObjectCharacterStatusOperatorModel",
        "PalMapObjectAmusementModel",
        "PalMapObjectRepairItemModel",
        "PalMapObjectBaseCampPassiveEffectModel",
        "PalMapObjectBaseCampPassiveWorkHardModel",
        "PalMapObjectItemChest_AffectCorruption",
        "PalMapObjectDamagedScarecrowModel",
        "PalMapObjectBaseCampWorkerDirectorModel",
        "PalMapObjectMonsterFarmModel",
        "PalMapObjectLampModel",
        "PalMapObjectHeatSourceModel",
    ]
)


def decode_bytes(
    parent_reader: FArchiveReader, m_bytes: Sequence[int], object_id: str
) -> Optional[dict[str, Any]]:
    if len(m_bytes) == 0:
        return {"values": []}
    reader = parent_reader.internal_copy(bytes(m_bytes), debug=False)
    data: dict[str, Any] = {}

    if object_id.lower() not in MAP_OBJECT_NAME_TO_CONCRETE_MODEL_CLASS:
        print(f"Warning: Map object '{object_id}' not in database, skipping")
        return {"values": m_bytes}

    # Base handling
    data["instance_id"] = reader.guid()
    data["model_instance_id"] = reader.guid()

    def pickup_base():
        data["auto_picked_up"] = reader.u32() > 0

    map_object_concrete_model = MAP_OBJECT_NAME_TO_CONCRETE_MODEL_CLASS[
        object_id.lower()
    ]
    data["concrete_model_type"] = map_object_concrete_model

    if map_object_concrete_model in NO_OP_TYPES:
        pass
    elif map_object_concrete_model == "PalMapObjectDeathDroppedCharacterModel":
        data["stored_parameter_id"] = reader.guid()
        data["owner_player_uid"] = reader.guid()
    elif map_object_concrete_model == "PalMapObjectConvertItemModel":
        data["current_recipe_id"] = reader.fstring()
        data["remain_product_num"] = reader.i32()
        data["requested_product_num"] = reader.i32()
        data["work_speed_additional_rate"] = reader.float()
    elif map_object_concrete_model == "PalMapObjectPickupItemOnLevelModel":
        pickup_base()
    elif map_object_concrete_model == "PalMapObjectDropItemModel":
        pickup_base()
        data["item_id"] = {
            "static_id": reader.fstring(),
            "dynamic_id": {
                "created_world_id": reader.guid(),
                "local_id_in_created_world": reader.guid(),
            },
        }
    elif map_object_concrete_model == "PalMapObjectItemDropOnDamagModel":
        data["drop_item_infos"] = reader.tarray(pal_item_and_num_read)
    elif map_object_concrete_model == "PalMapObjectDeathPenaltyStorageModel":
        data["owner_player_uid"] = reader.guid()
    elif map_object_concrete_model == "PalMapObjectDefenseBulletLauncherModel":
        data["remaining_bullets"] = reader.i32()
        data["magazine_size"] = reader.i32()
        data["bullet_item_name"] = reader.fstring()
    elif map_object_concrete_model == "PalMapObjectGenerateEnergyModel":
        data["stored_energy_amount"] = reader.float()
    elif map_object_concrete_model == "PalMapObjectFarmBlockV2Model":
        data["crop_data_id"] = reader.fstring()
        current_state = reader.byte()
        data["current_state"] = current_state
        data["crop_progress_rate_value"] = reader.float()
        data["water_stack_rate_value"] = reader.float()
        if not reader.eof():
            data["state_machine"] = {
                "growup_required_time": reader.float(),
                "growup_progress_time": reader.float(),
            }
    elif map_object_concrete_model == "PalMapObjectFastTravelPointModel":
        data["location_instance_id"] = reader.guid()
    elif map_object_concrete_model == "PalMapObjectShippingItemModel":
        data["shipping_hours"] = reader.tarray(lambda r: r.i32())
    elif map_object_concrete_model == "PalMapObjectProductItemModel":
        data["work_speed_additional_rate"] = reader.float()
        data["product_item_id"] = reader.fstring()
    elif map_object_concrete_model == "PalMapObjectRecoverOtomoModel":
        data["recover_amount_by_sec"] = reader.float()
    elif map_object_concrete_model == "PalMapObjectHatchingEggModel":
        data["hatched_character_save_parameter"] = reader.properties_until_end()
        data["unknown_bytes"] = reader.u32()
        data["hatched_character_guid"] = reader.guid()
    elif map_object_concrete_model == "PalMapObjectTreasureBoxModel":
        data["treasure_grade_type"] = reader.byte()
    elif map_object_concrete_model == "PalMapObjectBreedFarmModel":
        data["spawned_egg_instance_ids"] = reader.tarray(lambda r: r.guid())
    elif map_object_concrete_model == "PalMapObjectSignboardModel":
        data["signboard_text"] = reader.fstring()
    elif map_object_concrete_model == "PalMapObjectTorchModel":
        data["extinction_date_time"] = reader.i64()
    elif map_object_concrete_model == "PalMapObjectPalEggModel":
        data["unknown_bytes"] = reader.u32()
    elif map_object_concrete_model == "PalMapObjectBaseCampPoint":
        data["base_camp_id"] = reader.guid()
    else:
        print(
            f"Warning: Unknown map object concrete model {map_object_concrete_model}, skipping"
        )
        return {"values": m_bytes}

    if not reader.eof():
        raise Exception(
            f"Warning: EOF not reached for {object_id} {map_object_concrete_model}: ori: {''.join(f'{b:02x}' for b in m_bytes)} remaining: {reader.size - reader.data.tell()}"
        )
    return data


def encode_bytes(p: Optional[dict[str, Any]]) -> bytes:
    if p is None:
        return b""

    writer = FArchiveWriter()

    map_object_concrete_model = p["concrete_model_type"]

    # Base handling
    writer.guid(p["instance_id"])
    writer.guid(p["model_instance_id"])

    if map_object_concrete_model in NO_OP_TYPES:
        pass
    elif map_object_concrete_model == "PalMapObjectDeathDroppedCharacterModel":
        writer.guid(p["stored_parameter_id"])
        writer.guid(p["owner_player_uid"])
    elif map_object_concrete_model == "PalMapObjectConvertItemModel":
        writer.fstring(p["current_recipe_id"])
        writer.i32(p["remain_product_num"])
        writer.i32(p["requested_product_num"])
        writer.float(p["work_speed_additional_rate"])
    elif map_object_concrete_model == "PalMapObjectPickupItemOnLevelModel":
        writer.u32(1 if p["auto_picked_up"] else 0)
    elif map_object_concrete_model == "PalMapObjectDropItemModel":
        writer.u32(1 if p["auto_picked_up"] else 0)
        writer.fstring(p["item_id"]["static_id"])
        writer.guid(p["item_id"]["dynamic_id"]["created_world_id"])
        writer.guid(p["item_id"]["dynamic_id"]["local_id_in_created_world"])
    elif map_object_concrete_model == "PalMapObjectItemDropOnDamagModel":
        writer.tarray(pal_item_and_slot_writer, p["drop_item_infos"])
    elif map_object_concrete_model == "PalMapObjectDeathPenaltyStorageModel":
        writer.guid(p["owner_player_uid"])
    elif map_object_concrete_model == "PalMapObjectDefenseBulletLauncherModel":
        writer.i32(p["remaining_bullets"])
        writer.i32(p["magazine_size"])
        writer.fstring(p["bullet_item_name"])
    elif map_object_concrete_model == "PalMapObjectGenerateEnergyModel":
        writer.float(p["stored_energy_amount"])
    elif map_object_concrete_model == "PalMapObjectFarmBlockV2Model":
        writer.fstring(p["crop_data_id"])
        writer.byte(p["current_state"])
        writer.float(p["crop_progress_rate_value"])
        writer.float(p["water_stack_rate_value"])
        if "state_machine" in p:
            writer.float(p["state_machine"]["growup_required_time"])
            writer.float(p["state_machine"]["growup_progress_time"])
    elif map_object_concrete_model == "PalMapObjectFastTravelPointModel":
        writer.guid(p["location_instance_id"])
    elif map_object_concrete_model == "PalMapObjectShippingItemModel":
        writer.tarray(lambda w, x: w.i32(x), p["shipping_hours"])
    elif map_object_concrete_model == "PalMapObjectProductItemModel":
        writer.float(p["work_speed_additional_rate"])
        writer.fstring(p["product_item_id"])
    elif map_object_concrete_model == "PalMapObjectRecoverOtomoModel":
        writer.float(p["recover_amount_by_sec"])
    elif map_object_concrete_model == "PalMapObjectHatchingEggModel":
        writer.properties(p["hatched_character_save_parameter"])
        writer.u32(p["unknown_bytes"])
        writer.guid(p["hatched_character_guid"])
    elif map_object_concrete_model == "PalMapObjectTreasureBoxModel":
        writer.byte(p["treasure_grade_type"])
    elif map_object_concrete_model == "PalMapObjectBreedFarmModel":
        writer.tarray(lambda w, x: w.guid(x), p["spawned_egg_instance_ids"])
    elif map_object_concrete_model == "PalMapObjectSignboardModel":
        writer.fstring(p["signboard_text"])
    elif map_object_concrete_model == "PalMapObjectTorchModel":
        writer.i64(p["extinction_date_time"])
    elif map_object_concrete_model == "PalMapObjectPalEggModel":
        writer.u32(p["unknown_bytes"])
    elif map_object_concrete_model == "PalMapObjectBaseCampPoint":
        writer.guid(p["base_camp_id"])
    else:
        raise Exception(
            f"Unknown map object concrete model {map_object_concrete_model}"
        )

    encoded_bytes = writer.bytes()
    return encoded_bytes
