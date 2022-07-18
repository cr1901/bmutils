import re
import time
import tweepy

from datetime import datetime

from .. import netscape as nsutil

import NetscapeBookmarksFileParser as nsparser
import NetscapeBookmarksFileParser.creator  # noqa: F401
import NetscapeBookmarksFileParser.parser  # noqa: F401


class IdExtractor(nsutil.Visitor):
    def __init__(self, bookmarks):
        super().__init__(bookmarks)
        self.ids = []
        self.id_re = re.compile("https://twitter.com/.*/status/([0-9]*)")

    def visit_shortcut(self, shortcut):
        self.ids.append(self.id_re.match(shortcut.href)[1])


def save(args, client):
    def bookmarks_with_author(pagination_token):
        return client.get_bookmarks(expansions=["author_id"],
                                    tweet_fields=["created_at"],
                                    pagination_token=pagination_token)

    timestamp = int(time.time())
    bookmarks = NetscapeBookmarksFileParser.BookmarkFolder()
    bookmarks.name = "Twitter Bookmarks"
    bookmarks.add_date_unix = timestamp
    bookmarks.last_modified_unix = timestamp

    # tweet_user = []
    for resp in tweepy.Paginator(bookmarks_with_author):
        # It is up to us to make a quick mapping from author_id to user.
        user_dict = {}
        for u in resp.includes["users"]:
            user_dict[u.id] = u

        for tweet in resp.data:
            timestamp = int(datetime.fromisoformat(str(tweet.created_at))
                                    .timestamp())
            shortcut = nsparser.BookmarkShortcut()
            shortcut.name = f"{user_dict[tweet.author_id].name}: {tweet.text}"
            shortcut.href = f"https://twitter.com/{user_dict[tweet.author_id].username}/status/{tweet.id}"  # noqa: E501
            shortcut.add_date_unix = timestamp
            shortcut.last_modified_unix = timestamp
            bookmarks.items.append(shortcut)

        # ADD_DATE = Tweet post date.
        # LAST_MODIFIED = Heuristically a lower bound on when the bookmark
        # was added; Twitter does not save the time/date you added a bookmark.
        added_lower_bound = int(datetime.fromisoformat("2018-02-28").timestamp())  # noqa: E501

        for e in reversed(bookmarks.items):
            if e.add_date_unix > added_lower_bound:
                added_lower_bound = e.add_date_unix
            else:
                e.last_modified_unix = added_lower_bound

    nsutil.write(nsutil.prepare_top_level(bookmarks), args.outp)


def delete(args, client):
    with open(args.inp, encoding="utf-8") as fp:
        extractor = IdExtractor(nsparser.NetscapeBookmarksFile(fp).parse())
        extractor.visit()

    for id in extractor.ids:
        client.remove_bookmark(id)
