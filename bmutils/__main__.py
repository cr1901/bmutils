import argparse
from . import tabhamster
from . import chrome


def main():
    parser = argparse.ArgumentParser()
    # https://stackoverflow.com/a/61680800
    parser.set_defaults(func=lambda args: parser.print_help())
    subparsers = parser.add_subparsers()

    th_parser = subparsers.add_parser("tabhamster",
                                      help="Turn TabHamster export into Netscape bookmarks file.")  # noqa: E501
    zc_parser = subparsers.add_parser("zerochrome",
                                      help="Turn Chrome History entries with 0 `last_visit_time` into Netscape bookmarks file.")  # noqa: E501

    th_parser.add_argument("inp")
    th_parser.add_argument("outp", nargs="?")
    th_parser.set_defaults(func=tabhamster.write)

    zc_parser.add_argument("inp")
    zc_parser.add_argument("outp", nargs="?")
    zc_parser.set_defaults(func=chrome.write)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
