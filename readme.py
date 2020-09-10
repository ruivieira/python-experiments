# INFO: generates this README.md
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Info:
    filename: str
    description: str


projects = []

for path in Path('.').rglob('*.py'):
    x = open(path.resolve()).read().splitlines()
    descriptions = list(filter(lambda line : line.startswith("# INFO:"), x))
    if len(descriptions) > 0:
        info = Info(filename=path.name, description=descriptions[0][8:])
        projects.append(info)


projects = "\n".join([f"* `{p.filename}`, {p.description}" for p in projects])

template=f"""
# python-experiments

A place for Python experiments.

{projects}

"""

print(template)
