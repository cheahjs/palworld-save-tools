import struct

from typing import Tuple

class SaveType:
    CNK = 0x30  # Zlib compressed on xbox
    PLM = 0x31  # Oodle compressed
    PLZ = 0x32  # Zlib compressed

    @staticmethod
    def is_valid(save_type: int) -> bool:
        return save_type in (SaveType.PLZ, SaveType.PLM, SaveType.CNK)

class MagicBytes:
    CNK = b"CNK"  # Zlib magic on xbox
    PLZ = b"PlZ"  # Zlib magic
    PLM = b"PlM"  # Oodle magic

    @staticmethod
    def is_valid(magic: bytes) -> bool:
        return magic in (MagicBytes.PLZ, MagicBytes.PLM, MagicBytes.CNK)
    
class Compressor():
    def __init__(self):
        """
        Base class for compression and decompression of Palworld save files.
        """
        pass

    def _parse_sav_header(self, sav_data: bytes) -> Tuple[int, int, bytes, int, int]:
        """
        Parse SAV file header
        Returns: (uncompressed length, compressed length, magic bytes, save type, data offset)
        """
        if len(sav_data) < 24:
            raise ValueError("File too small to parse header")

        first_magic = sav_data[8:11]
        
        # Determine header offset and data offset
        if first_magic == MagicBytes.CNK:
            header_offset = 12
            data_offset = 24
        else:
            header_offset = 0
            data_offset = 12

        # Parse header fields
        uncompressed_len = struct.unpack(
            "<I", sav_data[header_offset : header_offset + 4]
        )[0]
        compressed_len = struct.unpack(
            "<I", sav_data[header_offset + 4 : header_offset + 8]
        )[0]
        magic = sav_data[header_offset + 8 : header_offset + 11]
        save_type = sav_data[header_offset + 11]
        
        if not MagicBytes.is_valid(magic):
            raise ValueError(f"Invalid magic bytes: {magic!r}")
        
        if not SaveType.is_valid(save_type):
            raise ValueError(f"Invalid save type: {save_type}")

        return uncompressed_len, compressed_len, magic, save_type, data_offset

    def _get_magic(self, save_type: int) -> bytes:
        if save_type == SaveType.PLZ:
            return MagicBytes.PLZ
        elif save_type == SaveType.PLM:
            return MagicBytes.PLM
        elif save_type == SaveType.CNK:
            return MagicBytes.CNK
    
    def check_savtype_format(self, save_type: int) -> str:
        if save_type == SaveType.PLM:
            return 1
        elif save_type == SaveType.PLZ:
            return 0
        else:
            return -1
        
    def check_sav_format(self, sav_data: bytes) -> int:
        """
        Check SAV file format.
        Returns: 1=PLM(Oodle), 0=PLZ(Zlib), -1=Unknown.
        (This method is preserved)
        """
        if len(sav_data) < 12:
            return -1
        magic = sav_data[8:11]
        print(f"Checking SAV format, magic bytes: {magic!r}")
        if magic == MagicBytes.PLM:
            return 1
        elif magic == MagicBytes.PLZ or magic == MagicBytes.CNK:
            return 0
        else:
            return -1
        
    def build_sav(self, compressed_data: bytes, uncompressed_len: int, compressed_len: int, magic_bytes: bytes, save_type: int) -> bytes:
        """
        Build SAV file header.
        Returns: bytes with the header.
        """
        print("Building .sav file...")
        result = bytearray()
        result.extend(uncompressed_len.to_bytes(4, "little"))
        result.extend(compressed_len.to_bytes(4, "little"))
        result.extend(magic_bytes)
        result.extend(bytes([save_type]))
        result.extend(compressed_data)

        print("Finished building .sav file.")
        return bytes(result)