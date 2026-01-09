from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, Optional

from .core import Graph, Node


@dataclass(frozen=True)
class LayoutConfig:
    column_width: float = 100.0
    row_height: float = 40.0
    left_margin: float = 80.0
    top_margin: float = 80.0


def assign_default_layout(graph: Graph, config: Optional[LayoutConfig] = None) -> None:
    cfg = config or LayoutConfig()

    dated: list[Node] = []
    undated: list[Node] = []
    for node in graph.iter_nodes():
        if node.event_date is None:
            undated.append(node)
        else:
            dated.append(node)

    dated.sort(key=lambda n: (n.event_date or date.min, n.id.value))
    undated.sort(key=lambda n: n.id.value)

    unique_dates: list[date] = []
    seen: set[date] = set()
    for node in dated:
        assert node.event_date is not None
        if node.event_date not in seen:
            unique_dates.append(node.event_date)
            seen.add(node.event_date)

    date_to_col = {d: idx for idx, d in enumerate(unique_dates)}

    for idx, node in enumerate(undated):
        node.x = cfg.left_margin
        node.y = cfg.top_margin + idx * cfg.row_height

    date_counts: dict[date, int] = {}
    for node in dated:
        assert node.event_date is not None
        
        count = date_counts.get(node.event_date, 0)
        date_counts[node.event_date] = count + 1
        
        col = date_to_col[node.event_date]
        node.x = cfg.left_margin + (col + 1) * cfg.column_width
        node.y = cfg.top_margin + count * cfg.row_height


def assign_default_layout_for_new_nodes(
    graph: Graph,
    new_node_ids: Iterable[str],
    config: Optional[LayoutConfig] = None,
) -> None:
    cfg = config or LayoutConfig()
    new_ids = set(new_node_ids)
    if not new_ids:
        return

    new_nodes: list[Node] = []
    seen = set()
    for nid in new_node_ids:
        if nid not in new_ids:
            continue
        if nid in seen:
            continue
        seen.add(nid)
        node = graph.nodes.get(nid)
        if node is not None:
            new_nodes.append(node)
            
    if not new_nodes:
        return

    existing = [n for n in graph.iter_nodes() if n.id.value not in new_ids]
    if existing:
        anchor_x = max(n.x for n in existing) + cfg.column_width
        anchor_y = min(n.y for n in existing)
    else:
        anchor_x = cfg.left_margin
        anchor_y = cfg.top_margin

    for i, node in enumerate(new_nodes):
        node.x = anchor_x + i * cfg.column_width
        node.y = anchor_y
