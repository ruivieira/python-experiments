# type: ignore
"""Task management"""
# INFO: Task management
# pylint: disable=R0903,C0103

from dataclasses import dataclass
from enum import Enum
from typing import List

from todoist import TodoistAPI

import common.fs as fs


class Todoist:
    """Todoist access manager"""

    def __init__(self, token: str):
        self.token = token
        self.api = TodoistAPI(self.token)
        self.api.sync()

    def get_all_active_tasks(self):
        """Get all active tasks"""
        for item in self.api.state["items"]:
            print(item)


class TaskStatus(Enum):
    """Task status enum"""

    TODO = "TODO"
    DONE = "DONE"
    LATER = "LATER"


@dataclass
class Task:
    """Task data class"""

    status: TaskStatus
    content: str


def _parse_LogSeq_task(line: str) -> Task:
    """Parse a string into a LogSeq (orgmode) task"""
    stripped = line.lstrip()
    if stripped.startswith("- TODO"):
        task = Task(TaskStatus.TODO, stripped[7:])
    elif stripped.startswith("- LATER"):
        task = Task(TaskStatus.LATER, stripped[8:])
    elif stripped.startswith("- DONE"):
        task = Task(TaskStatus.DONE, stripped[7:])
    else:
        task = Task(TaskStatus.TODO, stripped[2:])
    return task


def _isTask(line: str) -> bool:
    """Check if a LogSeq string is a task"""
    stripped = line.lstrip()
    return (
        stripped.startswith("- TODO")
        or stripped.startswith("- LATER")
        or stripped.startswith("- DONE")
    )


class LogSeqTasks:
    """LogSeq tasks manager"""

    def __init__(self, root):
        self.root = root
        self.tasks: List[Task] = []
        files = fs.get_all_files(root, "*.md")
        for file in files:
            # open the markdown file
            with open(file, "r") as md_file:
                lines = md_file.read().splitlines()
                for line in lines:
                    if _isTask(line):
                        self.tasks.append(_parse_LogSeq_task(line))
