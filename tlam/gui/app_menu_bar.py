from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMenu, QMenuBar, QInputDialog, QDialog

from tlam.gui.add_project_dialog import AddProjectDialog
from tlam.gui.database_worker import DatabaseWorker
from tlam.gui.projects_dialog import ProjectsDialog

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

logger = logging.getLogger(__name__)


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
        self.projects_menu.addAction(new_project_action)
        self.projects_menu.addAction(view_projects_action)
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
        logger.info("View projects action triggered")
        dialog = ProjectsDialog(self.database_worker, self)
        _ = dialog.exec()

    def on_new_project_action_triggered(self):
        logger.info("Add project action triggered")
        dialog = AddProjectDialog(self.database_worker, self)
        _ = dialog.exec()
