"""Utility to manipulate and query Bear notes"""
# INFO: utility to manipulate and query Bear notes
import argparse
from sqlite3 import Connection
from colorama import Style   # type: ignore
from libbear import database as db
from libbear import sync


if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Bear CLI utility.", prog="bear"
    )
    parser.add_argument(
        "--duplicates",
        dest="duplicates",
        action="store_true",
        help="Find notes with duplicate titles",
    )
    parser.add_argument(
        "--sync", dest="sync", action="store_true", help="Sync notes with Mardown files"
    )
    parser.add_argument(
        "--tasks", dest="tasks", action="store_true", help="List all tasks"
    )
    parser.add_argument("--links", dest="links", action="store_true", help="Show callback links")

    args: argparse.Namespace = parser.parse_args()

    conn: Connection = db.get_connection()

    if args.duplicates:
        db.get_duplicate_titles(conn)
    elif args.sync:
        bear_sync = sync.BearSync()
        bear_sync.sync()
    elif args.tasks:
        tasks = db.get_all_tasks(conn)
        for key in tasks:
            print(Style.DIM + key)
            if args.links:
                print(Style.DIM + f"bear://x-callback-url/open-note?id={tasks[key][0].identifier}")
            for task in tasks[key]:
                print(Style.NORMAL + f"\t{task.task}")
    else:
        parser.print_help()

    conn.close()
