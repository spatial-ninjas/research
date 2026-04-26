"""Tests for route-output parsing and evaluation utilities.

This module starts with JSON extraction tests for ``clean_json``. Later tests
should cover path extraction, candidate validation, route comparison metrics,
and top-level route-response evaluation.
"""

import pytest

from research.evaluation import (
    clean_json,
    extract_declared_length,
    extract_path,
    validate_candidate_path,
)
from research.graph import build_graph_from_ssal


SSAL = """
A:
  B {1.0, Road AB, 2w}
  C {5.0, Road AC, 1w}
B:
  C {1.0, Road BC, 2w}
  D {4.0, Road BD, 1w}
C:
  D {1.0, Road CD, 1w}
D:
E:
""".strip()


@pytest.fixture
def graph():
    return build_graph_from_ssal(SSAL)


# ---------------------------------------------------------------------------
# JSON extraction
# ---------------------------------------------------------------------------


def test_clean_json_extracts_plain_json_object():
    """A valid JSON object should be returned unchanged."""
    text = '{"status": "success"}'

    assert clean_json(text) == '{"status": "success"}'


def test_clean_json_extracts_json_from_surrounding_text():
    """Historical or imperfect model outputs may include text around the JSON."""
    text = 'Here is the route: {"status": "success", "total_length": 3.0} Done.'

    assert clean_json(text) == '{"status": "success", "total_length": 3.0}'


def test_clean_json_extracts_json_from_fenced_json_block():
    """The evaluator should accept JSON fenced as a markdown json block."""
    text = """
```json
{"status": "success", "origin": "A", "destination": "D"}
```
""".strip()

    assert clean_json(text) == '{"status": "success", "origin": "A", "destination": "D"}'


def test_clean_json_extracts_json_from_generic_fenced_block():
    """Some models use a generic markdown code block instead of ```json."""
    text = """
```
{"status": "success", "origin": "A", "destination": "D"}
```
""".strip()

    assert clean_json(text) == '{"status": "success", "origin": "A", "destination": "D"}'


def test_clean_json_extracts_multiline_json_from_fenced_block():
    """Multiline JSON should be preserved so json.loads can parse it later."""
    text = """
```json
{
  "origin": "A",
  "destination": "D",
  "total_length": 3.0,
  "status": "success"
}
```
""".strip()

    expected = """{
  "origin": "A",
  "destination": "D",
  "total_length": 3.0,
  "status": "success"
}"""

    assert clean_json(text) == expected


def test_clean_json_extracts_json_from_four_backtick_fenced_json_block():
    """Some model outputs may use four-backtick json fences."""
    text = """
````json
{"status": "success", "origin": "A", "destination": "D"}
````
""".strip()

    assert clean_json(text) == '{"status": "success", "origin": "A", "destination": "D"}'


def test_clean_json_extracts_json_from_four_backtick_generic_fenced_block():
    """Generic fences may also use more than three backticks."""
    text = """
````
{"status": "success", "origin": "A", "destination": "D"}
````
""".strip()

    assert clean_json(text) == '{"status": "success", "origin": "A", "destination": "D"}'


def test_clean_json_extracts_json_when_closing_fence_is_shorter():
    """LLM markdown fences are sometimes inconsistent in length."""
    text = """
````json
{"status": "success"}
```
""".strip()

    assert clean_json(text) == '{"status": "success"}'


def test_clean_json_extracts_json_when_closing_fence_is_longer():
    """LLM markdown fences are sometimes inconsistent in length."""
    text = """
```json
{"status": "success"}
````
""".strip()

    assert clean_json(text) == '{"status": "success"}'


def test_clean_json_prefers_fenced_json_when_text_contains_other_braces():
    """A fenced block should avoid accidentally capturing unrelated braces."""
    text = """
Some explanation with {not json}.

```json
{"status": "success"}
```
""".strip()

    assert clean_json(text) == '{"status": "success"}'


def test_clean_json_returns_none_when_no_json_object_exists():
    """Responses without any JSON object should be skipped later."""
    assert clean_json("No route found.") is None


def test_clean_json_returns_none_for_empty_string():
    """Empty model output should not crash JSON extraction."""
    assert clean_json("") is None


def test_clean_json_returns_none_for_none_input():
    """Defensive behavior: non-string empty input should return None."""
    assert clean_json(None) is None  # type: ignore[arg-type]


def test_clean_json_returns_none_for_non_string_input():
    """Defensive behavior: non-string input should return None."""
    assert clean_json({"status": "success"}) is None  # type: ignore[arg-type]


