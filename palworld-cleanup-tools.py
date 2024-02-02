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
from lib.archive import *
import pprint
import uuid
import argparse
import copy

pp = pprint.PrettyPrinter(width=80, compact=True, depth=4)
wsd = None
output_file = None
gvas_file = None
backup_gvas_file = None
backup_wsd = None
playerMapping = None
instanceMapping = None
output_path = None
args = None
player = None
filetime = None

def main():
    global wsd, output_file, gvas_file, playerMapping, instanceMapping, output_path, args, filetime

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
        help="Fix the too many capture logs (not need after 1.4.0)",
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
    filetime = os.stat(args.filename).st_mtime
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
        print("  ShowPlayers()                              - List the Players")
        print("  FixMissing()                               - Remove missing player instance")
        print("  ShowGuild(fix_capture=False)               - List the Guild and members")
        print("  RenamePlayer(uid,new_name)                 - Rename player to new_name")
        print("  DeletePlayer(uid,InstanceId=None,          ")
        print("               dry_run=False)                - Wipe player data from save")
        print("                                               InstanceId: delete specified InstanceId")
        print("                                               dry_run: only show how to delete")
        print("  EditPlayer(uid)                            - Allocate player base meta data to variable 'player'")
        print("  OpenBackup(filename)                       - Open Backup Level.sav file and assign to backup_wsd")
        print("  MigratePlayer(old_uid,new_uid)             - Migrate the player from old PlayerUId to new PlayerUId")
        print("                                               Note: the PlayerUId is use in the Sav file,")
        print("                                               when use to fix broken save, you can rename the old ")
        print("                                               player save to another UID and put in old_uid field.")
        print("  CopyPlayer(old_uid,new_uid, backup_wsd)    - Copy the player from old PlayerUId to new PlayerUId ")
        print("                                               Note: be sure you have already use the new playerUId to ")
        print("                                               login the game.")
        print("  Save()                                     - Save the file and exit")
        print()
        print("Advance feature:")
        print("  search_key(wsd, '<value>')                 - Locate the key in the structure")
        print("  search_values(wsd, '<value>')              - Locate the value in the structure")
        print("  PrettyPrint(value)                         - Use XML format to show the value")
        return

    if args.fix_missing or args.fix_capture:
        Save()

def EditPlayer(player_uid):
    global player
    for item in wsd['CharacterSaveParameterMap']['value']:
        if str(item['key']['PlayerUId']['value']) == player_uid:
            player = item['value']['RawData']['value']['object']['SaveParameter']['value']
            print("Player has allocated to 'player' variable, you can use player['Property']['value'] = xxx to modify")
            pp.pprint(player)

def RenamePlayer(player_uid, new_name):
    for item in wsd['CharacterSaveParameterMap']['value']:
        if str(item['key']['PlayerUId']['value']) == player_uid:
            player = item['value']['RawData']['value']['object']['SaveParameter']['value']
            print(
                "\033[32mRename User\033[0m  UUID: %s  Level: %d  CharacterID: \033[93m%s\033[0m -> %s" % (
                    str(item['key']['InstanceId']['value']), player['Level']['value'],
                    player['NickName']['value'], new_name))
            player['NickName']['value'] = new_name
    for group_data in wsd['GroupSaveDataMap']['value']:
        if str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Guild":
            item = group_data['value']['RawData']['value']
            for g_player in item['players']:
                if str(g_player['player_uid']) == player_uid:
                    print(
                        "\033[32mRename Guild User\033[0m  \033[93m%s\033[0m  -> %s" % (
                            g_player['player_info']['player_name'], new_name))
                    g_player['player_info']['player_name'] = new_name
                    break


def OpenBackup(filename):
    global backup_gvas_file, backup_wsd
    print(f"Loading {filename}...")
    with open(filename, "rb") as f:
        # Read the file
        data = f.read()
        raw_gvas, _ = decompress_sav_to_gvas(data)

        print(f"Parsing {filename}...", end="", flush=True)
        backup_gvas_file = GvasFile.read(raw_gvas, PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES)
        print("Done.")
    backup_wsd = backup_gvas_file.properties['worldSaveData']['value']


