"""X/Twitter-accurate text length counting.

X does not count code points the way Python's ``len()`` does:

- Characters in a few "light" Unicode ranges count as 1 (this includes
  Latin, Bangla, and most other scripts up to U+10FF).
- Everything else — Mathematical Alphanumeric styled letters, emoji,
  decorative symbols — counts as 2.
- Every http(s) URL is replaced by a t.co link and counts a flat 23,
  regardless of its real length.

Reference: twitter-text's config v3 (weightedLength / transformedURLLength).
"""

import re

_URL_RE = re.compile(r"https?://\S+")
URL_LENGTH = 23

# Inclusive codepoint ranges that X charges as weight 1.
_WEIGHT_ONE_RANGES = (
    (0, 4351),      # Latin, Latin ext., Greek, Cyrillic, Hebrew, Arabic, ...
    (8192, 8205),   # General Punctuation spaces + zero-width joiners
    (8208, 8223),   # dashes and smart quotes
    (8242, 8247),   # primes
)


def _char_weight(ch: str) -> int:
    cp = ord(ch)
    for lo, hi in _WEIGHT_ONE_RANGES:
        if lo <= cp <= hi:
            return 1
    return 2


def x_len(text: str) -> int:
    """Return the length X/Twitter actually charges for ``text``."""
    total = 0
    last = 0
    for m in _URL_RE.finditer(text):
        total += sum(_char_weight(c) for c in text[last:m.start()]) + URL_LENGTH
        last = m.end()
    total += sum(_char_weight(c) for c in text[last:])
    return total
