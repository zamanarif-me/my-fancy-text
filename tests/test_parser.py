import unittest

from mft.parser import parse_text, lines_from_upload, MAX_UPLOAD_MB


class FakeUpload:
    """Mimics a Streamlit UploadedFile (has .name, .size, .read())."""

    def __init__(self, name, data: bytes, size=None):
        self.name = name
        self._data = data
        self.size = len(data) if size is None else size

    def read(self):
        return self._data


SAMPLE = """Title: Hello
Facebook
Body:
Line1
Line2
Media: mylink
#tag1 #tag2
LinkedIn
Body:
LI body
---
Title: Second
X
Body:
hi there
"""


class TestParseText(unittest.TestCase):
    def setUp(self):
        self.posts = parse_text(SAMPLE.split("\n"))

    def test_section_count_and_platforms(self):
        self.assertEqual(len(self.posts), 3)
        self.assertEqual([p["platform"] for p in self.posts],
                         ["Facebook", "LinkedIn", "X"])

    def test_title_shared_across_block(self):
        self.assertEqual(self.posts[0]["title"], "Hello")
        self.assertEqual(self.posts[1]["title"], "Hello")
        self.assertEqual(self.posts[2]["title"], "Second")

    def test_body_media_hashtags(self):
        fb = self.posts[0]
        self.assertEqual(fb["body_lines"], ["Line1", "Line2"])
        self.assertEqual(fb["media"], "mylink")
        self.assertEqual(fb["hashtags"], "#tag1 #tag2")

    def test_trailing_blank_lines_trimmed(self):
        # LinkedIn body has no trailing blanks kept
        self.assertEqual(self.posts[1]["body_lines"], ["LI body"])

    def test_empty_input(self):
        self.assertEqual(parse_text([]), [])


class TestLinesFromUpload(unittest.TestCase):
    def test_rejects_bad_extension(self):
        with self.assertRaises(ValueError):
            lines_from_upload(FakeUpload("x.pdf", b"data"))

    def test_rejects_oversize(self):
        big = FakeUpload("big.txt", b"a", size=(MAX_UPLOAD_MB + 1) * 1024 * 1024)
        with self.assertRaises(ValueError):
            lines_from_upload(big)

    def test_rejects_empty(self):
        with self.assertRaises(ValueError):
            lines_from_upload(FakeUpload("e.txt", b""))

    def test_reads_txt(self):
        lines = lines_from_upload(FakeUpload("a.txt", b"Title: hi\nFacebook"))
        self.assertEqual(lines, ["Title: hi", "Facebook"])

    def test_reads_md_with_unicode(self):
        lines = lines_from_upload(FakeUpload("a.md", "Title: ধৈর্য".encode("utf-8")))
        self.assertEqual(lines, ["Title: ধৈর্য"])


if __name__ == "__main__":
    unittest.main()
