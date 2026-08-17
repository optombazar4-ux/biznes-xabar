import unittest
from io import BytesIO
from unittest.mock import Mock, patch

from PIL import Image

from app.services import storage
from app.services.image_gen import _compress_webp


class StorageServiceTests(unittest.TestCase):
    def configured(self):
        return (
            patch.object(storage, "SUPABASE_URL", "https://project.supabase.co"),
            patch.object(storage, "SUPABASE_SECRET_KEY", "server-secret"),
            patch.object(storage, "SUPABASE_STORAGE_BUCKET", "media"),
        )

    def test_uploads_bytes_with_server_auth_and_returns_public_url(self):
        response = Mock()
        response.raise_for_status.return_value = None
        url_patch, key_patch, bucket_patch = self.configured()
        with url_patch, key_patch, bucket_patch, patch.object(
            storage.httpx, "post", return_value=response
        ) as post:
            result = storage.upload_bytes(
                "images/test cover.webp",
                b"webp-data",
                "image/webp",
            )

        self.assertEqual(
            result,
            "https://project.supabase.co/storage/v1/object/public/media/"
            "images/test%20cover.webp",
        )
        request = post.call_args
        self.assertIn("/storage/v1/object/media/images/test%20cover.webp", request.args[0])
        self.assertEqual(request.kwargs["headers"]["apikey"], "server-secret")
        self.assertEqual(request.kwargs["headers"]["x-upsert"], "true")
        self.assertNotIn("server-secret", result)

    def test_rejects_oversized_file_before_network(self):
        url_patch, key_patch, bucket_patch = self.configured()
        with (
            url_patch,
            key_patch,
            bucket_patch,
            patch.object(storage, "STORAGE_MAX_FILE_MB", 1),
            patch.object(storage.httpx, "post") as post,
        ):
            result = storage.upload_bytes(
                "audio/large.wav",
                b"0" * (1024 * 1024 + 1),
                "audio/wav",
            )

        self.assertIsNone(result)
        post.assert_not_called()

    def test_existing_public_object_uses_head(self):
        response = Mock(status_code=200)
        url_patch, key_patch, bucket_patch = self.configured()
        with url_patch, key_patch, bucket_patch, patch.object(
            storage.httpx, "head", return_value=response
        ):
            result = storage.existing_public_object_url("audio/dars.mp3")

        self.assertTrue(result.endswith("/media/audio/dars.mp3"))

    def test_rejects_parent_path(self):
        url_patch, key_patch, bucket_patch = self.configured()
        with url_patch, key_patch, bucket_patch:
            with self.assertRaises(ValueError):
                storage.public_object_url("../secret.txt")


class ImageCompressionTests(unittest.TestCase):
    def test_compresses_and_resizes_to_webp(self):
        source = BytesIO()
        Image.new("RGB", (2000, 1000), color=(20, 80, 140)).save(
            source,
            format="PNG",
        )

        compressed = _compress_webp(source.getvalue())

        with Image.open(BytesIO(compressed)) as image:
            self.assertEqual(image.format, "WEBP")
            self.assertLessEqual(max(image.size), 1600)
        self.assertLess(len(compressed), len(source.getvalue()))


if __name__ == "__main__":
    unittest.main()
