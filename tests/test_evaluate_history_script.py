"""Tests for the offline route-history evaluation script.

These tests cover script-level wrapper behavior. The detailed route parsing,
path validation, Dijkstra comparison, and metric calculations are tested in
``research.evaluation``.
"""

import json

import pytest

from research.graph import Graph, build_graph_from_ssal
from research.network_loader import NetworkBundle
from scripts.evaluate_history import (
    evaluate_entry_file,
    evaluate_history_file,
    evaluate_route_history_entry,
    get_entry_metadata,
    get_response_text,
    get_route_context,
    load_entry,
    load_history,
)


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


SIMPLE_SSAL = """
A:
  B {1.0, Road AB, 2w}
B:
  C {1.0, Road BC, 2w}
C:
""".strip()


# ---------------------------------------------------------------------------
# Module import
# ---------------------------------------------------------------------------


def test_evaluate_history_script_can_be_imported():
    import scripts.evaluate_history

    assert scripts.evaluate_history is not None


# ---------------------------------------------------------------------------
# Single-entry JSON loading
# ---------------------------------------------------------------------------


def test_load_entry_loads_single_entry_json(tmp_path):
    entry_path = tmp_path / "entry.json"
    entry = {
        "id": "entry-1",
        "provider": "openai",
        "model": "gpt-test",
    }
    entry_path.write_text(json.dumps(entry), encoding="utf-8")

    result = load_entry(entry_path)

    assert result == entry


def test_load_entry_rejects_non_object_json(tmp_path):
    entry_path = tmp_path / "entry.json"
    entry_path.write_text(json.dumps([{"id": "entry-1"}]), encoding="utf-8")

    with pytest.raises(ValueError, match="Entry JSON must contain one object"):
        load_entry(entry_path)


# ---------------------------------------------------------------------------
# Bulk history JSON loading
# ---------------------------------------------------------------------------


def test_load_history_loads_bulk_history_json(tmp_path):
    history_path = tmp_path / "history.json"
    history = [
        {"id": "entry-1", "provider": "openai"},
        {"id": "entry-2", "provider": "google"},
    ]
    history_path.write_text(json.dumps(history), encoding="utf-8")

    result = load_history(history_path)

    assert result == history


def test_load_history_rejects_non_list_json(tmp_path):
    history_path = tmp_path / "history.json"
    history_path.write_text(json.dumps({"id": "entry-1"}), encoding="utf-8")

    with pytest.raises(ValueError, match="History JSON must contain a list"):
        load_history(history_path)


def test_load_history_rejects_non_object_entries(tmp_path):
    history_path = tmp_path / "history.json"
    history_path.write_text(json.dumps(["not an object"]), encoding="utf-8")

    with pytest.raises(ValueError, match="History JSON entries must be objects"):
        load_history(history_path)


# ---------------------------------------------------------------------------
# Response text extraction
# ---------------------------------------------------------------------------


def test_get_response_text_prefers_response_text():
    entry = {
        "response_text": "from response_text",
        "response": "from response",
        "text": "from text",
    }

    assert get_response_text(entry) == "from response_text"


def test_get_response_text_falls_back_to_response():
    entry = {
        "response": "from response",
        "text": "from text",
    }

    assert get_response_text(entry) == "from response"


def test_get_response_text_falls_back_to_text():
    entry = {"text": "from text"}

    assert get_response_text(entry) == "from text"


def test_get_response_text_returns_empty_string_when_missing():
    assert get_response_text({}) == ""


def test_get_response_text_converts_non_string_value_to_string():
    entry = {"response_text": 123}

    assert get_response_text(entry) == "123"


# ---------------------------------------------------------------------------
# Entry metadata extraction
# ---------------------------------------------------------------------------


def test_get_entry_metadata_normalizes_raw_id_to_entry_id():
    """Raw dashboard id should be preserved under the output key entry_id."""
    entry = {
        "id": "entry-1",
        "provider": "openai",
        "model": "gpt-test",
        "finish_status": "completed",
        "max_output_tokens": 4096,
    }

    assert get_entry_metadata(entry) == {
        "entry_id": "entry-1",
        "provider": "openai",
        "model": "gpt-test",
        "finish_status": "completed",
        "max_output_tokens": 4096,
    }


def test_get_entry_metadata_uses_entry_id_fallback_when_raw_id_is_missing():
    """Already-normalized entry_id should be kept when raw id is unavailable."""
    entry = {
        "entry_id": "entry-2",
        "provider": "google",
        "model": "gemini-test",
    }

    assert get_entry_metadata(entry) == {
        "entry_id": "entry-2",
        "provider": "google",
        "model": "gemini-test",
        "finish_status": None,
        "max_output_tokens": None,
    }


def test_get_entry_metadata_prefers_raw_id_over_entry_id():
    """Raw dashboard id should win if both id and entry_id are present."""
    entry = {
        "id": "raw-entry-id",
        "entry_id": "processed-entry-id",
    }

    assert get_entry_metadata(entry)["entry_id"] == "raw-entry-id"


