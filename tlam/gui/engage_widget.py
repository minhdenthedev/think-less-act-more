from typing import List
from PySide6.QtCore import QItemSelection, Qt, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QFrame,
    QLabel,
    QPushButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from tlam.core.record import TaskRecord
from tlam.gui.database_worker import DatabaseWorker


class EngagingPanel(QFrame):
    """Frame for engaging panel"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_task_label = QLabel("You are not engaging any task.")
        self.remind_label = QLabel("Pick a task from above and press 'Engage'.")

        layout = QVBoxLayout(self)
        layout.addWidget(self.current_task_label)
        layout.addWidget(self.remind_label)


class EngageWidget(QWidget):
    """Widget for engage page"""

    fetch_projects_sig = Signal()
    fetch_tasks_sig = Signal()

    def __init__(self, database_worker: DatabaseWorker, parent=None):
        super().__init__(parent)

        self.project_tree_items = {}

        self.engaging_panel = EngagingPanel(self)

        self.model = QStandardItemModel()
        self.root = self.model.invisibleRootItem()
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.selectionModel().selectionChanged.connect(self.on_item_selected)

        self.dialog_btn_box = QDialogButtonBox()
        self.engage_btn = QPushButton("Engage")
        self.engage_btn.setEnabled(False)
        self.dialog_btn_box.addButton(
            self.engage_btn, QDialogButtonBox.ButtonRole.ActionRole
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self.tree_view)
        layout.addWidget(self.engaging_panel)
        layout.addWidget(self.dialog_btn_box)

        self.database_worker = database_worker
        self.database_worker.projects_fetched_sig.connect(self.on_projects_fetched)
        self.database_worker.organized_fetched_sig.connect(
            self.on_organized_tasks_fetched
        )

        self.fetch_projects_sig.connect(self.database_worker.fetch_projects)
        self.fetch_tasks_sig.connect(self.database_worker.fetch_organized_tasks)

    def on_item_selected(self, selected: QItemSelection, deselected: QItemSelection):
        indexes = selected.indexes()

        if indexes:
            index = indexes[0]
            if index.parent().isValid():
                item = self.model.itemFromIndex(index)
                self.engaging_panel.current_task_label.setText(
                    f"Selected: {item.text()}"
                )
                self.engaging_panel.remind_label.setText(
                    "Press 'Engage' to engage this task."
                )
                self.engage_btn.setEnabled(True)
            else:
                self.engaging_panel.current_task_label.setText(
                    "You are not engaging any task."
                )
                self.engaging_panel.remind_label.setText(
                    "Pick a task from above and press 'Engage'."
                )
                self.engage_btn.setEnabled(False)

    def on_projects_fetched(self, projects):
        for project in projects:
            parent = QStandardItem(project.project_name)
            parent.setEditable(False)
            parent.setData(project, Qt.ItemDataRole.UserRole)
            self.root.appendRow(parent)
            self.project_tree_items[project.project_id] = parent
        self.fetch_tasks_sig.emit()

    def on_organized_tasks_fetched(self, tasks: List[TaskRecord]):
        for task in tasks:
            child = QStandardItem(task.task_title)
            child.setEditable(False)
            child.setData(task, Qt.ItemDataRole.UserRole)
            parent: QStandardItem = self.project_tree_items[task.project_id]
            parent.appendRow(child)

    def refresh_data(self):
        self.model.clear()
        self.root = self.model.invisibleRootItem()
        self.fetch_projects_sig.emit()
