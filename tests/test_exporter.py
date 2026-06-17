import io
import zipfile
import unittest

from mft.docx_io import DOCX_AVAILABLE
from mft.exporter import write_docx_bytes, build_zip


class TestZip(unittest.TestCase):
    def test_build_zip_contains_files(self):
        z = build_zip({"a.txt": b"hello", "b.txt": b"world"})
        zf = zipfile.ZipFile(io.BytesIO(z))
        self.assertEqual(set(zf.namelist()), {"a.txt", "b.txt"})
        self.assertEqual(zf.read("a.txt"), b"hello")


@unittest.skipUnless(DOCX_AVAILABLE, "python-docx not installed")
class TestDocx(unittest.TestCase):
    def test_writes_valid_docx_with_content(self):
        data = write_docx_bytes("Facebook", ["𝐇𝐢", "body text"])
        self.assertEqual(data[:2], b"PK")  # .docx is a ZIP container

        from docx import Document
        doc = Document(io.BytesIO(data))
        text = "\n".join(p.text for p in doc.paragraphs)
        self.assertIn("body text", text)
        self.assertIn("FACEBOOK", text)  # header line


if __name__ == "__main__":
    unittest.main()
