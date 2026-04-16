from typing import List
from PySide6.QtCore import QSize, QThread, Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QAbstractItemView,
    QListView,
    QVBoxLayout,
    QWidget,
    QDialogButtonBox,
)

from tlam.core.record import TaskRecord
from tlam.gui.clarify_item import ClarifyItemWidget
from tlam.gui.database_worker import DatabaseWorker


class ClarifyWidget(QWidget):
    """Widget for clarify page"""

    clarify_action_sig = Signal(str, str)
    delete_action_sig = Signal(str)
    fetch_thoughts_sig = Signal()

    def __init__(self, service, parent=None):
        super().__init__(parent)

        self.thought_model = QStandardItemModel()

        self.thought_list_view = QListView()
        self.thought_list_view.setModel(self.thought_model)
        self.thought_list_view.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection
        )

        self.dialog_btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.SaveAll)

        self.database_worker = DatabaseWorker(service)
        self.database_worker.capture_tasks.connect(self.display_thoughts)

        self.database_thread = QThread()
        self.database_worker.moveToThread(self.database_thread)
        self.database_thread.finished.connect(self.database_worker.deleteLater)
        self.database_thread.started.connect(self.fetch_thoughts_sig.emit)

        self.fetch_thoughts_sig.connect(self.database_worker.fetch_capture_tasks)
        self.delete_action_sig.connect(self.database_worker.delete_action)
        self.clarify_action_sig.connect(self.database_worker.clarify_action)

        self.database_thread.start()

        layout = QVBoxLayout(self)
        layout.addWidget(self.thought_list_view)
        layout.addWidget(self.dialog_btn_box)

    def delete_item_from_list_view(self, row):
        self.thought_model.removeRow(row)

    def display_thoughts(self, thoughts: List[TaskRecord]):
        for t in thoughts:
            item = QStandardItem()
            item.setEditable(False)
            item.setSizeHint(QSize(0, 40))
            self.thought_model.appendRow(item)

            index = item.index()
            clarify_widget = ClarifyItemWidget(
                thought=t,
                thought_list_view=self.thought_list_view,
                thought_model=self.thought_model,
            )
            clarify_widget.clarified_sig.connect(self.clarify_act)
            clarify_widget.delete_sig.connect(self.delete_act)

            self.thought_list_view.setIndexWidget(index, clarify_widget)

    def clarify_act(self, task_id, task_title):
        self.clarify_action_sig.emit(task_id, task_title)

    def delete_act(self, task_id):
        self.delete_action_sig.emit(task_id)

    def refresh_data(self):
        self.thought_model.clear()
        self.fetch_thoughts_sig.emit()