def to_storage_uuid(uuid_str):
    return UUID.from_str(str(uuid_str))

def CopyPlayer(player_uid, new_player_uid, old_wsd, dry_run=False):
    player_sav_file = os.path.dirname(os.path.abspath(args.filename)) + "/Players/" + player_uid.upper().replace("-",
                                                                                                                 "") + ".sav"
    new_player_sav_file = os.path.dirname(
        os.path.abspath(args.filename)) + "/Players/" + new_player_uid.upper().replace("-", "") + ".sav"
    playerInstanceId = None
    instances = []
    container_mapping = {}
    if not os.path.exists(player_sav_file) or not os.path.exists(new_player_sav_file):
        print("\033[33mWarning: Player Sav file Not exists: %s\033[0m" % player_sav_file)
        return
    else:
        with open(player_sav_file, "rb") as f:
            raw_gvas, _ = decompress_sav_to_gvas(f.read())
            player_gvas_file = GvasFile.read(raw_gvas, PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES)
        with open(new_player_sav_file, "rb") as f:
            raw_gvas, _ = decompress_sav_to_gvas(f.read())
            new_player_gvas_file = GvasFile.read(raw_gvas, PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES)
        new_player_gvas = new_player_gvas_file.properties['SaveData']['value']
        player_gvas = player_gvas_file.properties['SaveData']['value']
        player_uid = str(player_gvas['PlayerUId']['value'])
        player_gvas['PlayerUId']['value'] = new_player_gvas['PlayerUId']['value']
        player_gvas['IndividualId']['value']['PlayerUId']['value'] = new_player_gvas['PlayerUId']['value']
        player_gvas['IndividualId']['value']['InstanceId']['value'] = new_player_gvas['IndividualId']['value']['InstanceId']['value']
    # Clone Item from CharacterContainerSaveData
    for idx_key in ['OtomoCharacterContainerId', 'PalStorageContainerId']:
        for container in old_wsd['CharacterContainerSaveData']['value']:
            if container['key']['ID']['value'] == player_gvas[idx_key]['value']['ID']['value']:
                new_item = copy.deepcopy(container)
                IsFound = False
                for idx, insert_item in enumerate(wsd['CharacterContainerSaveData']['value']):
                    if insert_item['key']['ID']['value'] == player_gvas[idx_key]['value']['ID']['value']:
                        player_gvas[idx_key]['value']['ID']['value'] = to_storage_uuid(uuid.uuid4())
                        new_item['key']['ID']['value'] = player_gvas[idx_key]['value']['ID']['value']
                        IsFound = True
                        break
                container_mapping[idx_key] = new_item
                if not dry_run:
                    wsd['CharacterContainerSaveData']['value'].append(new_item)
                if IsFound:
                    print(
                        "\033[32mCopy Character Container\033[0m %s UUID: %s -> %s" % (idx_key,
                            str(container['key']['ID']['value']), str(new_item['key']['ID']['value'])))
                else:
                    print(
                        "\033[32mCopy Character Container\033[0m %s UUID: %s" % (idx_key,
                            str(container['key']['ID']['value'])))
                break
    for idx_key in ['CommonContainerId', 'DropSlotContainerId', 'EssentialContainerId', 'FoodEquipContainerId',
                        'PlayerEquipArmorContainerId', 'WeaponLoadOutContainerId']:
        for container in old_wsd['ItemContainerSaveData']['value']:
            if container['key']['ID']['value'] == player_gvas['inventoryInfo']['value'][idx_key]['value']['ID']['value']:
                new_item = copy.deepcopy(container)
                IsFound = False
                for idx, insert_item in enumerate(wsd['ItemContainerSaveData']['value']):
                    if insert_item['key']['ID']['value'] == player_gvas['inventoryInfo']['value'][idx_key]['value']['ID']['value']:
                        player_gvas['inventoryInfo']['value'][idx_key]['value']['ID']['value'] = to_storage_uuid(uuid.uuid4())
                        new_item['key']['ID']['value'] = player_gvas['inventoryInfo']['value'][idx_key]['value']['ID']['value']
                        IsFound = True
                        break
                container_mapping[idx_key] = new_item
                if not dry_run:
                    wsd['ItemContainerSaveData']['value'].append(new_item)
                if IsFound:
                    print(
                        "\033[32mCopy Item Container\033[0m %s UUID: %s -> %s" % (idx_key,
                            str(container['key']['ID']['value']), str(new_item['key']['ID']['value'])))
                else:
                    print(
                        "\033[32mCopy Item Container\033[0m %s UUID: %s" % (idx_key,
                            str(container['key']['ID']['value'])))
                break
    IsFoundUser = None
    copy_user_params = None
    for idx, insert_item in enumerate(wsd['CharacterSaveParameterMap']['value']):
        if str(insert_item['key']['PlayerUId']['value']) == new_player_uid:
            IsFoundUser = idx
            break
    for item in old_wsd['CharacterSaveParameterMap']['value']:
        player = item['value']['RawData']['value']['object']['SaveParameter']['value']
        if str(item['key']['PlayerUId']['value']) == player_uid:
            # if not IsFoundUser:
            copy_user_params = copy.deepcopy(item)
            copy_user_params['key']['PlayerUId']['value'] = to_storage_uuid(uuid.UUID(new_player_uid))
            copy_user_params['key']['InstanceId']['value'] = to_storage_uuid(uuid.UUID(str(player_gvas['IndividualId']['value']['InstanceId']['value'])))
            instances.append(
                {'guid': to_storage_uuid(uuid.UUID(new_player_uid)), 'instance_id': to_storage_uuid(uuid.UUID(str(player_gvas['IndividualId']['value']['InstanceId']['value'])))})
        elif 'OwnerPlayerUId' in player and str(player['OwnerPlayerUId']['value']) == player_uid:
            IsFound = str(item['key']['InstanceId']['value']) in instanceMapping
            new_item = copy.deepcopy(item)
            new_item['value']['RawData']['value']['object']['SaveParameter']['value']['OwnerPlayerUId']['value'] = player_gvas['PlayerUId']['value']
            new_item['value']['RawData']['value']['object']['SaveParameter']['value']['SlotID']['value']['ContainerId']['value']['ID'][
                'value'] = player_gvas['PalStorageContainerId']['value']['ID']['value']
            # for slot in container_mapping['PalStorageContainerId']['value']['Slots']['value']['values']:
            #     print(slot['IndividualId']['value']['InstanceId']['value'], slot['IndividualId']['value']['PlayerUId']['value'])
            if IsFound:
                new_item['key']['InstanceId']['value'] = to_storage_uuid(uuid.uuid4())
                print(
                    "\033[32mCopy Pal\033[0m  UUID: %s -> %s  Owner: %s  CharacterID: %s" % (
                        str(item['key']['InstanceId']['value']), str(new_item['key']['InstanceId']['value']), str(player['OwnerPlayerUId']['value']),
                        player['CharacterID']['value']))
            else:
                print(
                    "\033[32mCopy Pal\033[0m  UUID: %s  Owner: %s  CharacterID: %s" % (
                        str(item['key']['InstanceId']['value']), str(player['OwnerPlayerUId']['value']),
                        player['CharacterID']['value']))
            if not dry_run:
                wsd['CharacterSaveParameterMap']['value'].append(new_item)
            instances.append({'guid':player_gvas['PlayerUId']['value'], 'instance_id': new_item['key']['InstanceId']['value']})
    if IsFoundUser is None:
        if not dry_run:
            wsd['CharacterSaveParameterMap']['value'].append(copy_user_params)
        print("\033[32mCopy User\033[0m")
    else:
        wsd['CharacterSaveParameterMap']['value'][IsFoundUser] = copy_user_params
        print("\033[32mUpdate User\033[0m")
    # Copy Item from GroupSaveDataMap
    player_group = None
    for group_data in wsd['GroupSaveDataMap']['value']:
        if str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Guild":
            item = group_data['value']['RawData']['value']
            for g_player in item['players']:
                if str(g_player['player_uid']) == new_player_uid:
                    player_group = group_data
                    if not dry_run:
                        item['individual_character_handle_ids'] += instances
                    print(
                        "\033[32mCopy User to Guild\033[0m  \033[93m%s\033[0m   [\033[92m%s\033[0m] Last Online: %d" % (
                            g_player['player_info']['player_name'], str(g_player['player_uid']),
                            g_player['player_info']['last_online_real_time']))
                    copy_user_params['value']['RawData']['value']['group_id'] = group_data['value']['RawData']['value']['group_id']
                    break
    if player_group is None:
        for group_data in old_wsd['GroupSaveDataMap']['value']:
            if str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Guild":
                item = group_data['value']['RawData']['value']
                for player in item['players']:
                    if str(player['player_uid']) == player_uid:
                        # Check group is exists
                        player_group = None
                        for chk_group_data in wsd['GroupSaveDataMap']['value']:
                            if str(group_data['key']) == str(chk_group_data['key']):
                                player_group = chk_group_data
                                break
                        if player_group is None:
                            print(
                                "\033[32mCopy Guild\033[0m  \033[93m%s\033[0m   [\033[92m%s\033[0m] Last Online: %d" % (
                                    g_player['player_info']['player_name'], str(g_player['player_uid']),
                                    g_player['player_info']['last_online_real_time']))
                            copy_user_params['value']['RawData']['value']['group_id'] = \
                            group_data['value']['RawData']['value']['group_id']
                            player_group = copy.deepcopy(group_data)
                            wsd['GroupSaveDataMap']['value'].append(player_group)
                            n_item = player_group['value']['RawData']['value']
                            for n_player_info in n_item['players']:
                                if str(n_player_info['player_uid']) == player_uid:
                                    n_player_info['player_uid'] = to_storage_uuid(uuid.UUID(new_player_uid))
                                    n_item['players'] = [n_player_info]
                                    break
                            n_item['individual_character_handle_ids'] = instances
                        else:
                            print(
                                "\033[32mCopy User from Guild\033[0m  \033[93m%s\033[0m   [\033[92m%s\033[0m] Last Online: %d" % (
                                g_player['player_info']['player_name'], str(g_player['player_uid']),
                                g_player['player_info']['last_online_real_time']))
                            copy_user_params['value']['RawData']['value']['group_id'] = \
                            group_data['value']['RawData']['value']['group_id']
                            n_item = player_group['value']['RawData']['value']
                            is_player_found = False
                            for n_player_info in n_item['players']:
                                if str(n_player_info['player_uid']) == new_player_uid:
                                    n_player_info['player_info'] = copy.deepcopy(player_info['player_info'])
                                    is_player_found = True
                                    break
                            if not is_player_found:
                                print("\033[32mAdd User to Guild\033[0m  \033[93m%s\033[0m   [\033[92m%s\033[0m] Last Online: %d" % (
                                g_player['player_info']['player_name'], str(g_player['player_uid']),
                                g_player['player_info']['last_online_real_time']))
                                n_player_info['players'].append({
                                    'player_uid': to_storage_uuid(uuid.UUID(new_player_uid)),
                                    'player_info': copy.deepcopy(player_info['player_info'])
                                })
                            n_item['individual_character_handle_ids'] = instances
                        break
                if not dry_run:
                    item['individual_character_handle_ids'] += instances
    if not dry_run:
        with open(new_player_sav_file, "wb") as f:
            print("Saving new player sav %s" % (new_player_sav_file))
            if "Pal.PalWorldSaveGame" in player_gvas_file.header.save_game_class_name or "Pal.PalLocalWorldSaveGame" in player_gvas_file.header.save_game_class_name:
                save_type = 0x32
            else:
                save_type = 0x31
            sav_file = compress_gvas_to_sav(player_gvas_file.write(PALWORLD_CUSTOM_PROPERTIES), save_type)
            f.write(sav_file)

