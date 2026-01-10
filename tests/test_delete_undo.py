from brainmap_for_writing.core import Edge, EdgeId, Graph, Node, NodeId
from brainmap_for_writing.edit_ops import delete_nodes_and_edges, undo_delete


def test_delete_node_removes_incident_edges_and_undo_restores() -> None:
    g = Graph()
    a = Node(id=NodeId.new(), text="A", x=10.0, y=20.0)
    b = Node(id=NodeId.new(), text="B", x=30.0, y=40.0)
    g.add_node(a)
    g.add_node(b)
    e = Edge(id=EdgeId.new(), source=a.id, target=b.id)
    g.add_edge(e)

    snap = delete_nodes_and_edges(g, node_ids={b.id.value}, edge_ids=set())
    assert b.id.value not in g.nodes
    assert e.id.value not in g.edges
    assert snap.nodes == (b,)
    assert snap.edges == (e,)

    undo_delete(g, snap)
    assert b.id.value in g.nodes
    assert e.id.value in g.edges
    assert g.nodes[b.id.value].id.value == b.id.value
    assert g.nodes[b.id.value].x == 30.0
    assert g.nodes[b.id.value].y == 40.0


def test_delete_edge_and_undo_restores() -> None:
    g = Graph()
    a = Node(id=NodeId.new(), text="A")
    b = Node(id=NodeId.new(), text="B")
    g.add_node(a)
    g.add_node(b)
    e = Edge(id=EdgeId.new(), source=a.id, target=b.id)
    g.add_edge(e)

    snap = delete_nodes_and_edges(g, node_ids=set(), edge_ids={e.id.value})
    assert e.id.value not in g.edges
    assert snap.nodes == ()
    assert snap.edges == (e,)

    undo_delete(g, snap)
    assert e.id.value in g.edges
