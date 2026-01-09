from brainmap_for_writing.core import Edge, EdgeId, Graph, Node, NodeId
from brainmap_for_writing.visibility import compute_visible_nodes


def test_collapse_hides_downstream_chain() -> None:
    g = Graph()
    a = Node(id=NodeId.new(), text="A")
    b = Node(id=NodeId.new(), text="B")
    c = Node(id=NodeId.new(), text="C")
    g.add_node(a)
    g.add_node(b)
    g.add_node(c)
    e1 = Edge(id=EdgeId.new(), source=a.id, target=b.id)
    e2 = Edge(id=EdgeId.new(), source=b.id, target=c.id)
    g.add_edge(e1)
    g.add_edge(e2)

    e1.collapsed = True
    visible = compute_visible_nodes(g)
    assert visible == {a.id.value}


def test_collapse_at_intermediate_node() -> None:
    g = Graph()
    a = Node(id=NodeId.new(), text="A")
    b = Node(id=NodeId.new(), text="B")
    c = Node(id=NodeId.new(), text="C")
    g.add_node(a)
    g.add_node(b)
    g.add_node(c)
    e1 = Edge(id=EdgeId.new(), source=a.id, target=b.id)
    e2 = Edge(id=EdgeId.new(), source=b.id, target=c.id)
    g.add_edge(e1)
    g.add_edge(e2)

    e2.collapsed = True
    visible = compute_visible_nodes(g)
    assert visible == {a.id.value, b.id.value}


def test_expand_restores_downstream() -> None:
    g = Graph()
    a = Node(id=NodeId.new(), text="A")
    b = Node(id=NodeId.new(), text="B")
    c = Node(id=NodeId.new(), text="C")
    g.add_node(a)
    g.add_node(b)
    g.add_node(c)
    e1 = Edge(id=EdgeId.new(), source=a.id, target=b.id)
    e2 = Edge(id=EdgeId.new(), source=b.id, target=c.id)
    g.add_edge(e1)
    g.add_edge(e2)

    e2.collapsed = True
    assert compute_visible_nodes(g) == {a.id.value, b.id.value}
    e2.collapsed = False
    assert compute_visible_nodes(g) == {a.id.value, b.id.value, c.id.value}


def test_collapse_one_branch_keeps_other_branch() -> None:
    g = Graph()
    a = Node(id=NodeId.new(), text="A")
    b = Node(id=NodeId.new(), text="B")
    c = Node(id=NodeId.new(), text="C")
    g.add_node(a)
    g.add_node(b)
    g.add_node(c)
    e1 = Edge(id=EdgeId.new(), source=a.id, target=b.id)
    e2 = Edge(id=EdgeId.new(), source=a.id, target=c.id)
    g.add_edge(e1)
    g.add_edge(e2)

    e1.collapsed = True
    visible = compute_visible_nodes(g)
    assert visible == {a.id.value, c.id.value}
