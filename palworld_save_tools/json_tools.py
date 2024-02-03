import dataclasses
import json
import uuid

from palworld_save_tools.archive import UUID, SerializableBase


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, SerializableBase):
            return obj.to_json()
        return super(CustomEncoder, self).default(obj)
