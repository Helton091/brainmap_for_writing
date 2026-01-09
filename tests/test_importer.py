from datetime import date

import pytest

from brainmap_for_writing.importer import ImportErrorDetail, import_txt_lines


def test_import_txt_lines_creates_dated_nodes() -> None:
    lines = [
        "【2200.07.10】\n",
        "Hello\n",
        "World\n",
        "【2200.08.03】\n",
        "Next\n",
    ]
    graph = import_txt_lines(lines)
    dated = [n for n in graph.iter_nodes() if n.event_date is not None]
    assert len(dated) == 2
    assert {n.event_date for n in dated} == {date(2200, 7, 10), date(2200, 8, 3)}


def test_import_txt_lines_supports_single_digit_month_day() -> None:
    lines = [
        "【2200.7.1】\n",
        "Hello\n",
        "【2200-8-3】\n",
        "Next\n",
    ]
    graph = import_txt_lines(lines)
    dated = [n for n in graph.iter_nodes() if n.event_date is not None]
    assert {n.event_date for n in dated} == {date(2200, 7, 1), date(2200, 8, 3)}


def test_import_txt_lines_creates_undated_blocks_split_by_blank_lines() -> None:
    lines = [
        "Undated A\n",
        "\n",
        "Undated B\n",
        "Line 2\n",
        "\n",
        "\n",
        "Undated C\n",
    ]
    graph = import_txt_lines(lines)
    undated = [n for n in graph.iter_nodes() if n.event_date is None]
    texts = sorted(n.text for n in undated)
    assert texts == ["Undated A", "Undated B\nLine 2", "Undated C"]


def test_import_txt_lines_empty_raises() -> None:
    with pytest.raises(ImportErrorDetail):
        import_txt_lines(["\n", "\n"])
