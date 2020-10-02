"""Mastodon bot announcing new arXiv stats pre-prints"""
# INFO: Mastodon bot announcing new arXiv stats pre-prints

import sqlite3
import configparser
from datetime import date, timedelta
from typing import List
from mastodon import Mastodon  # type: ignore
from arxivist.core import Entry, ArXivist


connection = sqlite3.connect("arXiv.db")
c = connection.cursor()
c.execute(
    """CREATE TABLE IF NOT EXISTS papers
    (id INTEGER PRIMARY KEY, title INTEGER, arxiv_id TEXT, tooted INTEGER, UNIQUE(title))"""
)


today = date.today()
past = today - timedelta(days=1)
DATE_END = "{}-{:02d}-{:02d}".format(today.year, today.month, today.day)
DATE_START = "{}-{:02d}-{:02d}".format(past.year, past.month, past.day)
print("Getting papers from {} to {}".format(DATE_START, DATE_END))

entries: List[Entry] = ArXivist().fetch(DATE_START, DATE_END)

sql_entries = [(entry.title, entry.arxiv_id, False) for entry in entries]

c.executemany(
    """
    INSERT OR IGNORE INTO papers (title, arxiv_id, tooted)
    VALUES (?, ?, ?)""",
    sql_entries,
)


c.execute("SELECT * FROM papers WHERE tooted = 0")
rows = c.fetchall()

if len(rows) > 0:
    # get first row
    paper = rows[0]
    print(paper)

    c.execute("UPDATE papers SET tooted=? WHERE id=?", (1, paper[0]))

    config = configparser.ConfigParser()
    config.read("arxivstatsbot.tokens")

    appid = config["secrets"]["id"]
    secret = config["secrets"]["secret"]
    token = config["secrets"]["token"]

    api = Mastodon(appid, secret, token, api_base_url="https://botsin.space")
    api.toot(status="{} - {}".format(paper[1], f"https://arxiv.org/abs/{paper[2]}"))

connection.commit()
connection.close()