def test_clean_json_extracts_invalid_json_text_for_later_json_decode_error():
    """clean_json only extracts object-looking text; json.loads validates later."""
    text = "{not valid json}"

    assert clean_json(text) == "{not valid json}"


# ---------------------------------------------------------------------------
# Path extraction
# ---------------------------------------------------------------------------


def test_extract_path_from_primary_route_node_schema():
    """The primary LLM contract uses route[*].node."""
    route_json = {
        "origin": "A",
        "destination": "D",
        "total_length": 3.0,
        "route": [
            {"node": "A", "edge_name": "start"},
            {"node": "B", "edge_name": "Road AB"},
            {"node": "C", "edge_name": "Road BC"},
            {"node": "D", "edge_name": "Road CD"},
        ],
        "status": "success",
    }

    assert extract_path(route_json) == ["A", "B", "C", "D"]


def test_extract_path_ignores_edge_name_for_path_validity():
    """Only node IDs should define the path; edge_name is display/debug metadata."""
    route_json = {
        "route": [
            {"node": "A", "edge_name": "wrong street name"},
            {"node": "B", "edge_name": "also wrong"},
            {"node": "D", "edge_name": "not used for validation"},
        ]
    }

    assert extract_path(route_json) == ["A", "B", "D"]


def test_extract_path_converts_node_ids_to_strings():
    """Real SSAL node IDs are strings, so numeric-looking values should normalize."""
    route_json = {
        "route": [
            {"node": 1011021999, "edge_name": "start"},
            {"node": 1011022077, "edge_name": "Road"},
            {"node": 250658336, "edge_name": "Road"},
        ]
    }

    assert extract_path(route_json) == [
        "1011021999",
        "1011022077",
        "250658336",
    ]


def test_extract_path_ignores_route_entries_without_node():
    """Malformed route entries should be skipped instead of crashing extraction."""
    route_json = {
        "route": [
            {"node": "A", "edge_name": "start"},
            {"edge_name": "missing node"},
            {"node": "B", "edge_name": "Road AB"},
        ]
    }

    assert extract_path(route_json) == ["A", "B"]


def test_extract_path_returns_empty_path_when_route_is_missing():
    """Missing route means no candidate path was provided."""
    assert extract_path({}) == []


def test_extract_path_returns_empty_path_when_route_is_not_a_list():
    """Non-list route values should not crash extraction."""
    route_json = {
        "route": {"node": "A"},
    }

    assert extract_path(route_json) == []


def test_extract_path_falls_back_to_path_field_when_route_is_missing():
    """Fallback path support is useful for older/manual outputs."""
    route_json = {
        "path": [
            {"node": "A"},
            {"node": "B"},
            {"node": "D"},
        ]
    }

    assert extract_path(route_json) == ["A", "B", "D"]


def test_extract_path_prefers_route_over_fallback_path():
    """The current prompt contract should take priority over legacy path."""
    route_json = {
        "route": [
            {"node": "A"},
            {"node": "B"},
            {"node": "D"},
        ],
        "path": [
            {"node": "A"},
            {"node": "C"},
            {"node": "D"},
        ],
    }

    assert extract_path(route_json) == ["A", "B", "D"]


def test_extract_path_supports_fallback_path_entries_as_strings():
    """Fallback path may be a simple list of node IDs."""
    route_json = {
        "path": ["A", "B", "D"],
    }

    assert extract_path(route_json) == ["A", "B", "D"]


def test_extract_path_supports_fallback_path_dict_node_id():
    """Fallback dictionary entries may use node_id."""
    route_json = {
        "path": [
            {"node_id": "A"},
            {"node_id": "B"},
            {"node_id": "D"},
        ]
    }

    assert extract_path(route_json) == ["A", "B", "D"]


def test_extract_path_supports_fallback_path_dict_id():
    """Fallback dictionary entries may use id."""
    route_json = {
        "path": [
            {"id": "A"},
            {"id": "B"},
            {"id": "D"},
        ]
    }

    assert extract_path(route_json) == ["A", "B", "D"]


def test_extract_path_ignores_unsupported_path_entries():
    """Unsupported entries should be ignored instead of causing extraction failure."""
    route_json = {
        "route": [
            {"node": "A"},
            123,
            None,
            ["B"],
            {"unknown": "C"},
            {"node": "D"},
        ]
    }

    assert extract_path(route_json) == ["A", "D"]


