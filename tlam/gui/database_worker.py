from PySide6.QtCore import QObject, Signal
from tlam.core.services import GTDService


class DatabaseWorker(QObject):
    """Worker for database operations"""

    capture_tasks = Signal(object)
    clarified_fetched_sig = Signal(object)
    service_clarified_sig = Signal(object)
    projects_fetched_sig = Signal(object)

    def __init__(self, service: GTDService):
        super().__init__()
        self.service = service

    # Slot
    def fetch_capture_tasks(self):
        tasks = self.service.get_captured_tasks()
        self.capture_tasks.emit(tasks)

    def add_thought_to_database(self, thought):
        task = self.service.capture(thought)

    def delete_action(self, task_id):
        self.service.delete_task(task_id)

    def clarify_action(self, task_id, task_title):
        self.service.clarify(task_id, task_title)

    def fetch_clarified_tasks(self):
        tasks = self.service.get_clarified_tasks()
        self.clarified_fetched_sig.emit(tasks)

    def fetch_projects(self):
        projects = self.service.get_projects()
        self.projects_fetched_sig.emit(projects)

    def add_project(self, name: str, icon):
        if icon:
            self.service.new_project(name, icon)
        else:
            self.service.new_project(name)
        print(f"Project added: {name}")

    def organize_action(self, task_id, project_id):
        self.service.organized(task_id, project_id)
