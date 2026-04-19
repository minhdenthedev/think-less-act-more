from typing import List
from PySide6.QtCore import QSize, Signal
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

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

logger = logging.getLogger(__name__)


class ClarifyWidget(QWidget):
    """Widget for clarify page"""

    clarify_action_sig = Signal(str, str)
    delete_action_sig = Signal(str)
    fetch_thoughts_sig = Signal()

    def __init__(self, database_worker: DatabaseWorker, parent=None):
        super().__init__(parent)

        self.thought_model = QStandardItemModel()

        self.thought_list_view = QListView()
        self.thought_list_view.setModel(self.thought_model)
        self.thought_list_view.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection
        )

        self.dialog_btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.SaveAll)

        self.database_worker = database_worker
        self.database_worker.capture_tasks.connect(self.display_thoughts)
        self.database_worker.data_changed_sig.connect(self.refresh_data)

        self.fetch_thoughts_sig.connect(self.database_worker.fetch_capture_tasks)
        self.delete_action_sig.connect(self.database_worker.delete_action)
        self.clarify_action_sig.connect(self.database_worker.clarify_action)

        layout = QVBoxLayout(self)
        layout.addWidget(self.thought_list_view)
        layout.addWidget(self.dialog_btn_box)

    def delete_item_from_list_view(self, row):
        logger.info(f"Remove item from list view")
        self.thought_model.removeRow(row)

    def display_thoughts(self, thoughts: List[TaskRecord]):
        logger.info("Display thoughts")
        self.thought_model.clear()
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
        logger.info("Clarify act")
        self.clarify_action_sig.emit(task_id, task_title)
        logger.debug("clarify signal emitted")

    def delete_act(self, task_id):
        logger.info("Delete act")
        self.delete_action_sig.emit(task_id)
        logger.debug("delete signal emitted")

    def refresh_data(self):
        logger.info("Refresh data")
        self.fetch_thoughts_sig.emit()
        logger.debug("fetch thoughts signal emitted.")
