import io
import os
import tempfile
import unittest

from pipeline_utils import materialize_uploaded_video, safe_output_stem


class SafeOutputStemTests(unittest.TestCase):
    def test_preserves_expected_characters(self):
        self.assertEqual(safe_output_stem("/tmp/My demo-01_test.mp4"), "My demo-01_test")

    def test_removes_problematic_characters(self):
        self.assertEqual(safe_output_stem("/tmp/a:b?c*.mp4"), "abc")

    def test_never_returns_empty_name(self):
        self.assertEqual(safe_output_stem("/tmp/....mp4"), "video")


class MaterializeUploadedVideoTests(unittest.TestCase):
    def test_bytes_are_materialized_and_cleaned_up(self):
        with materialize_uploaded_video(b"video-bytes") as path:
            self.assertTrue(os.path.exists(path))
            with open(path, "rb") as handle:
                self.assertEqual(handle.read(), b"video-bytes")
        self.assertFalse(os.path.exists(path))

    def test_file_like_object_is_materialized_and_cleaned_up(self):
        upload = io.BytesIO(b"stream-data")
        with materialize_uploaded_video(upload) as path:
            self.assertTrue(os.path.exists(path))
            with open(path, "rb") as handle:
                self.assertEqual(handle.read(), b"stream-data")
        self.assertFalse(os.path.exists(path))

    def test_named_source_keeps_suffix_and_is_cleaned_up(self):
        with tempfile.NamedTemporaryFile(suffix=".mov", delete=False) as source:
            source.write(b"named-source")
            source_path = source.name

        class Upload:
            name = source_path

        try:
            with materialize_uploaded_video(Upload()) as path:
                self.assertTrue(path.endswith(".mov"))
                self.assertTrue(os.path.exists(path))
                with open(path, "rb") as handle:
                    self.assertEqual(handle.read(), b"named-source")
            self.assertFalse(os.path.exists(path))
        finally:
            os.remove(source_path)


if __name__ == "__main__":
    unittest.main()
