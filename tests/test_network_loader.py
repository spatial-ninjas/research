"""Tests for network bundle loading utilities.

This module covers the reusable network loading pieces in
research.network_loader:

- module import
- SSAL text hashing with sha256_text()
- local file hashing with sha256_file()
- NetworkBundle storage and immutability
- default SSAL loading options
- local GeoPackage bundle loading with mocked SSAL generation
- optional cached file loading and checksum verification
- optional real-data integration loading when a GeoPackage artifact is available
"""

import hashlib
from pathlib import Path

import pytest

from research.graph import Graph
from research.network_loader import (
    DEFAULT_INCLUDE_ATTRS,
    NetworkBundle,
    fetch_or_reuse_cached_file,
    load_network_bundle_from_gpkg,
    sha256_file,
    sha256_text,
)


MOCK_SSAL = """
A:
  B {1.0, Road AB, 2w}
B:
  C {2.0, Road BC, 1w}
C:
""".strip()


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


# ---------------------------------------------------------------------------
# Default SSAL loading options
# ---------------------------------------------------------------------------


def test_default_include_attrs_contains_routing_and_debug_fields():
    """Default SSAL fields should support routing, debugging, and display."""
    assert DEFAULT_INCLUDE_ATTRS == [
        "length",
        "name",
        "oneway",
        "from_x",
        "from_y",
        "to_x",
        "to_y",
    ]


# ---------------------------------------------------------------------------
# Local GeoPackage bundle loading
# ---------------------------------------------------------------------------


def test_load_network_bundle_from_gpkg_returns_complete_bundle(
    monkeypatch,
    tmp_path,
):
    """Local loader should return SSAL, graph, hash, path, and layer metadata."""
    gpkg_path = tmp_path / "network.gpkg"

    def fake_gpkg_to_ssal(**kwargs):
        return MOCK_SSAL

    monkeypatch.setattr(
        "research.network_loader.gpkg_to_ssal",
        fake_gpkg_to_ssal,
    )

    bundle = load_network_bundle_from_gpkg(
        gpkg_path=gpkg_path,
        edges_layer="edges",
        nodes_layer="nodes",
    )

    assert isinstance(bundle, NetworkBundle)
    assert bundle.gpkg_path == gpkg_path
    assert bundle.edges_layer == "edges"
    assert bundle.nodes_layer == "nodes"
    assert bundle.ssal_text == MOCK_SSAL
    assert bundle.ssal_hash == sha256_text(MOCK_SSAL)
    assert bundle.graph.has_edge("A", "B")
    assert bundle.graph.has_edge("B", "C")


def test_load_network_bundle_from_gpkg_passes_default_options(
    monkeypatch,
    tmp_path,
):
    """Default loader options should be passed through to SSAL generation."""
    captured = {}

    def fake_gpkg_to_ssal(**kwargs):
        captured.update(kwargs)
        return MOCK_SSAL

    monkeypatch.setattr(
        "research.network_loader.gpkg_to_ssal",
        fake_gpkg_to_ssal,
    )

    gpkg_path = tmp_path / "network.gpkg"

    load_network_bundle_from_gpkg(
        gpkg_path=gpkg_path,
        edges_layer="edges",
        nodes_layer="nodes",
    )

    assert captured == {
        "gpkg_path": str(gpkg_path),
        "edges_layer": "edges",
        "nodes_layer": "nodes",
        "include_coords": True,
        "include_direction": False,
        "include_attrs": DEFAULT_INCLUDE_ATTRS,
    }


def test_load_network_bundle_from_gpkg_passes_custom_options(
    monkeypatch,
    tmp_path,
):
    """Custom SSAL options should override loader defaults."""
    captured = {}

    def fake_gpkg_to_ssal(**kwargs):
        captured.update(kwargs)
        return MOCK_SSAL

    monkeypatch.setattr(
        "research.network_loader.gpkg_to_ssal",
        fake_gpkg_to_ssal,
    )

    gpkg_path = tmp_path / "network.gpkg"
    include_attrs = ["length", "name", "dir"]

    load_network_bundle_from_gpkg(
        gpkg_path=gpkg_path,
        edges_layer="custom_edges",
        nodes_layer="custom_nodes",
        include_coords=False,
        include_direction=True,
        include_attrs=include_attrs,
    )

    assert captured == {
        "gpkg_path": str(gpkg_path),
        "edges_layer": "custom_edges",
        "nodes_layer": "custom_nodes",
        "include_coords": False,
        "include_direction": True,
        "include_attrs": include_attrs,
    }


def test_load_network_bundle_from_gpkg_builds_graph_from_generated_ssal(
    monkeypatch,
    tmp_path,
):
    """The bundle graph should be parsed from the generated SSAL text."""
    generated_ssal = """
X:
  Y {7.5, Test Road, 2w}
Y:
""".strip()

    def fake_gpkg_to_ssal(**kwargs):
        return generated_ssal

    monkeypatch.setattr(
        "research.network_loader.gpkg_to_ssal",
        fake_gpkg_to_ssal,
    )

    bundle = load_network_bundle_from_gpkg(
        gpkg_path=tmp_path / "network.gpkg",
        edges_layer="edges",
        nodes_layer="nodes",
    )

    assert bundle.ssal_text == generated_ssal
    assert bundle.ssal_hash == sha256_text(generated_ssal)
    assert bundle.graph.has_node("X")
    assert bundle.graph.has_node("Y")
    assert bundle.graph.has_edge("X", "Y")
    assert bundle.graph.path_length(["X", "Y"]) == 7.5


