"""Utility to convert Jupyter to Markdown"""
# INFO: utility to convert Jupyter to Markdown
# pylint: disable=R0903
from typing import List, Union
import json


class Notebook:
    """A Jupyter notebook representation"""

    def __init__(self):
        self.cells: List[Union[MarkdownCell, SourceCell]] = []
        self.title: str = ""

    def to_jupyter_md(self) -> str:
        """Convert Jupyter notebook to Jupyter markdown"""
        markdown = ""
        for cell in self.cells:
            if isinstance(cell, MarkdownCell):
                markdown += "%% md\n"
                markdown += "".join(cell.contents) + "\n"
            elif isinstance(cell, SourceCell):
                markdown += "%% python\n"
                markdown += "".join(cell.contents) + "\n"
                markdown += "\n"
        return markdown


class MarkdownCell:
    """Represents a markdown cell"""

    def __init__(self):
        self.contents: str = ""


class SourceCell:
    """Represents a code cell"""

    def __init__(self):
        self.contents: str = ""


def parse_notebook(path: str) -> Notebook:
    """Parse a file into a Notebook"""
    with open(path, "r") as _notebook_file:
        data = _notebook_file.read()

    first_cell = True
    notebook_json = json.loads(data)
    _notebook = Notebook()
    for cell_json in notebook_json["cells"]:
        cell_type = cell_json["cell_type"]
        if cell_type == "markdown":
            md_cell = MarkdownCell()
            md_cell.contents = cell_json["source"]
            _notebook.cells.append(md_cell)
            if first_cell and md_cell.contents[0].startswith("# "):
                _notebook.title = md_cell.contents[0][2:]
                first_cell = False
        elif cell_type == "code":
            code_cell = SourceCell()
            code_cell.contents = cell_json["source"]
            _notebook.cells.append(code_cell)

    return _notebook
