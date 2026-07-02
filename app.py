# ╔══════════════════════════════════════════════════════════════════╗
# ║                          M Y   F A N C Y   T E X T                  ║
# ║                                                                    ║
# ║  Turn plain text into fancy Unicode social posts — copy-paste      ║
# ║  ready for Facebook | LinkedIn | Pinterest | X/Twitter.            ║
# ║                                                                    ║
# ║  This file is the Streamlit UI only. All logic lives in the mft/   ║
# ║  package (styles, parser, builders, exporter, hashtags, config)    ║
# ║  so it can be unit-tested without Streamlit.                       ║
# ╚══════════════════════════════════════════════════════════════════╝
#
# Run with:  streamlit run app.py
#
# ───────────────────────────────────────────────────────────────────
#  INPUT FORMAT  (paste in the text box, or upload a .docx/.md/.txt)
# ───────────────────────────────────────────────────────────────────
#
#  Title: Day 1: SEO Patience & Trust
#  Facebook
#  Body:
#  Your Facebook body text here.
#  Media: Follow me on LinkedIn: https://...
#  #SEOStrategy #DigitalMarketing #YourName
#  ---
#  Title: Day 2: Next Post Title
#  ...
#
#  Rules:
#  - One "Title:" per post block
#  - Platform names on their own line: Facebook / LinkedIn / Pinterest / X
#  - "Body:" on its own line, content below it
#  - "Media:" on its own line with the link text
#  - Hashtags on the line right after Media:
#  - Separate each post block with ---
# ───────────────────────────────────────────────────────────────────

import html
from collections import defaultdict

import streamlit as st

from mft.docx_io import DOCX_AVAILABLE
from mft.styles import STYLES, BANGLA_DECOR
from mft.config import (
    DEFAULT_CTA, PLATFORM_LIMIT, EMOJI_LIBRARY, HASHTAG_LIBRARY, SAMPLE,
)
from mft.parser import parse_text, lines_from_upload, MAX_UPLOAD_MB
from mft.hashtags import load_custom_sets, save_custom_sets, normalize_tags
from mft.builders import render_post
from mft.exporter import write_docx_bytes, build_zip


st.set_page_config(page_title="MyFancyText", page_icon="✨", layout="wide")

st.title("✨ MyFancyText")
st.caption(
    "Turn plain text into fancy Unicode posts — copy-paste ready for "
    "Facebook, LinkedIn, Pinterest & X/Twitter. English gets real Unicode "
    "styling; Bangla gets decorative frames."
)

# ── Sidebar options ──────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Style & weight")

    style_names = list(STYLES.keys())

    def _idx(name):
        return style_names.index(name)

    title_style = st.selectbox("Title style", style_names, index=_idx("Bold Italic"))
    body_style = st.selectbox("Body style", style_names, index=_idx("Italic"))
    media_style = st.selectbox("Media / hashtag style", style_names, index=_idx("Bold Italic"))

    st.divider()
    st.subheader("🅱️ Bangla decoration")
    st.caption("Unicode has no bold Bangla, so Bangla lines get a decorative frame instead.")
    bangla_decor = st.selectbox("Frame", list(BANGLA_DECOR.keys()), index=0)

    st.divider()
    st.subheader("🔠 Preview size")
    preview_px = st.slider("In-app preview only (does not affect copied text)", 14, 40, 18)
    big_preview = st.toggle("Show large preview", value=False)

    st.divider()
    st.subheader("📣 Call-To-Action")
    use_cta = st.toggle("Add CTA", value=True)
    cta_map = {}
    if use_cta:
        for plat in ["Facebook", "LinkedIn", "Pinterest", "X"]:
            cta_map[plat] = st.text_area(plat, value=DEFAULT_CTA[plat], height=90, key=f"cta_{plat}")
        cta_map["Twitter"] = cta_map["X"]

    st.divider()
    divider_len = st.slider("Divider length", 20, 60, 44)

    if not DOCX_AVAILABLE:
        st.divider()
        st.warning("`python-docx` not installed — .docx upload/download disabled. "
                   "Run `pip install python-docx` to enable it.")

