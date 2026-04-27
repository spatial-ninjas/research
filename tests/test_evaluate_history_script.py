"""Tests for the offline route-history evaluation CLI script.

These tests cover argument parsing and CLI wiring. Dashboard/export row
adaptation, file wrappers, summaries, and JSON output helpers are tested in
research.history_evaluation.
"""

import json

import pytest

from scripts.evaluate_history import (
    DEFAULT_EDGES_LAYER,
    DEFAULT_GPKG_PATH,
    DEFAULT_NODES_LAYER,
    main,
    parse_args,
)


# ---------------------------------------------------------------------------
# Module import
# ---------------------------------------------------------------------------


def test_evaluate_history_script_can_be_imported():
    import scripts.evaluate_history

    assert scripts.evaluate_history is not None


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------


def test_parse_args_accepts_entry_json_mode():
    """CLI should accept one-entry evaluation mode."""
    args = parse_args(
        [
            "--entry-json",
            "entry.json",
            "--gpkg-path",
            "network.gpkg",
            "--edges-layer",
            "edges",
            "--nodes-layer",
            "nodes",
            "--output",
            "result.json",
        ]
    )

    assert args.entry_json == "entry.json"
    assert args.history_json is None
    assert args.gpkg_path == "network.gpkg"
    assert args.edges_layer == "edges"
    assert args.nodes_layer == "nodes"
    assert args.output == "result.json"


def test_parse_args_accepts_history_json_mode():
    """CLI should accept bulk history-export evaluation mode."""
    args = parse_args(
        [
            "--history-json",
            "history.json",
            "--gpkg-path",
            "network.gpkg",
            "--edges-layer",
            "edges",
            "--nodes-layer",
            "nodes",
            "--output",
            "results.json",
        ]
    )

    assert args.history_json == "history.json"
    assert args.entry_json is None
    assert args.gpkg_path == "network.gpkg"
    assert args.edges_layer == "edges"
    assert args.nodes_layer == "nodes"
    assert args.output == "results.json"


def test_parse_args_requires_one_input_mode():
    """CLI should require either entry-json or history-json."""
    with pytest.raises(SystemExit):
        parse_args([])


def test_parse_args_rejects_both_entry_and_history_json():
    """CLI should reject ambiguous input mode selection."""
    with pytest.raises(SystemExit):
        parse_args(
            [
                "--entry-json",
                "entry.json",
                "--history-json",
                "history.json",
                "--gpkg-path",
                "network.gpkg",
                "--edges-layer",
                "edges",
                "--nodes-layer",
                "nodes",
            ]
        )


def test_parse_args_uses_network_defaults(monkeypatch):
    """CLI should provide local network defaults when no override is given."""
    monkeypatch.delenv("GPKG_PATH", raising=False)
    monkeypatch.delenv("EDGES_LAYER", raising=False)
    monkeypatch.delenv("NODES_LAYER", raising=False)

    args = parse_args(["--entry-json", "entry.json"])

    assert args.gpkg_path == DEFAULT_GPKG_PATH
    assert args.edges_layer == DEFAULT_EDGES_LAYER
    assert args.nodes_layer == DEFAULT_NODES_LAYER


def test_parse_args_uses_network_env_overrides(monkeypatch):
    """CLI should allow network defaults to come from environment variables."""
    monkeypatch.setenv("GPKG_PATH", "env-network.gpkg")
    monkeypatch.setenv("EDGES_LAYER", "env-edges")
    monkeypatch.setenv("NODES_LAYER", "env-nodes")

    args = parse_args(["--entry-json", "entry.json"])

    assert args.gpkg_path == "env-network.gpkg"
    assert args.edges_layer == "env-edges"
    assert args.nodes_layer == "env-nodes"


def test_parse_args_does_not_require_ors_api_key(monkeypatch):
    """CLI parsing should not depend on OpenRouteService credentials."""
    monkeypatch.delenv("ORS_API_KEY", raising=False)

    args = parse_args(
        [
            "--entry-json",
            "entry.json",
            "--gpkg-path",
            "network.gpkg",
            "--edges-layer",
            "edges",
            "--nodes-layer",
            "nodes",
        ]
    )

    assert args.entry_json == "entry.json"
    assert args.gpkg_path == "network.gpkg"


# ---------------------------------------------------------------------------
# CLI main wiring
# ---------------------------------------------------------------------------


