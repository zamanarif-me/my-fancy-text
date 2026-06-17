"""Unicode style engine + Bangla decoration.

Each style maps A-Z / a-z / 0-9 to a Unicode "Mathematical Alphanumeric" range.
Some ranges have holes where the glyph already lives in the "Letterlike Symbols"
block — those are patched via ``exceptions``. Bangla, emoji and other characters
are passed through unchanged.
"""


def _make_styler(upper_base, lower_base, digit_base=None, exceptions=None):
    exceptions = exceptions or {}

    def styler(text: str) -> str:
        out = []
        for ch in text:
            if ch in exceptions:
                out.append(exceptions[ch])
                continue
            cp = ord(ch)
            if upper_base is not None and 65 <= cp <= 90:        # A-Z
                out.append(chr(upper_base + cp - 65))
            elif lower_base is not None and 97 <= cp <= 122:     # a-z
                out.append(chr(lower_base + cp - 97))
            elif digit_base is not None and 48 <= cp <= 57:      # 0-9
                out.append(chr(digit_base + cp - 48))
            else:
                out.append(ch)                                   # Bangla, emoji, etc.
        return "".join(out)

    return styler


_ITALIC_EXC = {"h": "ℎ"}
_SCRIPT_EXC = {
    "B": "ℬ", "E": "ℰ", "F": "ℱ", "H": "ℋ", "I": "ℐ",
    "L": "ℒ", "M": "ℳ", "R": "ℛ",
    "e": "ℯ", "g": "ℊ", "o": "ℴ",
}
_FRAKTUR_EXC = {
    "C": "ℭ", "H": "ℌ", "I": "ℑ", "R": "ℜ", "Z": "ℨ",
}
_DOUBLE_EXC = {
    "C": "ℂ", "H": "ℍ", "N": "ℕ", "P": "ℙ",
    "Q": "ℚ", "R": "ℝ", "Z": "ℤ",
}

# Ordered so the most-used styles appear first in the dropdowns.
STYLES = {
    "Normal":            _make_styler(None, None, None),
    "Bold":              _make_styler(0x1D400, 0x1D41A, 0x1D7CE),
    "Italic":            _make_styler(0x1D434, 0x1D44E, None, _ITALIC_EXC),
    "Bold Italic":       _make_styler(0x1D468, 0x1D482, None, _ITALIC_EXC),
    "Sans Bold":         _make_styler(0x1D5D4, 0x1D5EE, 0x1D7EC),
    "Sans Italic":       _make_styler(0x1D608, 0x1D622),
    "Sans Bold Italic":  _make_styler(0x1D63C, 0x1D656),
    "Monospace":         _make_styler(0x1D670, 0x1D68A, 0x1D7F6),
    "Script":            _make_styler(0x1D49C, 0x1D4B6, None, _SCRIPT_EXC),
    "Bold Script":       _make_styler(0x1D4D0, 0x1D4EA),
    "Fraktur":           _make_styler(0x1D504, 0x1D51E, None, _FRAKTUR_EXC),
    "Bold Fraktur":      _make_styler(0x1D56C, 0x1D586),
    "Double-struck":     _make_styler(0x1D538, 0x1D552, 0x1D7D8, _DOUBLE_EXC),
}


# ── Bangla decoration ────────────────────────────────────────────────
# Unicode has no bold/italic Bangla letters, so Bangla text can't be "weighted".
# Instead we optionally wrap Bangla-containing lines with a decorative frame.

def has_bangla(text: str) -> bool:
    return any(0x0980 <= ord(c) <= 0x09FF for c in text)


BANGLA_DECOR = {
    "None":           None,
    "Sparkle ✨":      ("✨ ", " ✨"),
    "Stars ✦":        ("✦ ", " ✦"),
    "Brackets ❰❱":    ("❰ ", " ❱"),
    "Petals ❀":       ("❀ ", " ❀"),
    "Flower 🌸":       ("🌸 ", " 🌸"),
    "Arrow ➤":        ("➤ ", ""),
}


def decorate(line: str, decor_name: str) -> str:
    """Wrap a line in the chosen decorative frame, but only if it has Bangla."""
    frame = BANGLA_DECOR.get(decor_name)
    if frame and line.strip() and has_bangla(line):
        return frame[0] + line + frame[1]
    return line
