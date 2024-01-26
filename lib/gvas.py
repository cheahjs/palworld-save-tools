import base64
from lib.archive import FArchiveReader, FArchiveWriter
from typing import Any, Callable


def custom_version_reader(reader: FArchiveReader):
    return (reader.read_uuid(), reader.read_int32())


def custom_version_writer(writer: FArchiveWriter, value: tuple[str, int]):
    writer.write_uuid(value[0])
    writer.write_int32(value[1])


class GvasHeader:
    magic: int
    save_game_version: int
    package_file_version_ue4: int
    package_file_version_ue5: int
    engine_version_major: int
    engine_version_minor: int
    engine_version_patch: int
    engine_version_changelist: int
    engine_version_branch: str
    custom_version_format: int
    custom_versions: list[tuple[str, int]]
    save_game_class_name: str

    @staticmethod
    def read(reader: FArchiveReader) -> "GvasHeader":
        header = GvasHeader()
        # FileTypeTag
        header.magic = reader.read_int32()
        if header.magic != 0x53415647:
            raise Exception("invalid magic")
        # SaveGameFileVersion
        header.save_game_version = reader.read_int32()
        if header.save_game_version != 3:
            raise Exception(
                f"expected save game version 3, got {header.save_game_version}"
            )
        # PackageFileUEVersion
        header.package_file_version_ue4 = reader.read_int32()
        header.package_file_version_ue5 = reader.read_int32()
        # SavedEngineVersion
        header.engine_version_major = reader.read_uint16()
        header.engine_version_minor = reader.read_uint16()
        header.engine_version_patch = reader.read_uint16()
        header.engine_version_changelist = reader.read_uint32()
        header.engine_version_branch = reader.read_fstring()
        # CustomVersionFormat
        header.custom_version_format = reader.read_int32()
        if header.custom_version_format != 3:
            raise Exception(
                f"expected custom version format 3, got {header.custom_version_format}"
            )
        # CustomVersions
        header.custom_versions = reader.read_tarray(custom_version_reader)
        header.save_game_class_name = reader.read_fstring()
        return header

    @staticmethod
    def load(dict: dict[str, Any]) -> "GvasHeader":
        header = GvasHeader()
        header.magic = dict["magic"]
        header.save_game_version = dict["save_game_version"]
        header.package_file_version_ue4 = dict["package_file_version_ue4"]
        header.package_file_version_ue5 = dict["package_file_version_ue5"]
        header.engine_version_major = dict["engine_version_major"]
        header.engine_version_minor = dict["engine_version_minor"]
        header.engine_version_patch = dict["engine_version_patch"]
        header.engine_version_changelist = dict["engine_version_changelist"]
        header.engine_version_branch = dict["engine_version_branch"]
        header.custom_version_format = dict["custom_version_format"]
        header.custom_versions = dict["custom_versions"]
        header.save_game_class_name = dict["save_game_class_name"]
        return header

    def dump(self) -> dict[str, Any]:
        return {
            "magic": self.magic,
            "save_game_version": self.save_game_version,
            "package_file_version_ue4": self.package_file_version_ue4,
            "package_file_version_ue5": self.package_file_version_ue5,
            "engine_version_major": self.engine_version_major,
            "engine_version_minor": self.engine_version_minor,
            "engine_version_patch": self.engine_version_patch,
            "engine_version_changelist": self.engine_version_changelist,
            "engine_version_branch": self.engine_version_branch,
            "custom_version_format": self.custom_version_format,
            "custom_versions": self.custom_versions,
            "save_game_class_name": self.save_game_class_name,
        }

    def write(self, writer: FArchiveWriter):
        writer.write_int32(self.magic)
        writer.write_int32(self.save_game_version)
        writer.write_int32(self.package_file_version_ue4)
        writer.write_int32(self.package_file_version_ue5)
        writer.write_uint16(self.engine_version_major)
        writer.write_uint16(self.engine_version_minor)
        writer.write_uint16(self.engine_version_patch)
        writer.write_uint32(self.engine_version_changelist)
        writer.write_fstring(self.engine_version_branch)
        writer.write_int32(self.custom_version_format)
        writer.write_tarray(custom_version_writer, self.custom_versions)
        writer.write_fstring(self.save_game_class_name)


class GvasFile:
    header: GvasHeader
    properties: dict[str, Any]
    trailer: bytes

    @staticmethod
    def read(
        data: bytes,
        type_hints: dict[str, str] = {},
        custom_properties: dict[str, tuple[Callable, Callable]] = {},
    ) -> "GvasFile":
        gvas_file = GvasFile()
        reader = FArchiveReader(data, type_hints, custom_properties)
        gvas_file.header = GvasHeader.read(reader)
        gvas_file.properties = reader.read_properties_until_end()
        gvas_file.trailer = reader.read_to_end()
        if gvas_file.trailer != b"\x00\x00\x00\x00":
            print(
                f"{len(gvas_file.trailer)} bytes of trailer data, file may not have fully parsed"
            )
        return gvas_file

    @staticmethod
    def load(dict: dict[str, Any]) -> "GvasFile":
        gvas_file = GvasFile()
        gvas_file.header = GvasHeader.load(dict["header"])
        gvas_file.properties = dict["properties"]
        gvas_file.trailer = base64.b64decode(dict["trailer"])
        return gvas_file

    def dump(self) -> dict[str, Any]:
        return {
            "header": self.header.dump(),
            "properties": self.properties,
            "trailer": base64.b64encode(self.trailer).decode("utf-8"),
        }

    def write(
        self, custom_properties: dict[str, tuple[Callable, Callable]] = {}
    ) -> bytes:
        writer = FArchiveWriter(custom_properties)
        self.header.write(writer)
        writer.write_properties(self.properties)
        writer.write_bytes(self.trailer)
        return writer.bytes()
