"""Manage client-side Jupyter notebooks"""
# INFO: Manage client-side Jupyter notebooks
# pylint: disable=R0903,I1101
import argparse
import glob
import os
import pathlib
import shutil
import logging
import unicodedata
import re
import coloredlogs  # type: ignore
from jupex import Notebook, parse_notebook

# Create a logger object.
logger = logging.getLogger("sb")
coloredlogs.install(level="DEBUG")


def title_to_filename(value: str, allow_unicode=False) -> str:
    """
    Adapted from Django (https://github.com/django/django/blob/master/django/utils/text.py)
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


TEMPLATE = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>{title}</title>
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <link rel="icon" href="favicon.ico" />
    <style>
      @font-face {{
        font-family: JuliaMono;
        src: url("/fonts/JuliaMono-Regular.woff2") format("woff2");
      }}
    </style>
    <link href="/css/starboard-notebook-0.5.6.css" rel="stylesheet" />
    <link href="/css/style.css" rel="stylesheet" />
    <script src="/js/vendors~codemirror.chunk.js"></script>
    <script src="/js/codemirror.chunk.js"></script>

    <style>
      .cells-container {{
        margin-left: 25% !important;
        max-width: 50%;
      }}
      .celltype-python > .cell-top {{
        font-family: monospace !important;
      }}
      .ͼ1 .cm-line {{
        display: block;
        padding: 0px 2px 0px 4px;
        font-family: 'JuliaMono';
        font-size: 0.8rem;
      }}
      .cm-line > * {{
        font-family: 'JuliaMono';
        font-size: 0.8rem;
      }}
      .katex {{
        font-size: 0.9rem;
      }}
    </style>
  </head>
  <body>
    <div id="sidebar">
      <h2>Other pages</h2>
      <ul>
        <li><a href="/">Posts</a></li>
        <li><a href="/micro/">µ-posts</a></li>
        <li><a href="/pages/about.html">About</a></li>
      </ul>
      <h2>Codex</h2>
      <ul>
        <li><a href="/codex/machine-learning">Machine learning</a></li>
        <li><a href="/codex/python-experiments">Python experiments</a></li>
      </ul>
      <h2>Playground</h2>
      <ul>
        <li><a href="/playground/machine-learning">Machine learning</a></li>
      </ul>
    </div>

    <script>
      window.initialNotebookContent = `
{content}
`;
    </script>
    <script src="/js/starboard-notebook-0.5.6.min.js"></script>
  </body>
</html>
"""


def generate_html(_notebook: Notebook) -> str:
    """Generate HTML from a notebook"""
    return TEMPLATE.format(title=_notebook.title, content=_notebook.to_jupyter_md())


if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Jupyter notebooks -> pyiodide", prog="sb"
    )
    parser.add_argument(
        "--source",
        dest="source",
        help="Location of Jupyter notebooks",
    )

    args: argparse.Namespace = parser.parse_args()

    if args.source:
        SOURCE = args.source
        print(SOURCE)
        files = glob.glob(f"{args.source}/*.ipynb")
        if len(files) > 0:
            # check if build dir exists
            BUILD_DIR = os.path.join(SOURCE, "_build_sb")
            logger.debug("Source path -> %s", BUILD_DIR)
            dest = pathlib.Path(BUILD_DIR)
            if dest.exists():
                logger.debug("Output %s exists. Cleaning", BUILD_DIR)
                shutil.rmtree(BUILD_DIR)
            logger.debug("Creating %s.", BUILD_DIR)
            os.mkdir(BUILD_DIR)
            for notebook_file in files:
                notebook = parse_notebook(notebook_file)
                HTML_SOURCE = generate_html(notebook)
                html_file = (
                    os.path.join(
                        BUILD_DIR,
                        notebook.title.lower()
                        .replace(" ", "-")
                        .replace("?", "")
                        .replace("`", ""),
                    )
                    + ".html"
                )
                with open(html_file, "w") as text_file:
                    logger.debug("Saving %s.", html_file)
                    text_file.write(HTML_SOURCE)
    else:
        parser.print_help()
