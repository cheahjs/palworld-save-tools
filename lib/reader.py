import io
import struct
import uuid


def instance_id_reader(reader):
    return {
        "guid": reader.read_uuid(),
        "instance_id": reader.read_uuid(),
    }


def uuid_reader(reader):
    b = reader.read_bytes(16)
    return uuid.UUID(bytes=bytes([
        b[0x3], b[0x2], b[0x1], b[0x0],
        b[0x7], b[0x6], b[0x5], b[0x4],
        b[0xb], b[0xa], b[0x9], b[0x8],
        b[0xf], b[0xe], b[0xd], b[0xc],
    ]))


class FArchiveReader:
    data: io.BytesIO
    size: int

    def __init__(self, data):
        self.data = io.BytesIO(data)
        self.size = len(self.data.read())
        self.data.seek(0)

    def __enter__(self):
        self.size = len(self.data.read())
        self.data.seek(0)
        return self

    def __exit__(self, type, value, traceback):
        self.data.close()

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

        if LoadUCS2Char:
            data = []
            for i in range(size):
                if i == size - 1:
                    self.read_uint16()
                else:
                    data.append(self.read_uint16())
            string = ''.join([chr(v) for v in data])
            return string
        else:
            byte = self.data.read(size)[:-1]
            return byte.decode("utf-8")

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

    def read_properties_until_end(self):
        properties = {}
        while True:
            pos = self.data.tell()
            self.data.seek(pos)
            name = self.read_fstring()
            if name == "None":
                break
            type_name = self.read_fstring()
            size = self.read_uint64()
            properties[name] = self.read_property(type_name)
        return properties

    def read_property(self, type_name):
        value = {}
        match type_name:
            case "StructProperty":
                value = self.read_struct()
            case "IntProperty":
                value = {
                    'id': self.read_optional_uuid(),
                    'value': self.read_int32(),
                }
            case "Int64Property":
                value = {
                    'id': self.read_optional_uuid(),
                    'value': self.read_int64(),
                }
            case "FixedPoint64Property":
                value = {
                    'id': self.read_optional_uuid(),
                    'value': self.read_int32(),
                }
            case "FloatProperty":
                value = {
                    'id': self.read_optional_uuid(),
                    'value': self.read_float(),
                }
            case "StrProperty":
                value = {
                    'id': self.read_optional_uuid(),
                    'value': self.read_fstring(),
                }
            case "NameProperty":
                value = {
                    'id': self.read_optional_uuid(),
                    'value': self.read_fstring(),
                }
            case "EnumProperty":
                enum_type = self.read_fstring()
                _id = self.read_optional_uuid()
                enum_value = self.read_fstring()
                value = {
                    'id': _id,
                    'value': {
                        'type': enum_type,
                        'value': enum_value,
                    }
                }
            case "BoolProperty":
                value = {
                    'value': self.read_bool(),
                    'id': self.read_optional_uuid(),
                }
            case "ArrayProperty":
                array_type = self.read_fstring()
                value = {
                    'array_type': array_type,
                    'id': self.read_optional_uuid(),
                    'value': self.read_array_property(array_type),
                }
            case _:
                raise Exception(f'Unknown type: {type_name}')
        value['type'] = type_name
        return value

    def read_struct(self):
        struct_type = self.read_fstring()
        struct_id = self.read_uuid()
        _id = self.read_optional_uuid()
        value = self.read_struct_value(struct_type)
        return {
            "struct_type": struct_type,
            "struct_id": struct_id,
            "id": _id,
            "value": value
        }

    def read_struct_value(self, struct_type):
        if struct_type in [
            'PalIndividualCharacterSaveParameter',
            'PalWorkSuitabilityInfo',
            'FixedPoint64',
            'PalGotStatusPoint',
            'PalContainerId',
            'PalCharacterSlotId',
            'FloatContainer'
        ]:
            return self.read_properties_until_end()
        elif struct_type == 'Vector':
            return {
                'x': self.read_double(),
                'y': self.read_double(),
                'z': self.read_double(),
            }
        elif struct_type == 'DateTime':
            return self.read_uint64()
        elif struct_type == 'Guid':
            return self.read_uuid()
        else:
            raise Exception(f'Unknown struct type: {struct_type}')

    def read_array_property(self, array_type):
        count = self.read_uint32()
        value = {}
        if array_type == 'StructProperty':
            prop_name = self.read_fstring()
            prop_type = self.read_fstring()
            size = self.read_uint64()
            type_name = self.read_fstring()
            _id = self.read_uuid()
            self.skip(1)
            prop_values = []
            for _ in range(count):
                prop_values.append(self.read_struct_value(type_name))
            value = {
                'prop_name': prop_name,
                'prop_type': prop_type,
                'values': prop_values,
                'type_name': type_name,
                'id': _id,
            }
        else:
            value = {
                'values': self.read_array_value(array_type, count),
            }
        return value

    def read_array_value(self, array_type, count):
        values = []
        for _ in range(count):
            match array_type:
                case "EnumProperty":
                    values.append(self.read_fstring())
                case "NameProperty":
                    values.append(self.read_fstring())
                case "Guid":
                    values.append(self.read_uuid())
                case _:
                    raise Exception(f'Unknown array type: {array_type}')
        return values
