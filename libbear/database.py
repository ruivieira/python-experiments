import sqlite3
from pathlib import Path
from typing import List
import re
import argparse
from collections import Counter

HOME = str(Path.home())


def get_connection():
    return sqlite3.connect(
        f"{HOME}/Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear/Application Data/database.sqlite"
    )


def get_titles(conn) -> List[str]:
    cur = conn.cursor()
    cur.execute("SELECT ZTITLE FROM ZSFNOTE")

    rows = cur.fetchall()
    return [row[0] for row in rows]

def get_all_notes_text(conn) -> List[str]:
    cur = conn.cursor()
    cur.execute("SELECT ZTEXT FROM ZSFNOTE")

    rows = cur.fetchall()
    return [row[0] for row in rows]

def get_all_tasks(conn) -> List[str]:
    cur = conn.cursor()
    cur.execute("SELECT ZTITLE, ZTEXT FROM ZSFNOTE")

    rows = cur.fetchall()
    for row in rows:
        print("-"*80)
        print(row[0])
        tasks = re.findall(r"- \[ \] (.*)$", row[1])
        if len(tasks) > 0:
            for task in tasks:
                print("="*50)
                print(task)
    return "meh"

def get_duplicate_titles(conn):
    cur = conn.cursor()
    cur.execute("SELECT ZTITLE FROM ZSFNOTE")

    rows = cur.fetchall()    
    counts = Counter([row[0] for row in rows])
    counts = counts.items()
    total = 0
    for pair in counts:
        if pair[1] > 1:
            print(f"{pair[0]}: {pair[1]}")
            total += pair[1] - 1
    print("-"*80)
    print(f"Total: {total}")