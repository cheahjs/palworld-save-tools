import io
import os
import struct
from typing import Callable, Union
import uuid


def instance_id_reader(reader):
    return {
        "guid": reader.read_uuid(),
        "instance_id": reader.read_uuid(),
    }


def uuid_reader(reader):
    b = reader.read_bytes(16)
    return uuid.UUID(
        bytes=bytes(
            [
                b[0x3],
                b[0x2],
                b[0x1],
                b[0x0],
                b[0x7],
                b[0x6],
                b[0x5],
                b[0x4],
                b[0xB],
                b[0xA],
                b[0x9],
                b[0x8],
                b[0xF],
                b[0xE],
                b[0xD],
                b[0xC],
            ]
        )
    )


class FArchiveReader:
    data: io.BytesIO
    size: int
    type_hints: dict[str, str]
    custom_properties: dict[str, tuple[Callable, Callable]]

    def __init__(
        self,
        data,
        type_hints: dict[str, str] = {},
        custom_properties: dict[str, tuple[Callable, Callable]] = {},
    ):
        self.data = io.BytesIO(data)
        self.size = len(self.data.read())
        self.data.seek(0)
        self.type_hints = type_hints
        self.custom_properties = custom_properties

    def __enter__(self):
        self.size = len(self.data.read())
        self.data.seek(0)
        return self

    def __exit__(self, type, value, traceback):
        self.data.close()

    def get_type_or(self, path: str, default: str):
        if path in self.type_hints:
            return self.type_hints[path]
        else:
            print(f"Struct type for {path} not found, assuming {default}")
            return default

    def eof(self):
        return self.data.tell() >= self.size

    def read(self, size: int):
        return self.data.read(size)

    def read_to_end(self):
        return self.data.read(self.size - self.data.tell())

    def read_bool(self):
        return self.read_byte() > 0

    def read_fstring(self):
        size = self.read_int32()
        LoadUCS2Char: bool = size < 0

        if LoadUCS2Char:
            if size == -2147483648:
                raise Exception("Archive is corrupted.")

            size = -size

        if size == 0:
            return ""

        data: bytes
        encoding: str
        if LoadUCS2Char:
            data = self.read(size * 2)[:-2]
            encoding = "utf-16-le"
        else:
            data = self.read(size)[:-1]
            encoding = "ascii"
        try:
            return data.decode(encoding)
        except Exception as e:
            raise Exception(
                f"Error decoding {encoding} string of length {size}: {bytes(data)}"
            ) from e

    def read_int16(self):
        return struct.unpack("h", self.data.read(2))[0]

    def read_uint16(self):
        return struct.unpack("H", self.data.read(2))[0]

    def read_int32(self):
        return struct.unpack("i", self.data.read(4))[0]

    def read_uint32(self):
        return struct.unpack("I", self.data.read(4))[0]

    def read_int64(self):
        return struct.unpack("q", self.data.read(8))[0]

    def read_uint64(self):
        return struct.unpack("Q", self.data.read(8))[0]

    def read_float(self):
        return struct.unpack("f", self.data.read(4))[0]

    def read_double(self):
        return struct.unpack("d", self.data.read(8))[0]

    def read_byte(self):
        return struct.unpack("B", self.data.read(1))[0]

    def read_bytes(self, size: int):
        return struct.unpack(str(size) + "B", self.data.read(size))

    def skip(self, size: int):
        self.data.read(size)

    def read_uuid(self):
        return uuid_reader(self)

    def read_optional_uuid(self):
        return uuid_reader(self) if self.read_bool() else None

    def read_tarray(self, type_reader):
        count = self.read_uint32()
        array = []
        for _ in range(count):
            array.append(type_reader(self))
        return array

    def read_properties_until_end(self, path=""):
        properties = {}
        while True:
            name = self.read_fstring()
            if name == "None":
                break
            type_name = self.read_fstring()
            size = self.read_uint64()
            properties[name] = self.read_property(type_name, size, f"{path}.{name}")
        return properties

    def read_property(self, type_name, size, path, allow_custom=True):
        value = {}
        if allow_custom and path in self.custom_properties:
            value = self.custom_properties[path][0](self, type_name, size, path)
            value["custom_type"] = path
        elif type_name == "StructProperty":
            value = self.read_struct(path)
        elif type_name == "IntProperty":
            value = {
                "id": self.read_optional_uuid(),
                "value": self.read_int32(),
            }
        elif type_name == "Int64Property":
            value = {
                "id": self.read_optional_uuid(),
                "value": self.read_int64(),
            }
        elif type_name == "FixedPoint64Property":
            value = {
                "id": self.read_optional_uuid(),
                "value": self.read_int32(),
            }
        elif type_name == "FloatProperty":
            value = {
                "id": self.read_optional_uuid(),
                "value": self.read_float(),
            }
        elif type_name == "StrProperty":
            value = {
                "id": self.read_optional_uuid(),
                "value": self.read_fstring(),
            }
        elif type_name == "NameProperty":
            value = {
                "id": self.read_optional_uuid(),
                "value": self.read_fstring(),
            }
        elif type_name == "EnumProperty":
            enum_type = self.read_fstring()
            _id = self.read_optional_uuid()
            enum_value = self.read_fstring()
            value = {
                "id": _id,
                "value": {
                    "type": enum_type,
                    "value": enum_value,
                },
            }
        elif type_name == "BoolProperty":
            value = {
                "value": self.read_bool(),
                "id": self.read_optional_uuid(),
            }
        elif type_name == "ArrayProperty":
            array_type = self.read_fstring()
            value = {
                "array_type": array_type,
                "id": self.read_optional_uuid(),
                "value": self.read_array_property(array_type, size - 4, path),
            }
        elif type_name == "MapProperty":
            key_type = self.read_fstring()
            value_type = self.read_fstring()
            _id = self.read_optional_uuid()
            self.read_uint32()
            count = self.read_uint32()
            values = {}
            key_path = path + ".Key"
            if key_type == "StructProperty":
                key_struct_type = self.get_type_or(key_path, "Guid")
            else:
                key_struct_type = None
            value_path = path + ".Value"
            if value_type == "StructProperty":
                value_struct_type = self.get_type_or(value_path, "StructProperty")
            else:
                value_struct_type = None
            values = []
            for _ in range(count):
                key = self.read_prop_value(key_type, key_struct_type, key_path)
                value = self.read_prop_value(value_type, value_struct_type, value_path)
                values.append(
                    {
                        "key": key,
                        "value": value,
                    }
                )
            value = {
                "key_type": key_type,
                "value_type": value_type,
                "key_struct_type": key_struct_type,
                "value_struct_type": value_struct_type,
                "id": _id,
                "value": values,
            }
        else:
            raise Exception(f"Unknown type: {type_name} ({path})")
        value["type"] = type_name
        return value

    def read_prop_value(self, type_name, struct_type_name, path):
        if type_name == "StructProperty":
            return self.read_struct_value(struct_type_name, path)
        elif type_name == "EnumProperty":
            return self.read_fstring()
        elif type_name == "NameProperty":
            return self.read_fstring()
        elif type_name == "IntProperty":
            return self.read_int32()
        elif type_name == "BoolProperty":
            return self.read_bool()
        else:
            raise Exception(f"Unknown property value type: {type_name} ({path})")

    def read_struct(self, path):
        struct_type = self.read_fstring()
        struct_id = self.read_uuid()
        _id = self.read_optional_uuid()
        value = self.read_struct_value(struct_type, path)
        return {
            "struct_type": struct_type,
            "struct_id": struct_id,
            "id": _id,
            "value": value,
        }

    def read_struct_value(self, struct_type, path=""):
        if struct_type == "Vector":
            return {
                "x": self.read_double(),
                "y": self.read_double(),
                "z": self.read_double(),
            }
        elif struct_type == "DateTime":
            return self.read_uint64()
        elif struct_type == "Guid":
            return self.read_uuid()
        elif struct_type == "Quat":
            return {
                "x": self.read_double(),
                "y": self.read_double(),
                "z": self.read_double(),
                "w": self.read_double(),
            }
        elif struct_type == "LinearColor":
            return {
                "r": self.read_float(),
                "g": self.read_float(),
                "b": self.read_float(),
                "a": self.read_float(),
            }
        else:
            if os.environ.get("DEBUG", "0") == "1":
                print(f"Assuming struct type: {struct_type} ({path})")
            return self.read_properties_until_end(path)

    def read_array_property(self, array_type, size, path):
        count = self.read_uint32()
        value = {}
        if array_type == "StructProperty":
            prop_name = self.read_fstring()
            prop_type = self.read_fstring()
            self.read_uint64()
            type_name = self.read_fstring()
            _id = self.read_uuid()
            self.skip(1)
            prop_values = []
            for _ in range(count):
                prop_values.append(
                    self.read_struct_value(type_name, f"{path}.{prop_name}")
                )
            value = {
                "prop_name": prop_name,
                "prop_type": prop_type,
                "values": prop_values,
                "type_name": type_name,
                "id": _id,
            }
        else:
            value = {
                "values": self.read_array_value(array_type, count, size, path),
            }
        return value

    def read_array_value(self, array_type, count, size, path):
        values = []
        for _ in range(count):
            if array_type == "EnumProperty":
                values.append(self.read_fstring())
            elif array_type == "NameProperty":
                values.append(self.read_fstring())
            elif array_type == "Guid":
                values.append(self.read_uuid())
            elif array_type == "ByteProperty":
                if size == count:
                    values.append(self.read_byte())
                else:
                    raise Exception("Labelled ByteProperty not implemented")
            else:
                raise Exception(f"Unknown array type: {array_type} ({path})")
        return values


