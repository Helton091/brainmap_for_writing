from brainmap_for_writing.core import Edge, EdgeId, Graph, Node, NodeId
from brainmap_for_writing.visibility import compute_visible_nodes


def test_build_ai_prompt_uses_upstream_memory_and_target_text() -> None:
    from brainmap_for_writing.core import build_ai_friendly_prompt

    g = Graph()
    g.system_prompt = "SYS"
    g.world_document = "WORLD"
    a = Node(id=NodeId.new(), text="A", memory_block="MA")
    b = Node(id=NodeId.new(), text="B", memory_block="")
    c = Node(id=NodeId.new(), text="C", memory_block="MC")
    t = Node(id=NodeId.new(), text="TARGET")
    g.add_node(a)
    g.add_node(b)
    g.add_node(c)
    g.add_node(t)
    g.add_edge(Edge(id=EdgeId.new(), source=a.id, target=b.id))
    g.add_edge(Edge(id=EdgeId.new(), source=b.id, target=t.id))
    g.add_edge(Edge(id=EdgeId.new(), source=c.id, target=t.id))

    out = build_ai_friendly_prompt(g, t.id)
    assert "# System Prompt" in out
    assert "SYS" in out
    assert "# World Document" in out
    assert "WORLD" in out
    assert "MA" in out
    assert "MC" in out
    assert "TARGET" in out
    assert "##" in out


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
