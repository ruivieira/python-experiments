"""Utility to manipulate and query Bear notes"""
# INFO: utility to manipulate and query Bear notes
import argparse
from libbear import database as db
from libbear import sync

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bear CLI utility.', prog='bear')
    parser.add_argument('--duplicates', dest='duplicates', action='store_true',
        help="Find notes with duplicate titles")
    parser.add_argument('--sync', dest='sync', action='store_true',
        help="Sync notes with Mardown files")
    args = parser.parse_args()

    conn = db.get_connection()

    if args.duplicates:
        db.get_duplicate_titles(conn)
    elif args.sync:
        bear_sync = sync.BearSync()
        bear_sync.sync()
    else:
        parser.print_help()
