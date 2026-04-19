from typing import List
from PySide6.QtCore import QItemSelection, Qt, Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QListView,
    QPushButton,
    QVBoxLayout,
)

from tlam.core.record import ProjectRecord
from tlam.gui.add_project_dialog import AddProjectDialog
from tlam.gui.database_worker import DatabaseWorker
from tlam.gui.edit_project_dialog import EditProjectDialog


class ProjectsDialog(QDialog):
    """
    Dialog to manipulate projects
    """

    fetch_projects_sig = Signal()
    delete_project_sig = Signal(str)

    def __init__(self, database_worker: DatabaseWorker, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Projects")
        availabe_geom = self.screen().availableGeometry()
        self.resize(availabe_geom.width() // 3, availabe_geom.height() // 3)

        self.database_worker = database_worker
        self.database_worker.projects_fetched_sig.connect(self.on_projects_fetched)

        self.fetch_projects_sig.connect(self.database_worker.fetch_projects)
        self.delete_project_sig.connect(self.database_worker.delete_project)

        self.project_model = QStandardItemModel()
        self.list_view = QListView()
        self.list_view.setModel(self.project_model)
        self.list_view.selectionModel().selectionChanged.connect(
            self.on_project_selected
        )

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.on_add_button_clicked)

        self.delete_button = QPushButton("Delete")
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.on_delete_button_clicked)

        self.edit_button = QPushButton("Edit...")
        self.edit_button.setEnabled(False)
        self.edit_button.clicked.connect(self.on_edit_button_clicked)

        button_layout = QVBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addStretch(1)

        self.help_label = QLabel("View and manage your projects.")

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.list_view)
        h_layout.addLayout(button_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)

        layout = QVBoxLayout(self)
        layout.addWidget(self.help_label)
        layout.addLayout(h_layout)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

        self.button_box.rejected.connect(self.reject)

        self.fetch_projects_sig.emit()

    def on_projects_fetched(self, projects: List[ProjectRecord]):
        self.project_model.clear()
        for project in projects:
            item = QStandardItem(project.icon + " " + project.project_name)
            item.setEditable(False)
            item.setData(project, Qt.ItemDataRole.UserRole)
            self.project_model.appendRow(item)

    def on_project_selected(self, selected: QItemSelection, deselected):
        indexes = selected.indexes()

        if indexes:
            index = indexes[0]
            self.delete_button.setEnabled(True)
            self.edit_button.setEnabled(True)

    def on_delete_button_clicked(self):
        selected_index = self.list_view.selectedIndexes()[0]
        project: ProjectRecord = self.project_model.data(
            selected_index, Qt.ItemDataRole.UserRole
        )
        self.delete_project_sig.emit(str(project.project_id))
        row = selected_index.row()
        self.project_model.removeRow(row)
        
    def on_edit_button_clicked(self):
        selected_index = self.list_view.selectedIndexes()[0]
        project: ProjectRecord = self.project_model.data(
            selected_index, Qt.ItemDataRole.UserRole
        )
        dialog = EditProjectDialog(project, self.database_worker, self)
        _ = dialog.exec()
        
    def on_add_button_clicked(self):
        dialog = AddProjectDialog(self.database_worker, self)
        _ = dialog.exec()
