"""Generates this README.md"""
# INFO: generates this README.md
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import json


@dataclass
class Info:
    """Stores data about a project"""

    filename: str
    description: str
    url: Optional[str]


PROJECTS: List[Info] = []

for path in Path(".").rglob("*.py"):
    x = open(path.resolve()).read().splitlines()
    descriptions = list(filter(lambda line: line.startswith("# INFO:"), x))
    if len(descriptions) > 0:
        info = Info(filename=path.name, description=descriptions[0][8:], url=None)
        PROJECTS.append(info)

# sort the projects by description size
PROJECTS = sorted(
    PROJECTS, key=lambda project: len(project.filename + project.description)
)

PROJECTS_DESCRIPTION = "\n".join(
    [f"* `{p.filename}`, {p.description}" for p in PROJECTS]
)

# get the graduated projects
PROJECTS_GRADUATED: List[Info] = []

with open("graduated.json") as json_file:
    data = json.load(json_file)
    for p in data:
        project = Info(p["name"], p["description"], p["url"])
        PROJECTS_GRADUATED.append(project)

PROJECTS_GRADUATED_DESCRIPTION = "\n".join(
    [f"* `{p.filename}`, {p.description} [[repo]({p.url})]" for p in PROJECTS_GRADUATED]
)

template = f"""
# python-experiments ![builds.sr.ht status](https://builds.sr.ht/~ruivieira/python-experiments.svg) ![Tests](https://github.com/ruivieira/python-experiments/workflows/Tests/badge.svg)

![felix](docs/felix.png)

A place for Python experiments. Documentation available [here](https://ruivieira.github.io/python-experiments/).

{PROJECTS_DESCRIPTION}

![felix-graduated](docs/felix-graduated.png)
## Graduated
{PROJECTS_GRADUATED_DESCRIPTION}



![octopus](docs/octopus.png)
## (λ Hy!)

Things using the Hy programming language.

* [SICP exercises](https://ruivieira.dev/codex/python-experiments/sicp-chapter1.html)


![coconut](docs/coconut.png)
## coconut

Things using the `coconut` language
"""


print(template)
