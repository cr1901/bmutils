import sqlite3
import time

from . import netscape as nsutil

import NetscapeBookmarksFileParser as nsparser
import NetscapeBookmarksFileParser.creator  # noqa: F401


def make_bookmarks(con):
    rows = con.execute("SELECT * FROM urls WHERE last_visit_time == 0;").fetchall()  # noqa: E501
    timestamp = int(time.time())

    bookmarks = NetscapeBookmarksFileParser.BookmarkFolder()
    bookmarks.name = "Chrome History Entries With Zero Timestamps"
    bookmarks.add_date_unix = timestamp
    bookmarks.last_modified_unix = timestamp

    for r in sorted(rows, key=lambda r: r["id"]):
        shortcut = nsparser.BookmarkShortcut()
        shortcut.name = r["title"]
        shortcut.href = r["url"]
        shortcut.add_date_unix = timestamp
        shortcut.last_modified_unix = timestamp
        bookmarks.items.append(shortcut)

    return nsutil.prepare_top_level(bookmarks)


def write(args):
    with sqlite3.connect(f"file:{args.inp}?mode=ro", uri=True) as con:
        con.row_factory = sqlite3.Row
        bookmarks = make_bookmarks(con)

    nsutil.write(bookmarks, args.outp)
