"""Post builders: standard post + X/Twitter thread."""

from .styles import STYLES, decorate
from .config import X_LIMIT
from .textmetrics import x_len


def build_post(post: dict, cfg: dict) -> str:
    """Build a standard formatted post string using the chosen styles."""
    t_style = STYLES[cfg["title_style"]]
    b_style = STYLES[cfg["body_style"]]
    m_style = STYLES[cfg["media_style"]]
    decor = cfg["bangla_decor"]
    out = []

    # TITLE
    if post["title"]:
        out.append(decorate(t_style(post["title"]), decor))
        out.append("")

    # BODY (blank lines preserved as paragraph breaks)
    for line in post["body_lines"]:
        out.append(decorate(b_style(line), decor) if line.strip() else "")
    out.append("")

    # CTA
    if cfg["use_cta"]:
        cta = cfg["cta_map"].get(post["platform"].title(), "")
        if cta:
            out.append(cta)
            out.append("")

    # MEDIA + HASHTAGS
    media_text, hashtags = post["media"], post["hashtags"]
    if media_text or hashtags:
        divider = "─" * cfg["divider_len"]
        out.append(divider)
        if media_text:
            out.append(decorate(m_style(media_text), decor))
        if hashtags:
            out.append(m_style(hashtags))
        out.append(divider)

    while out and out[-1] == "":
        out.pop()
    return "\n".join(out)


def _hard_split(word: str, limit: int) -> list:
    """Split one unbreakable word into chunks whose weighted length fits."""
    parts, cur, w = [], "", 0
    for ch in word:
        cw = x_len(ch)
        if cur and w + cw > limit:
            parts.append(cur)
            cur, w = "", 0
        cur += ch
        w += cw
    if cur:
        parts.append(cur)
    return parts


def _wrap_to_limit(text: str, limit: int) -> list:
    """Word-wrap ``text`` into pieces whose x_len fits ``limit``."""
    if x_len(text) <= limit:
        return [text]
    pieces, current = [], ""
    for word in text.split(" "):
        chunks = [word] if x_len(word) <= limit else _hard_split(word, limit)
        for chunk in chunks:
            candidate = (current + " " + chunk) if current else chunk
            if x_len(candidate) <= limit:
                current = candidate
            else:
                if current:
                    pieces.append(current)
                current = chunk
    if current:
        pieces.append(current)
    return pieces or [""]


def build_x_thread(post: dict, cfg: dict) -> str:
    """Split a post into numbered tweets (n/N), each under the X limit.

    Lengths use ``x_len`` (X's weighted counting: styled math chars and
    emoji = 2, URLs = 23), and every part — title, body, media/hashtags —
    is wrapped, so no tweet can exceed the real limit.
    """
    t_style = STYLES[cfg["title_style"]]
    b_style = STYLES[cfg["body_style"]]
    m_style = STYLES[cfg["media_style"]]
    decor = cfg["bangla_decor"]
    tweets = []

    if post["title"]:
        tweets.extend(_wrap_to_limit(decorate(t_style(post["title"]), decor), X_LIMIT))

    current = ""
    for line in post["body_lines"]:
        formatted = decorate(b_style(line), decor) if line.strip() else ""
        for piece in _wrap_to_limit(formatted, X_LIMIT):
            candidate = (current + "\n" + piece).strip()
            if x_len(candidate) <= X_LIMIT:
                current = candidate
            else:
                if current:
                    tweets.append(current)
                current = piece
    if current:
        tweets.append(current)

    media_text, hashtags = post["media"], post["hashtags"]
    if media_text or hashtags:
        last = ""
        if media_text:
            last += decorate(m_style(media_text), decor)
        if hashtags:
            last += ("\n" if last else "") + m_style(hashtags)
        tweets.extend(_wrap_to_limit(last.strip(), X_LIMIT))

    if not tweets:
        return ""

    total = len(tweets)
    numbered = [f"({i + 1}/{total})\n{t}" for i, t in enumerate(tweets)]
    divider = "\n" + "· " * 22 + "\n"
    return divider.join(numbered)


def render_post(post: dict, cfg: dict) -> str:
    if post["platform"].lower() in ("x", "twitter"):
        return build_x_thread(post, cfg)
    return build_post(post, cfg)
