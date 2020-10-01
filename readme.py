"""Generates this README.md"""
# INFO: generates this README.md
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Info:
    """Stores data about a project"""

    filename: str
    description: str


PROJECTS: List[Info] = []

for path in Path(".").rglob("*.py"):
    x = open(path.resolve()).read().splitlines()
    descriptions = list(filter(lambda line: line.startswith("# INFO:"), x))
    if len(descriptions) > 0:
        info = Info(filename=path.name, description=descriptions[0][8:])
        PROJECTS.append(info)

# sort the projects by description size
PROJECTS = sorted(
    PROJECTS, key=lambda project: len(project.filename + project.description)
)

PROJECTS_DESCRIPTION = "\n".join(
    [f"* `{p.filename}`, {p.description}" for p in PROJECTS]
)

template = f"""
# python-experiments [![builds.sr.ht status](https://builds.sr.ht/~ruivieira/python-experiments.svg)](https://builds.sr.ht/~ruivieira/python-experiments?)

![snake](docs/felix.png)

A place for Python experiments.

{PROJECTS_DESCRIPTION}"""

print(template)
