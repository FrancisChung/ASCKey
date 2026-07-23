# ASCKey Macro Firmware Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Populate `../Config/TheKey.json` so the 3-key ASCKey macropad opens `https://claude.ai`, `https://stackoverflow.com`, and `https://chatgpt.com` in new browser tabs when its A / StackOverflow / C keys are pressed.

**Architecture:** A pure Python function converts a URL string into a kbfirmware.com macro action list (Ctrl+T, type each character, Enter). A generator script uses that function to build the full `TheKey.json` structure, preserving all non-key fields from the stock file untouched. A separate test file validates the final `../Config/TheKey.json` against the spec. All three files are plain-stdlib Python (`unittest`, `json`) — no new dependencies, matching this repo's current zero-tooling state.

**Tech Stack:** Python 3 standard library only (`unittest`, `json`).

## Global Constraints

- Modifier key is `KC_LCTL` (Ctrl), not `KC_LGUI` (Cmd) — target environments are Linux Mint/Cinnamon and Windows, both use Ctrl+T for new tab.
- URLs are typed in full (`https://...`), not bare domains.
- `../Config/TheKey.json`'s non-key fields (`controller`, `bounds`, `rows`, `cols`, `pins`, `quantum`, `settings`) and each key's `state`/`row`/`col`/`id` must remain byte-for-byte identical to the current stock file — only `legend` and `keycodes[0]` change per key, plus the top-level `macros` object.
- Key mapping (col 0→2, left to right): `A` → `https://claude.ai`, `SO` → `https://stackoverflow.com`, `C` → `https://chatgpt.com`.
- Full spec: `Docs/2026-07-23-key-macro-firmware-design.md`.

---

### Task 1: URL-to-macro pure function

**Files:**
- Create: `scripts/thekey_macro.py`
- Test: `tests/test_thekey_macro.py`

**Interfaces:**
- Produces: `char_to_actions(char: str) -> list[tuple[int, str]]` — one URL character to `(action_code, keycode)` pairs. Raises `ValueError` for unsupported characters.
- Produces: `url_open_macro(url: str) -> list[dict]` — full macro for one key: `[{"action": int, "argument": str}, ...]`, wrapping `char_to_actions` output with a Ctrl+T press/release prefix and an Enter press/release suffix. Action codes: `2`=press, `3`=release, `4`=type.
- Consumed by: Task 2 (`generate_thekey.py`), Task 3 (`test_thekey_json.py`).

- [ ] **Step 1: Write the failing tests**

Create `tests/test_thekey_macro.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /media/francis/Data2/Source/Fun/ASCKey && python3 -m unittest tests.test_thekey_macro -v`
Expected: `ModuleNotFoundError: No module named 'scripts'` (or `scripts.thekey_macro`) — the module doesn't exist yet.

- [ ] **Step 3: Write the implementation**

Create `scripts/thekey_macro.py`:

```python
"""Build kbfirmware.com macro action lists for opening a URL in a new browser tab."""

ACTION_PRESS = 2
ACTION_RELEASE = 3
ACTION_TYPE = 4


def char_to_actions(char):
    """Return a list of (action_code, keycode) tuples for one URL character."""
    if len(char) == 1 and char.isalpha() and char.islower():
        return [(ACTION_TYPE, "KC_" + char.upper())]
    if char == ".":
        return [(ACTION_TYPE, "KC_DOT")]
    if char == "/":
        return [(ACTION_TYPE, "KC_SLSH")]
    if char == ":":
        return [
            (ACTION_PRESS, "KC_LSFT"),
            (ACTION_TYPE, "KC_SCLN"),
            (ACTION_RELEASE, "KC_LSFT"),
        ]
    raise ValueError(f"unsupported character in URL: {char!r}")


def url_open_macro(url):
    """Return the full macro action list: Ctrl+T, type url, Enter.

    Output matches the kbfirmware.com macro JSON schema:
    [{"action": int, "argument": str}, ...]
    """
    actions = [
        (ACTION_PRESS, "KC_LCTL"),
        (ACTION_PRESS, "KC_T"),
        (ACTION_RELEASE, "KC_LCTL"),
        (ACTION_RELEASE, "KC_T"),
    ]
    for char in url:
        actions.extend(char_to_actions(char))
    actions.append((ACTION_PRESS, "KC_ENT"))
    actions.append((ACTION_RELEASE, "KC_ENT"))
    return [{"action": action, "argument": argument} for action, argument in actions]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /media/francis/Data2/Source/Fun/ASCKey && python3 -m unittest tests.test_thekey_macro -v`
