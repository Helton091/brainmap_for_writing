from __future__ import annotations

import json
from pathlib import Path

from .core import Graph, graph_from_dict, graph_to_dict


def save_project(path: str | Path, graph: Graph) -> None:
    p = Path(path)
    data = graph_to_dict(graph)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_project(path: str | Path) -> Graph:
    p = Path(path)
    raw = p.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {p}") from exc
    return graph_from_dict(data)