def test_main_entry_mode_evaluates_entry_and_writes_output(monkeypatch, tmp_path):
    """Entry-mode CLI should evaluate one entry and write JSON output."""
    output_path = tmp_path / "result.json"
    captured_call = {}

    def fake_evaluate_entry_file(**kwargs):
        captured_call.update(kwargs)
        return {
            "entry_id": "entry-1",
            "status": "evaluated",
        }

    monkeypatch.setattr(
        "scripts.evaluate_history.evaluate_entry_file",
        fake_evaluate_entry_file,
    )

    exit_code = main(
        [
            "--entry-json",
            "entry.json",
            "--gpkg-path",
            "network.gpkg",
            "--edges-layer",
            "edges",
            "--nodes-layer",
            "nodes",
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert captured_call == {
        "entry_json_path": "entry.json",
        "gpkg_path": "network.gpkg",
        "edges_layer": "edges",
        "nodes_layer": "nodes",
    }

    written = json.loads(output_path.read_text(encoding="utf-8"))
    assert written == {
        "result": {
            "entry_id": "entry-1",
            "status": "evaluated",
        }
    }


def test_main_history_mode_evaluates_history_summarizes_and_writes_output(
    monkeypatch,
    tmp_path,
):
    """Bulk-mode CLI should evaluate rows, summarize them, and write JSON output."""
    output_path = tmp_path / "results.json"
    captured_call = {}

    rows = [
        {
            "entry_id": "entry-1",
            "provider": "openai",
            "model": "gpt",
            "origin": "A",
            "destination": "C",
            "status": "evaluated",
            "valid_path": True,
            "relative_length_error": 0.0,
            "declared_length_relative_error": None,
        }
    ]

    def fake_evaluate_history_file(**kwargs):
        captured_call.update(kwargs)
        return rows

    monkeypatch.setattr(
        "scripts.evaluate_history.evaluate_history_file",
        fake_evaluate_history_file,
    )

    exit_code = main(
        [
            "--history-json",
            "history.json",
            "--gpkg-path",
            "network.gpkg",
            "--edges-layer",
            "edges",
            "--nodes-layer",
            "nodes",
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert captured_call == {
        "history_json_path": "history.json",
        "gpkg_path": "network.gpkg",
        "edges_layer": "edges",
        "nodes_layer": "nodes",
    }

    written = json.loads(output_path.read_text(encoding="utf-8"))

    assert written["results"] == rows
    assert written["summary"]["total_entries"] == 1
    assert written["summary"]["evaluated_entries"] == 1
    assert written["summary"]["per_model"]["openai/gpt"]["total_entries"] == 1
    assert written["summary"]["per_route"]["A->C"]["total_entries"] == 1


def test_main_entry_mode_prints_result_when_output_is_missing(
    monkeypatch,
    capsys,
):
    """Entry-mode CLI should print JSON when no output path is provided."""
    def fake_evaluate_entry_file(**kwargs):
        return {
            "entry_id": "entry-1",
            "status": "evaluated",
        }

    monkeypatch.setattr(
        "scripts.evaluate_history.evaluate_entry_file",
        fake_evaluate_entry_file,
    )

    exit_code = main(
        [
            "--entry-json",
            "entry.json",
            "--gpkg-path",
            "network.gpkg",
            "--edges-layer",
            "edges",
            "--nodes-layer",
            "nodes",
        ]
    )

    captured = capsys.readouterr()
    written = json.loads(captured.out)

    assert exit_code == 0
    assert written == {
        "result": {
            "entry_id": "entry-1",
            "status": "evaluated",
        }
    }


def test_main_history_mode_prints_results_and_summary_when_output_is_missing(
    monkeypatch,
    capsys,
):
    """Bulk-mode CLI should print rows and summary when no output path is provided."""
    def fake_evaluate_history_file(**kwargs):
        return [
            {
                "entry_id": "entry-1",
                "provider": "openai",
                "model": "gpt",
                "origin": "A",
                "destination": "C",
                "status": "evaluated",
                "valid_path": True,
                "relative_length_error": None,
                "declared_length_relative_error": None,
            }
        ]

    monkeypatch.setattr(
        "scripts.evaluate_history.evaluate_history_file",
        fake_evaluate_history_file,
    )

    exit_code = main(
        [
            "--history-json",
            "history.json",
            "--gpkg-path",
            "network.gpkg",
            "--edges-layer",
            "edges",
            "--nodes-layer",
            "nodes",
        ]
    )

    captured = capsys.readouterr()
    written = json.loads(captured.out)

    assert exit_code == 0
    assert len(written["results"]) == 1
    assert written["summary"]["total_entries"] == 1
