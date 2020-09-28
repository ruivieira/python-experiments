"""Generates this README.md"""
# INFO: generates this README.md
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Info:
    """Stores data about a project"""
    filename: str
    description: str


PROJECTS = []

for path in Path('.').rglob('*.py'):
    x = open(path.resolve()).read().splitlines()
    descriptions = list(filter(lambda line : line.startswith("# INFO:"), x))
    if len(descriptions) > 0:
        info = Info(filename=path.name, description=descriptions[0][8:])
        PROJECTS.append(info)

# sort the projects by description size
PROJECTS = sorted(PROJECTS, key=lambda project: len(project.filename + project.description))

PROJECTS = "\n".join([f"* `{p.filename}`, {p.description}" for p in PROJECTS])

template=f"""
# python-experiments

![](docs/snake.png)

A place for Python experiments.

{PROJECTS}

"""

print(template)