def uuid_writer(writer, s: Union[str, uuid.UUID]):
    if isinstance(s, str):
        u = uuid.UUID(s)
        b = u.bytes
    else:
        b = s.bytes
    ub = bytes(
        [
            b[0x3],
            b[0x2],
            b[0x1],
            b[0x0],
            b[0x7],
            b[0x6],
            b[0x5],
            b[0x4],
            b[0xB],
            b[0xA],
            b[0x9],
            b[0x8],
            b[0xF],
            b[0xE],
            b[0xD],
            b[0xC],
        ]
    )
    writer.write(ub)


def instance_id_writer(writer, d):
    uuid_writer(writer, d["guid"])
    uuid_writer(writer, d["instance_id"])


class FArchiveWriter:
    data: io.BytesIO
    size: int
    custom_properties: dict[str, tuple[Callable, Callable]]

    def __init__(self, custom_properties: dict[str, tuple[Callable, Callable]] = {}):
        self.data = io.BytesIO()
        self.custom_properties = custom_properties

    def __enter__(self):
        self.data.seek(0)
        return self

    def __exit__(self, type, value, traceback):
        self.data.close()

    def create_nested(self) -> "FArchiveWriter":
        return FArchiveWriter(self.custom_properties)

    def bytes(self):
        pos = self.data.tell()
        self.data.seek(0)
        b = self.data.read()
        self.data.seek(pos)
        return b

    def write(self, data):
        self.data.write(data)

    def write_bool(self, bool):
        self.data.write(struct.pack("?", bool))

    def write_fstring(self, string) -> int:
        start = self.data.tell()
        if string == "":
            self.write_int32(0)
        elif string.isascii():
            str_bytes = string.encode("utf-8")
            self.write_int32(len(string) + 1)
            self.data.write(str_bytes)
            self.data.write(b"\x00")
        else:
            str_bytes = string.encode("utf-16-le")
            self.write_int32(-(len(string) + 1))
            self.data.write(str_bytes)
            self.data.write(b"\x00\x00")
        return self.data.tell() - start

    def write_int16(self, i):
        self.data.write(struct.pack("h", i))

    def write_uint16(self, i):
        self.data.write(struct.pack("H", i))

    def write_int32(self, i):
        self.data.write(struct.pack("i", i))

    def write_uint32(self, i):
        self.data.write(struct.pack("I", i))

    def write_int64(self, i):
        self.data.write(struct.pack("q", i))

    def write_uint64(self, i):
        self.data.write(struct.pack("Q", i))

    def write_float(self, i):
        self.data.write(struct.pack("f", i))

    def write_double(self, i):
        self.data.write(struct.pack("d", i))

    def write_byte(self, b):
        self.data.write(bytes([b]))

    def write_uint8(self, b):
        self.data.write(struct.pack("B", b))

    def write_bytes(self, b):
        self.data.write(b)

    def write_uuid(self, u):
        uuid_writer(self, u)

    def write_optional_uuid(self, u):
        if u is None:
            self.write_bool(False)
        else:
            self.write_bool(True)
            uuid_writer(self, u)

    def write_tarray(self, type_writer, array):
        self.write_uint32(len(array))
        for i in range(len(array)):
            type_writer(self, array[i])

    def write_properties(self, properties):
        for key in properties:
            self.write_fstring(key)
            self.write_property(properties[key])
        self.write_fstring("None")

    def write_property(self, property):
        # write type_name
        self.write_fstring(property["type"])
        nested_writer = self.create_nested()
        size: int
        property_type = property["type"]
        size = nested_writer.write_property_inner(property_type, property)
        buf = nested_writer.bytes()
        # write size
        self.write_uint64(size)
        self.write_bytes(buf)

    def write_property_inner(self, property_type, property) -> int:
        if "custom_type" in property:
            if property["custom_type"] in self.custom_properties:
                size = self.custom_properties[property["custom_type"]][1](
                    self, property_type, property
                )
            else:
                raise Exception(
                    f"Unknown custom property type: {property['custom_type']}"
                )
        elif property_type == "StructProperty":
            size = self.write_struct(property)
        elif property_type == "IntProperty":
            self.write_optional_uuid(property.get("id", None))
            self.write_int32(property["value"])
            size = 4
        elif property_type == "Int64Property":
            self.write_optional_uuid(property.get("id", None))
            self.write_int64(property["value"])
            size = 8
        elif property_type == "FixedPoint64Property":
            self.write_optional_uuid(property.get("id", None))
            self.write_int32(property["value"])
            size = 4
        elif property_type == "FloatProperty":
            self.write_optional_uuid(property.get("id", None))
            self.write_float(property["value"])
            size = 4
        elif property_type == "StrProperty":
            self.write_optional_uuid(property.get("id", None))
            size = self.write_fstring(property["value"])
        elif property_type == "NameProperty":
            self.write_optional_uuid(property.get("id", None))
            size = self.write_fstring(property["value"])
        elif property_type == "EnumProperty":
            self.write_fstring(property["value"]["type"])
            self.write_optional_uuid(property.get("id", None))
            size = self.write_fstring(property["value"]["value"])
        elif property_type == "BoolProperty":
            self.write_bool(property["value"])
            self.write_optional_uuid(property.get("id", None))
            size = 0
        elif property_type == "ArrayProperty":
            self.write_fstring(property["array_type"])
            self.write_optional_uuid(property.get("id", None))
            array_writer = self.create_nested()
            array_writer.write_array_property(property["array_type"], property["value"])
            array_buf = array_writer.bytes()
            size = len(array_buf)
            self.write_bytes(array_buf)
        elif property_type == "MapProperty":
            self.write_fstring(property["key_type"])
            self.write_fstring(property["value_type"])
            self.write_optional_uuid(property.get("id", None))
            map_writer = self.create_nested()
            map_writer.write_uint32(0)
            map_writer.write_uint32(len(property["value"]))
            for entry in property["value"]:
                map_writer.write_prop_value(
                    property["key_type"], property["key_struct_type"], entry["key"]
                )
                map_writer.write_prop_value(
                    property["value_type"],
                    property["value_struct_type"],
                    entry["value"],
                )
            map_buf = map_writer.bytes()
            size = len(map_buf)
            self.write_bytes(map_buf)
        else:
            raise Exception(f"Unknown property type: {property_type}")
        return size

    def write_struct(self, property) -> int:
        self.write_fstring(property["struct_type"])
        self.write_uuid(property["struct_id"])
        self.write_optional_uuid(property.get("id", None))
        start = self.data.tell()
        self.write_struct_value(property["struct_type"], property["value"])
        return self.data.tell() - start

    def write_struct_value(self, struct_type, value):
        if struct_type == "Vector":
            self.write_double(value["x"])
            self.write_double(value["y"])
            self.write_double(value["z"])
        elif struct_type == "DateTime":
            self.write_uint64(value)
        elif struct_type == "Guid":
            self.write_uuid(value)
        elif struct_type == "Quat":
            self.write_double(value["x"])
            self.write_double(value["y"])
            self.write_double(value["z"])
            self.write_double(value["w"])
        elif struct_type == "LinearColor":
            self.write_float(value["r"])
            self.write_float(value["g"])
            self.write_float(value["b"])
            self.write_float(value["a"])
        else:
            if os.environ.get("DEBUG", "0") == "1":
                print(f"Assuming struct type: {struct_type}")
            return self.write_properties(value)

    def write_prop_value(self, type_name, struct_type_name, value):
        if type_name == "StructProperty":
            self.write_struct_value(struct_type_name, value)
        elif type_name == "EnumProperty":
            self.write_fstring(value)
        elif type_name == "NameProperty":
            self.write_fstring(value)
        elif type_name == "IntProperty":
            self.write_int32(value)
        elif type_name == "BoolProperty":
            self.write_bool(value)
        else:
            raise Exception(f"Unknown property value type: {type_name}")

    def write_array_property(self, array_type, value):
        count = len(value["values"])
        self.write_uint32(count)
        if array_type == "StructProperty":
            self.write_fstring(value["prop_name"])
            self.write_fstring(value["prop_type"])
            nested_writer = self.create_nested()
            for i in range(count):
                nested_writer.write_struct_value(value["type_name"], value["values"][i])
            data_buf = nested_writer.bytes()
            self.write_uint64(len(data_buf))
            self.write_fstring(value["type_name"])
            self.write_uuid(value["id"])
            self.write_uint8(0)
            self.write_bytes(data_buf)
        else:
            self.write_array_value(array_type, count, value["values"])

    def write_array_value(self, array_type, count, values):
        for i in range(count):
            if array_type == "IntProperty":
                self.write_int32(values[i])
            elif array_type == "Int64Property":
                self.write_int64(values[i])
            elif array_type == "FloatProperty":
                self.write_float(values[i])
            elif array_type == "StrProperty":
                self.write_fstring(values[i])
            elif array_type == "NameProperty":
                self.write_fstring(values[i])
            elif array_type == "EnumProperty":
                self.write_fstring(values[i])
            elif array_type == "BoolProperty":
                self.write_bool(values[i])
            elif array_type == "ByteProperty":
                self.write_byte(values[i])
            else:
                raise Exception(f"Unknown array type: {array_type}")
