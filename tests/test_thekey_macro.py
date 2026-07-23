import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.thekey_macro import char_to_actions, url_open_macro


class TestCharToActions(unittest.TestCase):
    def test_lowercase_letter(self):
        self.assertEqual(char_to_actions("h"), [(4, "KC_H")])

    def test_dot(self):
        self.assertEqual(char_to_actions("."), [(4, "KC_DOT")])

    def test_slash(self):
        self.assertEqual(char_to_actions("/"), [(4, "KC_SLSH")])

    def test_colon(self):
        self.assertEqual(
            char_to_actions(":"),
            [(2, "KC_LSFT"), (4, "KC_SCLN"), (3, "KC_LSFT")],
        )

    def test_unsupported_character_raises(self):
        with self.assertRaises(ValueError):
            char_to_actions("_")


class TestUrlOpenMacro(unittest.TestCase):
    def test_full_macro_for_claude_url(self):
        result = url_open_macro("https://claude.ai")
        expected = [
            {"action": 2, "argument": "KC_LCTL"},
            {"action": 2, "argument": "KC_T"},
            {"action": 3, "argument": "KC_LCTL"},
            {"action": 3, "argument": "KC_T"},
            {"action": 4, "argument": "KC_H"},
            {"action": 4, "argument": "KC_T"},
            {"action": 4, "argument": "KC_T"},
            {"action": 4, "argument": "KC_P"},
            {"action": 4, "argument": "KC_S"},
            {"action": 2, "argument": "KC_LSFT"},
            {"action": 4, "argument": "KC_SCLN"},
            {"action": 3, "argument": "KC_LSFT"},
            {"action": 4, "argument": "KC_SLSH"},
            {"action": 4, "argument": "KC_SLSH"},
            {"action": 4, "argument": "KC_C"},
            {"action": 4, "argument": "KC_L"},
            {"action": 4, "argument": "KC_A"},
            {"action": 4, "argument": "KC_U"},
            {"action": 4, "argument": "KC_D"},
            {"action": 4, "argument": "KC_E"},
            {"action": 4, "argument": "KC_DOT"},
            {"action": 4, "argument": "KC_A"},
            {"action": 4, "argument": "KC_I"},
            {"action": 2, "argument": "KC_ENT"},
            {"action": 3, "argument": "KC_ENT"},
        ]
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
