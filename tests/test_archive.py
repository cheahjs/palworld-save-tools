import unittest
import uuid

from parameterized import parameterized

from palworld_save_tools.archive import UUID, FArchiveReader, FArchiveWriter


class TestArchive(unittest.TestCase):
    @parameterized.expand(
        [
            (1.0, 1.0, 1.0),
            (0.0, 0.0, 0.0),
            (-1.0, -1.0, -1.0),
            (0.0, 0.0, 1.0),
            (0.0, 1.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 0.0, -1.0),
            (0.0, -1.0, 0.0),
            (-107929.0, -1815, 682),
            (107929, 1815, 682),
            (107929, -1815, -682),
            (-107929, 1815, -682),
            (12345678.0, -12345678.0, 12345678.0),
            (-12345678.0, 12345678.0, -12345678.0),
            (12345678.0, 12345678.0, -12345678.0),
            (-12345678.0, -12345678.0, 12345678.0),
        ]
    )
    def test_packed_vector_roundtrip(self, x, y, z):
        writer = FArchiveWriter()
        writer.packed_vector(1, x, y, z)
        reader = FArchiveReader(writer.bytes())
        x_e, y_e, z_e = reader.packed_vector(1)
        self.assertEqual(x, x_e)
        self.assertEqual(y, y_e)
        self.assertEqual(z, z_e)

    def test_uuid_wrapper(self):
        test_uuid = "c1b41f12-90d3-491f-be71-b34e8e0deb5a"
        expected = uuid.UUID(test_uuid)
        b = expected.bytes
        ue_bytes = bytes(
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
        wrapper = UUID(ue_bytes)
        self.assertEqual(str(expected), str(wrapper))
