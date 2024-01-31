import base64
import json
import unittest
from uuid import UUID

from parameterized import parameterized

from lib.archive import FArchiveReader, FArchiveWriter
from lib.gvas import GvasFile, GvasHeader
from lib.noindent import CustomEncoder
from lib.palsav import decompress_sav_to_gvas
from lib.paltypes import PALWORLD_CUSTOM_PROPERTIES, PALWORLD_TYPE_HINTS


class TestGvas(unittest.TestCase):
    def test_header(self):
        test_data = base64.b64decode(
            "R1ZBUwMAAAAKAgAA8AMAAAUAAQABAAAAAAASAAAAKytVRTUrUmVsZWFzZS01LjEAAwAAAEUAAACn+9JA5UxIS3VaOLCeSU6IBwAAAPp69fyDQnZQWOapuTItoP9MAAAAe0clCQFAPXZz1pGdEbR1CwEAAAAbIYhCxhZIRbJndhoAKnpQAQAAAMzOuRoTaQAAdUgAAPtRPSBkAAAAIZLvTDrUDkeMPWB+JleZFgEAAAB+fHHi00T1UkBTDJVeAxWzBwAAAO0KMRFhTVUuo5pnrywIocURAAAA+wyCp1lDpyAULFSMUM8jlhUAAAB4u9/25KBQu024GEAjr8tgAgAAAPN6uySDT0ZWwi0vH/+WrUkFAAAAKSOldrVFIwlB2K6Y2GovzwUAAAAHabxfrkDIVYTxZ44/8f9eAQAAAE5854KlQyMzxRNrtPMNMZcAAAAAbPb8D5lIkBH4nGCxXkdGSgEAAAAi1VScvk8mqEYHIZTQgrRhLAAAAOQy2LANT4kft37PrKJK/TYKAAAAKEPG4VNNLKKGjmyjjL0XZAAAAAA8wV43+0jkBvCEALV+cSomBAAAAO1osOTpQpT0C9oxokG7Ri4oAAAAP3T8z4BEsEPfFJGTcyAdFyUAAAC1SSuw6UQgu7cyBKNgA+RSAwAAAFwQ5KS1SaFZxEDFp+7fflQAAAAAyTHIOdxH5loXnESafI4cPgAAAAAzG/B4mE/q6+qEtLmiWrnMFAAAAA84MWbgQ00tJ88JgFqpVmkAAAAAn4v4EvxKdYgM2XymKb06OC0AAABM51p7EExw0phXWKlaKiELDQAAABhpKdfdS9YdqGTinYQ4wTwDAAAAeFKhwv5K57//kBdsVfcdUwEAAADUo6xuwUzsQO2LhrfFj0IJAwAAAN115SknRqPgdtIQnercLCMRAAAAXaZDr0dJ03+OPnOYBbvB2Q8AAADsbCZrj0vHHtnkC6MH/EIJAQAAAGE99w3qRz+i6Yknt5pJQQwBAAAAhhgdYIRPZKze0xaq1sfqDVAAAAC3Bkxb+EpjJHC/W4Dd0PXNCgAAAGhjCOdYTCNrcBs5hJFeJhYEAAAA1rz/nVgBT0mCEiHiiKiSPAoAAACs0K7yb0H+mn+qZIb81ib6AQAAAAsfTxelRca06C4/sX2R+9AKAAAAg0r5NWxAWOL1CRijfCQQlikAAABuwY+24kIbi1whU7T+RIgFAQAAAAaF4bLCz3NCu/ROpQe6i3UBAAAANon1ZLpCG/2Jcpa6TvrQ1QEAAACB1X1pq0FP5uxRSqootre+WAAAAEJem9hGTb0kqKwShHkXZN8pAAAAUl3aWUhJMhJ4WXi4i+m4cAgAAAAyWgcmCEcPczKM6YgFnVnxAAAAACfYDm+VSAmmjZmRnKQOGJACAAAA44vVMIJC6pVZseOmarDr2AEAAADnnn9xOkmw6TKRs4gHgTgbEAAAABlNDENwSVRxaZtph+WwkN8PAAAAvTL+qhRMlVMlXmq23dEyEAEAAACO4a8jWE7hTFLCYY23vlO5CwAAAOq3YqQ6Tpn0H+zBmbLhJIIEAAAAvf21LhBNrAGP8zaB2qWTMwUAAABPNZ1QL0nm9rKFSaccYzwHAAAAABwb47bsEZ/ShZ9+heJwmW8BAAAAQOtWStwR9RB+NNOS52rJsgIAAAAASorXl0ZY6LUZqLq0Rn1IEgAAAIb4eVUfTDqTewi6gy+5YWMCAAAAUr4vYQtAU9qRTw2RfIWxnwEAAAA2eiOkyUHqyvgYoo/zG2hYBQAAAHU/ToBJS4hwBozWpNy2fjwFAAAA9EjQHmhMLi+kU9CJLRCP8QEAAADyCmj7o0vvWbUZqLo9RMhzAgAAAA63UJkXThq0DfrMu9Z/gVcBAAAAllGWq/wI2EWNIte3nlateAEAAAAdAAAAL1NjcmlwdC9QYWwuUGFsV29ybGRTYXZlR2FtZQA="
        )
        reader = FArchiveReader(test_data)
        header = GvasHeader.read(reader)
        expected_header = {
            "magic": 1396790855,
            "save_game_version": 3,
            "package_file_version_ue4": 522,
            "package_file_version_ue5": 1008,
            "engine_version_major": 5,
            "engine_version_minor": 1,
            "engine_version_patch": 1,
            "engine_version_changelist": 0,
            "engine_version_branch": "++UE5+Release-5.1",
            "custom_version_format": 3,
            "custom_versions": [
                (UUID("40d2fba7-4b48-4ce5-b038-5a75884e499e"), 7),
                (UUID("fcf57afa-5076-4283-b9a9-e658ffa02d32"), 76),
                (UUID("0925477b-763d-4001-9d91-d6730b75b411"), 1),
                (UUID("4288211b-4548-16c6-1a76-67b2507a2a00"), 1),
                (UUID("1ab9cecc-0000-6913-0000-4875203d51fb"), 100),
                (UUID("4cef9221-470e-d43a-7e60-3d8c16995726"), 1),
                (UUID("e2717c7e-52f5-44d3-950c-5340b315035e"), 7),
                (UUID("11310aed-2e55-4d61-af67-9aa3c5a1082c"), 17),
                (UUID("a7820cfb-20a7-4359-8c54-2c149623cf50"), 21),
                (UUID("f6dfbb78-bb50-a0e4-4018-b84d60cbaf23"), 2),
                (UUID("24bb7af3-5646-4f83-1f2f-2dc249ad96ff"), 5),
                (UUID("76a52329-0923-45b5-98ae-d841cf2f6ad8"), 5),
                (UUID("5fbc6907-55c8-40ae-8e67-f1845efff13f"), 1),
                (UUID("82e77c4e-3323-43a5-b46b-13c597310df3"), 0),
                (UUID("0ffcf66c-1190-4899-b160-9cf84a46475e"), 1),
                (UUID("9c54d522-a826-4fbe-9421-074661b482d0"), 44),
                (UUID("b0d832e4-1f89-4f0d-accf-7eb736fd4aa2"), 10),
                (UUID("e1c64328-a22c-4d53-a36c-8e866417bd8c"), 0),
                (UUID("375ec13c-06e4-48fb-b500-84f0262a717e"), 4),
                (UUID("e4b068ed-f494-42e9-a231-da0b2e46bb41"), 40),
                (UUID("cffc743f-43b0-4480-9391-14df171d2073"), 37),
                (UUID("b02b49b5-bb20-44e9-a304-32b752e40360"), 3),
                (UUID("a4e4105c-59a1-49b5-a7c5-40c4547edfee"), 0),
                (UUID("39c831c9-5ae6-47dc-9a44-9c173e1c8e7c"), 0),
                (UUID("78f01b33-ebea-4f98-b9b4-84eaccb95aa2"), 20),
                (UUID("6631380f-2d4d-43e0-8009-cf276956a95a"), 0),
                (UUID("12f88b9f-8875-4afc-a67c-d90c383abd29"), 45),
                (UUID("7b5ae74c-d270-4c10-a958-57980b212a5a"), 13),
                (UUID("d7296918-1dd6-4bdd-9de2-64a83cc13884"), 3),
                (UUID("c2a15278-bfe7-4afe-6c17-90ff531df755"), 1),
                (UUID("6eaca3d4-40ec-4cc1-b786-8bed09428fc5"), 3),
                (UUID("29e575dd-e0a3-4627-9d10-d276232cdcea"), 17),
                (UUID("af43a65d-7fd3-4947-9873-3e8ed9c1bb05"), 15),
                (UUID("6b266cec-1ec7-4b8f-a30b-e4d90942fc07"), 1),
                (UUID("0df73d61-a23f-47ea-b727-89e90c41499a"), 1),
                (UUID("601d1886-ac64-4f84-aa16-d3de0deac7d6"), 80),
                (UUID("5b4c06b7-2463-4af8-805b-bf70cdf5d0dd"), 10),
                (UUID("e7086368-6b23-4c58-8439-1b7016265e91"), 4),
                (UUID("9dffbcd6-494f-0158-e221-12823c92a888"), 10),
                (UUID("f2aed0ac-9afe-416f-8664-aa7ffa26d6fc"), 1),
                (UUID("174f1f0b-b4c6-45a5-b13f-2ee8d0fb917d"), 10),
                (UUID("35f94a83-e258-406c-a318-09f59610247c"), 41),
                (UUID("b68fc16e-8b1b-42e2-b453-215c058844fe"), 1),
                (UUID("b2e18506-4273-cfc2-a54e-f4bb758bba07"), 1),
                (UUID("64f58936-fd1b-42ba-ba96-7289d5d0fa4e"), 1),
                (UUID("697dd581-e64f-41ab-aa4a-51ecbeb7b628"), 88),
                (UUID("d89b5e42-24bd-4d46-8412-aca8df641779"), 41),
                (UUID("59da5d52-1232-4948-b878-597870b8e98b"), 8),
                (UUID("26075a32-730f-4708-88e9-8c32f1599d05"), 0),
                (UUID("6f0ed827-a609-4895-9c91-998d90180ea4"), 2),
                (UUID("30d58be3-95ea-4282-a6e3-b159d8ebb06a"), 1),
                (UUID("717f9ee7-e9b0-493a-88b3-91321b388107"), 16),
                (UUID("430c4d19-7154-4970-8769-9b69df90b0e5"), 15),
                (UUID("aafe32bd-5395-4c14-b66a-5e251032d1dd"), 1),
                (UUID("23afe18e-4ce1-4e58-8d61-c252b953beb7"), 11),
                (UUID("a462b7ea-f499-4e3a-99c1-ec1f8224e1b2"), 4),
                (UUID("2eb5fdbd-01ac-4d10-8136-f38f3393a5da"), 5),
                (UUID("509d354f-f6e6-492f-a749-85b2073c631c"), 0),
                (UUID("b6e31b1c-d29f-11ec-857e-9f856f9970e2"), 1),
                (UUID("4a56eb40-10f5-11dc-92d3-347eb2c96ae7"), 2),
                (UUID("d78a4a00-e858-4697-baa8-19b5487d46b4"), 18),
                (UUID("5579f886-933a-4c1f-83ba-087b6361b92f"), 2),
                (UUID("612fbe52-da53-400b-910d-4f919fb1857c"), 1),
                (UUID("a4237a36-caea-41c9-8fa2-18f858681bf3"), 5),
                (UUID("804e3f75-7088-4b49-a4d6-8c063c7eb6dc"), 5),
                (UUID("1ed048f4-2f2e-4c68-89d0-53a4f18f102d"), 1),
                (UUID("fb680af2-59ef-4ba3-baa8-19b573c8443d"), 2),
                (UUID("9950b70e-b41a-4e17-bbcc-fa0d57817fd6"), 1),
                (UUID("ab965196-45d8-08fc-b7d7-228d78ad569e"), 1),
            ],
            "save_game_class_name": "/Script/Pal.PalWorldSaveGame",
        }
        self.assertEqual(
            header.dump(), expected_header, "header does not match expected"
        )
        writer = FArchiveWriter()
        header.write(writer)
        self.assertEqual(
            writer.bytes(), test_data, "header does not match expected after encoding"
        )

    @parameterized.expand(
        [
            ("Level.sav", "/Script/Pal.PalWorldSaveGame"),
            ("Level-tricky-unicode-player-name.sav", "/Script/Pal.PalWorldSaveGame"),
            ("LevelMeta.sav", "/Script/Pal.PalWorldBaseInfoSaveGame"),
            ("LocalData.sav", "/Script/Pal.PalLocalWorldSaveGame"),
            ("WorldOption.sav", "/Script/Pal.PalWorldOptionSaveGame"),
            (
                "00000000000000000000000000000001.sav",
                "/Script/Pal.PalWorldPlayerSaveGame",
            ),
            ("unicode-saves/Level.sav", "/Script/Pal.PalWorldSaveGame"),
            ("unicode-saves/LevelMeta.sav", "/Script/Pal.PalWorldBaseInfoSaveGame"),
            ("unicode-saves/LocalData.sav", "/Script/Pal.PalLocalWorldSaveGame"),
            ("unicode-saves/WorldOption.sav", "/Script/Pal.PalWorldOptionSaveGame"),
            (
                "unicode-saves/00000000000000000000000000000001.sav",
                "/Script/Pal.PalWorldPlayerSaveGame",
            ),
            ("larger-saves/Level.sav", "/Script/Pal.PalWorldSaveGame"),
            ("larger-saves/LocalData.sav", "/Script/Pal.PalLocalWorldSaveGame"),
            (
                "larger-saves/00000000000000000000000000000001.sav",
                "/Script/Pal.PalWorldPlayerSaveGame",
            ),
        ]
    )
    def test_sav_roundtrip(self, file_name, expected_save_game_class_name):
        with open("tests/testdata/" + file_name, "rb") as f:
            data = f.read()
        gvas_data, _ = decompress_sav_to_gvas(data)
        gvas_file = GvasFile.read(
            gvas_data, PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES
        )
        self.assertEqual(
            gvas_file.header.dump()["save_game_class_name"],
            expected_save_game_class_name,
            "sav save_game_class_name does not match expected",
        )
        dump = gvas_file.dump()
        js = json.dumps(dump, cls=CustomEncoder)
        new_js = json.loads(js)
        new_gvas_file = GvasFile.load(new_js)
        new_gvas_data = new_gvas_file.write(PALWORLD_CUSTOM_PROPERTIES)
        self.assertEqual(
            gvas_data,
            new_gvas_data,
            "sav does not match expected after roundtrip",
        )
