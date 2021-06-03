# type: ignore
"""Robby info manager"""
# INFO: Robby info manager

from common.secrets import load
import tasks

tokens = load("todoist")

print(tokens["token"])

todoist = tasks.Todoist(tokens["token"])

todoist.get_all_active_tasks()

logseq = tasks.LogSeqTasks("/Users/rui/notes/logseq")

print(logseq.tasks)
