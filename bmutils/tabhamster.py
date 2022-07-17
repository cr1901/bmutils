import json

from . import netscape as nsutil

import NetscapeBookmarksFileParser as nsparser
import NetscapeBookmarksFileParser.creator  # noqa: F401


def make_bookmarks(th_sess):
    # Convert from milliseconds since epoch to _rounded_ seconds since epoch.
    # From: https://stackoverflow.com/a/3950960
    def rounded_epoch_in_seconds(ts_ms):
        return (ts_ms + 1000 // 2) // 1000

    timestamps = list(map(lambda k: rounded_epoch_in_seconds(int(k[3:])),
                      filter(lambda k: k.startswith("tg_"), th_sess.keys())))

    bookmarks = nsparser.BookmarkFolder()
    bookmarks.name = "TabHamster Sessions"
    bookmarks.add_date_unix = min(timestamps)
    bookmarks.last_modified_unix = max(timestamps)

    for k, v in th_sess.items():
        if k.startswith("tg_"):
            timestamp = rounded_epoch_in_seconds(int(k[3:]))

            subfolder = nsparser.BookmarkFolder()
            subfolder.name = v["name"]
            subfolder.add_date_unix = timestamp
            subfolder.last_modified_unix = timestamp

            for t in sorted(v["tabs"], key=lambda t: t["id"]):
                shortcut = nsparser.BookmarkShortcut()
                shortcut.name = t["title"]
                shortcut.href = t["url"]
                shortcut.add_date_unix = timestamp
                shortcut.last_modified_unix = timestamp

                subfolder.items.append(shortcut)
            bookmarks.items.append(subfolder)

    return nsutil.prepare_top_level(bookmarks)


def write(args):
    with open(args.inp, "r", encoding="utf-8") as fp:
        th_sess = json.load(fp)
        bookmarks = make_bookmarks(th_sess)

    nsutil.write(bookmarks, args.outp)