def test_get_entry_metadata_uses_defaults_for_missing_fields():
    """Missing metadata should use stable defaults for summary grouping."""
    assert get_entry_metadata({}) == {
        "entry_id": None,
        "provider": "unknown",
        "model": "unknown",
        "finish_status": None,
        "max_output_tokens": None,
    }


# ---------------------------------------------------------------------------
# Route context extraction
# ---------------------------------------------------------------------------


def test_get_route_context_reads_origin_and_destination_fields():
    entry = {
        "origin": "A",
        "destination": "D",
    }

    assert get_route_context(entry) == {
        "origin": "A",
        "destination": "D",
    }


def test_get_route_context_converts_node_ids_to_strings():
    entry = {
        "origin": 101,
        "destination": 202,
    }

    assert get_route_context(entry) == {
        "origin": "101",
        "destination": "202",
    }


def test_get_route_context_reads_route_origin_and_route_destination_fields():
    entry = {
        "route_origin": "A",
        "route_destination": "D",
    }

    assert get_route_context(entry) == {
        "origin": "A",
        "destination": "D",
    }


def test_get_route_context_prefers_origin_destination_over_route_fields():
    entry = {
        "origin": "A",
        "destination": "D",
        "route_origin": "X",
        "route_destination": "Y",
    }

    assert get_route_context(entry) == {
        "origin": "A",
        "destination": "D",
    }


def test_get_route_context_returns_none_when_origin_is_missing():
    entry = {"destination": "D"}

    assert get_route_context(entry) is None


def test_get_route_context_returns_none_when_destination_is_missing():
    entry = {"origin": "A"}

    assert get_route_context(entry) is None


def test_get_route_context_returns_none_when_both_are_missing():
    assert get_route_context({}) is None


# ---------------------------------------------------------------------------
# Single-entry route evaluation
# ---------------------------------------------------------------------------


def test_evaluate_route_history_entry_evaluates_one_valid_entry():
    """One route-history row should be evaluated with the shared evaluator."""
    graph = build_graph_from_ssal(SIMPLE_SSAL)

    entry = {
        "id": "entry-1",
        "provider": "openai",
        "model": "gpt-test",
        "origin": "A",
        "destination": "C",
        "response_text": """
{
  "origin": "A",
  "destination": "C",
  "total_length": 2.0,
  "route": [
    {"node": "A", "edge_name": "start"},
    {"node": "B", "edge_name": "Road AB"},
    {"node": "C", "edge_name": "Road BC"}
  ],
  "status": "success"
}
""",
    }

    result = evaluate_route_history_entry(
        entry=entry,
        graph=graph,
        ssal_hash="hash123",
    )

    assert result["entry_id"] == "entry-1"
    assert result["provider"] == "openai"
    assert result["model"] == "gpt-test"
    assert result["origin"] == "A"
    assert result["destination"] == "C"
    assert result["ssal_hash"] == "hash123"

    assert result["status"] == "evaluated"
    assert result["valid_json"] is True
    assert result["valid_path"] is True
    assert result["candidate_path"] == ["A", "B", "C"]
    assert result["candidate_computed_length"] == 2.0
    assert result["ground_truth_path"] == ["A", "B", "C"]
    assert result["ground_truth_length"] == 2.0
    assert result["exact_path_match"] is True


def test_evaluate_route_history_entry_skips_missing_route_context():
    """Entries without origin/destination should be skipped before evaluation."""
    entry = {
        "id": "entry-1",
        "provider": "openai",
        "model": "gpt-test",
        "response_text": "{}",
    }

    result = evaluate_route_history_entry(
        entry=entry,
        graph=Graph(adjacency={}),
        ssal_hash="hash123",
    )

    assert result["status"] == "skipped"
    assert result["reason"] == "missing_route_context"
    assert result["entry_id"] == "entry-1"
    assert result["provider"] == "openai"
    assert result["model"] == "gpt-test"
    assert result["ssal_hash"] == "hash123"


# ---------------------------------------------------------------------------
# Entry-file route evaluation
# ---------------------------------------------------------------------------


