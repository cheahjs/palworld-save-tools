import ctypes
import json
import re
import uuid


class NoIndent(object):
    """Value wrapper."""

    def __init__(self, value):
        if not isinstance(value, (list, tuple)):
            raise TypeError("Only lists and tuples can be wrapped")
        self.value = value


class CustomEncoder(json.JSONEncoder):
    FORMAT_SPEC = "@@{}@@"
    regex = re.compile(FORMAT_SPEC.format(r"(\d+)"))

    def __init__(self, **kwargs):
        # Keyword arguments to ignore when encoding NoIndent wrapped values.
        ignore = {"cls", "indent"}

        # Save copy of any keyword argument values needed for use here.
        self._kwargs = {k: v for k, v in kwargs.items() if k not in ignore}
        super(CustomEncoder, self).__init__(**kwargs)

    def default(self, obj):
        if isinstance(obj, NoIndent):
            return self.FORMAT_SPEC.format(id(obj))
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        return super(CustomEncoder, self).default(obj)

    def iterencode(self, obj, **kwargs):
        format_spec = self.FORMAT_SPEC  # Local var to expedite access.

        # Replace any marked-up NoIndent wrapped values in the JSON repr
        # with the json.dumps() of the corresponding wrapped Python object.
        for encoded in super(CustomEncoder, self).iterencode(obj, **kwargs):
            match = self.regex.search(encoded)
            if match:
                id = int(match.group(1))
                no_indent = ctypes.cast(id, ctypes.py_object).value
                json_repr = json.dumps(no_indent.value, **self._kwargs)
                # Replace the matched id string with json formatted representation
                # of the corresponding Python object.
                encoded = encoded.replace(
                    '"{}"'.format(format_spec.format(id)), json_repr
                )

            yield encoded


class NoIndentByteDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if "value" in dct:
            if "values" in dct["value"]:
                if isinstance(dct["value"]["values"], list):
                    if isinstance(dct["value"]["values"][0], int):
                        dct["value"]["values"] = NoIndent(dct["value"]["values"])
        return dct
