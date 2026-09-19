from __future__ import annotations

import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


def safe_output_stem(path: str, fallback: str = "video") -> str:
    """Return a filesystem-safe, non-empty stem for generated artifacts."""
    stem = Path(str(path)).stem
    safe = "".join(ch for ch in stem if ch.isalnum() or ch in (" ", "-", "_")).strip()
    return safe or fallback


@contextmanager
def materialize_uploaded_video(video_file, default_suffix: str = ".mp4") -> Iterator[str]:
    """Copy an uploaded video-like object to a unique temporary path and always clean it up."""
    source_name = getattr(video_file, "name", "")
    suffix = Path(str(source_name)).suffix or default_suffix

    fd, temp_path = tempfile.mkstemp(prefix="videotopdf_", suffix=suffix)
    os.close(fd)

    try:
        if source_name and os.path.isfile(source_name):
            shutil.copyfile(source_name, temp_path)
        elif isinstance(video_file, (bytes, bytearray, memoryview)):
            with open(temp_path, "wb") as target:
                target.write(bytes(video_file))
        elif hasattr(video_file, "read"):
            with open(temp_path, "wb") as target:
                shutil.copyfileobj(video_file, target)
        else:
            raise TypeError("Unsupported uploaded video object")

        yield temp_path
    finally:
        try:
            os.remove(temp_path)
        except FileNotFoundError:
            pass