def MigratePlayer(player_uid, new_player_uid):
    player_sav_file = os.path.dirname(os.path.abspath(args.filename)) + "/Players/" + player_uid.upper().replace("-","") + ".sav"
    new_player_sav_file = os.path.dirname(os.path.abspath(args.filename)) + "/Players/" + new_player_uid.upper().replace("-","") + ".sav"
    DeletePlayer(new_player_uid)
    if not os.path.exists(player_sav_file) or not os.path.exists(new_player_sav_file):
        print("\033[33mWarning: Player Sav file Not exists: %s\033[0m" % player_sav_file)
        return
    else:
        with open(player_sav_file, "rb") as f:
            raw_gvas, _ = decompress_sav_to_gvas(f.read())
            player_gvas_file = GvasFile.read(raw_gvas, PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES)
        player_gvas = player_gvas_file.properties['SaveData']['value']
        with open(new_player_sav_file, "rb") as f:
            raw_gvas, _ = decompress_sav_to_gvas(f.read())
            new_player_gvas_file = GvasFile.read(raw_gvas, PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES)
        new_player_gvas = new_player_gvas_file.properties['SaveData']['value']
        # Copy Instance ID From new player
        player_uid = player_gvas['PlayerUId']['value']
        player_gvas['PlayerUId']['value'] = new_player_gvas['PlayerUId']['value']
        player_gvas['IndividualId']['value']['PlayerUId']['value'] = new_player_gvas['PlayerUId']['value']
        player_gvas['IndividualId']['value']['InstanceId']['value'] = new_player_gvas['IndividualId']['value']['InstanceId']['value']
        for idx_key in ['CommonContainerId', 'DropSlotContainerId', 'EssentialContainerId', 'FoodEquipContainerId',
                        'PlayerEquipArmorContainerId', 'WeaponLoadOutContainerId']:
           new_player_gvas['inventoryInfo']['value'][idx_key]['value']['ID']['value'] = player_gvas['inventoryInfo']['value'][idx_key]['value']['ID']['value']
        with open(new_player_sav_file, "wb") as f:
            print("Saving new player sav %s" % new_player_sav_file)
            if "Pal.PalWorldSaveGame" in player_gvas_file.header.save_game_class_name or "Pal.PalLocalWorldSaveGame" in player_gvas_file.header.save_game_class_name:
                save_type = 0x32
            else:
                save_type = 0x31
            sav_file = compress_gvas_to_sav(player_gvas_file.write(PALWORLD_CUSTOM_PROPERTIES), save_type)
            f.write(sav_file)
    for item in wsd['CharacterSaveParameterMap']['value']:
        player = item['value']['RawData']['value']['object']['SaveParameter']['value']
        if str(item['key']['PlayerUId']['value']) == str(player_uid):
            item['key']['PlayerUId']['value'] = new_player_gvas['PlayerUId']['value']
            item['key']['InstanceId']['value'] = new_player_gvas['IndividualId']['value']['InstanceId']['value']
            print(
                "\033[32mMigrate User\033[0m  UUID: %s  Level: %d  CharacterID: \033[93m%s\033[0m" % (
                    str(item['key']['InstanceId']['value']), player['Level']['value'] if 'Level' in player else -1,
                    player['NickName']['value']))
        elif 'OwnerPlayerUId' in player and str(player['OwnerPlayerUId']['value']) == str(player_uid):
            player['OwnerPlayerUId']['value'] = to_storage_uuid(uuid.UUID(new_player_uid))
            player['OldOwnerPlayerUIds']['value']['values'].insert(0, to_storage_uuid(uuid.UUID(new_player_uid)))
            print(
                "\033[32mMigrate Pal\033[0m  UUID: %s  Owner: %s  CharacterID: %s" % (
                    str(item['key']['InstanceId']['value']), str(player['OwnerPlayerUId']['value']),
                    player['CharacterID']['value']))
    for group_data in wsd['GroupSaveDataMap']['value']:
        if str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Guild":
            item = group_data['value']['RawData']['value']
            for player in item['players']:
                if str(player['player_uid']) == str(player_uid):
                    player['player_uid'] = new_player_gvas['PlayerUId']['value']
                    print(
                        "\033[32mMigrate User from Guild\033[0m  \033[93m%s\033[0m   [\033[92m%s\033[0m] Last Online: %d" % (
                            player['player_info']['player_name'], str(player['player_uid']),
                            player['player_info']['last_online_real_time']))
                    break
            if str(item['admin_player_uid']) == str(player_uid):
                item['admin_player_uid'] =  new_player_gvas['PlayerUId']['value']
                print("\033[32mMigrate Guild Admin \033[0m")
            for ind_char in item['individual_character_handle_ids']:
                if str(ind_char['guid']) == str(player_uid):
                    ind_char['guid'] = new_player_gvas['PlayerUId']['value']
                    ind_char['instance_id'] = new_player_gvas['IndividualId']['value']['InstanceId']['value']
                    print("\033[32mMigrate Guild Character %s\033[0m" % (str(ind_char['instance_id'])))
    for map_data in wsd['MapObjectSaveData']['value']['values']:
        if str(map_data['Model']['value']['RawData']['value']['build_player_uid']) == str(player_uid):
            map_data['Model']['value']['RawData']['value']['build_player_uid'] = new_player_gvas['PlayerUId']['value']
            print(
                "\033[32mMigrate Building\033[0m  \033[93m%s\033[0m" % (
                    str(map_data['MapObjectInstanceId']['value'])))
    print("Finish to migrate player from Save, please delete this file manually: %s" % player_sav_file)

