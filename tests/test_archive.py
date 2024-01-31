import unittest

from parameterized import parameterized

from lib.archive import FArchiveReader, FArchiveWriter


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
