from PySide6.QtCore import QItemSelection
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QFrame,
    QLabel,
    QPushButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
    QApplication,
)
import sys


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

    fake_data = {
        "Next": [
            "Email marketing team regarding Q3 budget",
            "Renew vehicle registration",
            "Fix the broken door handle in the kitchen",
            "Schedule annual dental checkup",
            "Draft project proposal for client X",
        ],
        "Someday/Maybe": [
            "Learn to play the cello",
            "Backpack through Southeast Asia",
            "Start a vegetable garden in the backyard",
            "Take a pottery workshop",
            "Build a custom mechanical keyboard",
        ],
        "Waiting": [
            "Refund from airline for cancelled flight",
            "Feedback on the first draft from Sarah",
            "Package delivery from Amazon (ordered Monday)",
            "Approval for the new hire requisition",
            "Repair estimate from the auto shop",
        ],
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self.engaging_panel = EngagingPanel(self)

        self.model = QStandardItemModel()
        self.root = self.model.invisibleRootItem()
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.selectionModel().selectionChanged.connect(self.on_item_selected)

        for project, tasks in self.fake_data.items():
            parent = QStandardItem(project)
            parent.setEditable(False)
            self.root.appendRow(parent)

            for task in tasks:
                child = QStandardItem(task)
                child.setEditable(False)
                parent.appendRow(child)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = EngageWidget()
    availabe_geom = widget.screen().availableGeometry()
    widget.resize(availabe_geom.width() // 2, availabe_geom.height() // 2)
    widget.show()

    app.exec()
