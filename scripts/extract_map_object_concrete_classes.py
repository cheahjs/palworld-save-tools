#!/usr/bin/env python3
# This script extracts the concrete classes of map objects from an FModel export

import json
import os
import sys


def main():
    export_path = sys.argv[1]
    # Load the map object DataTable
    with open(
        os.path.join(
            export_path,
            "Pal",
            "Content",
            "Pal",
            "DataTable",
            "MapObject",
            "DT_MapObjectMasterDataTable.json",
        ),
        "rb",
    ) as f:
        map_object_data_table = json.load(f)
    # Load the blueprints by walking down the export list
    blueprints = {}
    for root, dirs, files in os.walk(
        os.path.join(export_path, "Pal", "Content", "Pal", "Blueprint")
    ):
        for file in files:
            if file.endswith(".json"):
                with open(os.path.join(root, file), "rb") as f:
                    data = json.load(f)
                    # map the individual types
                    mapped = {}
                    for obj in data:
                        mapped[obj["Name"].lower()] = obj
                    blueprints[file.removesuffix(".json").lower()] = mapped

    # Extract the blueprints for each object
    object_blueprints = {}
    for object_name in map_object_data_table[0]["Rows"]:
        object_data = map_object_data_table[0]["Rows"][object_name]
        asset_path_name = object_data["BlueprintClassSoft"]["AssetPathName"]
        if asset_path_name == "None":
            print(f"Skipping {object_name} as it has no blueprint soft ptr")
            continue
        blueprint_class_name = object_data["BlueprintClassName"]
        if blueprint_class_name.lower() not in blueprints:
            print(
                f"Skipping {object_name} as the blueprint class {blueprint_class_name} is not found"
            )
            continue
        object_blueprints[object_name.lower()] = blueprint_class_name.lower()

    def resolve_concrete_class_name(class_name):
        if class_name.startswith("Class'"):
            return class_name.removesuffix("'").removeprefix("Class'")
        elif class_name.startswith("BlueprintGeneratedClass'"):
            blueprint_class_search = class_name.removesuffix("_C'").removeprefix(
                "BlueprintGeneratedClass'"
            )
            if blueprint_class_search.lower() not in blueprints:
                print(f"Warning: Blueprint class {blueprint_class_search} not found")
                return None
            blueprint_class = blueprints[blueprint_class_search.lower()]
            for _, class_data in blueprint_class.items():
                if class_data["Type"] == "BlueprintGeneratedClass":
                    return resolve_concrete_class_name(
                        class_data["SuperStruct"]["ObjectName"]
                    )
        print(f"Warning: Unhandled class name {class_name}")
        return None

    def resolve_object_super_concrete_class_name(class_name):
        if class_name.startswith("Class'"):
            return class_name.removesuffix("'").removeprefix("Class'")
        elif class_name.startswith("BlueprintGeneratedClass'"):
            blueprint_class_search = class_name.removesuffix("_C'").removeprefix(
                "BlueprintGeneratedClass'"
            )
            if blueprint_class_search.lower() not in blueprints:
                print(f"Warning: Blueprint class {blueprint_class_search} not found")
                return None
            blueprint_class = blueprints[blueprint_class_search.lower()]
            struct_data = blueprint_class.get(
                f"Default__{blueprint_class_search}_C".lower(), None
            )
            if struct_data is None:
                print("Warning: No struct found for", blueprint_class_search)
                return None
            if "ConcreteModelClass" in struct_data["Properties"]:
                return resolve_concrete_class_name(
                    struct_data["Properties"]["ConcreteModelClass"]["ObjectName"]
                )
        print(f"Warning: Unhandled class name {class_name}")
        return None

    # Extract the concrete classes
    concrete_classes = {}
    for object_name, blueprint_class_name in object_blueprints.items():
        print(blueprint_class_name)
        blueprint = blueprints[blueprint_class_name]
        # Search for the generated class definition
        struct_data = blueprint.get(f"Default__{blueprint_class_name}_C".lower(), None)
        if struct_data is None:
            print("Warning: No struct found for", blueprint_class_name)
            continue
        if "ConcreteModelClass" in struct_data["Properties"]:
            concrete_classes[object_name] = resolve_concrete_class_name(
                struct_data["Properties"]["ConcreteModelClass"]["ObjectName"]
            )
        else:
            # Search for the super class
            bp_gen_class = blueprint.get(f"{blueprint_class_name}_C".lower(), None)
            if bp_gen_class is None:
                print(
                    "Warning: No blueprint generated class found for",
                    blueprint_class_name,
                )
                continue
            concrete_class = resolve_object_super_concrete_class_name(
                bp_gen_class["SuperStruct"]["ObjectName"]
            )
            print(concrete_class)
            concrete_classes[object_name] = concrete_class
            if concrete_class is None:
                print("Warning: No concrete class found for", object_name)
                concrete_classes[object_name] = (
                    "DEFAULT_UNKNOWN_PalMapObjectConcreteModelBase"
                )

    print(concrete_classes)


if __name__ == "__main__":
    main()
