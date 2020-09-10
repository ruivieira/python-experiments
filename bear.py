# INFO: utility to manipulate and query Bear notes
import sqlite3
from pathlib import Path
from typing import List

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


if __name__ == "__main__":
    conn = get_connection()
    titles = get_titles(conn)
    print(titles)
