#!/usr/bin/env python3

import json
import os
import sys
from lib.palsav import *
from lib.rawdata import *
from lib.writer import *


def main():
    # Check if argument exists
    if len(sys.argv) < 3:
        print(sys.argv[0] + "<uesave.exe> <path to .sav.json file>")
        exit(1)
    # Take the first argument as the path to uesave.exe
    uesave_path = sys.argv[1]
    if not os.path.exists(uesave_path):
        print(f"uesave does not exist at {uesave_path}")
        exit(1)
    # Take the second argument as a path to a save file
    save_path = sys.argv[2]
    if not os.path.exists(save_path):
        print(f"Path {save_path} does not exist")
        exit(1)
    print(f"Loading JSON from {save_path}")
    with open(save_path, "rb") as f:
        data = json.load(f)
    if "worldSaveData" in data["root"]["properties"]:
        print(f"Encoding GroupSaveDataMap")
        encode_group_data(data)
        print(f"Encoding CharacterSaveParameterMap")
        encode_character_data(data)
    print(f"Converting JSON")
    convert_to_save(uesave_path, save_path, data)


if __name__ == "__main__":
    main()
