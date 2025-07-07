import os
import sys
import platform

from palworld_save_tools.compressor import (
    Compressor,
    SaveType
)

class OodleCompressor:
    Kraken    = 8
    Mermaid   = 9
    Selkie    = 11
    Hydra     = 12  # hydra doesn't exist in libooz
    Leviathan = 13

class OodleLevel:
    SuperFast = 1
    VeryFast  = 2
    Fast      = 3
    Normal    = 4
    Optimal1  = 5
    Optimal2  = 6
    Optimal3  = 7
    Optimal4  = 8
    Optimal5  = 9

    HyperFast1 = -1
    HyperFast2 = -2
    HyperFast3 = -3
    HyperFast4 = -4


class OozLib(Compressor):
    def __init__(self):
        """
        OozLib is an open source library for compression and decompression using Oodle.
        """
        self.SAFE_SPACE_PADDING = 128
        self.__load_ooz()
        
    def __load_ooz(self):
        """
        Load the Ooz library dynamically based on the platform.
        This is done to ensure compatibility with different operating systems.
        """
        lib_path = ''

        if sys.platform == 'win32':
            lib_path = 'windows'
        elif sys.platform == 'linux':
            arch = platform.machine().lower()
            if 'aarch64' in arch or 'arm' in arch:
                lib_path = 'linux_arm64'
            elif 'x86_64' in arch or 'amd64' in arch:
                lib_path = 'linux_x86_64'
            else:
                raise Exception(f"Unsupported Linux architecture: {arch}")
        elif sys.platform == 'darwin':
            arch = platform.machine().lower()
            if 'arm64' in arch:
                lib_path = 'mac_arm64'
            elif 'x86_64' in arch:
                lib_path = 'mac_x86_64'
            else:
                raise Exception(f"Unsupported Mac architecture: {arch}")
        else:
            raise Exception(f"Unsupported platform: {sys.platform}")
        
        local_ooz_path = os.path.join(os.path.dirname(__file__), '..', 'lib', lib_path)
        if os.path.isdir(local_ooz_path):
            sys.path.insert(0, local_ooz_path)

        try:
            import ooz
        except ImportError:
            raise ImportError(
                f"Failed to import 'ooz' module. Make sure the Ooz library exists in {local_ooz_path} or latest pyooz is installed in your Python environment. Install using 'pip install git+https://github.com/MRHRTZ/pyooz.git'"
            )
        
        self.ooz = ooz
        
    def compress(self, data: bytes, save_type: int) -> bytes:
        print("\nStarting compression process with libooz...")

        uncompressed_len = len(data)
        if uncompressed_len == 0:
            raise ValueError("Input data for compression must not be empty.")

        if save_type != SaveType.PLM:
            raise ValueError(
                f"Unhandled compression type: 0x{save_type:02X}, only 0x31 (PLM) is supported"
            )
            
        print("Compressing data...")
        
        compressed_data = self.ooz.compress(
            OodleCompressor.Kraken, 
            OodleLevel.Normal,
            data,
            uncompressed_len
        )

        if not compressed_data:
            raise RuntimeError(f"Ooz_Compress failed or returned empty result (code: {compressed_data})")

        compressed_len = len(compressed_data)
        magic_bytes = self._get_magic(save_type)
            
        print(f"Compression successful, compressed size: {compressed_len:,} bytes")

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
            save_type
        )
        
        return sav_data

    def decompress(self, data: bytes) -> bytes:
        print("\nStarting decompression process with libooz...")
        
        if not data:
            raise ValueError("SAV data cannot be empty")

        format_result = self.check_sav_format(data)
        if format_result == 0:
            raise ValueError(
                "Detected PLZ format (Zlib), this tool only supports PLM format (Oodle)"
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
        print(f"  Data offset: {data_offset} bytes")
        print("Detected PLM format (Oodle), starting decompression...")
    
        compressed_data = data[data_offset : data_offset + compressed_len]
        decompressed = self.ooz.decompress(compressed_data, uncompressed_len)
        
        if len(decompressed) != uncompressed_len:
            raise ValueError(
                f"Decompressed data length {len(decompressed)} does not match expected uncompressed length {uncompressed_len}"
            )
            
        print(f"Decompression successful, decompressed size: {len(decompressed):,} bytes")
        
        return decompressed, save_type

    
    
        