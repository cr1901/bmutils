import io
import sqlite3
import sys
import time

from . import netscape


def make_bookmarks(con):
    rows = con.execute("SELECT * FROM urls WHERE last_visit_time == 0;").fetchall()  # noqa: E501
    timestamp = int(time.time())

    bookmarks = netscape.Bookmarks(name="Chrome History Entries With Zero Timestamps",  # noqa: E501
                                   add_date=timestamp,
                                   last_modified=timestamp)

    for r in sorted(rows, key=lambda r: r["id"]):
        shortcut = netscape.Shortcut(name=r["title"],
                                     url=r["url"],
                                     add_date=timestamp,
                                     last_modified=timestamp)
        bookmarks.entries.append(shortcut)

    return bookmarks


def write(args):
    with sqlite3.connect(f"file:{args.inp}?mode=ro", uri=True) as con:
        con.row_factory = sqlite3.Row
        bookmarks = make_bookmarks(con)

    if args.outp is None:
        # https://stackoverflow.com/a/30673656
        utf8_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        bookmarks.write(utf8_stdout)
    else:
        with open(args.outp, "w", encoding="utf-8") as fp:
            bookmarks.write(fp)
