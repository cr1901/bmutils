class Subfolder:
    def __init__(self, *, name, add_date, last_modified):
        self.name = name
        self.add_date = add_date
        self.last_modified = last_modified
        self.entries = []

    def write(self, fp, indent, ind_inc):
        fp.write(f"{'':<{indent}}<DT><H3 ADD_DATE=\"{self.add_date}\" LAST_MODIFIED=\"{self.last_modified}\">{self.name}</H3>\n")  # noqa: E501
        fp.write(f"{'':<{indent}}<DL><P>\n")
        indent += ind_inc
        for e in self.entries:
            e.write(fp, indent, ind_inc)
        indent -= ind_inc
        fp.write(f"{'':<{indent}}</DL><P>\n")


class Shortcut:
    def __init__(self, *, name, url, add_date, last_modified):
        self.name = name
        self.url = url
        self.add_date = add_date
        self.last_modified = last_modified

    def write(self, fp, indent, ind_inc):
        fp.write(f"{'':<{indent}}<DT><A HREF=\"{self.url}\" ADD_DATE=\"{self.add_date}\" LAST_MODIFIED=\"{self.last_modified}\">{self.name}</A>\n")  # noqa: E501


class Bookmarks:
    def __init__(self, *, name, add_date, last_modified):
        self.name = name
        self.add_date = add_date
        self.last_modified = last_modified
        self.entries = []

    def write(self, fp):
        indent = 0
        ind_inc = 4

        # https://docs.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/aa753582(v=vs.85)?redirectedfrom=MSDN
        netscape_header = f"""{'':<{indent}}<!DOCTYPE NETSCAPE-Bookmark-file-1>
    {'':<{indent}}<!--This is an automatically generated file.
    {'':<{indent}}It will be read and overwritten.
    {'':<{indent}}Do Not Edit! -->
    {'':<{indent}}<Title>Bookmarks</Title>
    {'':<{indent}}<H1>Bookmarks</H1>"""

        fp.write(netscape_header)
        fp.write(f"{'':<{indent}}<DL>\n")
        indent += ind_inc
        fp.write(f"{'':<{indent}}<DT><H3 ADD_DATE=\"{self.add_date}\" LAST_MODIFIED=\"{self.last_modified}\">{self.name}</H3>\n")  # noqa: E501
        fp.write(f"{'':<{indent}}<DL><P>\n")
        indent += ind_inc

        for e in self.entries:
            e.write(fp, indent, ind_inc)

        indent -= ind_inc
        fp.write(f"{'':<{indent}}</DL><P>\n")
        indent -= ind_inc
        fp.write(f"{'':<{indent}}</DL>\n")
