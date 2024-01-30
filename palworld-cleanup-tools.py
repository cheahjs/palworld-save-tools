#!/usr/bin/env python3
# Author: MagicBear
# License: MIT License

import glob, os, datetime, zlib, subprocess
from operator import itemgetter, attrgetter
import json
import os
import sys
from lib.gvas import GvasFile
from lib.palsav import compress_gvas_to_sav, decompress_sav_to_gvas
from lib.paltypes import PALWORLD_CUSTOM_PROPERTIES, PALWORLD_TYPE_HINTS
import pprint
import uuid
import argparse

pp = pprint.PrettyPrinter(width=80, compact=True, depth=4)
wsd = None
output_file = None
gvas_file = None
playerMapping = None
instanceMapping = None
output_path = None
args = None


def main():
    global wsd, output_file, gvas_file, playerMapping, instanceMapping, output_path, args

    parser = argparse.ArgumentParser(
        prog="palworld-cleanup-tools",
        description="Cleanup the Level.sav",
    )
    parser.add_argument("filename")
    parser.add_argument(
        "--fix-missing",
        action="store_true",
        help="Delete the missing characters",
    )
    parser.add_argument(
        "--statistics",
        action="store_true",
        help="Show the statistics for all key",
    )
    parser.add_argument(
        "--fix-capture",
        action="store_true",
        help="Fix the too many capture logs",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file (default: <filename>_fixed.sav)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.filename):
        print(f"{args.filename} does not exist")
        exit(1)

    if not os.path.isfile(args.filename):
        print(f"{args.filename} is not a file")
        exit(1)

    print(f"Loading {args.filename}...")
    with open(args.filename, "rb") as f:
        # Read the file
        data = f.read()
        raw_gvas, _ = decompress_sav_to_gvas(data)

        print(f"Parsing {args.filename}...", end="", flush=True)
        gvas_file = GvasFile.read(raw_gvas, PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES)
        print("Done.")

    wsd = gvas_file.properties['worldSaveData']['value']

    if args.statistics:
        for key in wsd:
            print("%40s\t%.3f MB" % (key, len(str(wsd[key])) / 1048576))

    ShowPlayers()
    if args.fix_missing:
        FixMissing()

    ShowGuild(fix_capture=args.fix_capture)

    if not args.output:
        output_path = args.filename.replace(".sav", "_fixed.sav")
    else:
        output_path = args.output

    if sys.flags.interactive:
        print("Go To Interactive Mode (no auto save), we have follow command:")
        print("  ShowPlayers()                      - List the Players")
        print("  FixMissing()                       - Remove missing player instance")
        print("  ShowGuild(fix_capture=False)       - List the Guild and members")
        print("  RenamePlayer(uid,new_name)         - Rename player to new_name")
        print("  DeletePlayer(uid,dry_run=False)    - Wipe player data from save, dry_run: only show how to delete")
        print("  MigratePlayer(old_uid,new_uid)     - Migrate the player from old PlayerUId to new PlayerUId")
        print("  Save()                             - Save the file and exit")
        return

    if args.fix_missing or args.fix_capture:
        Save()


def RenamePlayer(player_uid, new_name):
    for item in wsd['CharacterSaveParameterMap']['value']:
        if item['key']['PlayerUId']['value'] == uuid.UUID(player_uid):
            player = item['value']['RawData']['value']['object']['SaveParameter']['value']
            print(
                "\033[31mRename User\033[0m  UUID: %s  Level: %d  CharacterID: \033[93m%s\033[0m -> %s" % (
                    str(item['key']['InstanceId']['value']), player['Level']['value'],
                    player['NickName']['value'], new_name))
            player['NickName']['value'] = new_name


