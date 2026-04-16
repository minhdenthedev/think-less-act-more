from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListView,
    QPushButton,
    QWidget,
)
from typing import List

from tlam.core.record import ProjectRecord, TaskRecord
from tlam.gui import const


class OrganizeItemWidget(QWidget):
    """Widget for organize item in a list view"""

    organize_sig = Signal(str, str)

    def __init__(
        self,
        action: TaskRecord,
        list_view: QListView,
        model: QStandardItemModel,
        projects: List[ProjectRecord] = [],
        parent=None,
    ):
        super().__init__(parent)

        self.list_view = list_view
        self.model = model

        self.label = QLabel(action.task_title)

        self.project_model = QStandardItemModel()
        self.combo_box = QComboBox()
        self.combo_box.setModel(self.project_model)

        for p in projects:
            item = QStandardItem(p.icon + " " + p.project_name)
            item.setData(p, Qt.ItemDataRole.UserRole)
            self.project_model.appendRow(item)

        self.ok_button = QPushButton(const.APPROVE_ICON)
        self.ok_button.clicked.connect(self.on_ok_button_clicked)

        layout = QHBoxLayout(self)
        layout.addWidget(self.label, stretch=1)
        layout.addWidget(self.combo_box)
        layout.addWidget(self.ok_button)

        self.task = action
        self.projects = projects

    def delete_this_item(self):
        index = self.list_view.indexAt(self.pos())
        if index.isValid():
            self.model.removeRow(index.row())

    def on_ok_button_clicked(self):
        self.delete_this_item()
        project = self.combo_box.currentData(Qt.ItemDataRole.UserRole)
        self.organize_sig.emit(str(self.task.task_id), str(project.project_id))
