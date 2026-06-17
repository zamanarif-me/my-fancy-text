import unittest
import tempfile
from pathlib import Path

import mft.hashtags as h


class TestNormalizeTags(unittest.TestCase):
    def test_adds_hash_and_dedupes(self):
        self.assertEqual(
            h.normalize_tags("#SEO LinkBuilding, growth\norganictraffic #SEO"),
            ["#SEO", "#LinkBuilding", "#growth", "#organictraffic"],
        )

    def test_handles_bangla(self):
        self.assertEqual(h.normalize_tags("বাংলা, #ফ্রিল্যান্সিং"),
                         ["#বাংলা", "#ফ্রিল্যান্সিং"])

    def test_empty(self):
        self.assertEqual(h.normalize_tags("   "), [])

    def test_strips_extra_hashes(self):
        self.assertEqual(h.normalize_tags("##tag"), ["#tag"])


class TestPersistence(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._orig = h.CUSTOM_FILE
        h.CUSTOM_FILE = Path(self._tmp.name) / "custom_hashtags.json"

    def tearDown(self):
        h.CUSTOM_FILE = self._orig
        self._tmp.cleanup()

    def test_load_missing_returns_empty(self):
        self.assertEqual(h.load_custom_sets(), {})

    def test_save_then_load_roundtrip(self):
        data = {"My Combo": ["#SEO", "#growth"], "Bangla": ["#বাংলা"]}
        h.save_custom_sets(data)
        self.assertEqual(h.load_custom_sets(), data)

    def test_corrupt_file_returns_empty(self):
        h.CUSTOM_FILE.write_text("not json{", encoding="utf-8")
        self.assertEqual(h.load_custom_sets(), {})


if __name__ == "__main__":
    unittest.main()
