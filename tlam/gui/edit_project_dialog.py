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

from tlam.core.record import ProjectRecord
from tlam.gui.database_worker import DatabaseWorker


class EditProjectDialog(QDialog):
    """
    Dialog to add and edit project
    """
    
    edit_project_sig = Signal(object)

    def __init__(self, project: ProjectRecord, database_worker: DatabaseWorker, parent=None):
        super().__init__(parent)
        
        self.project = project
        
        self.setWindowTitle("Edit a project")
        availabe_geom = self.screen().availableGeometry()
        self.resize(availabe_geom.width() // 6, 50)

        self.database_worker = database_worker
        self.edit_project_sig.connect(self.database_worker.update_project)
        
        form_layout = QFormLayout()

        self.icon_edit = QLineEdit(project.icon)
        self.icon_edit.setToolTip("Set icon for your project. UTF-8 icons are supported.")

        self.name_edit = QLineEdit(project.project_name)
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
        self.project.icon = self.icon_edit.text()
        self.project.project_name = self.name_edit.text()
        self.edit_project_sig.emit(self.project)
        super().accept()
