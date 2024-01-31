import json
import uuid


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super(CustomEncoder, self).default(obj)
