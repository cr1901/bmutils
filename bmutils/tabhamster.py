import io
import json
import sys

from . import netscape


def make_bookmarks(th_sess):
    # Convert from milliseconds since epoch to _rounded_ seconds since epoch.
    # From: https://stackoverflow.com/a/3950960
    def rounded_epoch_in_seconds(ts_ms):
        return (ts_ms + 1000 // 2) // 1000

    timestamps = list(map(lambda k: rounded_epoch_in_seconds(int(k[3:])),
                      filter(lambda k: k.startswith("tg_"), th_sess.keys())))

    bookmarks = netscape.Bookmarks(name="TabHamster Sessions",
                                   add_date=min(timestamps),
                                   last_modified=max(timestamps))

    for k, v in th_sess.items():
        if k.startswith("tg_"):
            timestamp = rounded_epoch_in_seconds(int(k[3:]))
            subfolder = netscape.Subfolder(name=v["name"],
                                           add_date=timestamp,
                                           last_modified=timestamp)

            for t in sorted(v["tabs"], key=lambda t: t["id"]):
                shortcut = netscape.Shortcut(name=t["title"],
                                             url=t["url"],
                                             add_date=timestamp,
                                             last_modified=timestamp)
                subfolder.entries.append(shortcut)
            bookmarks.entries.append(subfolder)

    return bookmarks


def write(args):
    with open(args.inp, "r", encoding="utf-8") as fp:
        th_sess = json.load(fp)
        bookmarks = make_bookmarks(th_sess)

    if args.outp is None:
        # https://stackoverflow.com/a/30673656
        utf8_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        bookmarks.write(utf8_stdout)
    else:
        with open(args.outp, "w", encoding="utf-8") as fp:
            bookmarks.write(fp)
