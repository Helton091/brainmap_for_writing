from __future__ import annotations

import html
from dataclasses import dataclass
from datetime import date, datetime
from math import atan2, cos, sin
from typing import Callable, Optional

from pathlib import Path

from PySide6.QtCore import QLineF, QPointF, QRectF, Qt, Signal, QUrl
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QDesktopServices,
    QFont,
    QKeySequence,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
)
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QColorDialog,
    QDockWidget,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGraphicsItem,
    QGraphicsPathItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QToolBar,
    QToolButton,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from .core import Edge, EdgeId, Graph, Node, NodeId, build_ai_friendly_prompt
from .edit_ops import DeleteSnapshot, delete_nodes_and_edges, undo_delete
from .edge_geometry import compute_parallel_edge_indices, curve_step
from .importer import ImportErrorDetail, import_txt_file
from .layout import assign_default_layout, assign_default_layout_for_new_nodes
from .persistence import load_project, save_project
from .visibility import compute_visible_nodes


@dataclass
class UiConfig:
    node_radius: float = 14.0
    # Date display format: "date" or "datetime"
    date_display_format: str = "date"
    edge_width: float = 2.0


class NodeEditDialog(QDialog):
    def __init__(self, parent: QWidget, node: Node) -> None:
        super().__init__(parent)
        self.setWindowTitle("Edit Node")

        self._date_input = QLineEdit(self)
        self._date_input.setPlaceholderText("YYYY-MM-DD or YYYY-MM-DD HH:MM:SS (optional)")
        self._date_input.setText(node.event_date.isoformat(sep=" ") if node.event_date else "")

        self._text_input = QTextEdit(self)
        self._text_input.setPlainText(node.text)

        form = QFormLayout()
        form.addRow("Date/Time", self._date_input)
        form.addRow("Text", self._text_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_values(self) -> tuple[Optional[datetime], str]:
        raw_date = self._date_input.text().strip()
        parsed_date: Optional[datetime]
        if raw_date == "":
            parsed_date = None
        else:
            try:
                # Try full datetime first
                parsed_date = datetime.fromisoformat(raw_date)
            except ValueError:
                try:
                    # Fallback to date only
                    d = date.fromisoformat(raw_date)
                    parsed_date = datetime.combine(d, datetime.min.time())
                except ValueError:
                     raise ValueError("Invalid Date Format")

        text = self._text_input.toPlainText().rstrip()
        return parsed_date, text


class DisplaySettingsDialog(QDialog):
    def __init__(self, parent: QWidget, cfg: UiConfig) -> None:
        super().__init__(parent)
        self.setWindowTitle("Display Settings")

        self._date_format = QComboBox(self)
        self._date_format.addItems(["date", "datetime"])
        if cfg.date_display_format == "datetime":
            self._date_format.setCurrentText("datetime")
        else:
            self._date_format.setCurrentText("date")

        self._node_radius = QDoubleSpinBox(self)
        self._node_radius.setRange(6.0, 80.0)
        self._node_radius.setDecimals(1)
        self._node_radius.setValue(float(cfg.node_radius))

        self._edge_width = QDoubleSpinBox(self)
        self._edge_width.setRange(1.0, 12.0)
        self._edge_width.setDecimals(1)
        self._edge_width.setValue(float(cfg.edge_width))

        form = QFormLayout()
        form.addRow("Date Display", self._date_format)
        form.addRow("Node Size", self._node_radius)
        form.addRow("Edge Thickness", self._edge_width)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_values(self) -> tuple[str, float, float]:
        return (
            self._date_format.currentText(),
            float(self._node_radius.value()),
            float(self._edge_width.value()),
        )


class NodeItem(QGraphicsItem):
    def __init__(self, node: Node, cfg: UiConfig) -> None:
        super().__init__()
        self._cfg = cfg
        self._brush = QBrush(QColor(250, 250, 250))
        self._pen = QPen(QColor(60, 60, 60), 2.0)
        self._selected_pen = QPen(QColor(30, 120, 220), 2.5)
        self.setFlags(
            QGraphicsItem.ItemIsMovable
            | QGraphicsItem.ItemIsSelectable
            | QGraphicsItem.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)

        self.node_id = node.id
        self._date_text = QGraphicsTextItem(self)
        self._note_text = QGraphicsTextItem(self)
        self._date_text.setDefaultTextColor(QColor(20, 20, 20))
        self._note_text.setDefaultTextColor(QColor(20, 20, 20))
        font = QFont()
        font.setPointSize(8)
        self._date_text.setFont(font)
        self._note_text.setFont(font)

        self.update_from_node(node)

    def boundingRect(self) -> QRectF:
        r = self._cfg.node_radius
        padding = 2.0
        label_h = 38.0
        return QRectF(-r - padding, -r - padding, (r + padding) * 2, (r + padding) * 2 + label_h)

    def paint(self, painter: QPainter, option, widget=None) -> None:
        painter.setRenderHint(QPainter.Antialiasing, True)
        r = self._cfg.node_radius
        painter.setBrush(self._brush)
        painter.setPen(self._selected_pen if self.isSelected() else self._pen)
        painter.drawEllipse(QPointF(0, 0), r, r)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        r = self._cfg.node_radius
        path.addEllipse(QPointF(0, 0), r, r)
        return path

    def radius(self) -> float:
        return self._cfg.node_radius

    def update_from_node(self, node: Node) -> None:
        self.prepareGeometryChange()
        if node.event_date:
            if self._cfg.date_display_format == "datetime":
                label = node.event_date.isoformat(sep=" ")
            else:
                label = node.event_date.date().isoformat()
        else:
            label = "----"

        self._date_text.setPlainText(label)
        self._date_text.setPos(-self._date_text.boundingRect().width() / 2, self._cfg.node_radius + 2)

        note = (node.note or "").strip()
        if len(note) > 10:
            note = note[:10] + "…"
        self._note_text.setPlainText(note)
        self._note_text.setPos(-self._note_text.boundingRect().width() / 2, self._cfg.node_radius + 18)

        if node.color:
            color = QColor(node.color)
            if color.isValid():
                self._brush = QBrush(color)
            else:
                self._brush = QBrush(QColor(250, 250, 250))
        else:
            self._brush = QBrush(QColor(250, 250, 250))

        text = node.text.strip()
        memory = (node.memory_block or "").strip()
        story_path = (node.story_txt_path or "").strip()

        parts: list[str] = []
        if text:
            parts.append(f"<b>Text</b><br/>{html.escape(text)}")
        else:
            parts.append("<b>Text</b><br/>(empty)")
        if memory:
            parts.append(f"<b>Memory</b><br/>{html.escape(memory)}")
        if story_path:
            parts.append(f"<b>Story TXT</b><br/>{html.escape(story_path)}")

        inner = "<br/><br/>".join(parts)
        self.setToolTip(f'<div style="width: 360px; white-space: pre-wrap;">{inner}</div>')
        self.update()

    def contextMenuEvent(self, event) -> None:
        scene = self.scene()
        if scene is None or not hasattr(scene, "_open_node_menu"):
            return
        scene._open_node_menu(self.node_id, event)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            scene = self.scene()
            if scene is not None and hasattr(scene, "_on_node_moved"):
                scene._on_node_moved(self.node_id, self.pos())
        return super().itemChange(change, value)


class EdgeItem(QGraphicsPathItem):
    def __init__(self, edge: Edge, source_item: NodeItem, target_item: NodeItem, cfg: UiConfig) -> None:
        super().__init__()
        self._cfg = cfg
        self.edge_id = edge.id
        self.source_id = edge.source
        self.target_id = edge.target
        self._collapsed = edge.collapsed
        self._source_item = source_item
        self._target_item = target_item
        self.setZValue(-10)
        self.setPen(QPen(QColor(30, 30, 30), float(self._cfg.edge_width)))
        self._arrow_brush = QBrush(QColor(30, 30, 30))
        self._arrow_poly = QPolygonF()
        self._toggle_center = QPointF(0, 0)
        self._toggle_radius = 11.0
        self._collapsed_label = ""
        self._curve_index = 0
        self.setFlags(QGraphicsItem.ItemIsSelectable)
        self.update_path()

    def sync_from_edge(self, edge: Edge, collapsed_label: str, curve_index: int) -> None:
        self._collapsed = edge.collapsed
        self._collapsed_label = collapsed_label
        self._curve_index = curve_index
        self.setPen(QPen(QColor(30, 30, 30), float(self._cfg.edge_width)))
        self.update_path()

    def update_path(self) -> None:
        a = self._source_item.mapToScene(QPointF(0, 0))
        b = self._target_item.mapToScene(QPointF(0, 0))
        base_line = QLineF(a, b)
        if base_line.length() < 1.0:
            self.setPath(QPainterPath())
            self._arrow_poly = QPolygonF()
            return

        u = QPointF(base_line.dx() / base_line.length(), base_line.dy() / base_line.length())
        n = QPointF(-u.y(), u.x())
        start_pad = self._source_item.radius() + 6.0
        end_pad = self._target_item.radius() + 8.0
        p1 = QPointF(a.x() + u.x() * start_pad, a.y() + u.y() * start_pad)
        p2 = QPointF(b.x() - u.x() * end_pad, b.y() - u.y() * end_pad)

        mid = QPointF((p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2)
        offset = float(self._curve_index) * curve_step(float(self._source_item.radius()), float(self._cfg.edge_width))
        control = QPointF(mid.x() + n.x() * offset, mid.y() + n.y() * offset)

        toggle_t = 0.55
        p01 = QPointF(p1.x() + (control.x() - p1.x()) * toggle_t, p1.y() + (control.y() - p1.y()) * toggle_t)
        p12 = QPointF(control.x() + (p2.x() - control.x()) * toggle_t, control.y() + (p2.y() - control.y()) * toggle_t)
        self._toggle_center = QPointF(p01.x() + (p12.x() - p01.x()) * toggle_t, p01.y() + (p12.y() - p01.y()) * toggle_t)

        if self._collapsed:
            self._arrow_poly = QPolygonF()
            path = QPainterPath()
            path.moveTo(p1)
            path.quadTo(p01, self._toggle_center)
            self.setPath(path)
            return

        tangent = QPointF(p2.x() - control.x(), p2.y() - control.y())
        angle = atan2(-tangent.y(), tangent.x())

        arrow_size = max(12.0, float(self._source_item.radius()) * 1.1)
        arrow_half_width = arrow_size * 0.5
        tip = p2
        back = QPointF(
            tip.x() - arrow_size * cos(angle),
            tip.y() + arrow_size * sin(angle),
        )
        left = QPointF(
            back.x() - arrow_half_width * cos(angle + 1.5708),
            back.y() + arrow_half_width * sin(angle + 1.5708),
        )
        right = QPointF(
            back.x() - arrow_half_width * cos(angle - 1.5708),
            back.y() + arrow_half_width * sin(angle - 1.5708),
        )
        self._arrow_poly = QPolygonF([tip, left, right])

        path = QPainterPath()
        path.moveTo(p1)
        path.quadTo(control, p2)
        self.setPath(path)

    def paint(self, painter: QPainter, option, widget=None) -> None:
        if self.isSelected():
            painter.setPen(QPen(QColor(30, 120, 220), 2.8))
            painter.setBrush(QBrush(QColor(30, 120, 220)))
        else:
            painter.setPen(self.pen())
            painter.setBrush(self._arrow_brush)
        painter.drawPath(self.path())
        if not self._arrow_poly.isEmpty():
            painter.drawPolygon(self._arrow_poly)

        painter.setPen(QPen(QColor(60, 60, 60), 1.2))
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(self._toggle_center, self._toggle_radius, self._toggle_radius)

        painter.setPen(QPen(QColor(30, 30, 30), 2.0))
        r = self._toggle_radius * 0.55
        painter.drawLine(
            QPointF(self._toggle_center.x() - r, self._toggle_center.y()),
            QPointF(self._toggle_center.x() + r, self._toggle_center.y()),
        )
        if self._collapsed:
            painter.drawLine(
                QPointF(self._toggle_center.x(), self._toggle_center.y() - r),
                QPointF(self._toggle_center.x(), self._toggle_center.y() + r),
            )

        if self._collapsed and self._collapsed_label:
            painter.setPen(QPen(QColor(30, 30, 30), 1.0))
            font = painter.font()
            font.setPointSize(9)
            painter.setFont(font)
            rect = painter.boundingRect(
                QRectF(0, 0, 180, 40),
                Qt.AlignLeft | Qt.AlignVCenter,
                self._collapsed_label,
            )
            rect.moveCenter(QPointF(self._toggle_center.x(), self._toggle_center.y() - 22))
            rect.adjust(-6, -4, 6, 4)
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.setPen(QPen(QColor(80, 80, 80), 1.0))
            painter.drawRoundedRect(rect, 6, 6)
            painter.setPen(QPen(QColor(30, 30, 30), 1.0))
            painter.drawText(rect, Qt.AlignCenter, self._collapsed_label)

    def boundingRect(self) -> QRectF:
        rect = super().boundingRect()
        
        # Include the toggle button
        r = self._toggle_radius
        toggle_rect = QRectF(self._toggle_center.x() - r, self._toggle_center.y() - r, r * 2, r * 2)
        rect = rect.united(toggle_rect)
        
        # Include the arrow head if not collapsed
        if not self._collapsed and not self._arrow_poly.isEmpty():
            arrow_rect = self._arrow_poly.boundingRect()
            rect = rect.united(arrow_rect)

        if self._collapsed and self._collapsed_label:
            label_rect = QRectF(self._toggle_center.x() - 100, self._toggle_center.y() - 52, 200, 44)
            rect = rect.united(label_rect)
        return rect

    def shape(self) -> QPainterPath:
        path = super().shape()
        toggle = QPainterPath()
        toggle.addEllipse(self._toggle_center, self._toggle_radius, self._toggle_radius)
        path.addPath(toggle)
        return path

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and QLineF(event.pos(), self._toggle_center).length() <= self._toggle_radius:
            scene = self.scene()
            if scene is not None and hasattr(scene, "_toggle_edge_collapsed"):
                scene._toggle_edge_collapsed(self.edge_id)
                event.accept()
                return
        super().mousePressEvent(event)

    def contextMenuEvent(self, event) -> None:
        scene = self.scene()
        if scene is None or not hasattr(scene, "_open_edge_menu"):
            return
        scene._open_edge_menu(self.edge_id, event)


class GraphScene(QGraphicsScene):
    legendChanged = Signal()

    def __init__(self, graph: Graph, cfg: UiConfig) -> None:
        super().__init__()
        self._graph = graph
        self._cfg = cfg
        self._node_items: dict[str, NodeItem] = {}
        self._edge_items: dict[str, EdgeItem] = {}
        self._undo_stack: list[DeleteSnapshot] = []
        self._connect_mode = False
        self._connect_source: Optional[NodeId] = None
        self.setSceneRect(-1000000, -1000000, 2000000, 2000000)

    def set_connect_mode(self, enabled: bool) -> None:
        self._connect_mode = enabled
        self._connect_source = None

    def clear_all(self) -> None:
        self.clear()
        self._node_items.clear()
        self._edge_items.clear()
        self._connect_source = None

    def load_graph(self, graph: Graph) -> None:
        self._graph = graph
        self.clear_all()
        for node in self._graph.iter_nodes():
            self._add_node_item(node)
        for edge in self._graph.iter_edges():
            self._add_edge_item(edge)
        self.refresh_visibility()

    def _open_node_menu(self, node_id: NodeId, event) -> None:
        node = self._graph.get_node(node_id)
        parent = event.widget() if hasattr(event, "widget") else None

        menu = QMenu(parent)

        edit_action = menu.addAction("Edit")
        color_action = menu.addAction("Set Color")
        clear_color_action = menu.addAction("Clear Color")
        note_action = menu.addAction("Set Note")
        clear_note_action = menu.addAction("Clear Note")
        menu.addSeparator()
        memory_action = menu.addAction("Set Memory Block")
        clear_memory_action = menu.addAction("Clear Memory Block")
        link_story_action = menu.addAction("Link Story TXT")
        open_story_action = menu.addAction("Open Story TXT")
        clear_story_action = menu.addAction("Clear Story TXT")
        export_action = menu.addAction("Export")
        menu.addSeparator()
        delete_action = menu.addAction("Delete")

        story_path = (node.story_txt_path or "").strip()
        open_story_action.setEnabled(bool(story_path))

        chosen = menu.exec(event.screenPos())
        if chosen is None:
            return

        if chosen == edit_action:
            view = self.views()[0] if self.views() else None
            dialog = NodeEditDialog(view or parent, node)
            try:
                accepted = dialog.exec() == QDialog.Accepted
            except ValueError:
                QMessageBox.warning(view or parent, "Invalid Date", "Date must be YYYY-MM-DD")
                return
            if not accepted:
                return
            try:
                new_date, new_text = dialog.get_values()
            except ValueError:
                QMessageBox.warning(view or parent, "Invalid Date", "Date must be YYYY-MM-DD")
                return
            node.event_date = new_date
            node.text = new_text
            item = self._node_items.get(node_id.value)
            if item is not None:
                item.update_from_node(node)
            return

        if chosen == color_action:
            initial = QColor(node.color) if node.color else QColor(250, 250, 250)
            color = QColorDialog.getColor(initial, parent, "Select Node Color")
            if not color.isValid():
                return
            node.color = color.name()
            if node.color not in self._graph.legend:
                self._graph.legend[node.color] = ""
                self.legendChanged.emit()
            item = self._node_items.get(node_id.value)
            if item is not None:
                item.update_from_node(node)
            return

        if chosen == clear_color_action:
            node.color = None
            item = self._node_items.get(node_id.value)
            if item is not None:
                item.update_from_node(node)
            return

        if chosen == note_action:
            text, ok = QInputDialog.getText(parent, "Node Note", "Note", text=node.note)
            if not ok:
                return
            node.note = text.strip()
            item = self._node_items.get(node_id.value)
            if item is not None:
                item.update_from_node(node)
            self.refresh_visibility()
            return

        if chosen == clear_note_action:
            node.note = ""
            item = self._node_items.get(node_id.value)
            if item is not None:
                item.update_from_node(node)
            self.refresh_visibility()
            return

        if chosen == memory_action:
            text, ok = QInputDialog.getMultiLineText(parent, "Node Memory Block", "Memory", text=node.memory_block)
            if not ok:
                return
            node.memory_block = text.rstrip()
            item = self._node_items.get(node_id.value)
            if item is not None:
                item.update_from_node(node)
            return

        if chosen == clear_memory_action:
            node.memory_block = ""
            item = self._node_items.get(node_id.value)
            if item is not None:
                item.update_from_node(node)
            return

        if chosen == link_story_action:
            path, _ = QFileDialog.getOpenFileName(parent, "Link Story TXT", "", "Text Files (*.txt);;All Files (*)")
            if not path:
                return
            node.story_txt_path = path
            item = self._node_items.get(node_id.value)
            if item is not None:
                item.update_from_node(node)
            return

        if chosen == open_story_action:
            path = (node.story_txt_path or "").strip()
            if not path:
                return
            p = Path(path)
            if not p.exists():
                QMessageBox.warning(parent, "Open Failed", f"File not found:\n{path}")
                return
            ok = QDesktopServices.openUrl(QUrl.fromLocalFile(str(p)))
            if not ok:
                QMessageBox.warning(parent, "Open Failed", f"Could not open file:\n{path}")
            return

        if chosen == clear_story_action:
            node.story_txt_path = None
            item = self._node_items.get(node_id.value)
            if item is not None:
                item.update_from_node(node)
            return

        if chosen == export_action:
            content = build_ai_friendly_prompt(self._graph, node_id)
            default_name = f"export_{node_id.value}.txt"
            path, _ = QFileDialog.getSaveFileName(parent, "Export Prompt", default_name, "Text Files (*.txt);;All Files (*)")
            if not path:
                return
            try:
                Path(path).write_text(content, encoding="utf-8")
            except OSError as exc:
                QMessageBox.critical(parent, "Export Failed", str(exc))
                return
            QMessageBox.information(parent, "Export", "Exported.")
            return

        if chosen == delete_action:
            self._delete_by_ids({node_id.value}, set())
            return

    def _open_edge_menu(self, edge_id: EdgeId, event) -> None:
        parent = event.widget() if hasattr(event, "widget") else None
        menu = QMenu(parent)
        delete_action = menu.addAction("Delete")
        chosen = menu.exec(event.screenPos())
        if chosen is None:
            return
        if chosen == delete_action:
            self._delete_by_ids(set(), {edge_id.value})

    def _delete_selected(self) -> None:
        node_ids: set[str] = set()
        edge_ids: set[str] = set()
        for item in self.selectedItems():
            if isinstance(item, NodeItem):
                node_ids.add(item.node_id.value)
            elif isinstance(item, EdgeItem):
                edge_ids.add(item.edge_id.value)
        self._delete_by_ids(node_ids, edge_ids)

    def _delete_by_ids(self, node_ids: set[str], edge_ids: set[str]) -> None:
        snapshot = delete_nodes_and_edges(self._graph, node_ids, edge_ids)
        if not snapshot.nodes and not snapshot.edges:
            return

        for edge in snapshot.edges:
            edge_item = self._edge_items.pop(edge.id.value, None)
            if edge_item is not None:
                self.removeItem(edge_item)

        for node in snapshot.nodes:
            node_item = self._node_items.pop(node.id.value, None)
            if node_item is not None:
                self.removeItem(node_item)
            if self._connect_source is not None and self._connect_source.value == node.id.value:
                self._connect_source = None

        self._undo_stack.append(snapshot)
        self.refresh_visibility()
        self.update()

    def _undo_delete(self) -> None:
        if not self._undo_stack:
            return
        snapshot = self._undo_stack.pop()
        undo_delete(self._graph, snapshot)

        for node in snapshot.nodes:
            if node.id.value not in self._node_items:
                self._add_node_item(node)

        for edge in snapshot.edges:
            if edge.id.value not in self._edge_items:
                self._add_edge_item(edge)

        for edge_item in self._edge_items.values():
            edge_item.update_path()
        self.refresh_visibility()
        self.update()

    def _add_node_item(self, node: Node) -> None:
        item = NodeItem(node=node, cfg=self._cfg)
        item.setPos(node.x, node.y)
        self.addItem(item)
        self._node_items[node.id.value] = item

    def _add_edge_item(self, edge: Edge) -> None:
        source_item = self._node_items.get(edge.source.value)
        target_item = self._node_items.get(edge.target.value)
        if source_item is None or target_item is None:
            return
        curve_map = compute_parallel_edge_indices(self._graph.iter_edges())
        curve_index = curve_map.get(edge.id.value, 0)
        item = EdgeItem(edge=edge, source_item=source_item, target_item=target_item, cfg=self._cfg)
        item.sync_from_edge(edge, self._edge_collapsed_label(edge), curve_index)
        self.addItem(item)
        self._edge_items[edge.id.value] = item

    def _edge_collapsed_label(self, edge: Edge) -> str:
        target = self._graph.nodes.get(edge.target.value)
        if target is None:
            return ""
        note = (target.note or "").strip()
        if not note:
            note = "----"
        if len(note) > 12:
            note = note[:12] + "…"
        return note

    def _toggle_edge_collapsed(self, edge_id: EdgeId) -> None:
        edge = self._graph.edges.get(edge_id.value)
        if edge is None:
            return
        edge.collapsed = not edge.collapsed
        item = self._edge_items.get(edge_id.value)
        if item is not None:
            item.sync_from_edge(edge, self._edge_collapsed_label(edge))
        self.refresh_visibility()

    def contextMenuEvent(self, event) -> None:
        super().contextMenuEvent(event)
        if event.isAccepted():
            return

        menu = QMenu()
        new_node_action = menu.addAction("New Node Here")
        chosen = menu.exec(event.screenPos())
        
        if chosen == new_node_action:
            pos = event.scenePos()
            node = Node(
                id=NodeId.new(),
                text="",
                event_date=None,
                x=pos.x(),
                y=pos.y()
            )
            self._graph.add_node(node)
            self._add_node_item(node)
            self.refresh_visibility()

    def _on_node_moved(self, node_id: NodeId, pos: QPointF) -> None:
        node = self._graph.get_node(node_id)
        node.x = float(pos.x())
        node.y = float(pos.y())
        for edge in self._graph.iter_edges():
            if edge.source == node_id or edge.target == node_id:
                item = self._edge_items.get(edge.id.value)
                if item is not None:
                    item.update_path()

    def mousePressEvent(self, event) -> None:
        item = self.itemAt(event.scenePos(), self.views()[0].transform()) if self.views() else None
        if self._connect_mode and isinstance(item, NodeItem) and event.button() == Qt.LeftButton:
            if self._connect_source is None:
                self._connect_source = item.node_id
            else:
                if self._connect_source != item.node_id:
                    edge = Edge(id=EdgeId.new(), source=self._connect_source, target=item.node_id)
                    self._graph.add_edge(edge)
                    self._add_edge_item(edge)
                    self.refresh_visibility()
                self._connect_source = None
            event.accept()
            return
        super().mousePressEvent(event)

    def refresh_visibility(self) -> None:
        curve_map = compute_parallel_edge_indices(self._graph.iter_edges())
        visible_nodes = compute_visible_nodes(self._graph)
        for node_id, item in self._node_items.items():
            item.setVisible(node_id in visible_nodes)
        for edge_id, item in self._edge_items.items():
            edge = self._graph.edges.get(edge_id)
            if edge is None:
                item.setVisible(False)
                continue
            source_visible = item.source_id.value in visible_nodes
            target_visible = item.target_id.value in visible_nodes
            is_visible = source_visible and (target_visible or edge.collapsed)
            item.setVisible(is_visible)
            if is_visible:
                item.sync_from_edge(edge, self._edge_collapsed_label(edge), curve_map.get(edge_id, 0))

    def refresh(self) -> None:
        for item in self._node_items.values():
            node = self._graph.get_node(item.node_id)
            item.update_from_node(node)
        self.refresh_visibility()




class GraphView(QGraphicsView):
    def __init__(self, scene: GraphScene) -> None:
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def wheelEvent(self, event) -> None:
        if event.modifiers() & Qt.ControlModifier:
            angle = event.angleDelta().y()
            if angle == 0:
                event.accept()
                return
            factor = 1.15 if angle > 0 else 1 / 1.15
            self.scale(factor, factor)
            event.accept()
            return
        super().wheelEvent(event)

    def keyPressEvent(self, event) -> None:
        key = event.key()
        if key in (Qt.Key_W, Qt.Key_A, Qt.Key_S, Qt.Key_D):
            # Dynamic scroll: Check if we are near the edge and need to expand scene rect?
            # Actually, since we removed setSceneRect, QGraphicsView should handle it?
            # No, without setSceneRect, it fits the items. But we want to pan infinitely.
            # So we just scroll the scrollbars.
            
            step = 50
            if event.modifiers() & Qt.ShiftModifier:
                step = 120
            if key == Qt.Key_W:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - step)
            elif key == Qt.Key_S:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() + step)
            elif key == Qt.Key_A:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - step)
            elif key == Qt.Key_D:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + step)
            event.accept()
            return

        if event.key() == Qt.Key_Delete:
            scene = self.scene()
            if isinstance(scene, GraphScene):
                scene._delete_selected()
            event.accept()
            return

        if event.matches(QKeySequence.Undo):
            scene = self.scene()
            if isinstance(scene, GraphScene):
                scene._undo_delete()
            event.accept()
            return
        super().keyPressEvent(event)


