from __future__ import annotations

from .core import Graph


def compute_visible_nodes(graph: Graph) -> set[str]:
    node_ids = set(graph.nodes.keys())
    if not node_ids:
        return set()

    incoming_count = {nid: 0 for nid in node_ids}
    outgoing: dict[str, list[tuple[str, bool]]] = {nid: [] for nid in node_ids}

    for edge in graph.iter_edges():
        s = edge.source.value
        t = edge.target.value
        if s in outgoing:
            outgoing[s].append((t, edge.collapsed))
        if t in incoming_count:
            incoming_count[t] += 1

    roots = [nid for nid, cnt in incoming_count.items() if cnt == 0]
    start = roots if roots else list(node_ids)

    visible: set[str] = set()
    stack: list[str] = list(start)
    while stack:
        nid = stack.pop()
        if nid in visible:
            continue
        visible.add(nid)
        for nxt, edge_collapsed in outgoing.get(nid, []):
            if edge_collapsed:
                continue
            if nxt in node_ids:
                stack.append(nxt)

    return visible