def DeletePlayer(player_uid, InstanceId = None, dry_run=False):
    player_sav_file = os.path.dirname(os.path.abspath(args.filename)) + "/Players/" + player_uid.upper().replace("-",
                                                                                                                 "") + ".sav"
    player_container_ids = []
    playerInstanceId = None
    if InstanceId is None:
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
    else:
        playerInstanceId = InstanceId
    remove_items = []
    remove_instance_id = []
    # Remove item from CharacterSaveParameterMap
    for item in wsd['CharacterSaveParameterMap']['value']:
        player = item['value']['RawData']['value']['object']['SaveParameter']['value']
        if str(item['key']['PlayerUId']['value']) == player_uid and (InstanceId is None or str(item['key']['InstanceId']['value']) == InstanceId):
            remove_items.append(item)
            remove_instance_id.append(item['key']['InstanceId']['value'])
            print(
                "\033[31mDelete User\033[0m  UUID: %s  Level: %d  CharacterID: \033[93m%s\033[0m" % (
                    str(item['key']['InstanceId']['value']), player['Level']['value'] if 'Level' in player else -1,
                    player['NickName']['value']))
        elif 'OwnerPlayerUId' in player and str(player['OwnerPlayerUId']['value']) == player_uid and InstanceId is None:
            remove_instance_id.append(item['key']['InstanceId']['value'])
            print(
                "\033[31mDelete Pal\033[0m  UUID: %s  Owner: %s  CharacterID: %s" % (
                    str(item['key']['InstanceId']['value']), str(player['OwnerPlayerUId']['value']),
                    player['CharacterID']['value']))
            remove_items.append(item)
        elif 'SlotID' in player and player['SlotID']['value']['ContainerId']['value']['ID'][
            'value'] in player_container_ids and InstanceId is None:
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
    remove_guilds = []
    for group_data in wsd['GroupSaveDataMap']['value']:
        if str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Guild":
            item = group_data['value']['RawData']['value']
            for player in item['players']:
                if str(player['player_uid']) == player_uid and InstanceId is None:
                    print(
                        "\033[31mDelete User \033[93m %s \033[0m from Guild\033[0m \033[93m %s \033[0m   [\033[92m%s\033[0m] Last Online: %d" % (
                            player['player_info']['player_name'],
                            item['guild_name'], str(player['player_uid']),
                            player['player_info']['last_online_real_time']))
                    if not dry_run:
                        item['players'].remove(player)
                        if len(item['players']) == 0:
                            remove_guilds.append(group_data)
                            print("\033[31mDelete Guild\033[0m \033[93m %s \033[0m  UUID: %s" % (
                                item['guild_name'], str(item['group_id'])))
                    break
            removeItems = []
            for ind_char in item['individual_character_handle_ids']:
                if ind_char['instance_id'] in remove_instance_id:
                    print("\033[31mDelete Guild Character %s\033[0m" % (str(ind_char['instance_id'])))
                    removeItems.append(ind_char)
            if not dry_run:
                for ind_char in removeItems:
                    item['individual_character_handle_ids'].remove(ind_char)
    for guild in remove_guilds:
        wsd['GroupSaveDataMap']['value'].remove(guild)
    if InstanceId is None:
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
        elif uuid_match is not None and uuid_match in dicts.values():
            print("Found UUID  at %s['%s']" % (level, list(dicts.keys())[list(dicts.values()).index(uuid_match)]))
            isFound = True
        for k in dicts:
            if level == "":
                print("Searching %s" % k)
            if isinstance(dicts[k], dict) or isinstance(dicts[k], list):
                isFound |= search_values(dicts[k], key, level + "['%s']" % k)
    elif isinstance(dicts, list):
        if key in dicts:
            print("Found value at %s[%d]" % (level, dicts.index(key)))
            isFound = True
        elif uuid_match is not None and uuid_match in dicts:
            print("Found UUID  at %s[%d]" % (level, dicts.index(uuid_match)))
            isFound = True
        for idx, l in enumerate(dicts):
            if level == "":
                print("Searching %s" % l)
            if isinstance(l, dict) or isinstance(l, list):
                isFound |= search_values(l, key, level + "[%d]" % idx)
    return isFound


