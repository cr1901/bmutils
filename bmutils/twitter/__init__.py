from . import bookmarks
from . import oauth


def write(args):
    if args.cmd in ("bmdel") and args.dry_run:
        client = None
    else:
        creds = oauth.get_credentials(args.username, args.reconfig)
        client = oauth.get_client(creds)

    if args.cmd == "bmsave":
        bookmarks.save(args, client)
    elif args.cmd == "bmsaveall":
        bookmarks.saveall(args, client)
    elif args.cmd == "bmdel":
        bookmarks.delete(args, client)
    elif args.cmd == "lists":
        raise NotImplementedError
    else:
        assert False
