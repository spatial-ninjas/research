"""Network bundle loading utilities.

This module loads a GeoPackage-derived route network into the artifacts that
must stay aligned during prompting and evaluation:

- SSAL text shown to the LLM
- graph parsed from that exact SSAL text
- stable hash of the SSAL text
- source GeoPackage and layer metadata

The main entry point is load_network_bundle_from_gpkg().
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import urllib.request

from research.graph import Graph, build_graph_from_ssal
from research.ssal import gpkg_to_ssal


# These fields keep the generated SSAL usable for route weighting, street-name
# display/debugging, and later coordinate-based visualization.
DEFAULT_INCLUDE_ATTRS = [
    "length",
    "name",
    "oneway",
    "from_x",
    "from_y",
    "to_x",
    "to_y",
]


@dataclass(frozen=True)
class NetworkBundle:
    """Loaded route-network artifacts for one SSAL representation.

    The bundle is frozen so the SSAL text, graph, and hash cannot accidentally
    drift apart after loading. A different SSAL representation should produce a
    new bundle instead of mutating an existing one.
    """

    gpkg_path: Path
    ssal_text: str
    ssal_hash: str
    graph: Graph
    edges_layer: str
    nodes_layer: str


def sha256_text(text: str) -> str:
    """Return a stable SHA-256 fingerprint for UTF-8 text.

    This is used for ssal_hash so experiment results can identify the exact
    SSAL representation used in prompting and evaluation.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: str | Path) -> str:
    """Return the SHA-256 checksum of a local file.

    Files are read in chunks so this also works for larger GeoPackage files.
    This checksum is for source-file verification, not for identifying the
    generated SSAL representation.
    """
    path = Path(path)
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def load_network_bundle_from_gpkg(
    gpkg_path: str | Path,
    edges_layer: str,
    nodes_layer: str,
    include_coords: bool = True,
    include_direction: bool = False,
    include_attrs: list[str] | None = None,
) -> NetworkBundle:
    """Load SSAL text, graph, and SSAL hash from a local GeoPackage.

    The graph is intentionally built from the generated SSAL text, not directly
    from the GeoPackage. This keeps the evaluator aligned with the exact network
    representation shown to the LLM.
    """
    gpkg_path = Path(gpkg_path)

    if include_attrs is None:
        include_attrs = DEFAULT_INCLUDE_ATTRS

    ssal_text = gpkg_to_ssal(
        gpkg_path=str(gpkg_path),
        edges_layer=edges_layer,
        nodes_layer=nodes_layer,
        include_coords=include_coords,
        include_direction=include_direction,
        include_attrs=include_attrs,
    )

    graph = build_graph_from_ssal(ssal_text)

    return NetworkBundle(
        gpkg_path=gpkg_path,
        ssal_text=ssal_text,
        ssal_hash=sha256_text(ssal_text),
        graph=graph,
        edges_layer=edges_layer,
        nodes_layer=nodes_layer,
    )


def fetch_or_reuse_cached_file(
    url: str,
    cache_path: str | Path,
    expected_sha256: str | None = None,
) -> Path:
    """Fetch a file into cache, reusing existing files when valid.

    If expected_sha256 is provided, cached and downloaded files must match
    it. Invalid cached files are replaced; invalid downloads are deleted and
    reported with a clear error.
    """
    cache_path = Path(cache_path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    if cache_path.exists():
        if expected_sha256 is None:
            return cache_path

        if sha256_file(cache_path) == expected_sha256:
            return cache_path

        cache_path.unlink()

    urllib.request.urlretrieve(url, cache_path)

    if expected_sha256 is not None:
        actual = sha256_file(cache_path)
        if actual != expected_sha256:
            cache_path.unlink(missing_ok=True)
            raise ValueError(
                "Downloaded file checksum mismatch: "
                f"expected {expected_sha256}, got {actual}"
            )

    return cache_path