def test_extract_path_allows_route_entries_as_strings_for_compatibility():
    """String route entries are not the primary contract, but are safe to support."""
    route_json = {
        "route": ["A", "B", "D"],
    }

    assert extract_path(route_json) == ["A", "B", "D"]


# ---------------------------------------------------------------------------
# Declared length extraction
# ---------------------------------------------------------------------------


def test_extract_declared_length_from_numeric_total_length():
    """Numeric total_length should be returned as a float."""
    route_json = {
        "total_length": 3.5,
    }

    assert extract_declared_length(route_json) == 3.5


def test_extract_declared_length_from_integer_total_length():
    """Integer total_length should still normalize to float."""
    route_json = {
        "total_length": 3,
    }

    assert extract_declared_length(route_json) == 3.0


def test_extract_declared_length_from_numeric_string_total_length():
    """String total_length is accepted because LLMs may quote numbers."""
    route_json = {
        "total_length": "3.5",
    }

    assert extract_declared_length(route_json) == 3.5


def test_extract_declared_length_from_numeric_string_with_whitespace():
    """Whitespace around a numeric string should not prevent parsing."""
    route_json = {
        "total_length": "  3.5  ",
    }

    assert extract_declared_length(route_json) == 3.5


def test_extract_declared_length_returns_none_when_total_length_is_missing():
    """Missing total_length means the model did not declare a route length."""
    route_json = {}

    assert extract_declared_length(route_json) is None


def test_extract_declared_length_returns_none_when_total_length_is_none():
    """Explicit null total_length should be treated as missing."""
    route_json = {
        "total_length": None,
    }

    assert extract_declared_length(route_json) is None


def test_extract_declared_length_returns_none_for_non_numeric_string():
    """Non-numeric total_length should not crash evaluation."""
    route_json = {
        "total_length": "unknown",
    }

    assert extract_declared_length(route_json) is None


def test_extract_declared_length_returns_none_for_list_value():
    """Unexpected structured values should not crash evaluation."""
    route_json = {
        "total_length": [3.5],
    }

    assert extract_declared_length(route_json) is None


def test_extract_declared_length_returns_none_for_dict_value():
    """Unexpected object values should not crash evaluation."""
    route_json = {
        "total_length": {"value": 3.5},
    }

    assert extract_declared_length(route_json) is None


def test_extract_declared_length_allows_zero_length():
    """Zero is valid for origin == destination cases."""
    route_json = {
        "total_length": 0,
    }

    assert extract_declared_length(route_json) == 0.0


def test_extract_declared_length_allows_negative_length_for_later_validation():
    """Parsing is separate from deciding whether a declared length is sensible."""
    route_json = {
        "total_length": -1.0,
    }

    assert extract_declared_length(route_json) == -1.0


# ---------------------------------------------------------------------------
# Candidate path validation
# ---------------------------------------------------------------------------


def test_validate_candidate_path_accepts_valid_shortest_path(graph):
    """A valid path should pass when all nodes and directed edges exist."""
    result = validate_candidate_path(
        graph=graph,
        path=["A", "B", "C", "D"],
        origin="A",
        destination="D",
    )

    assert result == {
        "valid": True,
        "errors": [],
        "unknown_nodes": [],
        "missing_edges": [],
        "computed_length": 3.0,
    }


def test_validate_candidate_path_accepts_valid_but_non_shortest_path(graph):
    """Validation checks path legality, not whether the path is shortest."""
    result = validate_candidate_path(
        graph=graph,
        path=["A", "B", "D"],
        origin="A",
        destination="D",
    )

    assert result == {
        "valid": True,
        "errors": [],
        "unknown_nodes": [],
        "missing_edges": [],
        "computed_length": 5.0,
    }


def test_validate_candidate_path_rejects_empty_path(graph):
    """An empty candidate route gives no usable route to evaluate."""
    result = validate_candidate_path(
        graph=graph,
        path=[],
        origin="A",
        destination="D",
    )

    assert result["valid"] is False
    assert result["errors"] == ["empty_path"]
    assert result["unknown_nodes"] == []
    assert result["missing_edges"] == []
    assert result["computed_length"] is None


def test_validate_candidate_path_rejects_wrong_origin(graph):
    """The candidate path must start at the requested origin."""
    result = validate_candidate_path(
        graph=graph,
        path=["B", "C", "D"],
        origin="A",
        destination="D",
    )

    assert result["valid"] is False
    assert "wrong_origin" in result["errors"]
    assert result["computed_length"] is None


