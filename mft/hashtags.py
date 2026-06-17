"""Custom hashtag sets: load / save / normalize.

Sets are persisted to ``custom_hashtags.json`` at the project root so they
survive app restarts (local use). Tests override ``CUSTOM_FILE`` to a temp path.
"""

import re
import json
from pathlib import Path

# Project root = parent of the mft/ package directory.
CUSTOM_FILE = Path(__file__).resolve().parent.parent / "custom_hashtags.json"


def load_custom_sets() -> dict:
    """Load the user's saved hashtag sets from disk ({name: [tags]})."""
    try:
        data = json.loads(CUSTOM_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return {str(k): list(v) for k, v in data.items()}
    except (OSError, ValueError, TypeError):
        pass
    return {}


def save_custom_sets(data: dict) -> None:
    """Persist the user's hashtag sets to disk."""
    try:
        CUSTOM_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except OSError:
        pass


def normalize_tags(raw: str) -> list:
    """Split free text on space/comma/newline into clean, de-duped #hashtags."""
    tags = []
    for part in re.split(r"[\s,]+", raw.strip()):
        if not part:
            continue
        tag = "#" + part.lstrip("#")
        if tag != "#" and tag not in tags:
            tags.append(tag)
    return tags
