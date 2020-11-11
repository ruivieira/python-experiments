"""Optimise Jupyter books"""
# INFO: Optimise Jupyter books

from typing import Dict, List, Union
import glob
import argparse
import os.path

from bs4 import BeautifulSoup  # type: ignore
from colorama import init, Fore, Style  # type: ignore


def action_log(colour, message: str, context: str, char: str = "├─") -> str:
    """Log an action to the console"""
    return f"{char}{colour}{message}: {context}"


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
    return BeautifulSoup(html, features="html.parser")


def remove_elements(
    doc: BeautifulSoup, selector: str, attrs: Dict[str, Union[str, List[str]]]
) -> None:
    """Remove elements which match the selector"""
    elems = doc.find_all(selector, attrs)
    if len(elems) > 0:
        print(
            action_log(
                Fore.RED,
                "[REMOVING]",
                f"Found {len(elems)} matching {selector} [{attrs}]",
            )
        )
        for element in elems:
            element.decompose()
    else:
        print(
            action_log(
                Style.DIM,
                "[NO MATCH]",
                f"No elements found matching {selector} [{attrs}]",
            )
        )


def save_doc(doc: BeautifulSoup, dest: str) -> None:
    """Save a doc as an HTML"""
    print(action_log(Style.BRIGHT, "[SAVING]", f"Saving file to: {dest}", char="└─"))
    text_file = open(dest, "w")
    _ = text_file.write(doc.prettify())
    text_file.close()


def append_to_head(doc: BeautifulSoup, html: str) -> None:
    """Append HTML string to head"""
    print(action_log(Fore.GREEN, "[APPEND]", "adding to head"))
    tag = BeautifulSoup(html, features="html.parser")
    if doc.head:
        doc.head.insert(0, tag)


def update_tag(
    doc: BeautifulSoup,
    selector: str,
    attrs: Dict[str, str],
    attr_to_change: str,
    value: str,
) -> None:
    """Update the value of a tag"""
    elems = doc.find_all(selector, attrs)
    if len(elems) > 0:
        print(
            action_log(
                Fore.YELLOW,
                "[UPDATE]",
                f"Updating {len(elems)} elements{Style.NORMAL} matching {selector} [{attrs}]",
            )
        )
        for element in elems:
            element.attrs[attr_to_change] = value
    else:
        print(
            action_log(
                Style.DIM,
                "[NO MATCH]",
                f"No elements found matching {selector} [{attrs}]",
            )
        )


if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="jboptim CLI utility.", prog="jboptim"
    )
    parser.add_argument(
        "--source",
        dest="source",
        action="store",
        help="Where to find the built HTML",
    )

    parser.add_argument(
        "--dest",
        dest="destination",
        action="store",
        help="Where to put the built HTML",
    )

    args: argparse.Namespace = parser.parse_args()

    html_files = get_html_files(args.source)
    init(autoreset=True)  # start colour ouput
    for html_file in html_files:
        print(f"{Style.BRIGHT}Processing {html_file}")
        source = read_file(html_file)
        soup = parse_html(source)

        # remove index links
        remove_elements(soup, "link", {"rel": "index"})
        remove_elements(soup, "link", {"rel": "search"})
        remove_elements(soup, "link", {"rel": "next"})
        remove_elements(soup, "link", {"rel": "prev"})
        remove_elements(soup, "a", {"class": "colab-button"})
        remove_elements(soup, "a", {"class": "binder-button"})
        remove_elements(
            soup, "script", {"src": "https://unpkg.com/thebelab@latest/lib/index.js"}
        )

        remove_elements(
            soup, "script", {"src": "_static/js/index.3da636dd464baa7582d2.js"}
        )
        remove_elements(soup, "script", {"type": "text/x-thebe-config"})
        remove_elements(soup, "link", {"href": "_static/sphinx-thebe.css"})
        remove_elements(soup, "script", {"src": "_static/sphinx-thebe.js"})
        remove_elements(
            soup,
            "link",
            {"href": "_static/vendor/fontawesome/5.13.0/webfonts/fa-solid-900.woff2"},
        )
        remove_elements(
            soup, "link", {"href": "_static/vendor/open-sans_all/1.44.1/index.css"}
        )
        remove_elements(
            soup, "link", {"href": "_static/vendor/lato_latin-ext/1.44.1/index.css"}
        )

        remove_elements(
            soup,
            "link",
            {"href": "_static/css/index.73d71520a4ca3b99cfee5594769eaaae.css"},
        )
        remove_elements(
            soup,
            "link",
            {"href": "_static/vendor/fontawesome/5.13.0/webfonts/fa-brands-400.woff2"},
        )
        remove_elements(
            soup, "link", {"href": "_static/vendor/fontawesome/5.13.0/css/all.min.css"}
        )
        remove_elements(soup, "div", {"class": "dropdown-buttons-trigger"})
        remove_elements(soup, "a", {"data-tooltip": "Copy"})
        remove_elements(soup, "a", {"class": "copybtn"})
        remove_elements(soup, "link", {"href": "_static/copybutton.css"})
        remove_elements(soup, "script", {"src": "_static/copybutton.js"})
        remove_elements(soup, "script", {"src": "_static/clipboard.min.js"})
        remove_elements(soup, "link", {"href": "_static/pygments.css"})
        remove_elements(soup, "link", {"href": "_static/togglebutton.css"})
        remove_elements(soup, "form", {"action": "search.html"})

        remove_elements(
            soup,
            "div",
            {"class": ["col", "pl-2", "topbar-main"]},
        )

        remove_elements(
            soup,
            "link",
            {"href": "_static/sphinx-book-theme.40e2e510f6b7d1648584402491bb10fe.css"},
        )

        append_to_head(
            soup,
            '<link rel="preload" as="font" type="font/woff2"'
            + ' crossorigin="" href="/fonts/JuliaMono-Regular.woff2">',
        )

        append_to_head(
            soup,
            '<link rel="preload" as="font" type="font/woff"'
            + ' crossorigin="" href="_static/icomoon.woff">',
        )
        append_to_head(soup, '<link rel="stylesheet" href="_static/icomoon.css">')

        append_to_head(soup, '<link rel="stylesheet" href="/css/style.css">')
        append_to_head(soup, '<link rel="stylesheet" href="/css/trac.css">')

        append_to_head(
            soup, "<style>.container { padding-left: 0 !important; }</style>"
        )

        update_tag(soup, "div", {"id": "site-navigation"}, "id", "sidebar")

        update_tag(soup, "div", {"id": "main-content"}, "class", "container")

        update_tag(soup, "div", {"id": "main-content"}, "id", "content")
        update_tag(soup, "div", {"id": "content"}, "class", "container")
        update_tag(soup, "table", {"border": "1"}, "border", "0")

        # update code cell blocks
        update_tag(
            soup,
            "div",
            {"class": "cell tag_hide-input docutils container"},
            "class",
            "cell tag_hide-input docutils container",
        )

        update_tag(soup, "div", {"id": "content"}, "class", "container")

        # add MathJax
        append_to_head(
            soup,
            '<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>',
        )
        append_to_head(
            soup,
            """
        <script type="text/x-mathjax-config">
            MathJax.Hub.Config({
                tex2jax: {
                    inlineMath: [ ['$','$'], ["\\(","\\)"] ],
                    processEscapes: true
                }
            });
        </script>
        """,
        )

        append_to_head(
            soup,
            """
            <script type="text/javascript"
            src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
            </script>
        """,
        )

        html_file_dest = os.path.join(args.destination, os.path.basename(html_file))
        save_doc(soup, html_file_dest)