# ---------------------------------------------------------------------------
# Cached URL file loading
# ---------------------------------------------------------------------------


def test_fetch_or_reuse_cached_file_reuses_existing_file_without_checksum(tmp_path):
    """Existing cached files should be reused when no checksum is required."""
    cache_path = tmp_path / "cache" / "network.gpkg"
    cache_path.parent.mkdir()
    cache_path.write_bytes(b"cached")

    result = fetch_or_reuse_cached_file(
        url="https://example.com/network.gpkg",
        cache_path=cache_path,
    )

    assert result == cache_path
    assert cache_path.read_bytes() == b"cached"


def test_fetch_or_reuse_cached_file_reuses_existing_file_when_checksum_matches(
    tmp_path,
):
    """Cached files should be reused when their checksum matches."""
    cache_path = tmp_path / "cache" / "network.gpkg"
    cache_path.parent.mkdir()
    cache_path.write_bytes(b"cached")

    expected = sha256_file(cache_path)

    result = fetch_or_reuse_cached_file(
        url="https://example.com/network.gpkg",
        cache_path=cache_path,
        expected_sha256=expected,
    )

    assert result == cache_path
    assert cache_path.read_bytes() == b"cached"


def test_fetch_or_reuse_cached_file_downloads_when_missing(monkeypatch, tmp_path):
    """Missing cached files should be downloaded into the requested path."""
    cache_path = tmp_path / "cache" / "network.gpkg"

    def fake_urlretrieve(url, filename):
        Path(filename).write_bytes(b"downloaded")
        return filename, None

    monkeypatch.setattr(
        "research.network_loader.urllib.request.urlretrieve",
        fake_urlretrieve,
    )

    result = fetch_or_reuse_cached_file(
        url="https://example.com/network.gpkg",
        cache_path=cache_path,
    )

    assert result == cache_path
    assert cache_path.read_bytes() == b"downloaded"


def test_fetch_or_reuse_cached_file_creates_parent_directory(
    monkeypatch,
    tmp_path,
):
    """The cache loader should create missing parent directories."""
    cache_path = tmp_path / "missing" / "nested" / "network.gpkg"

    def fake_urlretrieve(url, filename):
        Path(filename).write_bytes(b"downloaded")
        return filename, None

    monkeypatch.setattr(
        "research.network_loader.urllib.request.urlretrieve",
        fake_urlretrieve,
    )

    fetch_or_reuse_cached_file(
        url="https://example.com/network.gpkg",
        cache_path=cache_path,
    )

    assert cache_path.exists()
    assert cache_path.parent.exists()


def test_fetch_or_reuse_cached_file_refetches_when_cached_checksum_mismatches(
    monkeypatch,
    tmp_path,
):
    """A stale cached file should be replaced when checksum verification fails."""
    cache_path = tmp_path / "cache" / "network.gpkg"
    cache_path.parent.mkdir()
    cache_path.write_bytes(b"old bad cached file")

    expected_downloaded = b"downloaded"
    expected_hash = hashlib.sha256(expected_downloaded).hexdigest()

    def fake_urlretrieve(url, filename):
        Path(filename).write_bytes(expected_downloaded)
        return filename, None

    monkeypatch.setattr(
        "research.network_loader.urllib.request.urlretrieve",
        fake_urlretrieve,
    )

    result = fetch_or_reuse_cached_file(
        url="https://example.com/network.gpkg",
        cache_path=cache_path,
        expected_sha256=expected_hash,
    )

    assert result == cache_path
    assert cache_path.read_bytes() == expected_downloaded


def test_fetch_or_reuse_cached_file_deletes_download_and_raises_on_checksum_mismatch(
    monkeypatch,
    tmp_path,
):
    """Invalid downloads should not remain in the cache."""
    cache_path = tmp_path / "cache" / "network.gpkg"

    def fake_urlretrieve(url, filename):
        Path(filename).write_bytes(b"bad download")
        return filename, None

    monkeypatch.setattr(
        "research.network_loader.urllib.request.urlretrieve",
        fake_urlretrieve,
    )

    with pytest.raises(ValueError, match="checksum mismatch"):
        fetch_or_reuse_cached_file(
            url="https://example.com/network.gpkg",
            cache_path=cache_path,
            expected_sha256="not-the-real-hash",
        )

    assert not cache_path.exists()


# ---------------------------------------------------------------------------
# Real-data integration
# ---------------------------------------------------------------------------


REAL_GPKG_PATH = Path(
    "data/raw/routing_networks/osm_southern_helsinki_slimmed_cropped.gpkg"
)

REAL_EDGES_LAYER = "slimmed_cropped_edges"
REAL_NODES_LAYER = "slimmed_cropped_nodes"


@pytest.mark.integration
def test_load_network_bundle_from_real_gpkg_if_available():
    """A real versioned GeoPackage should load into a usable network bundle."""
    if not REAL_GPKG_PATH.exists():
        pytest.skip(f"GeoPackage not found: {REAL_GPKG_PATH}")

    bundle = load_network_bundle_from_gpkg(
        gpkg_path=REAL_GPKG_PATH,
        edges_layer=REAL_EDGES_LAYER,
        nodes_layer=REAL_NODES_LAYER,
    )

    assert bundle.gpkg_path == REAL_GPKG_PATH
    assert bundle.edges_layer == REAL_EDGES_LAYER
    assert bundle.nodes_layer == REAL_NODES_LAYER
    assert bundle.ssal_text
    assert bundle.ssal_hash == sha256_text(bundle.ssal_text)
    assert len(bundle.graph.nodes()) > 0
