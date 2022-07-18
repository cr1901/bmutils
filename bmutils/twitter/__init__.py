from . import bookmarks
from . import oauth


def write(args):
    creds = oauth.get_credentials(args.username, args.reconfig)
    client = oauth.get_client(creds)

    if args.cmd == "bmsave":
        bookmarks.save(args, client)
    if args.cmd == "bmsaveall":
        bookmarks.saveall(args, client)
    elif args.cmd == "bmdel":
        bookmarks.delete(args, client)
    elif args.cmd == "lists":
        raise NotImplementedError
    else:
        assert False
