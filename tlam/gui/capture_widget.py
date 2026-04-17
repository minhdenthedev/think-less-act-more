from typing import List
from PySide6.QtCore import Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView,
    QLineEdit,
    QListView,
    QVBoxLayout,
    QWidget,
)

from tlam.core.record import TaskRecord
from tlam.core.services import GTDService
from tlam.gui.database_worker import DatabaseWorker


class CaptureWidget(QWidget):
    """
    Widget for capture page
    """

    fetch_thoughts = Signal()
    add_thought = Signal(str)

    def __init__(self, database_worker: DatabaseWorker, parent=None):
        super().__init__(parent)

        self.thought_list_view = QListView()
        self.thought_list_view.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection
        )
        self.thought_model = QStandardItemModel()
        self.thought_list_view.setModel(self.thought_model)

        self.thought_input_field = QLineEdit()
        self.thought_input_field.setPlaceholderText("What's on your mind?")
        self.thought_input_field.returnPressed.connect(
            self.on_thought_input_field_enter
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self.thought_list_view)
        layout.addWidget(self.thought_input_field)

        self.database_worker = database_worker
        self.database_worker.capture_tasks.connect(self.display_thoughts)
        self.database_worker.data_changed_sig.connect(self.refresh_data)

        self.fetch_thoughts.connect(self.database_worker.fetch_capture_tasks)
        self.add_thought.connect(self.database_worker.add_thought_to_database)

    def on_thought_input_field_enter(self):
        thought = self.thought_input_field.text()
        self.thought_input_field.clear()
        self.add_thought.emit(thought)

    def display_thoughts(self, thoughts: List[TaskRecord]):
        self.thought_model.clear()
        for thought in thoughts:
            item = QStandardItem(thought.task_title)
            item.setEditable(False)
            self.thought_model.appendRow(item)

    def refresh_data(self):
        self.thought_model.clear()
        self.fetch_thoughts.emit()
