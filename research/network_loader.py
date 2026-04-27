"""Network bundle loading utilities.

This module groups the route-network artifacts that must stay aligned during
prompting and evaluation:

- SSAL text shown to the LLM
- graph parsed from that exact SSAL text
- stable hash of the SSAL text
- source GeoPackage and layer metadata

Only the hashing utilities and NetworkBundle container are implemented so
far. The GeoPackage-to-SSAL loading function is added in the next slice.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

from research.graph import Graph


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
