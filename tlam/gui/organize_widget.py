from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QAbstractItemView,
    QListView,
    QVBoxLayout,
    QWidget,
    QDialogButtonBox,
)
from PySide6.QtCore import QSize, Signal

from tlam.gui.database_worker import DatabaseWorker
from tlam.gui.organize_item import OrganizeItemWidget

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

logger = logging.getLogger(__name__)


class OrganizeWidget(QWidget):
    """Widget for organize page"""

    fetch_actions_sig = Signal()
    fetch_projects_sig = Signal()
    organize_action_sig = Signal(str, str)

    def __init__(self, database_worker: DatabaseWorker, parent=None):
        super().__init__(parent)

        self.action_model = QStandardItemModel()
        self.list_view = QListView()
        self.list_view.setModel(self.action_model)
        self.list_view.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        self.database_worker = database_worker
        self.database_worker.projects_fetched_sig.connect(self.on_projects_fetched)
        self.database_worker.clarified_fetched_sig.connect(self.on_actions_fetched)
        self.database_worker.data_changed_sig.connect(self.refresh_data)

        self.fetch_projects_sig.connect(self.database_worker.fetch_projects)
        self.fetch_actions_sig.connect(self.database_worker.fetch_clarified_tasks)

        self.dialog_btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.SaveAll)

        layout = QVBoxLayout(self)
        layout.addWidget(self.list_view)
        layout.addWidget(self.dialog_btn_box)

        self.projects = []

    def display_actions(self, actions):
        logger.info("Display actions")
        self.action_model.clear()
        for a in actions:
            item = QStandardItem()
            item.setSizeHint(QSize(0, 40))
            self.action_model.appendRow(item)

            index = item.index()
            organize_widget = OrganizeItemWidget(
                action=a,
                projects=self.projects,
                list_view=self.list_view,
                model=self.action_model,
            )
            organize_widget.organize_sig.connect(self.database_worker.organize_action)
            self.list_view.setIndexWidget(index, organize_widget)

    def on_projects_fetched(self, projects):
        logger.info("on projects fetched")
        self.projects = projects
        self.fetch_actions_sig.emit()
        logger.debug("fetch actions emitted")

    def on_actions_fetched(self, actions):
        logger.info("on actions fetched")
        self.display_actions(actions)

    def refresh_data(self):
        self.fetch_projects_sig.emit()
        logger.debug("fetch projects emitted.")