def MigratePlayer(player_uid, new_player_uid):
    player_sav_file = os.path.dirname(os.path.abspath(args.filename)) + "/Players/" + player_uid.upper().replace("-","") + ".sav"
    new_player_sav_file = os.path.dirname(os.path.abspath(args.filename)) + "/Players/" + new_player_uid.upper().replace("-","") + ".sav"
    playerInstanceId = None
    if not os.path.exists(player_sav_file):
        print("\033[33mWarning: Player Sav file Not exists: %s\033[0m" % player_sav_file)
        return
    else:
        with open(player_sav_file, "rb") as f:
            raw_gvas, _ = decompress_sav_to_gvas(f.read())
            player_gvas_file = GvasFile.read(raw_gvas, PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES)
        player_gvas = player_gvas_file.properties['SaveData']['value']
        player_gvas['PlayerUId']['value'] = uuid.UUID(new_player_uid)
        with open(new_player_sav_file, "wb") as f:
            print("Saving new player sav %s" % (new_player_sav_file))
            if "Pal.PalWorldSaveGame" in player_gvas_file.header.save_game_class_name or "Pal.PalLocalWorldSaveGame" in player_gvas_file.header.save_game_class_name:
                save_type = 0x32
            else:
                save_type = 0x31
            sav_file = compress_gvas_to_sav(player_gvas_file.write(PALWORLD_CUSTOM_PROPERTIES), save_type)
            f.write(sav_file)
    for item in wsd['CharacterSaveParameterMap']['value']:
        player = item['value']['RawData']['value']['object']['SaveParameter']['value']
        if item['key']['PlayerUId']['value'] == uuid.UUID(player_uid):
            item['key']['PlayerUId']['value'] = uuid.UUID(new_player_uid)
            print(
                "\033[32mMigrate User\033[0m  UUID: %s  Level: %d  CharacterID: \033[93m%s\033[0m" % (
                    str(item['key']['InstanceId']['value']), player['Level']['value'] if 'Level' in player else -1,
                    player['NickName']['value']))
        elif 'OwnerPlayerUId' in player and player['OwnerPlayerUId']['value'] == uuid.UUID(player_uid):
            player['OwnerPlayerUId']['value'] = uuid.UUID(new_player_uid)
            player['OldOwnerPlayerUIds']['value']['values'].insert(0, uuid.UUID(new_player_uid))
            print(
                "\033[32mMigrate Pal\033[0m  UUID: %s  Owner: %s  CharacterID: %s" % (
                    str(item['key']['InstanceId']['value']), str(player['OwnerPlayerUId']['value']),
                    player['CharacterID']['value']))
    for group_data in wsd['GroupSaveDataMap']['value']:
        if str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Guild":
            item = group_data['value']['RawData']['value']
            for player in item['players']:
                if player['player_uid'] == uuid.UUID(player_uid):
                    player['player_uid'] = uuid.UUID(new_player_uid)
                    print(
                        "\033[32mMigrate User from Guild\033[0m  \033[93m%s\033[0m   [\033[92m%s\033[0m] Last Online: %d" % (
                            player['player_info']['player_name'], str(player['player_uid']),
                            player['player_info']['last_online_real_time']))
                    break
            if item['admin_player_uid'] == uuid.UUID(player_uid):
                item['admin_player_uid'] =  uuid.UUID(new_player_uid)
                print("\033[32mMigrate Guild Admin \033[0m")
            for ind_char in item['individual_character_handle_ids']:
                if ind_char['guid'] == uuid.UUID(player_uid):
                    ind_char['guid'] = uuid.UUID(new_player_uid)
                    print("\033[32mMigrate Guild Character %s\033[0m" % (str(ind_char['instance_id'])))
    print("Finish to migrate player from Save, please delete this file manually: %s" % player_sav_file)

