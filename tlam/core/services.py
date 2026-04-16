import dataclasses
from datetime import datetime
from typing import List
from uuid import UUID

from tlam.core.gateways import (
    Initiator,
    ProjectGateway,
    TaskGateway,
    EngagingTaskGateway,
)
from tlam.core.record import TaskRecord, ProjectRecord


@dataclasses.dataclass
class GTDService:
    """Class to work with GTD framework"""

    db_initiator: Initiator
    project_gateway: ProjectGateway
    task_gateway: TaskGateway
    engaging_task_gateway: EngagingTaskGateway

    def initiate(self):
        self.db_initiator.initiate()
        self.new_project("Someday/Maybe", "🗳️")
        self.new_project("Waiting For", "⏳")
        self.new_project("Do It Now", "🗲")

    def capture(self, thought: str) -> TaskRecord:
        task = TaskRecord(task_title=thought)
        self.task_gateway.create(task)
        return task

    def clarify(self, task_id: str, task_title: str) -> TaskRecord:
        task = self.task_gateway.get_by_id(task_id)
        if task is None:
            raise ValueError(f"Task with id={task_id} not found.")
        task.task_title = task_title
        task.clarified = True
        self.task_gateway.update(task)
        return task

    def organized(self, task_id: str, project_id: str) -> TaskRecord:
        task = self.task_gateway.get_by_id(task_id)
        if task is None:
            raise ValueError(f"Task with id={task_id} not found.")
        task.project_id = UUID(project_id)
        task.organized = True
        self.task_gateway.update(task)
        return task

    def engage(self, task_id: str):
        self.engaging_task_gateway.engage(task_id)

    def get_engaging_task(self):
        try:
            engaging_task = self.engaging_task_gateway.get_current_task()
            task = self.task_gateway.get_by_id(engaging_task.task_id)
            if task is not None:
                duration = datetime.now() - engaging_task.started_at
                return task.task_id, task.task_title, task.project_id, duration
            else:
                raise RuntimeError("Not engagin any task.")
        except FileNotFoundError:
            print("No engaging task right now")

    def done(self):
        task = self.engaging_task_gateway.get_current_task()
        self.mark_task_as_done(task.task_id)
        self.engaging_task_gateway.unengage()

    def get_projects(self) -> List[ProjectRecord]:
        return self.project_gateway.get_all()

    def new_project(self, project_name: str, icon: str = "🗀") -> ProjectRecord:
        project = ProjectRecord(project_name=project_name, icon=icon)
        self.project_gateway.create(project)
        return project

    def delete_project(self, project_id: str):
        self.project_gateway.delete(UUID(project_id))

    def edit_project(
        self, project_id: str, project_name: str, icon: str
    ) -> ProjectRecord:
        project = ProjectRecord(UUID(project_id), project_name, icon)
        self.project_gateway.update(project)
        return project

    def mark_task_as_done(self, task_id: str):
        task = self.task_gateway.get_by_id(task_id)
        if task is not None:
            task.done = True
            self.task_gateway.update(task)
        else:
            raise ValueError("Task not found.")

    def delete_task(self, task_id: str):
        self.task_gateway.delete(task_id)

    def get_captured_tasks(self) -> List[TaskRecord]:
        return self.task_gateway.get_captured_tasks()

    def get_clarified_tasks(self) -> List[TaskRecord]:
        return self.task_gateway.get_clarified_tasks()

    def get_organized_tasks(self) -> List[TaskRecord]:
        return self.task_gateway.get_organized_tasks()