cfg = {
    "title_style": title_style,
    "body_style":  body_style,
    "media_style": media_style,
    "bangla_decor": bangla_decor,
    "use_cta":     use_cta,
    "cta_map":     cta_map,
    "divider_len": divider_len,
}

# ── Emoji & Hashtag library ──────────────────────────────────────────
# Init content first so the library's "Add" buttons can prepend safely
# (must happen before the text_area widget with key="content" is created).
if "content" not in st.session_state:
    st.session_state.content = ""
if "custom_sets" not in st.session_state:
    st.session_state.custom_sets = load_custom_sets()


def append_to_content(text: str):
    cur = st.session_state.get("content", "")
    sep = "" if (not cur or cur.endswith("\n")) else "\n"
    st.session_state.content = cur + sep + text


def add_custom_set():
    name = st.session_state.get("new_set_name", "").strip()
    tags = normalize_tags(st.session_state.get("new_set_tags", ""))
    if name and tags:
        st.session_state.custom_sets[name] = tags
        save_custom_sets(st.session_state.custom_sets)
        st.session_state.new_set_name = ""
        st.session_state.new_set_tags = ""


def delete_custom_set():
    name = st.session_state.get("del_set_name")
    if name in st.session_state.custom_sets:
        del st.session_state.custom_sets[name]
        save_custom_sets(st.session_state.custom_sets)


with st.expander("🎨 Emoji & Hashtag Library — click to copy or add to content"):
    e_tab, h_tab = st.tabs(["😀 Emoji", "#️⃣ Hashtags"])

    with e_tab:
        cat = st.selectbox("Category", list(EMOJI_LIBRARY), key="emoji_cat")
        row = "  ".join(EMOJI_LIBRARY[cat])
        st.code(row, language=None)  # one-click copy
        st.button("➕ Add this row to content", key="emoji_add",
                  on_click=append_to_content, args=(row,))

    with h_tab:
        # Built-in niches + the user's saved custom sets (custom override on clash)
        all_sets = {**HASHTAG_LIBRARY, **st.session_state.custom_sets}

        niches = st.multiselect(
            "Niche(s)", list(all_sets),
            default=[list(HASHTAG_LIBRARY)[0]], key="ht_niche",
        )
        pool = []
        for n in niches:
            for tag in all_sets.get(n, []):
                if tag not in pool:
                    pool.append(tag)
        if pool:
            if len(pool) > 3:
                max_n = st.slider("How many hashtags", 3, min(30, len(pool)),
                                  min(10, len(pool)), key="ht_max")
            else:
                max_n = len(pool)
            line = " ".join(pool[:max_n])
            st.code(line, language=None)  # one-click copy
            st.button("➕ Add these hashtags to content", key="ht_add",
                      on_click=append_to_content, args=(line,))
        else:
            st.caption("Pick at least one niche to build a hashtag set.")

        # ── Save / manage your own sets ──────────────────────────────
        with st.expander("⭐ My custom sets — save & reuse"):
            st.text_input("Set name", key="new_set_name", placeholder="My SEO combo")
            st.text_area(
                "Hashtags (space, comma, or newline separated — '#' optional)",
                key="new_set_tags", height=80,
                placeholder="#SEO #LinkBuilding growth organictraffic",
            )
            st.button("💾 Save set", on_click=add_custom_set)

            if st.session_state.custom_sets:
                st.caption("Saved: " + ", ".join(st.session_state.custom_sets))
                st.selectbox("Delete a set", list(st.session_state.custom_sets),
                             key="del_set_name")
                st.button("🗑️ Delete selected", on_click=delete_custom_set)
            else:
                st.caption("No custom sets yet. Saved sets also appear in the Niche list above.")

# ── Input ────────────────────────────────────────────────────────────
st.subheader("1 · Your content")

