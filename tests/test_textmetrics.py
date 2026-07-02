import unittest

from mft.textmetrics import x_len, URL_LENGTH


class TestXLen(unittest.TestCase):
    def test_ascii_counts_one_each(self):
        self.assertEqual(x_len("hello"), 5)

    def test_math_bold_counts_two_each(self):
        self.assertEqual(x_len(chr(0x1D400)), 2)          # 𝐀
        bold_alphabet = "".join(chr(0x1D400 + i) for i in range(26))
        self.assertEqual(x_len(bold_alphabet), 52)

    def test_bangla_counts_one_each(self):
        # Bengali (U+0980-09FF) is inside X's weight-1 range 0-4351.
        self.assertEqual(x_len("ক"), 1)

    def test_emoji_counts_two(self):
        self.assertEqual(x_len("✨"), 2)

    def test_mixed_text(self):
        # "Hi " (3×1) + 𝐇𝐢 (2×2)
        self.assertEqual(x_len("Hi " + chr(0x1D407) + chr(0x1D422)), 7)

    def test_url_counts_flat_23(self):
        self.assertEqual(
            x_len("see https://example.com/a/very/long/path/that/goes/on"),
            4 + URL_LENGTH,
        )

    def test_two_urls(self):
        self.assertEqual(x_len("https://a.co https://b.co"),
                         URL_LENGTH + 1 + URL_LENGTH)

    def test_empty(self):
        self.assertEqual(x_len(""), 0)


if __name__ == "__main__":
    unittest.main()
