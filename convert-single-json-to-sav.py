#!/usr/bin/env python3

import json
import os
import sys
from lib.gvas import GvasFile
from lib.palsav import *
from lib.paltypes import PALWORLD_CUSTOM_PROPERTIES
from lib.rawdata import *


def main():
    # Check if argument exists
    if len(sys.argv) < 2:
        print(sys.argv[0] + " <path to .sav.json file>")
        exit(1)
    # Take the first argument as a path to a save file
    save_path = sys.argv[1]
    if not os.path.exists(save_path):
        print(f"Path {save_path} does not exist")
        exit(1)
    if not os.path.isfile(save_path):
        print(f"Path {save_path} is not a file")
        exit(1)
    print(f"Loading JSON from {save_path}")
    with open(save_path, "r") as f:
        data = json.load(f)
    gvas_file = GvasFile.load(data)
    print(f"Compressing sav file")
    if (
        "Pal.PalWorldSaveGame" in gvas_file.header.save_game_class_name
        or "Pal.PalLocalWorldSaveGame" in gvas_file.header.save_game_class_name
    ):
        save_type = 0x32
    else:
        save_type = 0x31
    sav_file = compress_gvas_to_sav(
        gvas_file.write(PALWORLD_CUSTOM_PROPERTIES), save_type
    )
    output_path = save_path.replace(".json", "")
    print(f"Converting to .sav and writing to {output_path}")
    with open(output_path, "wb") as f:
        f.write(sav_file)


if __name__ == "__main__":
    main()
