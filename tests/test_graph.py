"""Tests for the SSAL graph data model and edge-attribute parser.

This test module covers the lower-level graph utilities in research.graph:

- the immutable Edge dataclass
- the Graph adjacency representation
- node and edge lookup helpers
- path-length calculation
- edge-attribute parsing from SSAL edge metadata strings, including generic
  key=value attributes

These tests do not cover full SSAL-to-graph parsing or Dijkstra yet. Those should
be added in separate tests once build_graph_from_ssal and
dijkstra_shortest_path are implemented.
"""

import dataclasses

import pytest

from research.graph import Edge, Graph, parse_edge_attrs


# ---------------------------------------------------------------------------
# Edge model
# ---------------------------------------------------------------------------


def test_edge_can_be_created_with_only_required_route_fields():
    """An edge only needs source, target, and length."""
    edge = Edge(
        source="A",
        target="B",
        length=12.5,
    )

    assert edge.source == "A"
    assert edge.target == "B"
    assert edge.length == 12.5
    assert edge.name is None
    assert edge.direction is None
    assert edge.attrs is None


def test_edge_can_store_optional_ssal_metadata():
    """Optional SSAL metadata should be preserved on the edge."""
    attrs = {
        "length": 12.5,
        "name": "Test Street",
        "direction": "2w",
        "from_x": 24.1,
        "from_y": 60.1,
    }

    edge = Edge(
        source="A",
        target="B",
        length=12.5,
        name="Test Street",
        direction="2w",
        attrs=attrs,
    )

    assert edge.source == "A"
    assert edge.target == "B"
    assert edge.length == 12.5
    assert edge.name == "Test Street"
    assert edge.direction == "2w"
    assert edge.attrs == attrs


def test_edge_is_immutable_after_creation():
    """Edge instances should be frozen so graph data is not changed accidentally."""
    edge = Edge(source="A", target="B", length=1.0)

    with pytest.raises(dataclasses.FrozenInstanceError):
        edge.length = 2.0  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Graph node and edge helpers
# ---------------------------------------------------------------------------


def test_nodes_returns_sorted_node_ids():
    """Graph.nodes() should return deterministic sorted node IDs."""
    graph = Graph(
        adjacency={
            "C": [],
            "A": [],
            "B": [],
        }
    )

    assert graph.nodes() == ["A", "B", "C"]


def test_has_node_reports_existing_nodes():
    """Graph.has_node() should return True for known nodes."""
    graph = Graph(
        adjacency={
            "A": [],
            "B": [],
        }
    )

    assert graph.has_node("A") is True
    assert graph.has_node("B") is True


def test_has_node_reports_missing_nodes():
    """Graph.has_node() should return False for unknown nodes."""
    graph = Graph(
        adjacency={
            "A": [],
        }
    )

    assert graph.has_node("UNKNOWN") is False


def test_get_edge_returns_the_directed_edge_from_source_to_target():
    """Graph.get_edge() should return the matching directed edge."""
    edge_ab = Edge(source="A", target="B", length=1.0)
    edge_ac = Edge(source="A", target="C", length=5.0)

    graph = Graph(
        adjacency={
            "A": [edge_ab, edge_ac],
            "B": [],
            "C": [],
        }
    )

    assert graph.get_edge("A", "B") == edge_ab
    assert graph.get_edge("A", "C") == edge_ac


def test_get_edge_returns_none_when_directed_edge_does_not_exist():
    """Graph.get_edge() should not infer missing or reverse edges."""
    graph = Graph(
        adjacency={
            "A": [Edge(source="A", target="B", length=1.0)],
            "B": [],
        }
    )

    assert graph.get_edge("A", "C") is None
    assert graph.get_edge("B", "A") is None
    assert graph.get_edge("UNKNOWN", "A") is None


def test_has_edge_reports_existing_directed_edge():
    """Graph.has_edge() should return True when the directed edge exists."""
    graph = Graph(
        adjacency={
            "A": [Edge(source="A", target="B", length=1.0)],
            "B": [],
        }
    )

    assert graph.has_edge("A", "B") is True


def test_has_edge_reports_missing_or_reverse_edge_as_false():
    """Graph.has_edge() should not infer reverse or missing edges."""
    graph = Graph(
        adjacency={
            "A": [Edge(source="A", target="B", length=1.0)],
            "B": [],
        }
    )

    assert graph.has_edge("B", "A") is False
    assert graph.has_edge("A", "C") is False


# ---------------------------------------------------------------------------
# Path length
# ---------------------------------------------------------------------------


def test_path_length_sums_all_directed_edge_lengths_in_order():
    """Graph.path_length() should sum consecutive directed edge lengths."""
    graph = Graph(
        adjacency={
            "A": [Edge(source="A", target="B", length=1.5)],
            "B": [Edge(source="B", target="C", length=2.5)],
            "C": [Edge(source="C", target="D", length=3.0)],
            "D": [],
        }
    )

    assert graph.path_length(["A", "B", "C", "D"]) == 7.0


