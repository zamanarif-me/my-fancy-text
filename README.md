# ✨ MyFancyText

Turn plain text into **fancy Unicode** social posts — copy-paste ready for
Facebook, LinkedIn, Pinterest, and X/Twitter. No native formatting needed; the
styled characters survive copy-paste on every platform.

- **English** → real Unicode styles (Bold, Italic, Script, Monospace, …)
- **Bangla** → decorative frames (Unicode has no bold/italic Bangla)
- Input: **paste text** or **upload `.docx` / `.md` / `.txt`**
- Output: per-platform **`.docx`**, bundled as a **ZIP**
- X/Twitter auto-threading (`n/N`)
- Built-in **Emoji & Hashtag library** (curated, one-click copy or add to content)
- **Save your own hashtag sets** — persisted to `custom_hashtags.json`, reusable across sessions
- **Validated uploads** — extension allow-list, 5 MB size limit, empty-file & real-`.docx` checks
- **Modular core + tests** — logic split into the `mft/` package with a 37-test suite

## Setup (local)

```powershell
cd "$env:USERPROFILE\OneDrive\Desktop\MyFancyText"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Opens at http://localhost:8501.

## How to use

1. **Paste text** (or **upload** a `.docx` / `.md` / `.txt`) using the format below.
2. In the sidebar pick **styles** for Title / Body / Media, a **Bangla frame**,
   toggle the **CTA**, and set the **preview size**.
3. Each platform tab shows the post with a one-click **copy** button.
4. **Download** all platforms as a ZIP of `.docx` files, or one at a time.

> **Note on size/weight:** copy-paste text cannot carry a real font *size* —
> social platforms ignore it. The "Preview size" slider only enlarges the
> in-app preview. *Weight/style* is real, via the Unicode style picker.

## Project structure

```
MyFancyText/
├── app.py              # Streamlit UI only (no business logic)
├── mft/                # Pure-Python core — no Streamlit, fully testable
│   ├── styles.py       # Unicode style engine + Bangla decoration
│   ├── parser.py       # Content parser + validated file upload
│   ├── builders.py     # Standard post + X/Twitter thread builders
│   ├── exporter.py     # DOCX writer + ZIP bundling
│   ├── hashtags.py     # Custom hashtag sets (load/save/normalize)
│   ├── config.py       # CTAs, limits, emoji/hashtag library, sample
│   └── docx_io.py      # Optional python-docx import (shared)
├── tests/              # unittest suite (also runs under pytest)
├── requirements.txt
└── requirements-dev.txt
```

## Run the tests

```powershell
pip install -r requirements-dev.txt
pytest -q            # or: python -m unittest discover -s tests
```

37 tests cover the style engine, Bangla decoration, parser, upload validation,
post/thread builders, hashtag persistence, and DOCX/ZIP export.

## Input format

```
Title: Day 1: SEO Patience & Trust
Facebook
Body:
Your Facebook body text here.
Second paragraph here.
Media: Follow me on LinkedIn: https://...
#SEOStrategy #DigitalMarketing #YourName
LinkedIn
Body:
Your LinkedIn body text here.
Media: Follow me on LinkedIn: https://...
#SEOStrategy #DigitalMarketing #YourName
---
Title: Day 2: Next Post Title
...
```

### Rules
- One `Title:` per post block.
- Platform names on their own line: `Facebook` / `LinkedIn` / `Pinterest` / `X`.
- `Body:` on its own line, content below it.
- `Media:` on its own line with the link text.
- Hashtags on the line right after `Media:`.
- Separate each post block with `---`.

## Deploy free on Streamlit Community Cloud (via GitHub)

1. **Push this folder to GitHub:**
   ```powershell
   cd "$env:USERPROFILE\OneDrive\Desktop\MyFancyText"
   git init
   git add .
   git commit -m "MyFancyText"
   git branch -M main
   git remote add origin https://github.com/<your-username>/MyFancyText.git
   git push -u origin main
   ```
   (Create the empty `MyFancyText` repo on github.com first.)

2. Go to **https://share.streamlit.io** → sign in with GitHub → **New app**.
3. Pick the repo, branch `main`, main file path `app.py` → **Deploy**.
4. Streamlit reads `requirements.txt` automatically and gives you a public URL.

Any future `git push` to `main` auto-redeploys the app.

## What changed vs. the original Colab script

- Removed the `google.colab` dependency — runs anywhere in the browser.
- Renamed to **MyFancyText**.
- Many Unicode **font styles / weights**, chosen per Title / Body / Media.
- **Bangla decorative frames** (sparkle, stars, brackets, …).
- Input from **paste**, `.docx`, `.md`, or `.txt`.
- Live per-platform preview with one-click copy + optional large preview.
- Character counters against each platform's limit.
- Toggle and fully customize the CTAs.
- Download everything as a single **ZIP**.
- **Emoji & Hashtag library** built in (SEO, marketing, motivation, Bangla, …).
- Ready-to-deploy on Streamlit Community Cloud via GitHub.