class LegendDockWidget(QDockWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__("Legend", parent)
        self._graph: Optional[Graph] = None
        self._updating = False

        body = QWidget(self)
        layout = QVBoxLayout()

        self._table = QTableWidget(0, 2, body)
        self._table.setHorizontalHeaderLabels(["Color", "Label"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        self._table.cellChanged.connect(self._on_cell_changed)

        buttons = QWidget(body)
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        self._add_btn = QPushButton("Add", buttons)
        self._remove_btn = QPushButton("Remove", buttons)
        self._add_btn.clicked.connect(self._add_color)
        self._remove_btn.clicked.connect(self._remove_selected)
        btn_layout.addWidget(self._add_btn)
        btn_layout.addWidget(self._remove_btn)
        buttons.setLayout(btn_layout)

        layout.addWidget(self._table)
        layout.addWidget(buttons)
        body.setLayout(layout)
        self.setWidget(body)

    def set_graph(self, graph: Graph) -> None:
        self._graph = graph
        self.refresh()

    def refresh(self) -> None:
        if self._graph is None:
            return
        self._updating = True
        try:
            items = sorted(self._graph.legend.items(), key=lambda kv: kv[0])
            self._table.setRowCount(len(items))
            for row, (color, label) in enumerate(items):
                color_item = QTableWidgetItem(color)
                color_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                qc = QColor(color)
                if qc.isValid():
                    color_item.setBackground(QBrush(qc))
                self._table.setItem(row, 0, color_item)

                label_item = QTableWidgetItem(label)
                label_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
                self._table.setItem(row, 1, label_item)
        finally:
            self._updating = False

    def _on_cell_changed(self, row: int, column: int) -> None:
        if self._updating or self._graph is None:
            return
        if column != 1:
            return
        color_item = self._table.item(row, 0)
        label_item = self._table.item(row, 1)
        if color_item is None or label_item is None:
            return
        color = color_item.text()
        label = label_item.text().strip()
        self._graph.legend[color] = label

    def _add_color(self) -> None:
        if self._graph is None:
            return
        color = QColorDialog.getColor(QColor(250, 250, 250), self, "Add Legend Color")
        if not color.isValid():
            return
        name = color.name()
        if name not in self._graph.legend:
            self._graph.legend[name] = ""
        self.refresh()

    def _remove_selected(self) -> None:
        if self._graph is None:
            return
        selected = self._table.currentRow()
        if selected < 0:
            return
        color_item = self._table.item(selected, 0)
        if color_item is None:
            return
        color = color_item.text()
        self._graph.legend.pop(color, None)
        self.refresh()


class DocumentDockWidget(QDockWidget):
    def __init__(self, title: str, parent: QWidget, getter: Callable[[Graph], str], setter: Callable[[Graph, str], None]) -> None:
        super().__init__(title, parent)
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self._collapsed = False
        self._graph: Optional[Graph] = None
        self._updating = False
        self._getter = getter
        self._setter = setter
        self._import_action: Optional[QAction] = None

        self._title_bar = QWidget(self)
        self._title_layout = QHBoxLayout()
        self._title_layout.setContentsMargins(6, 0, 6, 0)
        self._title_layout.setSpacing(6)
        self._toggle_btn = QToolButton(self._title_bar)
        self._toggle_btn.setArrowType(Qt.DownArrow)
        self._toggle_btn.setText("")
        self._toggle_btn.setCheckable(True)
        self._toggle_btn.setChecked(True)
        self._toggle_btn.toggled.connect(self._set_expanded)
        self._title_layout.addWidget(self._toggle_btn)
        self._title_label = QLabel(title, self._title_bar)
        self._title_layout.addWidget(self._title_label, 1)
        self._title_bar.setLayout(self._title_layout)
        self.setTitleBarWidget(self._title_bar)

        body = QWidget(self)
        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)

        self._import_btn = QPushButton("Import TXT", body)
        self._import_btn.clicked.connect(self._trigger_import)
        layout.addWidget(self._import_btn)

        self._text = QTextEdit(body)
        self._text.textChanged.connect(self._handle_text_changed)
        layout.addWidget(self._text)

        self._body = body
        self.setWidget(body)
        body.setLayout(layout)

    def _set_expanded(self, expanded: bool) -> None:
        self._collapsed = not expanded
        self._title_label.setVisible(expanded)
        if expanded:
            self._toggle_btn.setText("")
            self._toggle_btn.setArrowType(Qt.DownArrow)
            self._toggle_btn.setFixedSize(18, 18)
            self._title_layout.setContentsMargins(6, 0, 6, 0)
            self._title_layout.setSpacing(6)
            self._title_bar.setMinimumHeight(18)
            self._title_bar.setMaximumHeight(16777215)
        else:
            self._toggle_btn.setArrowType(Qt.NoArrow)
            self._toggle_btn.setText("+")
            self._toggle_btn.setFixedSize(18, 18)
            self._title_layout.setContentsMargins(0, 0, 0, 0)
            self._title_layout.setSpacing(0)
            self._title_bar.setMinimumHeight(18)
            self._title_bar.setMaximumHeight(18)

        self._body.setVisible(expanded)

        bar = self.titleBarWidget()
        bar_h = bar.sizeHint().height() if bar is not None else 24
        if expanded:
            self.setMinimumHeight(0)
            self.setMaximumHeight(16777215)
        else:
            h = int(bar_h + 8)
            self.setMinimumHeight(h)
            self.setMaximumHeight(h)

    def set_handlers(self, import_action: QAction) -> None:
        self._import_action = import_action
        self._text.setContextMenuPolicy(Qt.ActionsContextMenu)
        self._text.addAction(import_action)

    def _trigger_import(self) -> None:
        if self._import_action is not None:
            self._import_action.trigger()

    def set_graph(self, graph: Graph) -> None:
        self._graph = graph
        self.refresh()

    def refresh(self) -> None:
        if self._graph is None:
            return
        self._updating = True
        try:
            self._text.setPlainText(self._getter(self._graph))
        finally:
            self._updating = False

    def _handle_text_changed(self) -> None:
        if self._updating or self._graph is None:
            return
        self._setter(self._graph, self._text.toPlainText())


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Event Node Graph")

        self._cfg = UiConfig()
        self._graph = Graph()
        self._scene = GraphScene(self._graph, self._cfg)
        self._view = GraphView(self._scene)
        self.setCentralWidget(self._view)

        self._import_system_prompt_action = QAction("Import TXT", self)
        self._import_system_prompt_action.triggered.connect(self._import_system_prompt)
        self._import_world_document_action = QAction("Import TXT", self)
        self._import_world_document_action.triggered.connect(self._import_world_document)

        self._prompt_dock = DocumentDockWidget(
            "System Prompt",
            self,
            getter=lambda g: g.system_prompt,
            setter=lambda g, s: setattr(g, "system_prompt", s),
        )
        self._prompt_dock.set_handlers(self._import_system_prompt_action)
        self._prompt_dock.set_graph(self._graph)
        self.addDockWidget(Qt.LeftDockWidgetArea, self._prompt_dock)

        self._world_dock = DocumentDockWidget(
            "World Document",
            self,
            getter=lambda g: g.world_document,
            setter=lambda g, s: setattr(g, "world_document", s),
        )
        self._world_dock.set_handlers(self._import_world_document_action)
        self._world_dock.set_graph(self._graph)
        self.splitDockWidget(self._prompt_dock, self._world_dock, Qt.Vertical)

        self._legend_dock = LegendDockWidget(self)
        self._legend_dock.set_graph(self._graph)
        self.addDockWidget(Qt.RightDockWidgetArea, self._legend_dock)
        self._scene.legendChanged.connect(self._legend_dock.refresh)

        self._current_project_path: Optional[str] = None
        self._connect_action: Optional[QAction] = None

        self._init_toolbar()

        self._scene.selectionChanged.connect(self._on_selection_changed)

    def _init_toolbar(self) -> None:
        tb = QToolBar("Tools")
        self.addToolBar(tb)
        
        # --- File/Edit Actions ---

        new_node_action = QAction("New Node", self)
        new_node_action.triggered.connect(self._new_node)
        tb.addAction(new_node_action)

        self._connect_action = QAction("Connect", self)
        self._connect_action.setCheckable(True)
        self._connect_action.triggered.connect(self._toggle_connect_mode)
        tb.addAction(self._connect_action)

        edit_action = QAction("Edit", self)
        edit_action.triggered.connect(self._edit_selected_node)
        tb.addAction(edit_action)

        tb.addSeparator()

        import_action = QAction("Import TXT", self)
        import_action.triggered.connect(self._import_txt)
        tb.addAction(import_action)

        layout_action = QAction("Auto Layout", self)
        layout_action.triggered.connect(self._auto_layout)
        tb.addAction(layout_action)

        tb.addSeparator()

        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self._save)
        tb.addAction(save_action)

        save_as_action = QAction("Save As", self)
        save_as_action.triggered.connect(self._save_as)
        tb.addAction(save_as_action)

        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self._open)
        tb.addAction(open_action)

        tb.addSeparator()

        # --- View Actions ---

        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(lambda: self._view.scale(1.2, 1.2))
        tb.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(lambda: self._view.scale(1 / 1.2, 1 / 1.2))
        tb.addAction(zoom_out_action)

        zoom_reset_action = QAction("Reset Zoom", self)
        zoom_reset_action.triggered.connect(self._reset_zoom)
        tb.addAction(zoom_reset_action)
        
        goto_start_action = QAction("Go to Start", self)
        goto_start_action.triggered.connect(self._goto_earliest)
        tb.addAction(goto_start_action)

        tb.addSeparator()
        
        settings_action = QAction("Display Settings", self)
        settings_action.triggered.connect(self._open_display_settings)
        tb.addAction(settings_action)

        if hasattr(self, "_legend_dock"):
            tb.addAction(self._legend_dock.toggleViewAction())
            
    def _goto_earliest(self) -> None:
        if not self._graph.nodes:
            return
            
        # Find node with earliest date (or just any node if none have dates)
        earliest_node: Optional[Node] = None
        for node in self._graph.iter_nodes():
            if node.event_date is None:
                continue
            if earliest_node is None:
                earliest_node = node
            elif earliest_node.event_date is None:
                 earliest_node = node
            elif node.event_date < earliest_node.event_date:
                earliest_node = node
                
        if earliest_node is None:
            # Fallback to just the first node if no dates
            earliest_node = next(iter(self._graph.iter_nodes()), None)
            
        if earliest_node:
            item = self._scene._node_items.get(earliest_node.id.value)
            if item:
                self._view.centerOn(item)
    
    def _toggle_date_format(self) -> None:
        if self._cfg.date_display_format == "date":
            self._cfg.date_display_format = "datetime"
        else:
            self._cfg.date_display_format = "date"
        self._scene.refresh()

    def _open_display_settings(self) -> None:
        dialog = DisplaySettingsDialog(self, self._cfg)
        if dialog.exec() != QDialog.Accepted:
            return
        date_fmt, node_radius, edge_width = dialog.get_values()
        self._cfg.date_display_format = date_fmt
        self._cfg.node_radius = node_radius
        self._cfg.edge_width = edge_width
        self._scene.refresh()

    def _reset_zoom(self) -> None:
        self._view.resetTransform()

    def _toggle_connect_mode(self) -> None:
        enabled = bool(self._connect_action and self._connect_action.isChecked())
        self._scene.set_connect_mode(enabled)

    def _new_node(self) -> None:
        node = Node(id=NodeId.new(), text="", event_date=None, x=100.0, y=100.0)
        self._graph.add_node(node)
        self._scene._add_node_item(node)
        self._scene.refresh_visibility()

    def _selected_node_item(self) -> Optional[NodeItem]:
        for item in self._scene.selectedItems():
            if isinstance(item, NodeItem):
                return item
        return None

    def _edit_selected_node(self) -> None:
        item = self._selected_node_item()
        if item is None:
            return
        node = self._graph.get_node(item.node_id)
        dialog = NodeEditDialog(self, node)
        try:
            accepted = dialog.exec() == QDialog.Accepted
        except ValueError:
            QMessageBox.warning(self, "Invalid Date", "Date must be YYYY-MM-DD")
            return
        if not accepted:
            return
        try:
            new_date, new_text = dialog.get_values()
        except ValueError:
            QMessageBox.warning(self, "Invalid Date", "Date must be YYYY-MM-DD")
            return
        node.event_date = new_date
        node.text = new_text
        item.update_from_node(node)

    def _on_selection_changed(self) -> None:
        pass

    def _import_txt(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Import TXT", "", "Text Files (*.txt);;All Files (*)"
        )
        if not path:
            return

        try:
            new_graph = import_txt_file(path, self._graph)
            
            new_node_ids = list(new_graph.nodes.keys())
            
            for node in new_graph.iter_nodes():
                self._graph.add_node(node)
                self._scene._add_node_item(node)
            
            assign_default_layout_for_new_nodes(self._graph, new_node_ids)

            for nid in new_node_ids:
                node = self._graph.nodes.get(nid)
                item = self._scene._node_items.get(nid)
                if node is not None and item is not None:
                    item.setPos(node.x, node.y)
            for edge_item in self._scene._edge_items.values():
                edge_item.update_path()
            
            self._scene.refresh_visibility()
            self._scene.update()
            
            count = len(new_node_ids)
            if count == 0:
                 QMessageBox.information(self, "Import", "No new nodes were imported (duplicates skipped).")
            else:
                 QMessageBox.information(self, "Import", f"Imported {count} new nodes.")

        except ImportErrorDetail as e:
            QMessageBox.critical(self, "Import Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Unexpected error: {e}")

    def _auto_layout(self) -> None:
        assign_default_layout(self._graph)
        for node in self._graph.iter_nodes():
            item = self._scene._node_items.get(node.id.value)
            if item is not None:
                item.setPos(node.x, node.y)
        for edge_item in self._scene._edge_items.values():
            edge_item.update_path()

    def _save(self) -> None:
        if self._current_project_path is None:
            self._save_as()
            return
        try:
            save_project(self._current_project_path, self._graph)
        except Exception as exc:
            QMessageBox.critical(self, "Save Failed", str(exc))

    def _save_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "JSON Files (*.json);;All Files (*)")
        if not path:
            return
        self._current_project_path = path
        self._save()

    def _open(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open Project", "", "JSON Files (*.json);;All Files (*)")
        if not path:
            return
        try:
            graph = load_project(path)
        except Exception as exc:
            QMessageBox.critical(self, "Open Failed", str(exc))
            return
        self._current_project_path = path
        self._graph = graph
        self._scene.load_graph(self._graph)
        self._legend_dock.set_graph(self._graph)
        self._prompt_dock.set_graph(self._graph)
        self._world_dock.set_graph(self._graph)

    def _read_text_file(self, path: str) -> str:
        try:
            try:
                with open(path, "r", encoding="utf-8-sig") as f:
                    return f.read()
            except UnicodeDecodeError:
                with open(path, "r", encoding="gb18030") as f:
                    return f.read()
        except OSError as exc:
            raise RuntimeError(f"Failed to read file: {path}") from exc

    def _import_system_prompt(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Import System Prompt", "", "Text Files (*.txt);;All Files (*)")
        if not path:
            return
        try:
            self._graph.system_prompt = self._read_text_file(path)
        except Exception as exc:
            QMessageBox.critical(self, "Import Failed", str(exc))
            return
        self._prompt_dock.refresh()

    def _import_world_document(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Import World Document", "", "Text Files (*.txt);;All Files (*)")
        if not path:
            return
        try:
            self._graph.world_document = self._read_text_file(path)
        except Exception as exc:
            QMessageBox.critical(self, "Import Failed", str(exc))
            return
        self._world_dock.refresh()


def run_app() -> None:
    app = QApplication([])
    tooltip_font = QFont()
    tooltip_font.setPointSize(12)
    QToolTip.setFont(tooltip_font)
    window = MainWindow()
    window.resize(1200, 800)
    window.show()
    app.exec()


class LegendDockWidget(QDockWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__("Legend", parent)
        self._graph: Optional[Graph] = None
        self._updating = False

        body = QWidget(self)
        layout = QVBoxLayout()

        self._table = QTableWidget(0, 2, body)
        self._table.setHorizontalHeaderLabels(["Color", "Label"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        self._table.cellChanged.connect(self._on_cell_changed)

        buttons = QWidget(body)
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        self._add_btn = QPushButton("Add", buttons)
        self._remove_btn = QPushButton("Remove", buttons)
        self._add_btn.clicked.connect(self._add_color)
        self._remove_btn.clicked.connect(self._remove_selected)
        btn_layout.addWidget(self._add_btn)
        btn_layout.addWidget(self._remove_btn)
        buttons.setLayout(btn_layout)

        layout.addWidget(self._table)
        layout.addWidget(buttons)
        body.setLayout(layout)
        self.setWidget(body)

    def set_graph(self, graph: Graph) -> None:
        self._graph = graph
        self.refresh()

    def refresh(self) -> None:
        if self._graph is None:
            return
        self._updating = True
        try:
            items = sorted(self._graph.legend.items(), key=lambda kv: kv[0])
            self._table.setRowCount(len(items))
            for row, (color, label) in enumerate(items):
                color_item = QTableWidgetItem(color)
                color_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                qc = QColor(color)
                if qc.isValid():
                    color_item.setBackground(QBrush(qc))
                self._table.setItem(row, 0, color_item)

                label_item = QTableWidgetItem(label)
                self._table.setItem(row, 1, label_item)
        finally:
            self._updating = False

    def _on_cell_changed(self, row: int, column: int) -> None:
        if self._updating or self._graph is None:
            return
        if column != 1:
            return
        color_item = self._table.item(row, 0)
        label_item = self._table.item(row, 1)
        if color_item is None or label_item is None:
            return
        color = color_item.text()
        label = label_item.text().strip()
        self._graph.legend[color] = label

    def _add_color(self) -> None:
        if self._graph is None:
            return
        color = QColorDialog.getColor(QColor(250, 250, 250), self, "Add Legend Color")
        if not color.isValid():
            return
        name = color.name()
        if name not in self._graph.legend:
            self._graph.legend[name] = ""
        self.refresh()

    def _remove_selected(self) -> None:
        if self._graph is None:
            return
        selected = self._table.currentRow()
        if selected < 0:
            return
        color_item = self._table.item(selected, 0)
        if color_item is None:
            return
        color = color_item.text()
        self._graph.legend.pop(color, None)
        self.refresh()
