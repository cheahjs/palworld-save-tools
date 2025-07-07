from palworld_save_tools.compressor import Compressor
from palworld_save_tools.compressor.oozlib import OozLib
from palworld_save_tools.compressor.zlib import Zlib

compressor = Compressor()
oozlib = OozLib()
z_lib = Zlib()

        
def decompress_sav_to_gvas(data: bytes) -> tuple[bytes, int]:
    format = compressor.check_sav_format(data)
    
    if format == 0:
        return z_lib.decompress(data)
    elif format == 1:
        return oozlib.decompress(data)
    elif format == -1:
        raise Exception("Unknown save format")

def compress_gvas_to_sav(data: bytes, save_type: int, zlib: bool = False) -> bytes:
    format = compressor.check_savtype_format(save_type)

    if zlib:
        # Force using zlib regardless of format
        return z_lib.compress(data, save_type)
    else:
        if format == 0:
            return z_lib.compress(data, save_type)
        elif format == 1:
            return oozlib.compress(data, save_type)
        elif format == -1:
            raise Exception("Unknown save type format")