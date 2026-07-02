"""Content parser + validated file loading."""

import io

from .docx_io import Document, DOCX_AVAILABLE

KNOWN_PLATFORMS = {"facebook", "linkedin", "pinterest", "x", "twitter"}

MAX_UPLOAD_MB = 5
ALLOWED_EXTENSIONS = (".docx", ".md", ".txt")


def parse_text(lines: list) -> list:
    """
    Reads a list of text lines and returns a list of post dicts:
        { title, platform, body_lines, media, hashtags }
    Handles one Title with multiple platform sections per block.
    """
    blocks, current_block = [], []
    for line in lines:
        if line.strip() == "---":
            if current_block:
                blocks.append(current_block)
            current_block = []
        else:
            current_block.append(line)
    if current_block:
        blocks.append(current_block)

    all_posts = []

    for block in blocks:
        # Find the title without consuming the block: a block that has no
        # "Title:" line is still parsed in full (title stays empty).
        title = ""
        i = 0
        for j, ln in enumerate(block):
            stripped = ln.strip()
            if stripped.lower().startswith("title:"):
                title = stripped[6:].strip()
                i = j + 1
                break

        state = {"platform": "", "body": [], "media": "", "hashtags": "", "mode": None}

        def save_section():
            body = state["body"][:]
            while body and body[-1].strip() == "":
                body.pop()
            if state["platform"] or body:
                all_posts.append({
                    "title":      title,
                    "platform":   state["platform"],
                    "body_lines": body,
                    "media":      state["media"],
                    "hashtags":   state["hashtags"],
                })

        def _is_platform_header(pos):
            """A platform word mid-body is content, not a header, unless the
            next non-blank line starts a new section (Body:/Media:)."""
            if state["mode"] != "body":
                return True
            for nxt in block[pos + 1:]:
                s = nxt.strip().lower()
                if s:
                    return s.startswith(("body:", "media:"))
            return False

        while i < len(block):
            raw = block[i]
            line = raw.strip()

            if line.lower() in KNOWN_PLATFORMS and _is_platform_header(i):
                save_section()
                state.update(platform=line, body=[], media="", hashtags="", mode="platform")
            elif line.lower().startswith("body:"):
                rest = line[5:].strip()
                state["body"] = [rest] if rest else []
                state["mode"] = "body"
            elif line.lower().startswith("media:"):
                state["media"] = line[6:].strip()
                state["mode"] = "media"
            elif state["mode"] == "media" and line.startswith("#"):
                state["hashtags"] = line
                state["mode"] = "hashtags"
            elif state["mode"] == "body":
                state["body"].append(raw)   # keep original spacing

            i += 1

        save_section()

    return all_posts


def lines_from_upload(uploaded) -> list:
    """Return text lines from a validated .docx / .md / .txt upload.

    Raises ValueError with a user-friendly message on any failed check so the
    UI can surface it; the file is never parsed until all checks pass.
    """
    name = uploaded.name.lower()

    # 1) Extension allow-list (belt-and-suspenders alongside the uploader's type=)
    if not name.endswith(ALLOWED_EXTENSIONS):
        raise ValueError(f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}.")

    # 2) Size limit
    size_mb = getattr(uploaded, "size", 0) / (1024 * 1024)
    if size_mb > MAX_UPLOAD_MB:
        raise ValueError(f"File is {size_mb:.1f} MB — over the {MAX_UPLOAD_MB} MB limit.")

    data = uploaded.read()
    if not data:
        raise ValueError("File is empty.")

    if name.endswith(".docx"):
        if not DOCX_AVAILABLE:
            raise RuntimeError("python-docx is not installed.")
        # 3) Light magic-byte check: a real .docx is a ZIP container ("PK..").
        if data[:2] != b"PK":
            raise ValueError("This does not look like a real .docx file.")
        doc = Document(io.BytesIO(data))
        return [p.text for p in doc.paragraphs]

    # .md / .txt — decode as UTF-8 text; splitlines() handles \r\n and \r
    # so Windows-saved files don't leak carriage returns into the output.
    return data.decode("utf-8", errors="replace").splitlines()
