import zlib

from palworld_save_tools.compressor import (
    Compressor,
    SaveType
)

class Zlib(Compressor):
    def __init__(self):
        """
        OozLib is an open source library for compression and decompression using Oodle.
        """
        self.SAFE_SPACE_PADDING = 128
        
    def compress(self, data: bytes, save_type: int) -> bytes:
        print("\nStarting compression process with zlib...")
        
        uncompressed_len = len(data)
        compressed_data = zlib.compress(data)
        compressed_len = len(compressed_data)
        if save_type != 0x32:
            raise Exception(
                f"Unhandled compression type: 0x{save_type:02X}, only 0x32 (double zlib) is supported"
            )
        compressed_data = zlib.compress(compressed_data)
        magic_bytes = self._get_magic(save_type)
        
        print(f"File information (Compress):")
        print(f"  Magic bytes: {magic_bytes.decode('ascii', errors='ignore')}")
        print(f"  Save type: 0x{save_type:02X}")
        print(f"  Compressed size: {compressed_len:,} bytes")
        print(f"  Uncompressed size: {uncompressed_len:,} bytes")
        print(f"  Hex dump: {compressed_data.hex()[:64]}")
        
        
        sav_data = self.build_sav(        
            compressed_data,
            uncompressed_len,
            compressed_len,
            magic_bytes,
            save_type,
        )

        return sav_data

    def decompress(self, data: bytes) -> bytes:
        print("\nStarting decompression process with zlib...")
        
        format_result = self.check_sav_format(data)
        if format_result == 1:
            raise ValueError(
                "Detected PLM format (Oodle), this tool only supports PLZ format (Zlib)"
            )
        elif format_result == -1:
            raise ValueError("Unknown SAV file format")

        
        uncompressed_len, compressed_len, magic, save_type, data_offset = (
            self._parse_sav_header(data)
        )
        
        print(f"File information (Decompress):")
        print(f"  Magic bytes: {magic.decode('ascii', errors='ignore')}")
        print(f"  Save type: 0x{save_type:02X}")
        print(f"  Compressed size: {compressed_len:,} bytes")
        print(f"  Uncompressed size: {uncompressed_len:,} bytes")
        print("Detected PLZ format (Zlib), starting decompression...")
        
        uncompressed_data = zlib.decompress(data[data_offset:])
        
        if save_type == SaveType.PLZ:
            if compressed_len != len(uncompressed_data):
                raise Exception(f"incorrect compressed length: {compressed_len}")
            
            uncompressed_data = zlib.decompress(uncompressed_data)
            
        if uncompressed_len != len(uncompressed_data):
            raise Exception(f"incorrect uncompressed length: {uncompressed_len}")

        print(f"Decompression successful, decompressed size: {len(uncompressed_data):,} bytes")

        return uncompressed_data, save_type