Expected: `Ran 6 tests in 0.00Xs` / `OK`

- [ ] **Step 5: Commit**

```bash
git add scripts/thekey_macro.py tests/test_thekey_macro.py
git commit -m "Add URL-to-macro action generator for ASCKey firmware"
```

---

### Task 2: Generator script produces the final TheKey.json

**Files:**
- Create: `scripts/generate_thekey.py`
- Modify: `../Config/TheKey.json` (overwritten by running the script, not hand-edited)

**Interfaces:**
- Consumes: `scripts.thekey_macro.url_open_macro(url: str) -> list[dict]` from Task 1.
- Produces: a runnable script (`python3 -m scripts.generate_thekey`) that overwrites `../Config/TheKey.json`. No importable symbols are consumed by later tasks — Task 3 only reads the resulting JSON file.

- [ ] **Step 1: Write the generator**

Create `scripts/generate_thekey.py`:

```python
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
    macro_keycode = {"id": f"M({key_id})", "fields": []}
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
```

- [ ] **Step 2: Run the generator**

Run: `cd /media/francis/Data2/Source/Fun/ASCKey && python3 -m scripts.generate_thekey`
Expected: `Wrote /media/francis/Data2/Source/Fun/ASCKey/Reference/TheKey.json`

- [ ] **Step 3: Sanity-check the output is valid JSON**

Run: `cd /media/francis/Data2/Source/Fun/ASCKey && python3 -c "import json; json.load(open('Reference/TheKey.json'))" && echo VALID_JSON`
Expected: `VALID_JSON`

- [ ] **Step 4: Commit**

```bash
git add scripts/generate_thekey.py Reference/TheKey.json
git commit -m "Generate ASCKey TheKey.json with URL-opening macros"
```

---

### Task 3: Acceptance test for the final TheKey.json

**Files:**
- Create: `tests/test_thekey_json.py`

**Interfaces:**
- Consumes: `scripts.thekey_macro.url_open_macro(url: str) -> list[dict]` from Task 1; reads `../Config/TheKey.json` produced by Task 2.
- Produces: nothing consumed by later tasks — this is the final acceptance gate for the plan.

- [ ] **Step 1: Write the test**

Create `tests/test_thekey_json.py`:

```python
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
            self.assertEqual(key["keycodes"][0], {"id": f"M({key_id})", "fields": []})

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
```

- [ ] **Step 2: Run the test to verify it passes**

Run: `cd /media/francis/Data2/Source/Fun/ASCKey && python3 -m unittest tests.test_thekey_json -v`
Expected: `Ran 6 tests in 0.00Xs` / `OK`

(If this fails, the generator from Task 2 was not run, or its output doesn't match the spec — re-run `python3 -m scripts.generate_thekey` and retest before proceeding.)

- [ ] **Step 3: Commit**

```bash
git add tests/test_thekey_json.py
git commit -m "Add acceptance test for ASCKey TheKey.json macros"
```

---

## Manual verification (not automatable)

After Task 3 passes, the remaining verification is physical and must be done by the user, per the spec's "Out of scope"/"Verification" sections:

1. Go to the archived Keyboard Firmware Builder: `https://web.archive.org/web/20260214211516/https://docs.drop.com/thekey.json` page linked from the official Drop guide (or the current kbfirmware.com if still reachable).
2. Upload `../Config/TheKey.json` via "Upload Keyboard Firmware Builder configuration".
3. Go to the **Compile** tab, click **Download .hex**.
4. Flash the `.hex` file to the macropad using QMK Toolbox (confirm MCU shows `atmega32u4`).
5. With a browser window focused, press each of the 3 keys and confirm it opens a new tab to the correct URL.
