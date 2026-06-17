import unittest

from mft.styles import STYLES, has_bangla, decorate


class TestStyles(unittest.TestCase):
    def test_bold_letters_and_digits(self):
        self.assertEqual(STYLES["Bold"]("A"), chr(0x1D400))
        self.assertEqual(STYLES["Bold"]("a"), chr(0x1D41A))
        self.assertEqual(STYLES["Bold"]("0"), chr(0x1D7CE))

    def test_italic_h_exception(self):
        # italic lowercase 'h' has no math slot; uses Planck constant ℎ
        self.assertEqual(STYLES["Italic"]("h"), "ℎ")

    def test_script_exception(self):
        self.assertEqual(STYLES["Script"]("H"), "ℋ")

    def test_double_struck_exception_and_digit(self):
        self.assertEqual(STYLES["Double-struck"]("R"), "ℝ")
        self.assertEqual(STYLES["Double-struck"]("7"), chr(0x1D7D8 + 7))

    def test_normal_is_identity(self):
        self.assertEqual(STYLES["Normal"]("Hello 123 #tag"), "Hello 123 #tag")

    def test_bangla_passes_through_unchanged(self):
        self.assertEqual(STYLES["Bold"]("ক"), "ক")
        self.assertEqual(STYLES["Bold"]("ধৈর্য X"), "ধৈর্য " + chr(0x1D417))  # X -> 𝐗

    def test_emoji_and_symbols_unchanged(self):
        self.assertEqual(STYLES["Bold"]("✨!"), "✨!")


class TestBangla(unittest.TestCase):
    def test_has_bangla(self):
        self.assertTrue(has_bangla("ধৈর্য"))
        self.assertTrue(has_bangla("mixed ক text"))
        self.assertFalse(has_bangla("English only 123"))

    def test_decorate_wraps_bangla(self):
        out = decorate("ধৈর্য", "Sparkle ✨")
        self.assertTrue(out.startswith("✨ "))
        self.assertTrue(out.endswith(" ✨"))
        self.assertIn("ধৈর্য", out)

    def test_decorate_skips_english(self):
        self.assertEqual(decorate("English only", "Sparkle ✨"), "English only")

    def test_decorate_none_is_identity(self):
        self.assertEqual(decorate("ধৈর্য", "None"), "ধৈর্য")

    def test_decorate_skips_blank(self):
        self.assertEqual(decorate("   ", "Sparkle ✨"), "   ")


if __name__ == "__main__":
    unittest.main()
