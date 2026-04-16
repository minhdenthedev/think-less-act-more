import dataclasses
from typing import Optional
import uuid
from dataclasses import field
from datetime import datetime


@dataclasses.dataclass
class ProjectRecord:
    """Represent a project in database"""

    project_id: uuid.UUID = field(default_factory=uuid.uuid4)
    project_name: str = "No title"
    icon: str = ""


@dataclasses.dataclass
class TaskRecord:
    """Represent a fully organized task in database"""

    task_id: uuid.UUID = field(default_factory=uuid.uuid4)
    task_title: str = "No title"
    project_id: Optional[uuid.UUID] = None
    clarified: bool = False
    organized: bool = False
    done: bool = False


@dataclasses.dataclass
class EngagingTaskRecord:
    task_id: str
    started_at: datetime
