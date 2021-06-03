# type: ignore
"""Robby info manager"""
# INFO: Robby info manager

import tasks
from common.secrets import load

tokens = load("todoist")

todoist = tasks.Todoist(tokens["token"])

logseq = tasks.LogSeqTasks("/Users/rui/notes/logseq")

tasks = todoist.get_all_active_tasks() + logseq.tasks

print(tasks)
