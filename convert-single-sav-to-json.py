#!/usr/bin/env python3

import json
import os
import sys
from lib.gvas import GvasFile
from lib.noindent import *
from lib.palsav import *
from lib.paltypes import PALWORLD_CUSTOM_PROPERTIES, PALWORLD_TYPE_HINTS
from lib.rawdata import *


def main():
    # Check if argument exists
    if len(sys.argv) < 2:
        print(sys.argv[0] + " <path to .sav file>")
        exit(1)
    # Take the first argument as a path to a save file
    save_path = sys.argv[1]
    if not os.path.exists(save_path):
        print(f"Path {save_path} does not exist")
        exit(1)
    if not os.path.isfile(save_path):
        print(f"Path {save_path} is not a file")
        exit(1)
    print(f"Converting {save_path} to JSON")
    print(f"Decompressing sav file")
    with open(save_path, "rb") as f:
        data = f.read()
        raw_gvas, _ = decompress_sav_to_gvas(data)
    print(f"Loading GVAS file")
    gvas_file = GvasFile.read(raw_gvas, PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES)
    output_path = save_path + ".json"
    print(f"Writing JSON to {output_path}")
    with open(output_path, "w", encoding="utf8") as f:
        json.dump(gvas_file.dump(), f, indent=2, cls=CustomEncoder, ensure_ascii=False)


if __name__ == "__main__":
    main()
