import argparse
from . import tabhamster
from . import chrome
from . import twitter


def main():
    parser = argparse.ArgumentParser()
    # https://stackoverflow.com/a/61680800
    parser.set_defaults(func=lambda args: parser.print_help())
    subparsers = parser.add_subparsers()

    th_parser = subparsers.add_parser("tabhamster",
                                      help="turn TabHamster export into Netscape bookmarks file")  # noqa: E501
    zc_parser = subparsers.add_parser("zerochrome",
                                      help="turn Chrome History entries with 0 `last_visit_time` into Netscape bookmarks file")  # noqa: E501
    twt_parser = subparsers.add_parser("twitter",
                                       help="turn Twitter bookmarks and lists into Netscape bookmarks file")  # noqa: E501

    th_parser.add_argument("inp")
    th_parser.add_argument("outp", nargs="?")
    th_parser.set_defaults(func=tabhamster.write)

    zc_parser.add_argument("inp")
    zc_parser.add_argument("outp", nargs="?")
    zc_parser.set_defaults(func=chrome.write)

    twt_parser.add_argument("-c", dest="reconfig", action="store_true",
                            help="force credential update")
    twt_parser.add_argument("username", help="Twitter username")
    twt_parser.set_defaults(func=twitter.write)
    twt_subparsers = twt_parser.add_subparsers(dest="cmd")

    twt_list_parser = twt_subparsers.add_parser("lists", help="parse Twitter lists")  # noqa: E501
    twt_bmsave_parser = twt_subparsers.add_parser("bmsave", help="parse Twitter bookmarks")  # noqa: E501
    twt_bmdel_parser = twt_subparsers.add_parser("bmdel", help="delete Twitter bookmarks from account")  # noqa: E501

    twt_list_parser.add_argument("outp")
    twt_bmsave_parser.add_argument("outp")
    twt_bmdel_parser.add_argument("inp")

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
