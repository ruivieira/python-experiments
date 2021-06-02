from common.secrets import load
import tasks
import common.notes as notes

tokens = load("todoist")

print(tokens['token'])

todoist = tasks.Todoist(tokens['token'])

todoist.getAllActiveTasks()

logseq = tasks.LogSeqTasks("/Users/rui/notes/logseq")