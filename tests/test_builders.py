import unittest

from mft.builders import render_post, build_post, build_x_thread
from mft.textmetrics import x_len

X_HARD_LIMIT = 280
THREAD_DIVIDER = "\n" + "· " * 22 + "\n"


def cfg(**over):
    base = dict(
        title_style="Bold", body_style="Normal", media_style="Normal",
        bangla_decor="None", use_cta=False, cta_map={}, divider_len=10,
    )
    base.update(over)
    return base


class TestBuildPost(unittest.TestCase):
    def _post(self, **over):
        post = {
            "title": "Hi", "platform": "facebook",
            "body_lines": ["line one", "", "line two"],
            "media": "mylink", "hashtags": "#a #b",
        }
        post.update(over)
        return post

    def test_title_is_styled_bold(self):
        out = build_post(self._post(), cfg())
        self.assertIn(chr(0x1D407) + chr(0x1D422), out)  # 𝐇𝐢

    def test_divider_and_media_and_hashtags(self):
        out = build_post(self._post(), cfg(divider_len=12))
        self.assertIn("─" * 12, out)
        self.assertIn("mylink", out)
        self.assertIn("#a #b", out)

    def test_cta_included_when_enabled(self):
        out = build_post(self._post(), cfg(use_cta=True, cta_map={"Facebook": "CALL TO ACTION"}))
        self.assertIn("CALL TO ACTION", out)

    def test_cta_absent_when_disabled(self):
        out = build_post(self._post(), cfg(use_cta=False, cta_map={"Facebook": "CALL TO ACTION"}))
        self.assertNotIn("CALL TO ACTION", out)


class TestXThread(unittest.TestCase):
    def test_thread_is_numbered_and_split(self):
        post = {
            "title": "T", "platform": "x",
            "body_lines": ["a" * 100, "b" * 100, "c" * 100],
            "media": "m", "hashtags": "#h",
        }
        out = build_x_thread(post, cfg())
        # title + packed(a,b) + c + media/hashtags = 4 tweets
        self.assertIn("(1/4)", out)
        self.assertIn("(4/4)", out)
        self.assertIn("· ", out)  # thread divider

    def test_render_post_routes_x_to_thread(self):
        post = {"title": "T", "platform": "twitter", "body_lines": ["hi"],
                "media": "", "hashtags": ""}
        out = render_post(post, cfg())
        self.assertIn("(1/", out)


class TestXThreadLimits(unittest.TestCase):
    """Regressions: every tweet must fit X's *weighted* 280 limit."""

    @staticmethod
    def _tweets(out):
        return out.split(THREAD_DIVIDER)

    def _assert_all_fit(self, out):
        for tweet in self._tweets(out):
            self.assertLessEqual(x_len(tweet), X_HARD_LIMIT, repr(tweet[:60]))

    def test_long_single_line_is_word_wrapped(self):
        # One 600-char paragraph used to become a single over-limit tweet.
        post = {"title": "", "platform": "x",
                "body_lines": ["word " * 120], "media": "", "hashtags": ""}
        out = build_x_thread(post, cfg())
        self.assertGreater(len(self._tweets(out)), 1)
        self._assert_all_fit(out)

    def test_styled_text_packs_by_weighted_length(self):
        # Bold math chars count 2 on X; len()-based packing overflowed.
        post = {"title": "", "platform": "x",
                "body_lines": ["alpha " * 40], "media": "", "hashtags": ""}
        out = build_x_thread(post, cfg(body_style="Bold"))
        self.assertGreater(len(self._tweets(out)), 1)
        self._assert_all_fit(out)

    def test_title_and_media_tweets_are_wrapped(self):
        post = {"title": "t " * 200, "platform": "x",
                "body_lines": ["hi"], "media": "m " * 200,
                "hashtags": "#tag " * 80}
        out = build_x_thread(post, cfg())
        self._assert_all_fit(out)

    def test_unbreakable_word_is_hard_split(self):
        post = {"title": "", "platform": "x",
                "body_lines": ["x" * 700], "media": "", "hashtags": ""}
        out = build_x_thread(post, cfg())
        self.assertGreaterEqual(len(self._tweets(out)), 3)
        self._assert_all_fit(out)


if __name__ == "__main__":
    unittest.main()
