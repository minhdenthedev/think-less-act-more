from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLineEdit,
    QVBoxLayout,
)

from tlam.gui.database_worker import DatabaseWorker


class AddProjectDialog(QDialog):
    """
    Dialog to add and edit project
    """
    
    add_project_sig = Signal(str, str)

    def __init__(self, database_worker: DatabaseWorker, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add a project")
        availabe_geom = self.screen().availableGeometry()
        self.resize(availabe_geom.width() // 6, 50)

        self.database_worker = database_worker
        self.add_project_sig.connect(self.database_worker.add_project)
        
        form_layout = QFormLayout()

        self.icon_edit = QLineEdit("")
        self.icon_edit.setToolTip("Set icon for your project. UTF-8 icons are supported.")

        self.name_edit = QLineEdit("")
        self.name_edit.setToolTip("Set your project's name")
        
        form_layout.addRow("Project's name:", self.name_edit)
        form_layout.addRow("Icon:", self.icon_edit)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setFocus()
        self.button_box.rejected.connect(self.reject)
        self.button_box.accepted.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(self.button_box)

        self.setLayout(layout)
        
    def accept(self, /) -> None:
        icon = self.icon_edit.text()
        name = self.name_edit.text()
        
        self.add_project_sig.emit(name, icon)
        
        super().accept()
