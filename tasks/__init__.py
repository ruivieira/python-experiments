from todoist import TodoistAPI
import common.fs as fs

class Todoist:
    def __init__(self, token: str):
        self.token = token
        self.api = TodoistAPI(self.token)
        self.api.sync()

    def getAllActiveTasks(self):
        """Get all active tasks"""
        for item in self.api.state['items']:
            print(item)

class LogSeqTasks:
    def __init__(self, root):
        self.root = root
        files = fs.get_all_files(root, "*.md")
        for file in files:
            # open the markdown file
            with open(file, 'r') as md_file:
                lines = md_file.read().splitlines()
                for line in lines:
                    print(line)