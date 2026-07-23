"""Regenerate Reference/TheKey.json with the ASCKey URL-opening macros.

Run from the repo root: python3 -m scripts.generate_thekey
"""

import json
import os

from scripts.thekey_macro import url_open_macro

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(REPO_ROOT, "Reference", "TheKey.json")

KEY_URLS = {
    0: ("A", "https://claude.ai"),
    1: ("SO", "https://stackoverflow.com"),
    2: ("C", "https://chatgpt.com"),
}

TRNS_KEYCODE = {"id": "KC_TRNS", "fields": []}

STOCK_KEY_STATE = {
    "r": 0,
    "rx": 0,
    "ry": 0,
    "w": 1,
    "h": 1,
    "x2": 0,
    "y2": 0,
    "w2": 0,
    "h2": 0,
    "a": 7,
}

STOCK_PINS = {
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

STOCK_QUANTUM = (
    "void matrix_init_user(void) {\n}\n\n"
    "void matrix_scan_user(void) {\n}\n\n"
    "bool process_record_user(uint16_t keycode, keyrecord_t *record) {\n\treturn true;\n}"
)

STOCK_SETTINGS = {
    "diodeDirection": 1,
    "name": "3 KEY",
    "bootloaderSize": 2,
    "rgbNum": 2,
    "backlightLevels": 3,
}


def build_key(key_id):
    legend, url = KEY_URLS[key_id]
    state = {"x": key_id, "y": 0, **STOCK_KEY_STATE}
    macro_keycode = {"id": "M()", "fields": [key_id]}
    keycodes = [macro_keycode] + [dict(TRNS_KEYCODE) for _ in range(15)]
    return {
        "id": key_id,
        "legend": legend,
        "state": state,
        "row": 0,
        "col": key_id,
        "keycodes": keycodes,
    }


def build_config():
    macros = {str(key_id): url_open_macro(url) for key_id, (_legend, url) in KEY_URLS.items()}
    return {
        "version": 1,
        "keyboard": {
            "keys": [build_key(key_id) for key_id in sorted(KEY_URLS)],
            "controller": 1,
            "bounds": {"min": {"x": 0, "y": 0}, "max": {"x": 3, "y": 1}},
            "rows": 1,
            "cols": 3,
            "pins": STOCK_PINS,
            "macros": macros,
            "quantum": STOCK_QUANTUM,
            "settings": STOCK_SETTINGS,
        },
    }


def main():
    config = build_config()
    with open(OUTPUT_PATH, "w") as f:
        json.dump(config, f)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
