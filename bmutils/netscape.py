import io
import sys

import NetscapeBookmarksFileParser as netscape
import NetscapeBookmarksFileParser.creator  # noqa: F401

# Convenience functions and classes for writing out/reading in Netscape
# Bookmarks files, using an exising parser.


class Visitor:
    def __init__(self, bookmarks):
        # Make the top-level bookmarks object a list if it isn't already
        # (to support passing in various object types).
        if isinstance(bookmarks, netscape.NetscapeBookmarksFile):
            self.bookmarks = [bookmarks.bookmarks]
        elif isinstance(bookmarks, netscape.BookmarkFolder):
            self.bookmarks = [bookmarks]

    def visit(self):
        to_visit = list(reversed(self.bookmarks))

        last_visited = None

        while to_visit:
            entry = to_visit[-1]

            if isinstance(entry, netscape.BookmarkFolder):
                if entry.items[-1] is last_visited:
                    self.visit_folder(entry)
                    last_visited = entry
                    to_visit.pop()
                else:
                    to_visit.extend(list(reversed(entry.items)))
            elif isinstance(entry, netscape.BookmarkShortcut):
                self.visit_shortcut(entry)
                last_visited = entry
                to_visit.pop()
            elif isinstance(entry, netscape.NetscapeBookmarksFile):
                to_visit.extend(entry.bookmarks)
            else:
                raise ValueError("not a parsed Netscape bookmarks file")

    def visit_shortcut(self, shortcut):
        pass

    def visit_folder(self, folder):
        pass


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
