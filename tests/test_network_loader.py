"""Tests for network loading utilities."""

import pytest
import hashlib

from research.network_loader import sha256_file, sha256_text


def test_network_loader_module_can_be_imported():
    import research.network_loader

    assert research.network_loader is not None


def test_sha256_text_matches_known_sha256_value():
    expected = hashlib.sha256("abc".encode("utf-8")).hexdigest()

    assert sha256_text("abc") == expected


def test_sha256_text_same_text_returns_same_hash():
    assert sha256_text("same SSAL") == sha256_text("same SSAL")


def test_sha256_text_different_text_returns_different_hashes():
    assert sha256_text("A:") != sha256_text("B:")


def test_sha256_text_hashes_unicode_with_utf8_encoding():
    text = "Helsinki → Otaniemi"
    expected = hashlib.sha256(text.encode("utf-8")).hexdigest()

    assert sha256_text(text) == expected


def test_sha256_file_matches_known_sha256_value(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_bytes(b"abc")

    expected = hashlib.sha256(b"abc").hexdigest()

    assert sha256_file(path) == expected


def test_sha256_file_changes_when_file_contents_change(tmp_path):
    path = tmp_path / "sample.txt"

    path.write_bytes(b"abc")
    first = sha256_file(path)

    path.write_bytes(b"abcd")
    second = sha256_file(path)

    assert first != second


def test_sha256_file_raises_for_missing_file(tmp_path):
    missing = tmp_path / "missing.gpkg"

    with pytest.raises(FileNotFoundError):
        sha256_file(missing)
