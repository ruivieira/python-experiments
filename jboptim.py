"""Optimise Jupyter books"""
# INFO: Optimise Jupyter books

from typing import List
import glob
from bs4 import BeautifulSoup  # type: ignore

SOURCE = "../../documentation/python/books/ml/_build/html"


def read_file(path: str) -> str:
    """Read the HTML file's content"""
    with open(path, "r") as _html_file:
        data = _html_file.read()
    return data


def get_html_files(src: str) -> List[str]:
    """Get all the HTML file names in the source directory"""
    _html_files = glob.glob(f"{src}/*.html")
    return _html_files


def parse_html(html: str) -> BeautifulSoup:
    """Parse the HTML with Beautiful Soup"""
    return BeautifulSoup(html, "lxml")


if __name__ == "__main__":
    html_files = get_html_files(SOURCE)
    print(html_files)