def ShowPlayers():
    global playerMapping, instanceMapping
    playerMapping = {}
    instanceMapping = {}
    for item in wsd['CharacterSaveParameterMap']['value']:
        instanceMapping[str(item['key']['InstanceId']['value'])] = item
        if "00000000-0000-0000-0000-000000000000" != str(item['key']['PlayerUId']['value']):
            player = item['value']['RawData']['value']['object']['SaveParameter']
            if player['struct_type'] == 'PalIndividualCharacterSaveParameter':
                playerParams = player['value']
                playerMeta = {}
                for player_k in playerParams:
                    playerMeta[player_k] = playerParams[player_k]['value']
                playerMeta['InstanceId'] = item['key']['InstanceId']['value']
                playerMapping[str(item['key']['PlayerUId']['value'])] = playerMeta
            print("PlayerUId \033[32m %s \033[0m [InstanceID \033[33m %s \033[0m] -> Level %2d  %s" % (
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


def FixMissing(dry_run=False):
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
                removeItems.append(item)
    if not dry_run:
        for item in removeItems:
            wsd['CharacterSaveParameterMap']['value'].remove(item)


def TickToHuman(tick):
    seconds = (wsd['GameTimeSaveData']['value']['RealDateTimeTicks']['value'] - tick) / 1e7
    s = ""
    if seconds > 86400:
        s += " %d d" % (seconds // 86400)
        seconds %= 86400
    if seconds > 3600:
        s += " %d h" % (seconds // 3600)
        seconds %= 3600
    if seconds > 60:
        s += " %d m" % (seconds // 60)
        seconds %= 60
    s += " %d s" % seconds
    return s

def TickToLocal(tick):
    ts = filetime + (tick - wsd['GameTimeSaveData']['value']['RealDateTimeTicks']['value']) / 1e7
    t = datetime.datetime.fromtimestamp(ts)
    return t.strftime("%Y-%m-%d %H:%M:%S")


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
                print("    Player \033[93m %-30s \033[0m\t[\033[92m%s\033[0m] Last Online: %s - %s" % (
                    player['player_info']['player_name'], str(player['player_uid']),
                    TickToLocal(player['player_info']['last_online_real_time']),
                    TickToHuman(player['player_info']['last_online_real_time'])))
            removeItems = []
            for ind_char in mapObjectMeta['individual_character_handle_ids']:
                if str(ind_char['instance_id']) in instanceMapping:
                    character = \
                        instanceMapping[str(ind_char['instance_id'])]['value']['RawData']['value']['object'][
                            'SaveParameter'][
                            'value']
                    # if 'NickName' in character:
                    #     print("    Player %s -> %s" % (str(ind_char['instance_id']), character['NickName']['value']))
                    # else:
                    #     print("    Character %s -> %s" % (str(ind_char['instance_id']), character['CharacterID']['value']))
                else:
                    print("    \033[31mInvalid Character %s\033[0m" % (str(ind_char['instance_id'])))
                    removeItems.append(ind_char)
            print("After remove character count: %d" % (len(
                group_data['value']['RawData']['value']['individual_character_handle_ids']) - len(removeItems)))
            if fix_capture:
                for rmitem in removeItems:
                    item['individual_character_handle_ids'].remove(rmitem)
            print()
        # elif str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Neutral":
        #     item = group_data['value']['RawData']['value']
        #     print("Neutral Group ID %s  Character Count: %d" % (str(item['group_id']), len(item['individual_character_handle_ids'])))
        #     for ind_char in item['individual_character_handle_ids']:
        #         if ind_char['instance_id'] not in instanceMapping:
        #             print("    \033[31mInvalid Character %s\033[0m" % (str(ind_char['instance_id'])))


def PrettyPrint(data, level = 0):
    simpleType = ['DateTime', 'Guid', 'LinearColor', 'Quat', 'Vector', 'PalContainerId']
    if 'struct_type' in data:
        if data['struct_type'] == 'DateTime':
            print("%s<Value Type='DateTime'>%d</Value>" % ("  " * level, data['value']))
        elif data['struct_type'] == 'Guid':
            print("\033[96m%s\033[0m" % (data['value']), end="")
        elif data['struct_type'] == "LinearColor":
            print("%.f %.f %.f %.f" % (data['value']['r'],
                                                                           data['value']['g'],
                                                                           data['value']['b'],
                                                                           data['value']['a']), end="")
        elif data['struct_type'] == "Quat":
            print("%.f %.f %.f %.f" % (data['value']['x'],
                                                                           data['value']['y'],
                                                                           data['value']['z'],
                                                                           data['value']['w']), end="")
        elif data['struct_type'] == "Vector":
            print("%.f %.f %.f" % (data['value']['x'],
                                                                           data['value']['y'],
                                                                           data['value']['z']), end="")
        elif data['struct_type'] == "PalContainerId":
            print("\033[96m%s\033[0m" % (data['value']['ID']['value']), end="")
        elif isinstance(data['struct_type'], dict):
            print("%s<%s>" % ("  " * level, data['struct_type']))
            for key in data['value']:
                PrettyPrint(data['value'], level + 1)
            print("%s</%s>" % ("  " * level, data['struct_type']))
        else:
            PrettyPrint(data['value'], level + 1)
    else:
        for key in data:
            if not isinstance(data[key], dict):
                print("%s<%s type='unknow'>%s</%s>" % ("  " * level, key, data[key], key))
                continue
            if 'struct_type' in data[key] and data[key]['struct_type'] in simpleType:
                print("%s<%s type='%s'>" % ("  " * level, key, data[key]['struct_type']), end="")
                PrettyPrint(data[key], level + 1)
                print("</%s>" % (key))
            elif 'type' in data[key] and data[key]['type'] in ["IntProperty", "Int64Property", "BoolProperty"]:
                print("%s<%s Type='%s'>\033[95m%d\033[0m</%s>" % ("  " * level, key, data[key]['type'], data[key]['value'], key))
            elif 'type' in data[key] and data[key]['type'] == "FloatProperty":
                print("%s<%s Type='%s'>\033[95m%f\033[0m</%s>" % ("  " * level, key, data[key]['type'], data[key]['value'], key))
            elif 'type' in data[key] and data[key]['type'] in ["StrProperty", "ArrayProperty", "NameProperty"]:
                print("%s<%s Type='%s'>\033[95m%s\033[0m</%s>" % ("  " * level, key, data[key]['type'], data[key]['value'], key))
            elif isinstance(data[key], list):
                print("%s<%s Type='%s'>%s</%s>" % ("  " * level, key, data[key]['struct_type'] if 'struct_type' in data[
                    key] else "\033[31munknow struct\033[0m", str(data[key]), key))
            else:
                print("%s<%s Type='%s'>" % ("  " * level, key, data[key]['struct_type'] if 'struct_type' in data[key] else "\033[31munknow struct\033[0m"))
                PrettyPrint(data[key], level + 1)
                print("%s</%s>" % ("  " * level, key))

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
