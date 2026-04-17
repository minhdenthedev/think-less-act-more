import sys
from PySide6.QtCore import QThread
from PySide6.QtWidgets import QApplication, QMainWindow

from tlam.core.services import GTDService
from tlam.gui.app_menu_bar import AppMenuBar
from tlam.gui.database_worker import DatabaseWorker
from tlam.gui.main_tab_widget import MainTabWidget
from tlam.core.gateways import (
    EngagingTaskGateway,
    Initiator,
    ProjectGateway,
    TaskGateway,
)
from tlam.gui.const import DATABASE_PATH

if __name__ == "__main__":
    initiator = Initiator(DATABASE_PATH)
    task_gateway = TaskGateway(DATABASE_PATH)
    project_gateway = ProjectGateway(DATABASE_PATH)
    engagin_task_gateway = EngagingTaskGateway(DATABASE_PATH)

    service = GTDService(initiator, project_gateway, task_gateway, engagin_task_gateway)

    database_worker = DatabaseWorker(service)
    database_thread = QThread(database_worker)
    database_thread.finished.connect(database_worker.deleteLater)

    database_thread.start()

    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Think Less Act More")
    availabe_geom = window.screen().availableGeometry()
    window.resize(availabe_geom.width() // 2, availabe_geom.height() // 2)
    central_widget = MainTabWidget(database_worker, window)
    window.setCentralWidget(central_widget)
    menu_bar = AppMenuBar(database_worker, window)
    window.setMenuBar(menu_bar)

    # database_worker.data_changed_sig.connect(central_widget.refresh_pages)

    window.show()
    app.exec()
