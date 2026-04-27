"""Tests for network bundle loading utilities.

This module currently covers the first small slices of ``research.network_loader``:

- module import
- SSAL text hashing with ``sha256_text()``
- local file hashing with ``sha256_file()``
- ``NetworkBundle`` storage and immutability

GeoPackage-to-SSAL loading tests should be added later once
``load_network_bundle_from_gpkg()`` is implemented.
"""

import hashlib
from pathlib import Path

import pytest

from research.graph import Graph
from research.network_loader import NetworkBundle, sha256_file, sha256_text


# ---------------------------------------------------------------------------
# Module import
# ---------------------------------------------------------------------------


def test_network_loader_module_can_be_imported():
    import research.network_loader

    assert research.network_loader is not None


# ---------------------------------------------------------------------------
# Text hashing
# ---------------------------------------------------------------------------


def test_sha256_text_matches_known_sha256_value():
    """Text hashing should match Python's SHA-256 implementation."""
    expected = hashlib.sha256("abc".encode("utf-8")).hexdigest()

    assert sha256_text("abc") == expected


def test_sha256_text_same_text_returns_same_hash():
    """Identical SSAL text should produce a stable identifier."""
    assert sha256_text("same SSAL") == sha256_text("same SSAL")


def test_sha256_text_different_text_returns_different_hashes():
    """Different SSAL text should produce different identifiers."""
    assert sha256_text("A:") != sha256_text("B:")


def test_sha256_text_hashes_unicode_with_utf8_encoding():
    """Unicode text should be hashed using explicit UTF-8 encoding."""
    text = "Helsinki → Otaniemi"
    expected = hashlib.sha256(text.encode("utf-8")).hexdigest()

    assert sha256_text(text) == expected


# ---------------------------------------------------------------------------
# File hashing
# ---------------------------------------------------------------------------


def test_sha256_file_matches_known_sha256_value(tmp_path):
    """File hashing should match SHA-256 over the file bytes."""
    path = tmp_path / "sample.txt"
    path.write_bytes(b"abc")

    expected = hashlib.sha256(b"abc").hexdigest()

    assert sha256_file(path) == expected


def test_sha256_file_changes_when_file_contents_change(tmp_path):
    """Changing file bytes should change the checksum."""
    path = tmp_path / "sample.txt"

    path.write_bytes(b"abc")
    first = sha256_file(path)

    path.write_bytes(b"abcd")
    second = sha256_file(path)

    assert first != second


def test_sha256_file_raises_for_missing_file(tmp_path):
    """Missing files should fail clearly instead of returning a fake checksum."""
    missing = tmp_path / "missing.gpkg"

    with pytest.raises(FileNotFoundError):
        sha256_file(missing)


# ---------------------------------------------------------------------------
# NetworkBundle
# ---------------------------------------------------------------------------


def test_network_bundle_stores_network_artifacts():
    """NetworkBundle should keep all artifacts needed for route evaluation."""
    graph = Graph(adjacency={})

    bundle = NetworkBundle(
        gpkg_path=Path("network.gpkg"),
        ssal_text="A:",
        ssal_hash="dummy-hash",
        graph=graph,
        edges_layer="edges",
        nodes_layer="nodes",
    )

    assert bundle.gpkg_path == Path("network.gpkg")
    assert bundle.ssal_text == "A:"
    assert bundle.ssal_hash == "dummy-hash"
    assert bundle.graph is graph
    assert bundle.edges_layer == "edges"
    assert bundle.nodes_layer == "nodes"


def test_network_bundle_is_frozen():
    """Loaded network artifacts should not accidentally drift after creation."""
    bundle = NetworkBundle(
        gpkg_path=Path("network.gpkg"),
        ssal_text="A:",
        ssal_hash="dummy-hash",
        graph=Graph(adjacency={}),
        edges_layer="edges",
        nodes_layer="nodes",
    )

    with pytest.raises(Exception):
        bundle.ssal_hash = "changed"  # type: ignore[misc]