def test_validate_candidate_path_rejects_wrong_destination(graph):
    """The candidate path must end at the requested destination."""
    result = validate_candidate_path(
        graph=graph,
        path=["A", "B", "C"],
        origin="A",
        destination="D",
    )

    assert result["valid"] is False
    assert "wrong_destination" in result["errors"]
    assert result["computed_length"] is None


def test_validate_candidate_path_reports_both_wrong_origin_and_destination(graph):
    """Origin and destination errors should both be reported when both apply."""
    result = validate_candidate_path(
        graph=graph,
        path=["B", "C"],
        origin="A",
        destination="D",
    )

    assert result["valid"] is False
    assert "wrong_origin" in result["errors"]
    assert "wrong_destination" in result["errors"]
    assert result["computed_length"] is None


def test_validate_candidate_path_rejects_unknown_nodes(graph):
    """Unknown nodes should be reported explicitly."""
    result = validate_candidate_path(
        graph=graph,
        path=["A", "UNKNOWN", "D"],
        origin="A",
        destination="D",
    )

    assert result["valid"] is False
    assert "unknown_nodes" in result["errors"]
    assert result["unknown_nodes"] == ["UNKNOWN"]
    assert result["missing_edges"] == []
    assert result["computed_length"] is None


def test_validate_candidate_path_reports_multiple_unknown_nodes(graph):
    """All unknown nodes should be listed to make debugging easier."""
    result = validate_candidate_path(
        graph=graph,
        path=["A", "UNKNOWN_1", "UNKNOWN_2", "D"],
        origin="A",
        destination="D",
    )

    assert result["valid"] is False
    assert "unknown_nodes" in result["errors"]
    assert result["unknown_nodes"] == ["UNKNOWN_1", "UNKNOWN_2"]
    assert result["computed_length"] is None


def test_validate_candidate_path_reports_missing_directed_edge(graph):
    """A path can use known nodes but still be invalid because an edge is missing."""
    result = validate_candidate_path(
        graph=graph,
        path=["A", "D"],
        origin="A",
        destination="D",
    )

    assert result["valid"] is False
    assert "missing_edges" in result["errors"]
    assert result["unknown_nodes"] == []
    assert result["missing_edges"] == [["A", "D"]]
    assert result["computed_length"] is None


def test_validate_candidate_path_reports_multiple_missing_directed_edges(graph):
    """All missing directed edges should be reported."""
    result = validate_candidate_path(
        graph=graph,
        path=["D", "C", "A"],
        origin="D",
        destination="A",
    )

    assert result["valid"] is False
    assert "missing_edges" in result["errors"]
    assert result["missing_edges"] == [["D", "C"], ["C", "A"]]
    assert result["computed_length"] is None


def test_validate_candidate_path_does_not_infer_reverse_edges(graph):
    """Reverse traversal should fail unless the directed edge exists in the graph."""
    result = validate_candidate_path(
        graph=graph,
        path=["D", "C", "B", "A"],
        origin="D",
        destination="A",
    )

    assert result["valid"] is False
    assert "missing_edges" in result["errors"]
    assert result["computed_length"] is None


def test_validate_candidate_path_skips_edge_checks_when_unknown_nodes_exist(graph):
    """Unknown-node errors are more useful than derived missing-edge noise."""
    result = validate_candidate_path(
        graph=graph,
        path=["A", "UNKNOWN", "D"],
        origin="A",
        destination="D",
    )

    assert result["valid"] is False
    assert "unknown_nodes" in result["errors"]
    assert "missing_edges" not in result["errors"]
    assert result["missing_edges"] == []
    assert result["computed_length"] is None


def test_validate_candidate_path_accepts_origin_equals_destination(graph):
    """A single-node route is valid when origin and destination are the same."""
    result = validate_candidate_path(
        graph=graph,
        path=["A"],
        origin="A",
        destination="A",
    )

    assert result == {
        "valid": True,
        "errors": [],
        "unknown_nodes": [],
        "missing_edges": [],
        "computed_length": 0.0,
    }


def test_validate_candidate_path_rejects_unknown_single_node_origin_destination(graph):
    """A single-node path still needs to refer to a known graph node."""
    result = validate_candidate_path(
        graph=graph,
        path=["UNKNOWN"],
        origin="UNKNOWN",
        destination="UNKNOWN",
    )

    assert result["valid"] is False
    assert result["errors"] == ["unknown_nodes"]
    assert result["unknown_nodes"] == ["UNKNOWN"]
    assert result["computed_length"] is None
