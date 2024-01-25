from lib.reader import FArchiveReader
from lib.writer import FArchiveWriter
from typing import Self


class GvasReader():
    reader: FArchiveReader

    def __init__(self, buffer: bytes):
        self.reader = FArchiveReader(buffer)

    def parse(self):
        header = GvasHeader.read(self.reader)

class GvasHeader():
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
    custom_format: Vec<CustomFormatData>

    @staticmethod
    def read(reader: FArchiveReader) -> Self:
        header = GvasHeader()
        # FileTypeTag
        header.magic = reader.read_int32()
        if header.magic != 0x53415647:
            raise Exception("Invalid magic")
        # SaveGameFileVersion
        header.save_game_version = reader.read_int32()
        # PackageFileUEVersion
        header.package_file_version_ue4 = reader.read_int32()
        header.package_file_version_ue5 = reader.read_int32()
        # SavedEngineVersion
        header.engine_version_major = reader.read_uint16()
        header.engine_version_minor = reader.read_uint16()
        header.engine_version_patch = reader.read_uint16()
        header.engine_version_changelist = reader.read_uint32()
        header.engine_version_branch = reader.read_string()
        # CustomVersionFormat
        header.custom_version_format = reader.read_int32()
        # CustomVersions
        

    def write(self, writer: FArchiveWriter):
        pass


class PackageVersion():
