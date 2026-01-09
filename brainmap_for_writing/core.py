from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Iterable, Optional
from uuid import uuid4


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


@dataclass(frozen=True)
class NodeId:
    value: str

    @staticmethod
    def new() -> NodeId:
        return NodeId(new_id("node"))


@dataclass(frozen=True)
class EdgeId:
    value: str

    @staticmethod
    def new() -> EdgeId:
        return EdgeId(new_id("edge"))


@dataclass
class Node:
    id: NodeId
    text: str
    event_date: Optional[datetime] = None
    color: Optional[str] = None
    note: str = ""
    x: float = 0.0
    y: float = 0.0


@dataclass
class Edge:
    id: EdgeId
    source: NodeId
    target: NodeId
    collapsed: bool = False


@dataclass
class Graph:
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: dict[str, Edge] = field(default_factory=dict)
    legend: dict[str, str] = field(default_factory=dict)

    def add_node(self, node: Node) -> None:
        self.nodes[node.id.value] = node

    def add_edge(self, edge: Edge) -> None:
        if edge.source.value not in self.nodes:
            raise ValueError(f"Unknown source node: {edge.source.value}")
        if edge.target.value not in self.nodes:
            raise ValueError(f"Unknown target node: {edge.target.value}")
        self.edges[edge.id.value] = edge

    def remove_edge(self, edge_id: EdgeId) -> None:
        self.edges.pop(edge_id.value, None)

    def get_node(self, node_id: NodeId) -> Node:
        try:
            return self.nodes[node_id.value]
        except KeyError as exc:
            raise KeyError(f"Unknown node: {node_id.value}") from exc

    def iter_nodes(self) -> Iterable[Node]:
        return self.nodes.values()

    def iter_edges(self) -> Iterable[Edge]:
        return self.edges.values()


def graph_to_dict(graph: Graph) -> dict[str, Any]:
    return {
        "version": 1,
        "legend": dict(graph.legend),
        "nodes": [
            {
                "id": n.id.value,
                "text": n.text,
                "event_date": n.event_date.isoformat() if n.event_date else None,
                "color": n.color,
                "note": n.note,
                "x": n.x,
                "y": n.y,
            }
            for n in graph.iter_nodes()
        ],
        "edges": [
            {
                "id": e.id.value,
                "source": e.source.value,
                "target": e.target.value,
                "collapsed": e.collapsed,
            }
            for e in graph.iter_edges()
        ],
    }


def graph_from_dict(data: dict[str, Any]) -> Graph:
    if not isinstance(data, dict):
        raise ValueError("Project data must be a JSON object")
    version = data.get("version", 1)
    if version != 1:
        raise ValueError(f"Unsupported project version: {version}")

    raw_nodes = data.get("nodes")
    raw_edges = data.get("edges")
    raw_legend = data.get("legend", {})
    if not isinstance(raw_nodes, list) or not isinstance(raw_edges, list):
        raise ValueError("Project data must contain 'nodes' and 'edges' arrays")

    if not isinstance(raw_legend, dict):
        raise ValueError("Project data 'legend' must be an object")

    graph = Graph()
    for k, v in raw_legend.items():
        if isinstance(k, str) and isinstance(v, str):
            graph.legend[k] = v
    for raw in raw_nodes:
        if not isinstance(raw, dict):
            raise ValueError("Each node must be an object")
        node_id = raw.get("id")
        text = raw.get("text")
        if not isinstance(node_id, str) or not isinstance(text, str):
            raise ValueError("Node must contain string 'id' and 'text'")
        raw_date = raw.get("event_date")
        parsed_date: Optional[datetime]
        if raw_date is None:
            parsed_date = None
        elif isinstance(raw_date, str):
            try:
                # Try full datetime format first
                parsed_date = datetime.fromisoformat(raw_date)
            except ValueError:
                try:
                    # Fallback to date only, appending min time
                    d = date.fromisoformat(raw_date)
                    parsed_date = datetime.combine(d, datetime.min.time())
                except ValueError as exc:
                    raise ValueError(f"Invalid node event_date: {raw_date}") from exc
        else:
            raise ValueError("Node 'event_date' must be a string or null")

        x = raw.get("x", 0.0)
        y = raw.get("y", 0.0)
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise ValueError("Node 'x' and 'y' must be numbers")

        raw_color = raw.get("color")
        if raw_color is None:
            color: Optional[str] = None
        elif isinstance(raw_color, str):
            color = raw_color
        else:
            raise ValueError("Node 'color' must be a string or null")

        raw_note = raw.get("note", "")
        if raw_note is None:
            note = ""
        elif isinstance(raw_note, str):
            note = raw_note
        else:
            raise ValueError("Node 'note' must be a string")

        graph.add_node(
            Node(
                id=NodeId(node_id),
                text=text,
                event_date=parsed_date,
                color=color,
                note=note,
                x=float(x),
                y=float(y),
            )
        )

    for raw in raw_edges:
        if not isinstance(raw, dict):
            raise ValueError("Each edge must be an object")
        edge_id = raw.get("id")
        source = raw.get("source")
        target = raw.get("target")
        if not isinstance(edge_id, str) or not isinstance(source, str) or not isinstance(target, str):
            raise ValueError("Edge must contain string 'id', 'source', and 'target'")
        raw_collapsed = raw.get("collapsed", False)
        if not isinstance(raw_collapsed, bool):
            raise ValueError("Edge 'collapsed' must be a boolean")
        graph.add_edge(
            Edge(id=EdgeId(edge_id), source=NodeId(source), target=NodeId(target), collapsed=raw_collapsed)
        )

    return graph
