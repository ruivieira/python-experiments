# pylint: skip-file
"""TiddlyWiki access library"""
# INFO: TiddlyWiki access library
from dataclasses import dataclass
from typing import Dict, Any, List
import os.path
import html

from bs4 import BeautifulSoup  # type: ignore
import frontmatter  # type: ignore


def read_file(path: str) -> str:
    """Read the HTML file's content"""
    with open(path, "r") as _html_file:
        data = _html_file.read()
    return data


def parse_html(html: str) -> BeautifulSoup:
    """Parse the HTML with Beautiful Soup"""
    return BeautifulSoup(html, features="html.parser")


@dataclass
class Tiddler:
    title: str
    fields: Dict[str, Any]
    contents: List[str]


def element_to_tiddler(element) -> Tiddler:
    _tiddler = Tiddler(
        title=element["title"],
        fields=element.attrs,
        contents=[str(c) for c in element.find("pre").contents],
    )
    # _tiddler = Tiddler(title=element['title'], fields=element.attrs, contents=[str(c) for c in element.contents])
    return _tiddler


def convert_to_markdown(_tiddler: Tiddler) -> str:
    front_matter = "---\n"
    for key, value in _tiddler.fields.items():
        v = html.escape(value.replace("\\", ""))
        front_matter += f'{key}:\t"{v}"\n'
    front_matter += "---\n"
    front_matter += "".join(_tiddler.contents)
    return front_matter


def export_to_markdown(input, output):
    source = read_file(input)
    soup = parse_html(source)

    elems = soup.find_all("div")

    if len(elems) > 0:
        for element in elems:
            if "title" in element.attrs and not element.attrs["title"].startswith(
                "$:/"
            ):
                tiddler = element_to_tiddler(element)
                md = convert_to_markdown(tiddler)
                # save to markdown file
                OUTPUT_FILE = os.path.join(
                    output, tiddler.title.replace("/", "-") + ".md"
                )
                print(OUTPUT_FILE)
                print(md, file=open(OUTPUT_FILE, "w"))


def import_from_markdown(input):
    fm = frontmatter.load(input)
    return fm


def import_files(source_dir, wiki):
    source = read_file(wiki)
    soup = parse_html(source)

    for path, subdirs, files in os.walk(source_dir):
        for name in files:
            if os.path.splitext(name)[1] == ".md":
                filename = os.path.join(path, name)
                print(filename)
                fm = import_from_markdown(filename)
                # print(fm)
                # check if exists
                print(fm.metadata["title"])
                tiddler_div = soup.find(title=fm.metadata["title"])
                if tiddler_div:
                    for key, value in fm.metadata.items():
                        tiddler_div.attrs[key] = value

                    pre = BeautifulSoup(
                        "\n<pre>\n" + fm.content + "\n</pre>\n", features="html.parser"
                    )
                    print(pre)
                    tiddler_div.find("pre").replace_with(pre)

    with open("index2.html", "w") as file:
        file.write(soup.prettify(formatter=None))


VAULT = "/Users/rui/Sync/documents/wiki/garden"
# export_to_markdown("index.html", VAULT)
import_files(VAULT, "index.html")