def DeletePlayer(player_uid, dry_run=False):
    player_sav_file = os.path.dirname(os.path.abspath(args.filename)) + "/Players/" + player_uid.upper().replace("-",
                                                                                                                 "") + ".sav"
    player_container_ids = []
    playerInstanceId = None
    if not os.path.exists(player_sav_file):
        print("\033[33mWarning: Player Sav file Not exists: %s\033[0m" % player_sav_file)
        player_gvas_file = None
    else:
        with open(player_sav_file, "rb") as f:
            raw_gvas, _ = decompress_sav_to_gvas(f.read())
            player_gvas_file = GvasFile.read(raw_gvas, PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES)
        print("Player Container ID:")
        player_gvas = player_gvas_file.properties['SaveData']['value']
        playerInstanceId = player_gvas['IndividualId']['value']['InstanceId']['value']
        for key in ['OtomoCharacterContainerId', 'PalStorageContainerId']:
            print("  %s" % player_gvas[key]['value']['ID']['value'])
            player_container_ids.append(player_gvas[key]['value']['ID']['value'])
        for key in ['CommonContainerId', 'DropSlotContainerId', 'EssentialContainerId', 'FoodEquipContainerId',
                    'PlayerEquipArmorContainerId', 'WeaponLoadOutContainerId']:
            print("  %s" % player_gvas['inventoryInfo']['value'][key]['value']['ID']['value'])
            player_container_ids.append(player_gvas['inventoryInfo']['value'][key]['value']['ID']['value'])
    remove_items = []
    remove_instance_id = []
    # Remove item from CharacterSaveParameterMap
    for item in wsd['CharacterSaveParameterMap']['value']:
        player = item['value']['RawData']['value']['object']['SaveParameter']['value']
        if item['key']['PlayerUId']['value'] == uuid.UUID(player_uid):
            remove_items.append(item)
            remove_instance_id.append(item['key']['InstanceId']['value'])
            print(
                "\033[31mDelete User\033[0m  UUID: %s  Level: %d  CharacterID: \033[93m%s\033[0m" % (
                    str(item['key']['InstanceId']['value']), player['Level']['value'] if 'Level' in player else -1,
                    player['NickName']['value']))
        elif 'OwnerPlayerUId' in player and player['OwnerPlayerUId']['value'] == uuid.UUID(player_uid):
            remove_instance_id.append(item['key']['InstanceId']['value'])
            print(
                "\033[31mDelete Pal\033[0m  UUID: %s  Owner: %s  CharacterID: %s" % (
                    str(item['key']['InstanceId']['value']), str(player['OwnerPlayerUId']['value']),
                    player['CharacterID']['value']))
            remove_items.append(item)
        elif 'SlotID' in player and player['SlotID']['value']['ContainerId']['value']['ID'][
            'value'] in player_container_ids:
            remove_instance_id.append(item['key']['InstanceId']['value'])
            print(
                "\033[31mDelete Pal\033[0m  UUID: %s  Slot: %s  CharacterID: %s" % (
                    str(item['key']['InstanceId']['value']),
                    str(player['SlotID']['value']['ContainerId']['value']['ID']['value']),
                    player['CharacterID']['value']))
            remove_items.append(item)
    if not dry_run:
        for item in remove_items:
            wsd['CharacterSaveParameterMap']['value'].remove(item)
    # Remove Item from CharacterContainerSaveData
    remove_items = []
    for container in wsd['CharacterContainerSaveData']['value']:
        if container['key']['ID']['value'] in player_container_ids:
            remove_items.append(container)
            print(
                "\033[31mDelete Character Container\033[0m  UUID: %s" % (
                    str(container['key']['ID']['value'])))
    if not dry_run:
        for item in remove_items:
            wsd['CharacterContainerSaveData']['value'].remove(item)
    # Remove Item from ItemContainerSaveData
    remove_items = []
    for container in wsd['ItemContainerSaveData']['value']:
        if container['key']['ID']['value'] in player_container_ids:
            remove_items.append(container)
            print(
                "\033[31mDelete Item Container\033[0m  UUID: %s" % (
                    str(container['key']['ID']['value'])))
    if not dry_run:
        for item in remove_items:
            wsd['ItemContainerSaveData']['value'].remove(item)
    # Remove Item from CharacterSaveParameterMap
    remove_items = []
    for container in wsd['CharacterSaveParameterMap']['value']:
        if container['key']['InstanceId']['value'] == playerInstanceId:
            remove_items.append(container)
            print(
                "\033[31mDelete CharacterSaveParameterMap\033[0m  UUID: %s" % (
                    str(container['key']['InstanceId']['value'])))
    if not dry_run:
        for item in remove_items:
            wsd['CharacterSaveParameterMap']['value'].remove(item)
    # Remove Item from GroupSaveDataMap
    for group_data in wsd['GroupSaveDataMap']['value']:
        if str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Guild":
            item = group_data['value']['RawData']['value']
            for player in item['players']:
                if player['player_uid'] == uuid.UUID(player_uid):
                    print(
                        "\033[31mDelete User from Guild\033[0m  \033[93m%s\033[0m   [\033[92m%s\033[0m] Last Online: %d" % (
                            player['player_info']['player_name'], str(player['player_uid']),
                            player['player_info']['last_online_real_time']))
                    if not dry_run:
                        item['players'].remove(player)
                    break
            removeItems = []
            for ind_char in item['individual_character_handle_ids']:
                if ind_char['instance_id'] in remove_instance_id:
                    print("\033[31mDelete Guild Character %s\033[0m" % (str(ind_char['instance_id'])))
                    removeItems.append(ind_char)
            if not dry_run:
                for ind_char in removeItems:
                    item['individual_character_handle_ids'].remove(ind_char)
    print("Finish to remove player from Save, please delete this file manually: %s" % player_sav_file)


