from PySide6.QtWidgets import QTabWidget

from tlam.core.services import GTDService
from tlam.gui.capture_widget import CaptureWidget
from tlam.gui.clarify_widget import ClarifyWidget
from tlam.gui.database_worker import DatabaseWorker
from tlam.gui.engage_widget import EngageWidget
from tlam.gui.organize_widget import OrganizeWidget


class MainTabWidget(QTabWidget):
    """
    Central widget of the application. Switch between pages:
            1. Capture
            2. Clarify
            3. Organize
            4. Engage
            6. Settings

    """

    def __init__(self, database_worker: DatabaseWorker, parent=None):
        super().__init__(parent)

        self.tabs = {
            "Capture": CaptureWidget(database_worker),
            "Clarify": ClarifyWidget(database_worker),
            "Organize": OrganizeWidget(database_worker),
            "Engage": EngageWidget(database_worker),
        }

        self.setup_tabs()

        for tab in self.tabs.values():
            tab.refresh_data()

    def setup_tabs(self):
        for name, widget in self.tabs.items():
            self.addTab(widget, name)
