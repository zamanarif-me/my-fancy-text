"""Optional python-docx import, shared by the parser and exporter.

python-docx is only needed to read/write .docx files. Importing it lazily here
keeps the rest of the app (paste mode, copy buttons, .md/.txt) working even when
the library is not installed.
"""

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    DOCX_AVAILABLE = True
except ImportError:  # pragma: no cover - only hit when python-docx is absent
    Document = None
    Pt = RGBColor = Inches = None
    DOCX_AVAILABLE = False