def test_path_length_for_single_node_path_is_zero():
    """A path with one node contains no edges, so its length is zero."""
    graph = Graph(
        adjacency={
            "A": [],
        }
    )

    assert graph.path_length(["A"]) == 0.0


def test_path_length_for_empty_path_is_zero():
    """An empty path contains no edges, so its length is zero."""
    graph = Graph(
        adjacency={
            "A": [],
        }
    )

    assert graph.path_length([]) == 0.0


def test_path_length_raises_when_any_consecutive_edge_is_missing():
    """Path length calculation should fail clearly on invalid node sequences."""
    graph = Graph(
        adjacency={
            "A": [Edge(source="A", target="B", length=1.0)],
            "B": [],
            "C": [],
        }
    )

    with pytest.raises(ValueError, match="No edge from B to C"):
        graph.path_length(["A", "B", "C"])


# ---------------------------------------------------------------------------
# SSAL edge-attribute parsing
# ---------------------------------------------------------------------------


def test_parse_edge_attrs_reads_core_fields_and_key_value_metadata():
    """SSAL edge metadata should parse core fields and generic key=value attributes."""
    attrs = parse_edge_attrs(
        "12.4, Otaniementie, 2w, from_x=24.1, from_y=60.1, surface=asphalt"
    )

    assert attrs["length"] == 12.4
    assert attrs["name"] == "Otaniementie"
    assert attrs["direction"] == "2w"
    assert attrs["from_x"] == 24.1
    assert attrs["from_y"] == 60.1
    assert attrs["surface"] == "asphalt"


def test_parse_edge_attrs_parses_numeric_key_value_metadata():
    """Numeric key=value metadata should be converted to floats."""
    attrs = parse_edge_attrs(
        "18.7, Erottajankatu, 1w, "
        "from_x=24.9439, from_y=60.16637, "
        "to_x=24.94388, to_y=60.16654, "
        "speed_limit=30"
    )

    assert attrs == {
        "length": 18.7,
        "name": "Erottajankatu",
        "direction": "1w",
        "from_x": 24.9439,
        "from_y": 60.16637,
        "to_x": 24.94388,
        "to_y": 60.16654,
        "speed_limit": 30.0,
    }


def test_parse_edge_attrs_rejects_non_numeric_length():
    """The first SSAL edge field must be a numeric length."""
    with pytest.raises(ValueError, match="Invalid edge length: 'not-a-number'"):
        parse_edge_attrs("not-a-number, Road, 2w")


def test_parse_edge_attrs_allows_empty_metadata_string():
    """Empty edge metadata returns an empty attribute dictionary."""
    attrs = parse_edge_attrs("")

    assert "length" not in attrs
    assert attrs == {}


def test_parse_edge_attrs_accepts_length_only():
    """An edge metadata string may contain only length."""
    attrs = parse_edge_attrs("7.5")

    assert attrs == {
        "length": 7.5,
    }


def test_parse_edge_attrs_accepts_length_and_name_without_direction():
    """Direction is optional if the SSAL edge string only includes length and name."""
    attrs = parse_edge_attrs("7.5, Test Street")

    assert attrs == {
        "length": 7.5,
        "name": "Test Street",
    }


def test_parse_edge_attrs_accepts_length_name_and_direction():
    """The first three SSAL fields map to length, name, and direction."""
    attrs = parse_edge_attrs("7.5, Test Street, 2w")

    assert attrs == {
        "length": 7.5,
        "name": "Test Street",
        "direction": "2w",
    }


def test_parse_edge_attrs_ignores_extra_parts_that_are_not_key_value_pairs():
    """Extra metadata parts without '=' are ignored."""
    attrs = parse_edge_attrs("7.5, Test Street, 2w, ignored-part")

    assert attrs == {
        "length": 7.5,
        "name": "Test Street",
        "direction": "2w",
    }


def test_parse_edge_attrs_keeps_non_numeric_key_value_metadata_as_strings():
    """Non-numeric key-value metadata should be preserved as strings."""
    attrs = parse_edge_attrs(
        "7.5, Test Street, 2w, surface=asphalt, note=main segment"
    )

    assert attrs["length"] == 7.5
    assert attrs["name"] == "Test Street"
    assert attrs["direction"] == "2w"
    assert attrs["surface"] == "asphalt"
    assert attrs["note"] == "main segment"


def test_parse_edge_attrs_strips_whitespace_around_fields_and_values():
    """Whitespace around comma-separated fields and key-value pairs is ignored."""
    attrs = parse_edge_attrs(
        "  7.5  ,  Test Street  ,  2w  ,  from_x = 24.1  "
    )

    assert attrs["length"] == 7.5
    assert attrs["name"] == "Test Street"
    assert attrs["direction"] == "2w"
    assert attrs["from_x"] == 24.1


def test_parse_edge_attrs_allows_negative_length_for_later_validation():
    """Negative length is parsed here; Dijkstra should reject it later."""
    attrs = parse_edge_attrs("-1.0, Road, 1w")

    assert attrs["length"] == -1.0
    assert attrs["name"] == "Road"
    assert attrs["direction"] == "1w"