input_lines = None
tab_paste, tab_upload = st.tabs(["📋 Paste text", "📄 Upload file"])

with tab_paste:
    if st.button("Load sample"):
        st.session_state.content = SAMPLE
    st.text_area(
        "Paste your content (format is in the comments / README)",
        key="content",
        height=260,
        placeholder=SAMPLE,
    )

with tab_upload:
    types = ["docx", "md", "txt"] if DOCX_AVAILABLE else ["md", "txt"]
    uploaded = st.file_uploader(
        f"Upload {' / '.join('.' + t for t in types)} (max {MAX_UPLOAD_MB} MB)",
        type=types,
    )
    if uploaded is not None:
        try:
            input_lines = lines_from_upload(uploaded)
            st.success(f"Loaded: {uploaded.name}  ({len(input_lines)} lines)")
        except Exception as e:  # noqa: BLE001
            st.error(f"Could not read file: {e}")

# Upload takes precedence; otherwise use the pasted text.
if input_lines is None and st.session_state.content.strip():
    input_lines = st.session_state.content.splitlines()

# ── Parse & render ───────────────────────────────────────────────────
if not input_lines:
    st.info("👆 Paste your content or upload a file. Click **Load sample** to try it instantly.")
    st.stop()

posts = parse_text(input_lines)
if not posts:
    st.error("No posts found. Check that your text follows the required format.")
    st.stop()

st.subheader(f"2 · {len(posts)} post-section(s) found")

platform_posts = defaultdict(list)
for post in posts:
    plat = post["platform"].strip()
    key = "X" if plat.lower() in ("x", "twitter") else (plat.title() if plat else "Untitled")
    platform_posts[key].append(post)

platform_names = list(platform_posts.keys())
tabs = st.tabs([f"{p} ({len(platform_posts[p])})" for p in platform_names])

for tab, plat in zip(tabs, platform_names):
    with tab:
        for idx, post in enumerate(platform_posts[plat]):
            rendered = render_post(post, cfg)
            limit = PLATFORM_LIMIT.get(plat)
            count = len(rendered)

            label = post["title"] or f"Post {idx + 1}"
            st.markdown(f"**{idx + 1}. {label}**")

            if limit:
                if count > limit and plat != "X":
                    st.warning(f"{count:,} chars — over the {limit:,} limit for {plat}.")
                else:
                    note = " (split into a thread)" if plat == "X" else f" / {limit:,} limit"
                    st.caption(f"{count:,} characters{note}")

            # st.code gives a built-in one-click copy button (this is what you paste).
            st.code(rendered, language=None)

            # Optional large visual preview (display only — size never transfers).
            if big_preview:
                safe = html.escape(rendered).replace("\n", "<br>")
                st.markdown(
                    f"<div style='font-size:{preview_px}px; line-height:1.5; "
                    f"white-space:pre-wrap; padding:12px; border-radius:8px; "
                    f"border:1px solid rgba(128,128,128,.3)'>{safe}</div>",
                    unsafe_allow_html=True,
                )
            st.divider()

# ── Download ─────────────────────────────────────────────────────────
st.subheader("3 · Download")

if DOCX_AVAILABLE:
    platform_files = {}
    for plat, plist in platform_posts.items():
        texts = [render_post(p, cfg) for p in plist]
        platform_files[f"myfancytext_{plat.lower()}.docx"] = write_docx_bytes(plat, texts)

    zip_bytes = build_zip(platform_files)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "⬇️ Download all as ZIP",
            data=zip_bytes,
            file_name="myfancytext_posts.zip",
            mime="application/zip",
            use_container_width=True,
        )
    with col2:
        pick = st.selectbox("…or one platform", list(platform_files.keys()))
        st.download_button(
            f"⬇️ Download {pick}",
            data=platform_files[pick],
            file_name=pick,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
else:
    st.info("Install `python-docx` to enable .docx downloads. You can still copy from the boxes above.")
