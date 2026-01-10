from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .core import Edge


def compute_parallel_edge_indices(edges: Iterable[Edge]) -> dict[str, int]:
    groups: dict[tuple[str, str], list[Edge]] = defaultdict(list)
    for e in edges:
        groups[(e.source.value, e.target.value)].append(e)

    result: dict[str, int] = {}
    for _, group in groups.items():
        group_sorted = sorted(group, key=lambda e: e.id.value)

        indices: list[int] = []
        if len(group_sorted) == 1:
            indices = [0]
        else:
            k = 1
            while len(indices) < len(group_sorted):
                indices.append(k)
                if len(indices) < len(group_sorted):
                    indices.append(-k)
                k += 1

        for e, idx in zip(group_sorted, indices, strict=False):
            result[e.id.value] = idx
    return result


def curve_step(node_radius: float, edge_width: float) -> float:
    return max(32.0, node_radius * 1.7 + edge_width * 16.0)
