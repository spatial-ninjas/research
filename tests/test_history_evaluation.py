"""Tests for offline route-history evaluation helpers.

These tests cover dashboard/export row adaptation, file wrappers, summaries,
and JSON output helpers. Core route parsing, path validation, Dijkstra, and
metric calculations are tested in research.evaluation.
"""

import json

import pytest

from research.graph import Graph, build_graph_from_ssal
from research.history_evaluation import (
    evaluate_entry_file,
    evaluate_history_file,
    evaluate_route_history_entry,
    format_results_json,
    get_entry_metadata,
    get_response_text,
    get_route_context,
    load_entry,
    load_history,
    summarize_results,
    write_results_json,
)
from research.network_loader import NetworkBundle


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
        "research.history_evaluation.load_network_bundle_from_gpkg",
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
        "research.history_evaluation.load_network_bundle_from_gpkg",
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


# ---------------------------------------------------------------------------
# Bulk result summaries
# ---------------------------------------------------------------------------


def test_summarize_results_counts_evaluated_and_skipped_entries():
    """Bulk summary should count evaluated rows, skips, and available metrics."""
    results = [
        {
            "status": "evaluated",
            "provider": "openai",
            "model": "gpt",
            "valid_path": True,
            "relative_length_error": 0.0,
            "declared_length_relative_error": 0.1,
        },
        {
            "status": "evaluated",
            "provider": "openai",
            "model": "gpt",
            "valid_path": False,
            "relative_length_error": None,
            "declared_length_relative_error": None,
        },
        {
            "status": "skipped",
            "reason": "missing_route_context",
            "provider": "google",
            "model": "gemini",
        },
    ]

    summary = summarize_results(results)

    assert summary["total_entries"] == 3
    assert summary["evaluated_entries"] == 2
    assert summary["skipped_entries"] == 1
    assert summary["skip_reasons"] == {"missing_route_context": 1}
    assert summary["valid_path_rate"] == 0.5
    assert summary["average_relative_length_error"] == 0.0
    assert summary["average_declared_length_relative_error"] == 0.1


def test_summarize_results_includes_per_model_counts():
    """Bulk summaries should include grouped provider/model metrics."""
    results = [
        {
            "status": "evaluated",
            "provider": "openai",
            "model": "gpt",
            "valid_path": True,
            "relative_length_error": 0.0,
            "declared_length_relative_error": 0.1,
        },
        {
            "status": "skipped",
            "reason": "missing_route_context",
            "provider": "openai",
            "model": "gpt",
        },
        {
            "status": "evaluated",
            "provider": "google",
            "model": "gemini",
            "valid_path": False,
            "relative_length_error": 0.5,
            "declared_length_relative_error": None,
        },
    ]

    summary = summarize_results(results)

    assert summary["per_model"] == {
        "google/gemini": {
            "total_entries": 1,
            "evaluated_entries": 1,
            "skipped_entries": 0,
            "skip_reasons": {},
            "valid_path_rate": 0.0,
            "average_relative_length_error": 0.5,
            "average_declared_length_relative_error": None,
        },
        "openai/gpt": {
            "total_entries": 2,
            "evaluated_entries": 1,
            "skipped_entries": 1,
            "skip_reasons": {"missing_route_context": 1},
            "valid_path_rate": 1.0,
            "average_relative_length_error": 0.0,
            "average_declared_length_relative_error": 0.1,
        },
    }


def test_summarize_results_handles_empty_results():
    """Empty bulk results should produce zero counts and no averages."""
    summary = summarize_results([])

    assert summary == {
        "total_entries": 0,
        "evaluated_entries": 0,
        "skipped_entries": 0,
        "skip_reasons": {},
        "valid_path_rate": None,
        "average_relative_length_error": None,
        "average_declared_length_relative_error": None,
        "per_model": {},
        "per_route": {},
    }


def test_summarize_results_ignores_missing_optional_metric_fields():
    """Missing optional metric fields should not break bulk summaries."""
    results = [
        {
            "status": "evaluated",
            "valid_path": True,
        }
    ]

    summary = summarize_results(results)

    expected_unknown_summary = {
        "total_entries": 1,
        "evaluated_entries": 1,
        "skipped_entries": 0,
        "skip_reasons": {},
        "valid_path_rate": 1.0,
        "average_relative_length_error": None,
        "average_declared_length_relative_error": None,
    }

    assert summary["total_entries"] == 1
    assert summary["evaluated_entries"] == 1
    assert summary["skipped_entries"] == 0
    assert summary["skip_reasons"] == {}
    assert summary["valid_path_rate"] == 1.0
    assert summary["average_relative_length_error"] is None
    assert summary["average_declared_length_relative_error"] is None
    assert summary["per_model"] == {
        "unknown/unknown": expected_unknown_summary,
    }
    assert summary["per_route"] == {
        "unknown->unknown": expected_unknown_summary,
    }


def test_summarize_results_counts_missing_skip_reason_as_unknown():
    """Missing skip reasons should be grouped under unknown."""
    results = [{"status": "skipped"}]

    summary = summarize_results(results)

    expected_unknown_summary = {
        "total_entries": 1,
        "evaluated_entries": 0,
        "skipped_entries": 1,
        "skip_reasons": {"unknown": 1},
        "valid_path_rate": None,
        "average_relative_length_error": None,
        "average_declared_length_relative_error": None,
    }

    assert summary["skip_reasons"] == {"unknown": 1}
    assert summary["per_model"] == {
        "unknown/unknown": expected_unknown_summary,
    }
    assert summary["per_route"] == {
        "unknown->unknown": expected_unknown_summary,
    }


