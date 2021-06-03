"""# INFO: Common filesystem operation"""
# INFO: Common filesystem operation
import common.fs as fs


def get_all_markdown_files(root: str):
    """Get all markdown files in `root`"""
    for path in fs.get_all_files(root, "*.md"):
        print(path.resolve())
