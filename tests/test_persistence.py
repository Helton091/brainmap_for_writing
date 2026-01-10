import json
from datetime import datetime
from pathlib import Path

from brainmap_for_writing.core import Edge, EdgeId, Graph, Node, NodeId
from brainmap_for_writing.persistence import load_project, save_project


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    g = Graph()
    g.legend["#ff0000"] = "重要"
    g.system_prompt = "You are helpful."
    g.world_document = "World rules..."
    n1 = Node(
        id=NodeId.new(),
        text="hello",
        event_date=datetime(2200, 7, 10),
        color="#ff0000",
        note="H",
        memory_block="overview",
        story_txt_path=str(tmp_path / "story.txt"),
        x=10,
        y=20,
    )
    n2 = Node(id=NodeId.new(), text="world", event_date=None, color=None, note="", x=30, y=40)
    g.add_node(n1)
    g.add_node(n2)
    e = Edge(id=EdgeId.new(), source=n1.id, target=n2.id, collapsed=True)
    g.add_edge(e)

    p = tmp_path / "p.json"
    save_project(p, g)

    raw = json.loads(p.read_text(encoding="utf-8"))
    assert raw["version"] == 1
    assert raw["legend"]["#ff0000"] == "重要"
    assert raw["system_prompt"] == "You are helpful."
    assert raw["world_document"] == "World rules..."
    assert len(raw["nodes"]) == 2
    assert len(raw["edges"]) == 1
    n1_raw = next(n for n in raw["nodes"] if n["id"] == n1.id.value)
    assert n1_raw["color"] == "#ff0000"
    assert n1_raw["note"] == "H"
    assert n1_raw["memory_block"] == "overview"
    assert n1_raw["story_txt_path"] == str(tmp_path / "story.txt")
    assert "collapsed" not in n1_raw

    g2 = load_project(p)
    assert len(list(g2.iter_nodes())) == 2
    assert len(list(g2.iter_edges())) == 1
    assert g2.legend["#ff0000"] == "重要"
    assert g2.system_prompt == "You are helpful."
    assert g2.world_document == "World rules..."
    n1_loaded = g2.get_node(n1.id)
    assert n1_loaded.color == "#ff0000"
    assert n1_loaded.note == "H"
    assert n1_loaded.memory_block == "overview"
    assert n1_loaded.story_txt_path == str(tmp_path / "story.txt")
    e_loaded = next(iter(g2.iter_edges()))
    assert e_loaded.collapsed is True


def test_load_project_defaults_documents(tmp_path: Path) -> None:
    p = tmp_path / "p.json"
    p.write_text(
        json.dumps(
            {
                "version": 1,
                "legend": {},
                "nodes": [],
                "edges": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    g = load_project(p)
    assert g.system_prompt == ""
    assert g.world_document == ""


def test_load_project_defaults_node_memory_and_story_path(tmp_path: Path) -> None:
    p = tmp_path / "p.json"
    p.write_text(
        json.dumps(
            {
                "version": 1,
                "legend": {},
                "nodes": [
                    {
                        "id": "node_1",
                        "text": "t",
                        "event_date": None,
                        "x": 0,
                        "y": 0,
                    }
                ],
                "edges": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    g = load_project(p)
    n = g.get_node(NodeId("node_1"))
    assert n.memory_block == ""
    assert n.story_txt_path is None
