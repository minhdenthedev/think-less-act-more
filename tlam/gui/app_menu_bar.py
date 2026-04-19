from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMenu, QMenuBar, QInputDialog

from tlam.gui.database_worker import DatabaseWorker
from tlam.gui.projects_dialog import ProjectsDialog


class AppMenuBar(QMenuBar):
    """Menu bar of the application"""

    add_project_sig = Signal(str, str)

    def __init__(self, database_worker: DatabaseWorker, parent=None):
        super().__init__(parent)

        # --- FILE ---
        self.file_menu = QMenu("&File")
        new_data_action = QAction("&New", self)
        new_data_action.setShortcut(QKeySequence.StandardKey.New)
        open_data_action = QAction("&Open...", self)
        open_data_action.setShortcut(QKeySequence.StandardKey.Open)
        export_data_action = QAction("&Export data", self)
        export_data_action.setShortcut("Ctrl+E")
        close_action = QAction("Quit", self)
        close_action.setShortcut(QKeySequence.StandardKey.Close)
        self.file_menu.addAction(new_data_action)
        self.file_menu.addAction(open_data_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(export_data_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(close_action)
        # ------------

        # --- PROJECTS ---
        self.projects_menu = QMenu("&Projects")
        new_project_action = QAction("&New project", self)
        new_project_action.triggered.connect(self.on_new_project_action_triggered)
        view_projects_action = QAction("&View projects", self)
        view_projects_action.setShortcut("Ctrl+P")
        view_projects_action.triggered.connect(self.on_view_projects_action_triggered)
        delete_project_action = QAction("&Delete project", self)
        edit_project_action = QAction("&Edit project", self)
        self.projects_menu.addAction(new_project_action)
        self.projects_menu.addAction(view_projects_action)
        self.projects_menu.addAction(delete_project_action)
        self.projects_menu.addAction(edit_project_action)
        # ----------------

        # --- SETTINGS ---
        self.settings_menu = QMenu("&Settings")
        # ----------------

        # --- HELP ---
        self.help_menu = QMenu("&Help")
        about_action = QAction("About", self)
        self.help_menu.addAction(about_action)
        # ------------

        self.addMenu(self.file_menu)
        self.addMenu(self.projects_menu)
        self.addMenu(self.settings_menu)
        self.addMenu(self.help_menu)

        self.database_worker = database_worker

        self.add_project_sig.connect(self.database_worker.add_project)

    def on_view_projects_action_triggered(self):
        dialog = ProjectsDialog(self.database_worker, self)
        dialog.exec()

    def on_new_project_action_triggered(self):
        name, ok = QInputDialog.getText(self, "New Project", "Enter project name:")

        if ok and name.strip():
            self.add_project_sig.emit(name, None)
