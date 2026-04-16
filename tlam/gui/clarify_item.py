from PySide6.QtCore import Signal
from PySide6.QtGui import QStandardItemModel, Qt
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QListView, QPushButton, QWidget

from tlam.core.record import TaskRecord
from tlam.gui import const


class ClarifyItemWidget(QWidget):
    """Item for clarify list widget"""

    clarified_sig = Signal(str, str)
    delete_sig = Signal(str)

    def __init__(
        self,
        thought: TaskRecord,
        thought_list_view: QListView,
        thought_model: QStandardItemModel,
        parent=None,
    ):
        super().__init__(parent)

        self.though = thought

        self.though_model = thought_model
        self.thought_list_view = thought_list_view

        self.lineEdit = QLineEdit()
        self.lineEdit.setText(thought.task_title)
        self.lineEdit.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.deleteBtn = QPushButton(const.DELETE_ICON)
        self.deleteBtn.clicked.connect(self.on_delete_btn_clicked)

        self.clarfiedBtn = QPushButton(const.APPROVE_ICON)
        self.clarfiedBtn.clicked.connect(self.on_clarified_btn_clicked)

        layout = QHBoxLayout(self)
        layout.addWidget(self.lineEdit, stretch=1)
        layout.addWidget(self.deleteBtn)
        layout.addWidget(self.clarfiedBtn)

    def delete_this_item(self):
        index = self.thought_list_view.indexAt(self.pos())
        if index.isValid():
            self.though_model.removeRow(index.row())

    def on_delete_btn_clicked(self):
        self.delete_this_item()
        self.delete_sig.emit(str(self.though.task_id))

    def on_clarified_btn_clicked(self):
        self.delete_this_item()
        self.clarified_sig.emit(str(self.though.task_id), self.lineEdit.text().strip())
