import contextlib
import os
import subprocess
import unittest

from parameterized import parameterized


class TestCliScripts(unittest.TestCase):
    @parameterized.expand(
        [
            ("Level.sav"),
            ("Level-tricky-unicode-player-name.sav"),
            ("LevelMeta.sav"),
            ("LocalData.sav"),
            ("WorldOption.sav"),
        ]
    )
    def test_sav_roundtrip(self, file_name):
        try:
            # Convert sav to JSON
            run = subprocess.run(
                [
                    "python3",
                    "convert.py",
                    f"tests/testdata/{file_name}",
                ]
            )
            self.assertEqual(run.returncode, 0)
            self.assertTrue(os.path.exists(f"tests/testdata/{file_name}.json"))
            # Convert JSON back to sav
            os.rename(
                f"tests/testdata/{file_name}.json",
                f"tests/testdata/1-{file_name}.json",
            )
            run = subprocess.run(
                [
                    "python3",
                    "convert.py",
                    f"tests/testdata/1-{file_name}.json",
                ]
            )
            self.assertEqual(run.returncode, 0)
            self.assertTrue(os.path.exists(f"tests/testdata/1-{file_name}"))
            # Reconvert sav back to JSON
            os.rename(
                f"tests/testdata/1-{file_name}",
                f"tests/testdata/2-{file_name}",
            )
            run = subprocess.run(
                [
                    "python3",
                    "convert.py",
                    f"tests/testdata/2-{file_name}",
                ]
            )
            self.assertEqual(run.returncode, 0)
            self.assertTrue(os.path.exists(f"tests/testdata/2-{file_name}.json"))
            # Reconvert JSON back to sav
            os.rename(
                f"tests/testdata/2-{file_name}.json",
                f"tests/testdata/3-{file_name}.json",
            )
            run = subprocess.run(
                [
                    "python3",
                    "convert.py",
                    f"tests/testdata/3-{file_name}.json",
                ]
            )
            self.assertEqual(run.returncode, 0)
            self.assertTrue(os.path.exists(f"tests/testdata/3-{file_name}"))
            # Compare the final sav to the intermediate save
            with open(f"tests/testdata/2-{file_name}", "rb") as f:
                intermediate_data = f.read()
            with open(f"tests/testdata/3-{file_name}", "rb") as f:
                final_data = f.read()
            self.assertEqual(intermediate_data, final_data)
        finally:
            with contextlib.suppress(FileNotFoundError):
                os.remove(f"tests/testdata/{file_name}.json")
            with contextlib.suppress(FileNotFoundError):
                os.remove(f"tests/testdata/1-{file_name}")
            with contextlib.suppress(FileNotFoundError):
                os.remove(f"tests/testdata/1-{file_name}.json")
            with contextlib.suppress(FileNotFoundError):
                os.remove(f"tests/testdata/2-{file_name}")
            with contextlib.suppress(FileNotFoundError):
                os.remove(f"tests/testdata/2-{file_name}.json")
            with contextlib.suppress(FileNotFoundError):
                os.remove(f"tests/testdata/3-{file_name}")
            with contextlib.suppress(FileNotFoundError):
                os.remove(f"tests/testdata/3-{file_name}.json")
