from datetime import datetime

from brainmap_for_writing.core import Graph, Node, NodeId
from brainmap_for_writing.layout import assign_default_layout, assign_default_layout_for_new_nodes


def test_layout_places_later_dates_more_right() -> None:
    g = Graph()
    n1 = Node(id=NodeId.new(), text="a", event_date=datetime(2200, 1, 1))
    n2 = Node(id=NodeId.new(), text="b", event_date=datetime(2200, 2, 1))
    g.add_node(n1)
    g.add_node(n2)

    assign_default_layout(g)
    assert n2.x > n1.x


def test_layout_for_new_nodes_does_not_move_existing() -> None:
    g = Graph()
    existing = Node(id=NodeId.new(), text="a", event_date=datetime(2200, 1, 1), x=111, y=222)
    g.add_node(existing)
    new_node = Node(id=NodeId.new(), text="b", event_date=datetime(2200, 2, 1))
    g.add_node(new_node)

    assign_default_layout_for_new_nodes(g, [new_node.id.value])
    assert (existing.x, existing.y) == (111, 222)