def test_evaluate_entry_file_loads_bundle_and_evaluates_entry(
    monkeypatch,
    tmp_path,
):
    """Entry-file evaluation should load a bundle and evaluate the entry."""
    entry_path = tmp_path / "entry.json"
    entry = {
        "id": "entry-1",
        "provider": "openai",
        "model": "gpt-test",
        "origin": "A",
        "destination": "C",
        "response_text": """
{
  "origin": "A",
  "destination": "C",
  "total_length": 2.0,
  "route": [
    {"node": "A", "edge_name": "start"},
    {"node": "B", "edge_name": "Road AB"},
    {"node": "C", "edge_name": "Road BC"}
  ],
  "status": "success"
}
""",
    }
    entry_path.write_text(json.dumps(entry), encoding="utf-8")

    graph = build_graph_from_ssal(SIMPLE_SSAL)
    bundle = NetworkBundle(
        gpkg_path=tmp_path / "network.gpkg",
        ssal_text=SIMPLE_SSAL,
        ssal_hash="hash123",
        graph=graph,
        edges_layer="edges",
        nodes_layer="nodes",
    )

    captured_loader = {}

    def fake_load_network_bundle_from_gpkg(**kwargs):
        """Avoid real GeoPackage loading; return a tiny test bundle instead."""
        captured_loader.update(kwargs)
        return bundle

    # Patch only the network loader used by evaluate_entry_file().
    # The actual entry evaluation still runs through evaluate_route_history_entry().
    monkeypatch.setattr(
        "scripts.evaluate_history.load_network_bundle_from_gpkg",
        fake_load_network_bundle_from_gpkg,
    )

    result = evaluate_entry_file(
        entry_json_path=entry_path,
        gpkg_path="network.gpkg",
        edges_layer="edges",
        nodes_layer="nodes",
    )

    assert captured_loader == {
        "gpkg_path": "network.gpkg",
        "edges_layer": "edges",
        "nodes_layer": "nodes",
    }

    assert result["entry_id"] == "entry-1"
    assert result["provider"] == "openai"
    assert result["model"] == "gpt-test"
    assert result["origin"] == "A"
    assert result["destination"] == "C"
    assert result["ssal_hash"] == "hash123"

    assert result["status"] == "evaluated"
    assert result["valid_path"] is True
    assert result["candidate_path"] == ["A", "B", "C"]
    assert result["candidate_computed_length"] == 2.0
    assert result["ground_truth_length"] == 2.0


# ---------------------------------------------------------------------------
# Bulk history-file route evaluation
# ---------------------------------------------------------------------------


def test_evaluate_history_file_uses_single_entry_evaluator_for_each_entry(
    monkeypatch,
    tmp_path,
):
    """Bulk history evaluation should reuse the single-entry evaluation path."""
    history_path = tmp_path / "history.json"
    history = [
        {
            "id": "entry-1",
            "provider": "openai",
            "model": "gpt-test",
            "origin": "A",
            "destination": "C",
            "response_text": """
{
  "origin": "A",
  "destination": "C",
  "total_length": 2.0,
  "route": [
    {"node": "A", "edge_name": "start"},
    {"node": "B", "edge_name": "Road AB"},
    {"node": "C", "edge_name": "Road BC"}
  ],
  "status": "success"
}
""",
        },
        {
            "id": "entry-2",
            "provider": "google",
            "model": "gemini-test",
            "origin": "B",
            "destination": "C",
            "response_text": """
{
  "origin": "B",
  "destination": "C",
  "total_length": 1.0,
  "route": [
    {"node": "B", "edge_name": "start"},
    {"node": "C", "edge_name": "Road BC"}
  ],
  "status": "success"
}
""",
        },
    ]
    history_path.write_text(json.dumps(history), encoding="utf-8")

    graph = build_graph_from_ssal(SIMPLE_SSAL)
    bundle = NetworkBundle(
        gpkg_path=tmp_path / "network.gpkg",
        ssal_text=SIMPLE_SSAL,
        ssal_hash="hash123",
        graph=graph,
        edges_layer="edges",
        nodes_layer="nodes",
    )

    captured_loader = {}
    load_count = 0

    def fake_load_network_bundle_from_gpkg(**kwargs):
        """Avoid real GeoPackage loading; return a tiny test bundle instead."""
        nonlocal load_count
        load_count += 1
        captured_loader.update(kwargs)
        return bundle

    # Patch only the network-loading boundary. The bulk wrapper should still
    # call the real single-entry evaluator for each row.
    monkeypatch.setattr(
        "scripts.evaluate_history.load_network_bundle_from_gpkg",
        fake_load_network_bundle_from_gpkg,
    )

    rows = evaluate_history_file(
        history_json_path=history_path,
        gpkg_path="network.gpkg",
        edges_layer="edges",
        nodes_layer="nodes",
    )

    assert load_count == 1
    assert captured_loader == {
        "gpkg_path": "network.gpkg",
        "edges_layer": "edges",
        "nodes_layer": "nodes",
    }

    assert len(rows) == 2

    assert rows[0]["entry_id"] == "entry-1"
    assert rows[0]["provider"] == "openai"
    assert rows[0]["model"] == "gpt-test"
    assert rows[0]["origin"] == "A"
    assert rows[0]["destination"] == "C"
    assert rows[0]["ssal_hash"] == "hash123"
    assert rows[0]["status"] == "evaluated"
    assert rows[0]["valid_path"] is True
    assert rows[0]["candidate_path"] == ["A", "B", "C"]
    assert rows[0]["candidate_computed_length"] == 2.0

    assert rows[1]["entry_id"] == "entry-2"
    assert rows[1]["provider"] == "google"
    assert rows[1]["model"] == "gemini-test"
    assert rows[1]["origin"] == "B"
    assert rows[1]["destination"] == "C"
    assert rows[1]["ssal_hash"] == "hash123"
    assert rows[1]["status"] == "evaluated"
    assert rows[1]["valid_path"] is True
    assert rows[1]["candidate_path"] == ["B", "C"]
    assert rows[1]["candidate_computed_length"] == 1.0
