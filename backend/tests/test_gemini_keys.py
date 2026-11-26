import unittest
from unittest.mock import Mock, patch

from app.services import gemini_keys


class GeminiKeyRotationTests(unittest.TestCase):
    def test_keys_are_deduplicated_and_ordered(self):
        with patch.object(gemini_keys, "GEMINI_EXTRA_API_KEYS", ("k1", "k0", "k2")):
            self.assertEqual(gemini_keys.gemini_keys("k0"), ["k0", "k1", "k2"])
            self.assertEqual(gemini_keys.gemini_keys(""), ["k1", "k0", "k2"])

    def test_rotates_to_next_key_on_429(self):
        used = []

        def fake_post(url, json=None, headers=None, timeout=None):
            key = headers["x-goog-api-key"]
            used.append(key)
            return Mock(status_code=429 if key == "k0" else 200)

        with (
            patch.object(gemini_keys, "GEMINI_EXTRA_API_KEYS", ("k1",)),
            patch.object(gemini_keys.httpx, "post", side_effect=fake_post),
        ):
            response = gemini_keys.post_gemini("https://x", {}, "k0")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(used, ["k0", "k1"])

    def test_returns_last_429_when_all_keys_exhausted(self):
        with (
            patch.object(gemini_keys, "GEMINI_EXTRA_API_KEYS", ("k1",)),
            patch.object(
                gemini_keys.httpx, "post", return_value=Mock(status_code=429)
            ) as post,
        ):
            response = gemini_keys.post_gemini("https://x", {}, "k0")

        self.assertEqual(response.status_code, 429)
        self.assertEqual(post.call_count, 2)


if __name__ == "__main__":
    unittest.main()