def search_keys(dicts, key, level=""):
    if isinstance(dicts, dict):
        if key in dicts:
            print("Found at %s->%s" % (level, key))
        for k in dicts:
            if isinstance(dicts[k], dict) or isinstance(dicts[k], list):
                search_keys(dicts[k], key, level + "->" + k)
    elif isinstance(dicts, list):
        for idx, l in enumerate(dicts):
            if isinstance(l, dict) or isinstance(l, list):
                search_keys(l, key, level + "[%d]" % idx)


def search_values(dicts, key, level=""):
    try:
        uuid_match = uuid.UUID(str(key))
    except ValueError:
        uuid_match = None
    isFound = False
    if isinstance(dicts, dict):
        if key in dicts.values():
            print("Found value at %s['%s']" % (level, list(dicts.keys())[list(dicts.values()).index(key)]))
            isFound = True
        elif uuid_match in dicts.values():
            print("Found UUID  at %s['%s']" % (level, list(dicts.keys())[list(dicts.values()).index(uuid_match)]))
            isFound = True
        for k in dicts:
            if isinstance(dicts[k], dict) or isinstance(dicts[k], list):
                isFound |= search_values(dicts[k], key, level + "['%s']" % k)
    elif isinstance(dicts, list):
        if key in dicts:
            print("Found value at %s[%d]" % (level, dicts.index(key)))
            isFound = True
        elif uuid_match in dicts:
            print("Found UUID  at %s[%d]" % (level, dicts.index(uuid_match)))
            isFound = True
        for idx, l in enumerate(dicts):
            if isinstance(l, dict) or isinstance(l, list):
                isFound |= search_values(l, key, level + "[%d]" % idx)
    return isFound


def ShowPlayers():
    global playerMapping, instanceMapping
    playerMapping = {}
    instanceMapping = {}
    for item in wsd['CharacterSaveParameterMap']['value']:
        instanceMapping[item['key']['InstanceId']['value']] = item
        if "00000000-0000-0000-0000-000000000000" != str(item['key']['PlayerUId']['value']):
            player = item['value']['RawData']['value']['object']['SaveParameter']
            if player['struct_type'] == 'PalIndividualCharacterSaveParameter':
                playerParams = player['value']
                playerMeta = {}
                for player_k in playerParams:
                    playerMeta[player_k] = playerParams[player_k]['value']
                playerMeta['InstanceId'] = item['key']['InstanceId']['value']
                playerMapping[str(item['key']['PlayerUId']['value'])] = playerMeta
            print("%s [\033[32m%s\033[0m] -> Level %2d  %s" % (
                item['key']['PlayerUId']['value'], playerMeta['InstanceId'],
                playerMeta['Level'] if 'Level' in playerMeta else -1, playerMeta['NickName']))
        else:
            # Non Player
            player = item['value']['RawData']['value']['object']['SaveParameter']
            if player['struct_type'] == 'PalIndividualCharacterSaveParameter':
                playerParams = player['value']
                playerMeta = {}
                for player_k in playerParams:
                    playerMeta[player_k] = playerParams[player_k]['value']


