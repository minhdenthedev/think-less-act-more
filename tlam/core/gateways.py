import dataclasses
import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from tlam.core.record import ProjectRecord, TaskRecord, EngagingTaskRecord


@dataclasses.dataclass
class Initiator:
    """Initiating the database"""

    db_path: Path

    def check_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Query the internal master table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()

        tables = [t[0] for t in tables]
        return "tasks" in tables and "projects" in tables

    def initiate(self):
        if self.check_tables():
            return False
        else:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
            -- Create the Projects table first (Parent)
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY NOT NULL,
                project_name TEXT DEFAULT 'No title',
                icon TEXT DEFAULT ''
            );
            """)
            conn.execute("""
            -- Create the Tasks table (Child)
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY NOT NULL,
                task_title TEXT DEFAULT 'No title',
                project_id TEXT,
                clarified BOOLEAN DEFAULT 0 CHECK (clarified IN (0, 1)),
                organized BOOLEAN DEFAULT 0 CHECK (organized IN (0, 1)),
                done BOOLEAN DEFAULT 0 CHECK (done IN (0, 1)),
                
                -- Link task to a project
                FOREIGN KEY (project_id) REFERENCES projects (project_id) 
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
            """)
            conn.commit()
            conn.close()

            return True


# Helper to convert SQLite Row -> Dataclass
def _row_to_project_record(row):
    return ProjectRecord(
        project_id=uuid.UUID(row["project_id"]),
        project_name=row["project_name"],
        icon=row["icon"],
    )


@dataclasses.dataclass
class ProjectGateway:
    """Project CRUD"""

    db_path: Path

    def _get_connection(self):
        # Return a connection that treats rows like dictionaries
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    # --- CREATE ---
    def create(self, project: ProjectRecord):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO projects (project_id, project_name, icon) VALUES (?, ?, ?)",
                (str(project.project_id), project.project_name, project.icon),
            )

    # --- READ ---
    def get_by_id(self, project_id: uuid.UUID):
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM projects WHERE project_id = ?", (str(project_id),)
            ).fetchone()
            return _row_to_project_record(row) if row else None

    def get_all(self):
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM projects").fetchall()
            return [_row_to_project_record(row) for row in rows]

    # --- UPDATE ---
    def update(self, project: ProjectRecord):
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE projects SET project_name = ?, icon = ? WHERE project_id = ?",
                (project.project_name, project.icon, str(project.project_id)),
            )

    # --- DELETE ---
    def delete(self, project_id: uuid.UUID):
        with self._get_connection() as conn:
            conn.execute(
                "DELETE FROM projects WHERE project_id = ?", (str(project_id),)
            )


# Helper to convert SQLite Row -> Dataclass
def _row_to_task_record(row):
    return TaskRecord(
        task_id=uuid.UUID(row["task_id"]),
        task_title=row["task_title"],
        # Convert string back to UUID only if it exists
        project_id=uuid.UUID(row["project_id"]) if row["project_id"] else None,
        # Convert 0/1 back to True/False
        clarified=bool(row["clarified"]),
        organized=bool(row["organized"]),
        done=bool(row["done"]),
    )


@dataclasses.dataclass
class TaskGateway:
    """Task CRUD"""

    db_path: Path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def get_captured_tasks(self) -> List[TaskRecord]:
        with self._get_connection() as conn:
            rows = conn.execute("""
            SELECT task_id, task_title, project_id, clarified, organized, done
            FROM tasks
            WHERE clarified = 0;
            """).fetchall()
            return [_row_to_task_record(row) for row in rows]

    def get_clarified_tasks(self) -> List[TaskRecord]:
        with self._get_connection() as conn:
            rows = conn.execute("""
            SELECT task_id, task_title, project_id, clarified, organized, done
            FROM tasks
            WHERE clarified = 1 AND organized = 0;
            """).fetchall()
            return [_row_to_task_record(row) for row in rows]

    def get_organized_tasks(self) -> List[TaskRecord]:
        with self._get_connection() as conn:
            rows = conn.execute("""
            SELECT task_id, task_title, project_id, clarified, organized, done
            FROM tasks
            WHERE clarified = 1 AND organized = 1 AND done = 0;
            """).fetchall()
            return [_row_to_task_record(row) for row in rows]

    # --- CREATE ---
    def create(self, task: TaskRecord):
        with self._get_connection() as conn:
            conn.execute(
                """INSERT INTO tasks 
                   (task_id, task_title, project_id, clarified, organized, done) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    str(task.task_id),
                    task.task_title,
                    str(task.project_id) if task.project_id else None,
                    int(task.clarified),
                    int(task.organized),
                    int(task.done),
                ),
            )

    # --- READ ---
    def get_by_id(self, task_id: str) -> Optional[TaskRecord]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM tasks WHERE task_id = ?", (str(task_id),)
            ).fetchone()
            return _row_to_task_record(row) if row else None

    def get_by_project(self, project_id: uuid.UUID):
        """Fetch all tasks belonging to a specific project"""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE project_id = ?", (str(project_id),)
            ).fetchall()
            return [_row_to_task_record(row) for row in rows]

    # --- UPDATE ---
    def update(self, task: TaskRecord):
        with self._get_connection() as conn:
            conn.execute(
                """UPDATE tasks SET 
                   task_title = ?, project_id = ?, clarified = ?, organized = ?, done = ? 
                   WHERE task_id = ?""",
                (
                    task.task_title,
                    str(task.project_id) if task.project_id else None,
                    int(task.clarified),
                    int(task.organized),
                    int(task.done),
                    str(task.task_id),
                ),
            )

    # --- DELETE ---
    def delete(self, task_id: str):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))


@dataclasses.dataclass
class EngagingTaskGateway:
    db_path: Path

    def get_current_task(self) -> EngagingTaskRecord:
        with self.db_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return EngagingTaskRecord(
                task_id=data["task_id"],
                started_at=datetime.fromisoformat(data["started_at"]),
            )

    def save_current_task(self, task: EngagingTaskRecord):
        self.db_path.touch(exist_ok=True)
        with self.db_path.open("w", encoding="utf-8") as f:
            data = dataclasses.asdict(task)
            data["started_at"] = str(data["started_at"])
            json.dump(data, f)

    def unengage(self) -> EngagingTaskRecord:
        task = self.get_current_task()
        self.db_path.unlink(missing_ok=True)
        return task

    def engage(self, task_id: str):
        task = EngagingTaskRecord(task_id, datetime.now())
        self.save_current_task(task)
