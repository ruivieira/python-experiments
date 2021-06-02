import common.fs as fs


def get_all_markdown_files(root: str):
    for path in fs.get_all_files(root, "*.md"):
        print(path.resolve())
