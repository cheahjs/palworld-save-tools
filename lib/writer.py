import io
import struct
from uuid import UUID


def uuid_writer(writer, s):
    uuid = UUID(s)
    b = uuid.bytes
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

    def __init__(self):
        self.data = io.BytesIO()

    def __enter__(self):
        self.data.seek(0)
        return self

    def __exit__(self, type, value, traceback):
        self.data.close()

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

    def write_uuid_str(self, u):
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
        nested_writer = FArchiveWriter()
        size: int
        match property["type"]:
            case "StructProperty":
                size = nested_writer.write_struct(property)
            case "IntProperty":
                nested_writer.write_optional_uuid(property.get("id", None))
                nested_writer.write_int32(property["value"])
                size = 4
            case "Int64Property":
                nested_writer.write_optional_uuid(property.get("id", None))
                nested_writer.write_int64(property["value"])
                size = 8
            case "FixedPoint64Property":
                nested_writer.write_optional_uuid(property.get("id", None))
                nested_writer.write_int32(property["value"])
                size = 4
            case "FloatProperty":
                nested_writer.write_optional_uuid(property.get("id", None))
                nested_writer.write_float(property["value"])
                size = 4
            case "StrProperty":
                nested_writer.write_optional_uuid(property.get("id", None))
                size = nested_writer.write_fstring(property["value"])
            case "NameProperty":
                nested_writer.write_optional_uuid(property.get("id", None))
                size = nested_writer.write_fstring(property["value"])
            case "EnumProperty":
                nested_writer.write_fstring(property["value"]["type"])
                nested_writer.write_optional_uuid(property.get("id", None))
                size = nested_writer.write_fstring(property["value"]["value"])
            case "BoolProperty":
                nested_writer.write_bool(property["value"])
                nested_writer.write_optional_uuid(property.get("id", None))
                size = 0
            case "ArrayProperty":
                nested_writer.write_fstring(property["array_type"])
                nested_writer.write_optional_uuid(property.get("id", None))
                array_writer = FArchiveWriter()
                array_writer.write_array_property(property["array_type"], property["value"])
                array_buf = array_writer.bytes()
                size = len(array_buf)
                nested_writer.write_bytes(array_buf)
            case _:
                raise Exception(f'Unknown property type: {property["type"]}')
        buf = nested_writer.bytes()
        # write size
        self.write_uint64(size)
        self.write_bytes(buf)

    def write_struct(self, property) -> int:
        self.write_fstring(property["struct_type"])
        self.write_uuid_str(property["struct_id"])
        self.write_optional_uuid(property.get("id", None))
        start = self.data.tell()
        self.write_struct_value(property["struct_type"], property["value"])
        return self.data.tell() - start

    def write_struct_value(self, struct_type, value):
        if struct_type in [
            "PalIndividualCharacterSaveParameter",
            "PalWorkSuitabilityInfo",
            "FixedPoint64",
            "PalGotStatusPoint",
            "PalContainerId",
            "PalCharacterSlotId",
            "FloatContainer",
        ]:
            return self.write_properties(value)
        elif struct_type == "Vector":
            self.write_double(value["x"])
            self.write_double(value["y"])
            self.write_double(value["z"])
        elif struct_type == "DateTime":
            self.write_uint64(value)
        elif struct_type == "Guid":
            self.write_uuid_str(value)
        else:
            raise Exception(f"Unknown struct type: {struct_type}")

    def write_array_property(self, array_type, value):
        count = len(value["values"])
        self.write_uint32(count)
        if array_type == "StructProperty":
            self.write_fstring(value["prop_name"])
            self.write_fstring(value["prop_type"])
            nested_writer = FArchiveWriter()
            for i in range(count):
                nested_writer.write_struct_value(value["type_name"], value["values"][i])
            data_buf = nested_writer.bytes()
            self.write_uint64(len(data_buf))
            self.write_fstring(value["type_name"])
            self.write_uuid_str(value["id"])
            self.write_uint8(0)
            self.write_bytes(data_buf)
        else:
            self.write_array_value(array_type, count, value["values"])

    def write_array_value(self, array_type, count, values):
        for i in range(count):
            match array_type:
                case "IntProperty":
                    self.write_int32(values[i])
                case "Int64Property":
                    self.write_int64(values[i])
                case "FloatProperty":
                    self.write_float(values[i])
                case "StrProperty":
                    self.write_fstring(values[i])
                case "NameProperty":
                    self.write_fstring(values[i])
                case "EnumProperty":
                    self.write_fstring(values[i])
                case "BoolProperty":
                    self.write_bool(values[i])
                case _:
                    raise Exception(f"Unknown array type: {array_type}")
