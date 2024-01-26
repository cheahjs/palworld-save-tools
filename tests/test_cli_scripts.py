import unittest
import subprocess
import os
import contextlib


class TestCliScripts(unittest.TestCase):
    def test_player_roundtrip(self):
        try:
            run = subprocess.run(
                [
                    "python3",
                    "convert.py",
                    "tests/testdata/00000000000000000000000000000001.sav",
                ]
            )
            self.assertEqual(run.returncode, 0)
            self.assertTrue(
                os.path.exists(
                    "tests/testdata/00000000000000000000000000000001.sav.json"
                )
            )
            os.rename(
                "tests/testdata/00000000000000000000000000000001.sav.json",
                "tests/testdata/00000000000000000000000000000001-2.sav.json",
            )
            run = subprocess.run(
                [
                    "python3",
                    "convert.py",
                    "tests/testdata/00000000000000000000000000000001-2.sav.json",
                ]
            )
            self.assertEqual(run.returncode, 0)
            self.assertTrue(
                os.path.exists("tests/testdata/00000000000000000000000000000001-2.sav")
            )
            os.rename(
                "tests/testdata/00000000000000000000000000000001-2.sav",
                "tests/testdata/00000000000000000000000000000001-3.sav",
            )
            run = subprocess.run(
                [
                    "python3",
                    "convert.py",
                    "tests/testdata/00000000000000000000000000000001-3.sav",
                ]
            )
            self.assertEqual(run.returncode, 0)
            self.assertTrue(
                os.path.exists(
                    "tests/testdata/00000000000000000000000000000001-3.sav.json"
                )
            )
        finally:
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/00000000000000000000000000000001.sav.json")
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/00000000000000000000000000000001-2.sav.json")
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/00000000000000000000000000000001-3.sav")
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/00000000000000000000000000000001-3.sav.json")

    def test_level_roundtrip(self):
        try:
            run = subprocess.run(["python3", "convert.py", "tests/testdata/Level.sav"])
            self.assertEqual(run.returncode, 0)
            self.assertTrue(os.path.exists("tests/testdata/Level.sav.json"))
            os.rename(
                "tests/testdata/Level.sav.json", "tests/testdata/Level-2.sav.json"
            )
            run = subprocess.run(
                [
                    "python3",
                    "convert.py",
                    "tests/testdata/Level-2.sav.json",
                ]
            )
            self.assertEqual(run.returncode, 0)
            self.assertTrue(os.path.exists("tests/testdata/Level-2.sav"))
            os.rename("tests/testdata/Level-2.sav", "tests/testdata/Level-3.sav")
            run = subprocess.run(
                [
                    "python3",
                    "convert.py",
                    "tests/testdata/Level-3.sav",
                ]
            )
            self.assertEqual(run.returncode, 0)
            self.assertTrue(os.path.exists("tests/testdata/Level-3.sav.json"))
        finally:
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/Level.sav.json")
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/Level-2.sav.json")
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/Level-3.sav")
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/Level-3.sav.json")

    def test_level_tricky_unicode_player_name_roundtrip(self):
        try:
            run = subprocess.run(
                [
                    "python3",
                    "convert.py",
                    "tests/testdata/Level-tricky-unicode-player-name.sav",
                ]
            )
            self.assertEqual(run.returncode, 0)
            self.assertTrue(
                os.path.exists(
                    "tests/testdata/Level-tricky-unicode-player-name.sav.json"
                )
            )
            os.rename(
                "tests/testdata/Level-tricky-unicode-player-name.sav.json",
                "tests/testdata/Level-tricky-unicode-player-name-2.sav.json",
            )
            run = subprocess.run(
                [
                    "python3",
                    "convert.py",
                    "tests/testdata/Level-tricky-unicode-player-name-2.sav.json",
                ]
            )
            self.assertEqual(run.returncode, 0)
            self.assertTrue(
                os.path.exists("tests/testdata/Level-tricky-unicode-player-name-2.sav")
            )
            os.rename(
                "tests/testdata/Level-tricky-unicode-player-name-2.sav",
                "tests/testdata/Level-tricky-unicode-player-name-3.sav",
            )
            run = subprocess.run(
                [
                    "python3",
                    "convert.py",
                    "tests/testdata/Level-tricky-unicode-player-name-3.sav",
                ]
            )
            self.assertEqual(run.returncode, 0)
            self.assertTrue(
                os.path.exists(
                    "tests/testdata/Level-tricky-unicode-player-name-3.sav.json"
                )
            )
        finally:
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/Level-tricky-unicode-player-name.sav.json")
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/Level-tricky-unicode-player-name-2.sav.json")
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/Level-tricky-unicode-player-name-3.sav")
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/Level-tricky-unicode-player-name-3.sav.json")

    def test_levelmeta_roundtrip(self):
        try:
            run = subprocess.run(
                [
                    "python3",
                    "convert.py",
                    "tests/testdata/LevelMeta.sav",
                ]
            )
            self.assertEqual(run.returncode, 0)
            self.assertTrue(os.path.exists("tests/testdata/LevelMeta.sav.json"))
            os.rename(
                "tests/testdata/LevelMeta.sav.json",
                "tests/testdata/LevelMeta-2.sav.json",
            )
            run = subprocess.run(
                [
                    "python3",
                    "convert.py",
                    "tests/testdata/LevelMeta-2.sav.json",
                ]
            )
            self.assertEqual(run.returncode, 0)
            self.assertTrue(os.path.exists("tests/testdata/LevelMeta-2.sav"))
            os.rename(
                "tests/testdata/LevelMeta-2.sav", "tests/testdata/LevelMeta-3.sav"
            )
            run = subprocess.run(
                [
                    "python3",
                    "convert.py",
                    "tests/testdata/LevelMeta-3.sav",
                ]
            )
            self.assertEqual(run.returncode, 0)
            self.assertTrue(os.path.exists("tests/testdata/LevelMeta-3.sav.json"))
        finally:
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/LevelMeta.sav.json")
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/LevelMeta-2.sav.json")
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/LevelMeta-3.sav")
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/LevelMeta-3.sav.json")

    def test_localdata_roundtrip(self):
        try:
            run = subprocess.run(
                [
                    "python3",
                    "convert.py",
                    "tests/testdata/LocalData.sav",
                ]
            )
            self.assertEqual(run.returncode, 0)
            self.assertTrue(os.path.exists("tests/testdata/LocalData.sav.json"))
            os.rename(
                "tests/testdata/LocalData.sav.json",
                "tests/testdata/LocalData-2.sav.json",
            )
            run = subprocess.run(
                [
                    "python3",
                    "convert.py",
                    "tests/testdata/LocalData-2.sav.json",
                ]
            )
            self.assertEqual(run.returncode, 0)
            self.assertTrue(os.path.exists("tests/testdata/LocalData-2.sav"))
            os.rename(
                "tests/testdata/LocalData-2.sav", "tests/testdata/LocalData-3.sav"
            )
            run = subprocess.run(
                [
                    "python3",
                    "convert.py",
                    "tests/testdata/LocalData-3.sav",
                ]
            )
            self.assertEqual(run.returncode, 0)
            self.assertTrue(os.path.exists("tests/testdata/LocalData-3.sav.json"))
        finally:
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/LocalData.sav.json")
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/LocalData-2.sav.json")
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/LocalData-3.sav")
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/LocalData-3.sav.json")

    def test_worldoption_roundtrip(self):
        try:
            run = subprocess.run(
                [
                    "python3",
                    "convert.py",
                    "tests/testdata/WorldOption.sav",
                ]
            )
            self.assertEqual(run.returncode, 0)
            self.assertTrue(os.path.exists("tests/testdata/WorldOption.sav.json"))
            os.rename(
                "tests/testdata/WorldOption.sav.json",
                "tests/testdata/WorldOption-2.sav.json",
            )
            run = subprocess.run(
                [
                    "python3",
                    "convert.py",
                    "tests/testdata/WorldOption-2.sav.json",
                ]
            )
            self.assertEqual(run.returncode, 0)
            self.assertTrue(os.path.exists("tests/testdata/WorldOption-2.sav"))
            os.rename(
                "tests/testdata/WorldOption-2.sav", "tests/testdata/WorldOption-3.sav"
            )
            run = subprocess.run(
                [
                    "python3",
                    "convert.py",
                    "tests/testdata/WorldOption-3.sav",
                ]
            )
            self.assertEqual(run.returncode, 0)
            self.assertTrue(os.path.exists("tests/testdata/WorldOption-3.sav.json"))
        finally:
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/WorldOption.sav.json")
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/WorldOption-2.sav.json")
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/WorldOption-3.sav")
            with contextlib.suppress(FileNotFoundError):
                os.remove("tests/testdata/WorldOption-3.sav.json")
