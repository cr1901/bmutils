import time
import tweepy

from datetime import datetime

from .. import netscape


def save(args, client):
    def bookmarks_with_author(pagination_token):
        return client.get_bookmarks(expansions=["author_id"],
                                    tweet_fields=["created_at"],
                                    pagination_token=pagination_token)

    timestamp = int(time.time())
    bookmarks = netscape.Bookmarks(name="Twitter Bookmarks",
                                   add_date=timestamp,
                                   last_modified=timestamp)

    # tweet_user = []
    for resp in tweepy.Paginator(bookmarks_with_author):
        # It is up to us to make a quick mapping from author_id to user.
        user_dict = {}
        for u in resp.includes["users"]:
            user_dict[u.id] = u

        for tweet in resp.data:
            timestamp = int(datetime.fromisoformat(str(tweet.created_at))
                                    .timestamp())
            shortcut = netscape.Shortcut(name=f"{user_dict[tweet.author_id].name}: {tweet.text}",  # noqa: E501
                                         url=f"https://twitter.com/{user_dict[tweet.author_id].username}/status/{tweet.id}",  # noqa: E501
                                         add_date=timestamp,
                                         last_modified=timestamp)

            bookmarks.entries.append(shortcut)

        # ADD_DATE = Tweet post date.
        # LAST_MODIFIED = Heuristically a lower bound on when the bookmark
        # was added; Twitter does not save the time/date you added a bookmark.
        added_lower_bound = int(datetime.fromisoformat("2018-02-28").timestamp())  # noqa: E501

        for e in reversed(bookmarks.entries):
            if e.add_date > added_lower_bound:
                added_lower_bound = e.add_date
            else:
                e.last_modified = added_lower_bound

    with open(args.outp, "w", encoding="utf-8") as fp:
        bookmarks.write(fp)
