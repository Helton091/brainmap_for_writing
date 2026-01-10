from brainmap_for_writing.core import Edge, EdgeId, NodeId
from brainmap_for_writing.edge_geometry import compute_parallel_edge_indices, curve_step


def test_parallel_edge_indices_two_edges() -> None:
    a = NodeId.new()
    b = NodeId.new()
    e1 = Edge(id=EdgeId.new(), source=a, target=b)
    e2 = Edge(id=EdgeId.new(), source=a, target=b)

    m = compute_parallel_edge_indices([e1, e2])
    assert set(m.keys()) == {e1.id.value, e2.id.value}
    assert set(m.values()) == {1, -1}


def test_parallel_edge_indices_three_edges_include_negative() -> None:
    a = NodeId.new()
    b = NodeId.new()
    edges = [Edge(id=EdgeId.new(), source=a, target=b) for _ in range(3)]
    m = compute_parallel_edge_indices(edges)
    assert set(m.values()) == {1, -1, 2}


def test_curve_step_increases_with_radius_and_width() -> None:
    s1 = curve_step(14.0, 2.0)
    s2 = curve_step(24.0, 2.0)
    s3 = curve_step(24.0, 6.0)
    assert s2 > s1
    assert s3 > s2
