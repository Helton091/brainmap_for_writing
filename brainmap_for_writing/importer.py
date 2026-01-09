from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Iterable, Optional

from .core import Graph, Node, NodeId


@dataclass(frozen=True)
class ImportErrorDetail(Exception):
    message: str
    line_number: Optional[int] = None

    def __str__(self) -> str:
        if self.line_number is None:
            return self.message
        return f"Line {self.line_number}: {self.message}"


_DATE_MARKER_RE = re.compile(
    r"^\s*【\s*(?P<y>\d{4})\s*[\.\/\-．:：]\s*(?P<m>\d{1,2})\s*[\.\/\-．:：]\s*(?P<d>\d{1,2})"
    r"(?:\s*[\.\/\-．:：]\s*(?P<H>\d{1,2})\s*[\.\/\-．:：]\s*(?P<M>\d{1,2})(?:\s*[\.\/\-．:：]\s*(?P<S>\d{1,2}))?)?\s*】\s*$"
)


def _parse_date_marker(line: str, line_number: int) -> Optional[datetime]:
    match = _DATE_MARKER_RE.match(line)
    if not match:
        return None
    y = int(match.group("y"))
    m = int(match.group("m"))
    d = int(match.group("d"))
    
    H_str = match.group("H")
    M_str = match.group("M")
    S_str = match.group("S")
    
    H = int(H_str) if H_str else 0
    M = int(M_str) if M_str else 0
    S = int(S_str) if S_str else 0
    
    try:
        return datetime(y, m, d, H, M, S)
    except ValueError as exc:
        raise ImportErrorDetail("Invalid date marker", line_number=line_number) from exc


def _finalize_text_blocks(lines: list[str]) -> list[str]:
    text = "\n".join(lines).strip("\n")
    if not text.strip():
        return []

    blocks: list[str] = []
    current: list[str] = []
    for raw_line in text.splitlines():
        if raw_line.strip() == "":
            if current:
                blocks.append("\n".join(current).strip("\n"))
                current = []
            continue
        current.append(raw_line)
    if current:
        blocks.append("\n".join(current).strip("\n"))
    return [b for b in blocks if b.strip()]


def import_txt_lines(lines: Iterable[str], existing_graph: Optional[Graph] = None) -> Graph:
    graph = Graph()
    
    # Pre-calculate existing timestamps for conflict detection
    existing_timestamps: set[datetime] = set()
    if existing_graph:
        for node in existing_graph.iter_nodes():
            if node.event_date:
                existing_timestamps.add(node.event_date)

    current_date: Optional[datetime] = None
    current_lines: list[str] = []
    pending_undated_lines: list[str] = []

    def flush_dated_block() -> None:
        nonlocal current_date, current_lines
        if current_date is None:
            return
        
        # Conflict check: if this timestamp exists in the *original* graph, skip it
        # Note: We also check if we already added it in *this* import session (graph.nodes)
        # But for now, user asked to check against "old events".
        # Assuming "old events" means what's in existing_graph.
        if current_date in existing_timestamps:
             # Skip this event as it conflicts with an existing one
             current_date = None
             current_lines = []
             return

        text = "\n".join(current_lines).strip("\n")
        node = Node(id=NodeId.new(), text=text.strip(), event_date=current_date)
        graph.add_node(node)
        current_date = None
        current_lines = []

    def flush_undated_blocks() -> None:
        nonlocal pending_undated_lines
        for block in _finalize_text_blocks(pending_undated_lines):
            graph.add_node(Node(id=NodeId.new(), text=block, event_date=None))
        pending_undated_lines = []

    for idx, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n").rstrip("\r")
        marker_date = _parse_date_marker(line, idx)
        if marker_date is not None:
            flush_dated_block()
            flush_undated_blocks()
            current_date = marker_date
            continue

        if current_date is None:
            pending_undated_lines.append(line)
        else:
            current_lines.append(line)

    flush_dated_block()
    flush_undated_blocks()

    if not graph.nodes:
        raise ImportErrorDetail("No nodes could be imported")
    return graph


def import_txt_file(path: str, existing_graph: Optional[Graph] = None) -> Graph:
    try:
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                return import_txt_lines(f, existing_graph)
        except UnicodeDecodeError:
            with open(path, "r", encoding="gb18030") as f:
                return import_txt_lines(f, existing_graph)
    except OSError as exc:
        raise ImportErrorDetail(f"Failed to read file: {path}") from exc
