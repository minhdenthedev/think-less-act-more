from PySide6.QtWidgets import QTabWidget

from tlam.core.services import GTDService
from tlam.gui.capture_widget import CaptureWidget
from tlam.gui.clarify_widget import ClarifyWidget
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

    def __init__(self, service: GTDService, parent=None):
        super().__init__(parent)

        self.tabs = {
            "Capture": CaptureWidget(service),
            "Clarify": ClarifyWidget(service),
            "Organize": OrganizeWidget(service),
            "Engage": EngageWidget(service),
        }

        self.setup_tabs()

        self.currentChanged.connect(self.on_tab_changed)

    def setup_tabs(self):
        for name, widget in self.tabs.items():
            self.addTab(widget, name)

    def on_tab_changed(self, index):
        widget = self.widget(index)
        if hasattr(widget, "refresh_data"):
            widget.refresh_data()  # type: ignore
