"""Post builders: standard post + X/Twitter thread."""

from .styles import STYLES, decorate
from .config import X_LIMIT


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


def build_x_thread(post: dict, cfg: dict) -> str:
    """Split a post into numbered tweets (n/N), each under the X limit."""
    t_style = STYLES[cfg["title_style"]]
    b_style = STYLES[cfg["body_style"]]
    m_style = STYLES[cfg["media_style"]]
    decor = cfg["bangla_decor"]
    tweets = []

    if post["title"]:
        tweets.append(decorate(t_style(post["title"]), decor))

    current = ""
    for line in post["body_lines"]:
        formatted = decorate(b_style(line), decor) if line.strip() else ""
        candidate = (current + "\n" + formatted).strip()
        if len(candidate) <= X_LIMIT:
            current = candidate
        else:
            if current:
                tweets.append(current)
            current = formatted
    if current:
        tweets.append(current)

    media_text, hashtags = post["media"], post["hashtags"]
    if media_text or hashtags:
        last = ""
        if media_text:
            last += decorate(m_style(media_text), decor)
        if hashtags:
            last += ("\n" if last else "") + m_style(hashtags)
        tweets.append(last.strip())

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