def FixMissing():
    # Remove Unused in CharacterSaveParameterMap
    removeItems = []
    for item in wsd['CharacterSaveParameterMap']['value']:
        if "00000000-0000-0000-0000-000000000000" == str(item['key']['PlayerUId']['value']):
            player = item['value']['RawData']['value']['object']['SaveParameter']['value']
            if 'OwnerPlayerUId' in player and str(player['OwnerPlayerUId']['value']) not in playerMapping:
                print(
                    "\033[31mInvalid item on CharacterSaveParameterMap\033[0m  UUID: %s  Owner: %s  CharacterID: %s" % (
                        str(item['key']['InstanceId']['value']), str(player['OwnerPlayerUId']['value']),
                        player['CharacterID']['value']))

    for item in removeItems:
        wsd['CharacterSaveParameterMap']['value'].remove(item)


def ShowGuild(fix_capture=False):
    # Remove Unused in GroupSaveDataMap
    for group_data in wsd['GroupSaveDataMap']['value']:
        # print("%s %s" % (group_data['key'], group_data['value']['GroupType']['value']['value']))
        if str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Guild":
            # pp.pprint(str(group_data['value']['RawData']['value']))
            item = group_data['value']['RawData']['value']
            mapObjectMeta = {}
            for m_k in item:
                mapObjectMeta[m_k] = item[m_k]
            # pp.pprint(mapObjectMeta)
            print("Guild \033[93m%s\033[0m   Admin \033[96m%s\033[0m  Group ID %s  Character Count: %d" % (
                mapObjectMeta['guild_name'], str(mapObjectMeta['admin_player_uid']), str(mapObjectMeta['group_id']),
                len(mapObjectMeta['individual_character_handle_ids'])))
            for player in mapObjectMeta['players']:
                print("    Player \033[93m%s\033[0m [\033[92m%s\033[0m] Last Online: %d" % (
                    player['player_info']['player_name'], str(player['player_uid']),
                    player['player_info']['last_online_real_time']))
            removeItems = []
            for ind_char in mapObjectMeta['individual_character_handle_ids']:
                if ind_char['instance_id'] in instanceMapping:
                    character = \
                        instanceMapping[ind_char['instance_id']]['value']['RawData']['value']['object'][
                            'SaveParameter'][
                            'value']
                    # if 'NickName' in character:
                    #     print("    Player %s -> %s" % (str(ind_char['instance_id']), character['NickName']['value']))
                    # else:
                    #     print("    Character %s -> %s" % (str(ind_char['instance_id']), character['CharacterID']['value']))
                else:
                    print("    \033[31mInvalid Character %s\033[0m" % (str(ind_char['instance_id'])))
                    removeItems.append(ind_char)
            if fix_capture:
                for rmitem in removeItems:
                    item['individual_character_handle_ids'].remove(rmitem)
            print("After remove character count: %d" % len(
                group_data['value']['RawData']['value']['individual_character_handle_ids']))
            print()
        # elif str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Neutral":
        #     item = group_data['value']['RawData']['value']
        #     print("Neutral Group ID %s  Character Count: %d" % (str(item['group_id']), len(item['individual_character_handle_ids'])))
        #     for ind_char in item['individual_character_handle_ids']:
        #         if ind_char['instance_id'] not in instanceMapping:
        #             print("    \033[31mInvalid Character %s\033[0m" % (str(ind_char['instance_id'])))


def Save():
    print("processing GVAS to Sav file...", end="", flush=True)
    if "Pal.PalWorldSaveGame" in gvas_file.header.save_game_class_name or "Pal.PalLocalWorldSaveGame" in gvas_file.header.save_game_class_name:
        save_type = 0x32
    else:
        save_type = 0x31
    sav_file = compress_gvas_to_sav(gvas_file.write(PALWORLD_CUSTOM_PROPERTIES), save_type)
    print("Done")

    print("Saving Sav file...", end="", flush=True)
    with open(output_path, "wb") as f:
        f.write(sav_file)
    print("Done")

    sys.exit(0)


if __name__ == "__main__":
    main()
