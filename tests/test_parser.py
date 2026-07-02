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

    def test_block_without_title_is_kept(self):
        # Regression: blocks missing "Title:" used to be silently dropped.
        posts = parse_text(["Facebook", "Body:", "hello world"])
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["title"], "")
        self.assertEqual(posts[0]["platform"], "Facebook")
        self.assertEqual(posts[0]["body_lines"], ["hello world"])

    def test_platform_word_inside_body_stays_in_body(self):
        # Regression: a lone "x" in the body used to start a phantom
        # X section and drop the lines after it.
        posts = parse_text(
            ["Title: t", "Facebook", "Body:", "option a", "x", "option b"])
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["body_lines"], ["option a", "x", "option b"])

    def test_platform_after_body_still_starts_new_section(self):
        posts = parse_text(
            ["Title: t", "Facebook", "Body:", "fb body",
             "LinkedIn", "Body:", "li body"])
        self.assertEqual([p["platform"] for p in posts],
                         ["Facebook", "LinkedIn"])
        self.assertEqual(posts[0]["body_lines"], ["fb body"])
        self.assertEqual(posts[1]["body_lines"], ["li body"])


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

    def test_crlf_upload_leaves_no_carriage_returns(self):
        # Regression: Windows CRLF files used to leak \r into body lines.
        up = FakeUpload(
            "a.txt",
            b"Title: hi\r\nFacebook\r\nBody:\r\nline one\r\nline two\r\n")
        lines = lines_from_upload(up)
        self.assertTrue(all("\r" not in ln for ln in lines))
        posts = parse_text(lines)
        self.assertEqual(posts[0]["body_lines"], ["line one", "line two"])


if __name__ == "__main__":
    unittest.main()
