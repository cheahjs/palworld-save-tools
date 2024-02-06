from typing import Any

from palworld_save_tools.archive import Any, FArchiveReader, FArchiveWriter


def pal_item_and_num_read(reader: FArchiveReader) -> dict[str, Any]:
    return {
        "item_id": {
            "static_id": reader.fstring(),
            "dynamic_id": {
                "created_world_id": reader.guid(),
                "local_id_in_created_world": reader.guid(),
            },
        },
        "num": reader.u32(),
    }


def pal_item_and_slot_writer(writer: FArchiveWriter, p: dict[str, Any]) -> None:
    writer.fstring(p["item_id"]["static_id"])
    writer.guid(p["item_id"]["dynamic_id"]["created_world_id"])
    writer.guid(p["item_id"]["dynamic_id"]["local_id_in_created_world"])
    writer.u32(p["num"])
