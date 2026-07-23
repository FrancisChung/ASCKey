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
