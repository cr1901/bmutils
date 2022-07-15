from . import bookmarks
from . import oauth


def write(args):
    creds = oauth.get_credentials(args.username, args.reconfig)
    client = oauth.get_client(creds)

    if args.cmd == "bmsave":
        bookmarks.save(args, client)
    elif args.cmd == "bmdel":
        raise NotImplementedError
    elif args.cmd == "lists":
        raise NotImplementedError
    else:
        assert False
