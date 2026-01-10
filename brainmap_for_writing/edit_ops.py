from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .core import Edge, Graph, Node


@dataclass(frozen=True)
class DeleteSnapshot:
    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...]


def delete_nodes_and_edges(graph: Graph, node_ids: Iterable[str], edge_ids: Iterable[str]) -> DeleteSnapshot:
    node_id_set = {nid for nid in node_ids if isinstance(nid, str) and nid}
    edge_id_set = {eid for eid in edge_ids if isinstance(eid, str) and eid}

    incident_edge_ids: set[str] = set()
    if node_id_set:
        for e in graph.iter_edges():
            if e.source.value in node_id_set or e.target.value in node_id_set:
                incident_edge_ids.add(e.id.value)

    edge_id_set |= incident_edge_ids

    deleted_nodes: list[Node] = []
    for nid in node_id_set:
        node = graph.nodes.get(nid)
        if node is not None:
            deleted_nodes.append(node)

    deleted_edges: list[Edge] = []
    for eid in edge_id_set:
        edge = graph.edges.get(eid)
        if edge is not None:
            deleted_edges.append(edge)

    for edge in deleted_edges:
        graph.edges.pop(edge.id.value, None)

    for node in deleted_nodes:
        graph.nodes.pop(node.id.value, None)

    return DeleteSnapshot(nodes=tuple(deleted_nodes), edges=tuple(deleted_edges))


def undo_delete(graph: Graph, snapshot: DeleteSnapshot) -> None:
    for node in snapshot.nodes:
        graph.nodes[node.id.value] = node

    for edge in snapshot.edges:
        if edge.source.value in graph.nodes and edge.target.value in graph.nodes:
            graph.edges[edge.id.value] = edge
