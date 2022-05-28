import argparse
import json
import sys


# Convert from milliseconds since epoch to _rounded_ seconds since epoch.
# From: https://stackoverflow.com/a/3950960
def rounded_epoch_in_seconds(ts_ms):
    return (ts_ms + 1000 // 2) // 1000


def write_bookmarks(fp, th_sess):
    indent = 0
    ind_inc = 4

    # https://docs.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/aa753582(v=vs.85)?redirectedfrom=MSDN
    netscape_header = f"""{'':<{indent}}<!DOCTYPE NETSCAPE-Bookmark-file-1>
    {'':<{indent}}<!--This is an automatically generated file.
    {'':<{indent}}It will be read and overwritten.
    {'':<{indent}}Do Not Edit! -->
    {'':<{indent}}<Title>Bookmarks</Title>
    {'':<{indent}}<H1>Bookmarks</H1>"""

    timestamps = list(map(lambda k: rounded_epoch_in_seconds(int(k[3:])),
                      filter(lambda k: k.startswith("tg_"), th_sess.keys())))

    fp.write(netscape_header)
    fp.write(f"{'':<{indent}}<DL>\n")
    indent += ind_inc
    fp.write(f"{'':<{indent}}<DT><H3 ADD_DATE=\"{min(timestamps)}\" LAST_MODIFIED=\"{max(timestamps)}\">TabHamster Sessions</H3>\n")  # noqa: E501
    fp.write(f"{'':<{indent}}<DL><P>\n")
    indent += ind_inc

    for k, v in th_sess.items():
        if k.startswith("tg_"):
            timestamp = rounded_epoch_in_seconds(int(k[3:]))
            fp.write(f"{'':<{indent}}<DT><H3 ADD_DATE=\"{timestamp}\" LAST_MODIFIED=\"{timestamp}\">{v['name']}</H3>\n")  # noqa: E501
            fp.write(f"{'':<{indent}}<DL><P>\n")

            indent += ind_inc
            for t in sorted(v["tabs"], key=lambda t: t["id"]):
                fp.write(f"{'':<{indent}}<DT><A HREF=\"{t['url']}\" ADD_DATE=\"{timestamp}\" LAST_MODIFIED=\"{timestamp}\">{t['title']}</A>\n")  # noqa: E501
            indent -= ind_inc
            fp.write(f"{'':<{indent}}</DL><P>\n")

    indent -= ind_inc
    fp.write(f"{'':<{indent}}</DL><P>\n")
    indent -= ind_inc
    fp.write(f"{'':<{indent}}</DL>\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("inp")
    parser.add_argument("outp", nargs="?")

    args = parser.parse_args()

    with open(args.inp, "r", encoding="utf-8") as fp:
        th_sess = json.load(fp)

    if args.outp is None:
        write_bookmarks(sys.stdout, th_sess)
    else:
        with open(args.outp, "w", encoding="utf-8") as fp:
            write_bookmarks(fp, th_sess)
