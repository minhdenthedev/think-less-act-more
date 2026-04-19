from PySide6.QtCore import QObject, Signal
from tlam.core.record import ProjectRecord
from tlam.core.services import GTDService

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

logger = logging.getLogger(__name__)


class DatabaseWorker(QObject):
    """Worker for database operations"""

    capture_tasks = Signal(object)
    clarified_fetched_sig = Signal(object)
    organized_fetched_sig = Signal(object)
    service_clarified_sig = Signal(object)
    projects_fetched_sig = Signal(object)
    data_changed_sig = Signal()

    def __init__(self, service: GTDService):
        super().__init__()
        self.service = service

    # Slot
    def fetch_capture_tasks(self):
        logger.debug("fetch capture tasks")
        tasks = self.service.get_captured_tasks()
        self.capture_tasks.emit(tasks)

    def add_thought_to_database(self, thought):
        logger.debug(f"Add thought: {thought}")
        self.service.capture(thought)
        self.data_changed_sig.emit()
        logger.debug("Data changed signal emitted")


    def delete_action(self, task_id):
        logger.debug(f"Delete action: {task_id}")
        self.service.delete_task(task_id)
        self.data_changed_sig.emit()
        logger.debug("Data changed signal emitted")


    def clarify_action(self, task_id, task_title):
        logger.debug(f"Clarify action: {task_id, task_title}")
        self.service.clarify(task_id, task_title)
        self.data_changed_sig.emit()
        logger.debug("Data changed signal emitted")


    def fetch_clarified_tasks(self):
        logger.debug("Fetch clarified tasks")
        tasks = self.service.get_clarified_tasks()
        self.clarified_fetched_sig.emit(tasks)

    def fetch_organized_tasks(self):
        logger.debug("Fetch organized tasks")
        tasks = self.service.get_organized_tasks()
        self.organized_fetched_sig.emit(tasks)

    def fetch_projects(self):
        logger.debug("Fetch projects")
        projects = self.service.get_projects()
        self.projects_fetched_sig.emit(projects)

    def add_project(self, name: str, icon):
        logger.debug("Add project")
        if icon:
            self.service.new_project(name, icon)
        else:
            self.service.new_project(name)
        self.data_changed_sig.emit()
        logger.debug("Data changed signal emitted")


    def delete_project(self, project_id: str):
        logger.debug("Delete project")
        self.service.delete_project(project_id)
        
    def update_project(self, project: ProjectRecord):
        logger.debug("Update project")
        self.service.edit_project(project)
        self.data_changed_sig.emit()
        logger.debug("Data changed signal emitted")


    def organize_action(self, task_id, project_id):
        logger.debug(f"Organize: {task_id, project_id}")
        self.service.organized(task_id, project_id)
