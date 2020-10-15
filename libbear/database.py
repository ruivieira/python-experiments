"""Bear database handling methods"""
import sqlite3
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List
import re
from collections import Counter

HOME: str = str(Path.home())


@dataclass
class Task:
    """Class to hold information about a single task"""

    identifier: str
    task: str
    title: str


def get_connection() -> sqlite3.Connection:
    """Return a connection"""
    return sqlite3.connect(
        f"{HOME}/Library/Group Containers/"
        + "9K33E3U3T4.net.shinyfrog.bear/Application Data/database.sqlite"
    )


def get_titles(conn: sqlite3.Connection) -> List[str]:
    """Get all titles"""
    cur = conn.cursor()
    cur.execute("SELECT ZTITLE FROM ZSFNOTE")

    rows = cur.fetchall()
    return [row[0] for row in rows]


def get_all_notes_text(conn: sqlite3.Connection) -> List[str]:
    """Get all notes' text"""
    cur = conn.cursor()
    cur.execute("SELECT ZTEXT FROM ZSFNOTE")

    rows = cur.fetchall()
    return [row[0] for row in rows]


def get_all_tasks(conn: sqlite3.Connection) -> Dict[str, List[Task]]:
    """Get all tasks"""
    cur = conn.cursor()
    cur.execute("SELECT ZUNIQUEIDENTIFIER, ZTITLE, ZTEXT FROM ZSFNOTE")
    rows = cur.fetchall()

    tasks: Dict[str, List[Task]] = {}

    for row in rows:
        _tasks: List[str] = re.findall(r"- \[ \] (.*)", row[2])
        if len(_tasks) > 0:
            if row[1] not in tasks:
                tasks[row[1]] = []
            for match in _tasks:
                task = Task(identifier=row[0], title=row[1], task=match)

                tasks[row[1]].append(task)
    return tasks


def get_duplicate_titles(conn: sqlite3.Connection) -> None:
    """Get all duplicate titles"""
    cur = conn.cursor()
    cur.execute("SELECT ZTITLE FROM ZSFNOTE")

    rows = cur.fetchall()
    counts = Counter([row[0] for row in rows])
    total = 0
    for pair in counts.items():
        if pair[1] > 1:
            print(f"{pair[0]}: {pair[1]}")
            total += pair[1] - 1
    print("-" * 80)
    print(f"Total: {total}")