def test_summarize_results_includes_per_route_counts():
    """Bulk summaries should include grouped origin/destination metrics."""
    results = [
        {
            "status": "evaluated",
            "provider": "openai",
            "model": "gpt",
            "origin": "A",
            "destination": "C",
            "valid_path": True,
            "relative_length_error": 0.0,
            "declared_length_relative_error": 0.1,
        },
        {
            "status": "evaluated",
            "provider": "google",
            "model": "gemini",
            "origin": "A",
            "destination": "C",
            "valid_path": False,
            "relative_length_error": 0.5,
            "declared_length_relative_error": None,
        },
        {
            "status": "skipped",
            "reason": "missing_route_context",
            "provider": "openai",
            "model": "gpt",
        },
    ]

    summary = summarize_results(results)

    assert summary["per_route"] == {
        "A->C": {
            "total_entries": 2,
            "evaluated_entries": 2,
            "skipped_entries": 0,
            "skip_reasons": {},
            "valid_path_rate": 0.5,
            "average_relative_length_error": 0.25,
            "average_declared_length_relative_error": 0.1,
        },
        "unknown->unknown": {
            "total_entries": 1,
            "evaluated_entries": 0,
            "skipped_entries": 1,
            "skip_reasons": {"missing_route_context": 1},
            "valid_path_rate": None,
            "average_relative_length_error": None,
            "average_declared_length_relative_error": None,
        },
    }


# ---------------------------------------------------------------------------
# JSON output writing
# ---------------------------------------------------------------------------


def test_write_results_json_writes_single_result(tmp_path):
    """Single-entry output should be wrapped under result."""
    output_path = tmp_path / "result.json"
    result = {
        "entry_id": "entry-1",
        "status": "evaluated",
        "valid_path": True,
    }

    write_results_json(output_path, result=result)

    written = json.loads(output_path.read_text(encoding="utf-8"))

    assert written == {
        "result": result,
    }


def test_write_results_json_writes_summary_and_results(tmp_path):
    """Bulk output should include summary and row-level results."""
    output_path = tmp_path / "results.json"
    results = [
        {
            "entry_id": "entry-1",
            "status": "evaluated",
        }
    ]
    summary = {
        "total_entries": 1,
        "evaluated_entries": 1,
        "skipped_entries": 0,
        "skip_reasons": {},
        "valid_path_rate": 1.0,
        "average_relative_length_error": 0.0,
        "average_declared_length_relative_error": None,
        "per_model": {
            "openai/gpt": {
                "total_entries": 1,
                "evaluated_entries": 1,
                "skipped_entries": 0,
                "skip_reasons": {},
                "valid_path_rate": 1.0,
                "average_relative_length_error": 0.0,
                "average_declared_length_relative_error": None,
            }
        },
        "per_route": {
            "A->C": {
                "total_entries": 1,
                "evaluated_entries": 1,
                "skipped_entries": 0,
                "skip_reasons": {},
                "valid_path_rate": 1.0,
                "average_relative_length_error": 0.0,
                "average_declared_length_relative_error": None,
            }
        },
    }

    write_results_json(output_path, results=results, summary=summary)

    written = json.loads(output_path.read_text(encoding="utf-8"))

    assert written == {
        "summary": summary,
        "results": results,
    }


def test_write_results_json_creates_parent_directories(tmp_path):
    """Output writing should create missing parent directories."""
    output_path = tmp_path / "nested" / "outputs" / "result.json"
    result = {"status": "evaluated"}

    write_results_json(output_path, result=result)

    assert output_path.exists()


def test_write_results_json_rejects_missing_payload(tmp_path):
    """Output writing should require either single or bulk payload data."""
    output_path = tmp_path / "result.json"

    with pytest.raises(ValueError, match="exactly one output mode"):
        write_results_json(output_path)


def test_write_results_json_rejects_mixed_single_and_bulk_payloads(tmp_path):
    """Output writing should not mix single-entry and bulk payloads."""
    output_path = tmp_path / "result.json"

    with pytest.raises(ValueError, match="exactly one output mode"):
        write_results_json(
            output_path,
            result={"status": "evaluated"},
            results=[{"status": "evaluated"}],
            summary={"total_entries": 1},
        )


def test_write_results_json_rejects_incomplete_bulk_payload(tmp_path):
    """Bulk output should include both results and summary."""
    output_path = tmp_path / "results.json"

    with pytest.raises(ValueError, match="bulk output requires results and summary"):
        write_results_json(
            output_path,
            results=[{"status": "evaluated"}],
        )


def test_format_results_json_formats_single_result():
    result = {
        "entry_id": "entry-1",
        "status": "evaluated",
    }

    text = format_results_json(result=result)
    parsed = json.loads(text)

    assert parsed == {
        "result": result,
    }


def test_format_results_json_formats_bulk_results_and_summary():
    results = [{"entry_id": "entry-1", "status": "evaluated"}]
    summary = {
        "total_entries": 1,
        "evaluated_entries": 1,
        "skipped_entries": 0,
        "skip_reasons": {},
        "valid_path_rate": 1.0,
        "average_relative_length_error": None,
        "average_declared_length_relative_error": None,
        "per_model": {},
        "per_route": {},
    }

    text = format_results_json(results=results, summary=summary)
    parsed = json.loads(text)

    assert parsed == {
        "summary": summary,
        "results": results,
    }
