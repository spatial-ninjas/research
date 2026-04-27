"""Network bundle loading utilities."""

from __future__ import annotations

import hashlib


def sha256_text(text: str) -> str:
    """Return the SHA-256 hash of UTF-8 encoded text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
