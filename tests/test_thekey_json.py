import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.thekey_macro import url_open_macro

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEKEY_PATH = os.path.join(REPO_ROOT, "Reference", "TheKey.json")

EXPECTED_URLS = {
    0: ("A", "https://claude.ai"),
    1: ("SO", "https://stackoverflow.com"),
    2: ("C", "https://chatgpt.com"),
}

EXPECTED_PINS = {
    "row": ["D4"],
    "col": ["D2", "D1", "D0"],
    "num": None,
    "caps": None,
    "scroll": None,
    "compose": None,
    "kana": None,
    "led": "B6",
    "rgb": "B1",
}

EXPECTED_SETTINGS = {
    "diodeDirection": 1,
    "name": "3 KEY",
    "bootloaderSize": 2,
    "rgbNum": 2,
    "backlightLevels": 3,
}


class TestTheKeyJson(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(THEKEY_PATH) as f:
            cls.config = json.load(f)
        cls.keyboard = cls.config["keyboard"]

    def test_preserved_top_level_fields(self):
        self.assertEqual(self.keyboard["controller"], 1)
        self.assertEqual(self.keyboard["bounds"], {"min": {"x": 0, "y": 0}, "max": {"x": 3, "y": 1}})
        self.assertEqual(self.keyboard["rows"], 1)
        self.assertEqual(self.keyboard["cols"], 3)
        self.assertEqual(self.keyboard["pins"], EXPECTED_PINS)
        self.assertEqual(self.keyboard["settings"], EXPECTED_SETTINGS)

    def test_three_keys_present(self):
        self.assertEqual(len(self.keyboard["keys"]), 3)

    def test_key_legends_and_macro_assignment(self):
        for key_id, (legend, _url) in EXPECTED_URLS.items():
            key = self.keyboard["keys"][key_id]
            self.assertEqual(key["legend"], legend)
            self.assertEqual(key["keycodes"][0], {"id": "M()", "fields": [key_id]})

    def test_non_layer0_keycodes_remain_transparent(self):
        for key in self.keyboard["keys"]:
            self.assertEqual(key["keycodes"][1:], [{"id": "KC_TRNS", "fields": []}] * 15)

    def test_key_position_fields_untouched(self):
        for key_id in EXPECTED_URLS:
            key = self.keyboard["keys"][key_id]
            self.assertEqual(key["row"], 0)
            self.assertEqual(key["col"], key_id)
            self.assertEqual(key["state"]["x"], key_id)
            self.assertEqual(key["state"]["y"], 0)

    def test_macros_match_expected_urls(self):
        macros = self.keyboard["macros"]
        self.assertEqual(set(macros.keys()), {"0", "1", "2"})
        for key_id, (_legend, url) in EXPECTED_URLS.items():
            self.assertEqual(macros[str(key_id)], url_open_macro(url))


if __name__ == "__main__":
    unittest.main()
