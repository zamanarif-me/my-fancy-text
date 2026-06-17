"""MyFancyText core package — pure-Python logic, no Streamlit dependency.

Importing this package (or any submodule) is safe in tests and scripts; only
``app.py`` pulls in Streamlit. python-docx is optional and imported lazily via
``mft.docx_io``.
"""

__all__ = [
    "styles",
    "config",
    "parser",
    "hashtags",
    "builders",
    "exporter",
    "docx_io",
]
