import argparse
from . import tabhamster


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    th_parser = subparsers.add_parser("tabhamster",
                                      help="Turn TabHamster export into Netscape bookmarks file.")  # noqa: E501

    th_parser.add_argument("inp")
    th_parser.add_argument("outp", nargs="?")
    th_parser.set_defaults(func=tabhamster.write)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
