"""DOCX writer + ZIP bundling for download."""

import io
import zipfile

from .docx_io import Document, Pt, RGBColor, Inches


def write_docx_bytes(platform: str, posts_text: list) -> bytes:
    """Write all posts for one platform into a .docx and return its bytes.

    Requires python-docx; callers must guard on ``DOCX_AVAILABLE`` first.
    """
    doc = Document()

    sec = doc.sections[0]
    sec.page_width = Inches(8.5)
    sec.page_height = Inches(11)
    sec.left_margin = Inches(1.2)
    sec.right_margin = Inches(1.2)
    sec.top_margin = Inches(1.0)
    sec.bottom_margin = Inches(1.0)

    doc.styles["Normal"].font.name = "Segoe UI"
    doc.styles["Normal"].font.size = Pt(12)

    total = len(posts_text)

    for idx, post_text in enumerate(posts_text):
        hdr = doc.add_paragraph()
        hdr.paragraph_format.space_after = Pt(4)
        r = hdr.add_run(
            f"{'─' * 14}  {platform.upper()}  •  POST {idx + 1} of {total}  {'─' * 14}"
        )
        r.font.size = Pt(8)
        r.font.color.rgb = RGBColor(0xBB, 0xBB, 0xBB)

        inst = doc.add_paragraph()
        inst.paragraph_format.space_after = Pt(10)
        r2 = inst.add_run("Select the text below  →  Ctrl+C  →  Paste on platform")
        r2.font.size = Pt(8)
        r2.italic = True
        r2.font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)

        for line in post_text.split("\n"):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(line)
            run.font.name = "Segoe UI Emoji"
            run.font.size = Pt(12)

        if idx < total - 1:
            doc.add_page_break()

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def build_zip(platform_files: dict) -> bytes:
    """Bundle {filename: bytes} into a single .zip and return its bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, data in platform_files.items():
            zf.writestr(filename, data)
    return buf.getvalue()
