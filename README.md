# `bmutils`

`bmutils` is a Python 3 application which converts various browser history
and add-on formats into a [Netscape-compatible](https://docs.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/aa753582(v=vs.85))
bookmarks format that basically any browser can import.

Right now, I have importers for the [TabHamster](https://github.com/onikienko/TabHamster)
export format and Chrome `History` [SQLite](https://www.sqlite.org/index.html)
DB for finding entries with a missing/zero `last_visit_time` value.

Because [f-strings](https://peps.python.org/pep-0498/) are liberally used, this
application requires Python 3.6 or above.

## Installation

I don't plan on releasing this onto [PyPI](https://pypi.org), so installation
for now is:

```sh
pip3 install git+https://github.com/cr1901/bmutils.git
```

To install a development snapshot, run the following:

```sh
git clone https://github.com/cr1901/bmutils.git
cd bmutils
pip3 install -e .
```

## Example Usage

Before installing (from within the Git repo root):

```console
python3 -m bmutils tabhamster /path/to/tabhamster/export.txt tabhamster.html
```

After installing:

```console
bmutils tabhamster /path/to/tabhamster/export.txt tabhamster.html
```

If the output HTML argument isn't supplied, `bmutils` will print `utf-8` to
`stdout` by default.
