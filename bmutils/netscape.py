import io
import sys

import NetscapeBookmarksFileParser as netscape
import NetscapeBookmarksFileParser.creator  # noqa: F401

# Convenience functions for writing out/reading in Netscape Bookmarks files,
# using an exising parser.


def prepare_top_level(bookmarks):
    top_level = netscape.NetscapeBookmarksFile()
    # Top-level bookmarks name is ignored without these lines.
    top_level.bookmarks = netscape.BookmarkFolder()
    top_level.bookmarks.items.append(bookmarks)

    return top_level


def write(bookmarks, fn):
    if fn is None:
        # https://stackoverflow.com/a/30673656
        utf8_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        utf8_stdout.write("\n".join(bookmarks.create_file()))
    else:
        with open(fn, "w", encoding="utf-8") as fp:
            fp.write("\n".join(bookmarks.create_file()))
