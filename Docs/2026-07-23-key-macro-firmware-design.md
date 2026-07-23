## Background

This spec covers implementing the functionality described in `2026-07-22-initial-design.md`: configuring the 3-key StackOverflow "The Key" macropad (repurposed as ASCKey) so each key opens a browser tab to a specific URL.

Both reference guides in `/Reference` (Drop's official help article and Helge Johnsen's unofficial guide) describe the same mechanism and tooling, confirmed against the existing `Reference/TheKey.json` (currently the stock/default file — keys are unconfigured `KC_1`/`KC_2`/`KC_3`, no macros defined).

## Target environment

- Primary: Linux Mint 22.2 (Cinnamon)
- Secondary: Windows (occasional use)
- Both use `Ctrl` (not `Cmd`) as the modifier for "new browser tab" — a single macro definition covers both, no per-OS variants needed.

## Mechanism (per reference docs' convention)

The keyboard is a dumb QMK macropad — it has no ability to launch applications. Each key's macro works by injecting raw keystrokes via `kbfirmware.com`'s macro system:

`Press Ctrl → Press T → Release Ctrl → Release T → type the full URL character-by-character → Press Enter → Release Enter`

This assumes a browser window is already open and focused when the key is pressed — Ctrl+T is sent to whatever currently has focus. Neither reference doc addresses this limitation; it's accepted as the standard convention for this device, and confirmed with the user as acceptable.

URLs are typed in full (`https://...`), not bare domains, per user preference — this differs from Helge's example (which types a bare domain), but follows the exact same macro mechanics.

## Key mapping

Physical left-to-right order matches `2026-07-22-initial-design.md`: A, StackOverflow logo, C.

| Key | col | Legend | Macro | Types |
|---|---|---|---|---|
| 0 | 0 | `A` | `M(0)` | `https://claude.ai` |
| 1 | 1 | `SO` | `M(1)` | `https://stackoverflow.com` |
| 2 | 2 | `C` | `M(2)` | `https://chatgpt.com` |

Legends are set to plain text placeholders (`A`, `SO`, `C`) since the config tool only supports text legends — this only affects the editor UI, not device behavior.

## Macro construction detail

Each macro follows this action sequence (action codes per the JSON schema: `2`=press, `3`=release, `4`=type/tap):

1. Press `KC_LCTL`
2. Press `KC_T`
3. Release `KC_LCTL`
4. Release `KC_T`
5. For each character in the URL:
   - Alphanumeric / `.` / `/`: a single `type` action against the matching `KC_*` keycode (e.g. `KC_H`, `KC_DOT`, `KC_SLSH`)
   - `:` (appears twice, in `https://`): no direct keycode exists on a US layout — must be emitted as `Press KC_LSFT → type KC_SCLN → Release KC_LSFT`
6. Press `KC_ENT`
7. Release `KC_ENT`

## Deliverable

`Reference/TheKey.json`, fully populated, replacing the current stock/default content. All non-key fields (`pins`, `controller`, `bounds`, `rows`/`cols`, `settings`, `quantum`) are already correct for this hardware and must be preserved unchanged — only the 3 keys' `keycodes` arrays (layer-0 entry becomes `M(0)`/`M(1)`/`M(2)`, legends set) and the top-level `macros` object are modified.

The file must remain valid JSON matching the existing schema (as shown in both reference PDFs and the current stock file).

## Out of scope

- No companion OS-level software (scripts, daemons, custom shortcuts) — ruled out during design in favor of the simpler Ctrl+T convention.
- No RGB/layer/other customization beyond the 3 URL macros.
- No macOS support (Cmd+T variant) — not a target environment.

## Verification

This is a hardware firmware artifact — verification is necessarily manual and cannot be fully automated:

- **Automatable**: confirm `Reference/TheKey.json` is well-formed JSON and structurally matches the existing schema (same top-level keys, same non-key fields preserved, keycodes/macros populated as specified).
- **Manual (user)**: import the file into kbfirmware.com's Keyboard Firmware Builder, compile to `.hex`, flash via QMK Toolbox, and physically press each key to confirm it opens the correct URL in a new tab.
