import inspect
import os
import pprint

from .defaults import DEFAULT_WIDTH

#: Filesystem path to the Python standard library
OS_SOURCE = inspect.getsourcefile(os)
STDLIB_PATH = None if OS_SOURCE is None \
    else os.path.dirname(os.path.realpath(OS_SOURCE))

#: A dictionary keyed by type with values as the wrapper for string
#: representation of the type
REFORMAT = {
    dict: ("{", "}"),
    list: ("[", "]"),
    tuple: ("(", ")"),
    set: ("set([", "])"),
    frozenset: ("frozenset([", "])"),
}


def format_filename(options, filename):
    if options.shorten_filenames:
        filename = os.path.realpath(filename)
        if STDLIB_PATH is not None \
                and filename.startswith(STDLIB_PATH):
            filename = filename.replace(STDLIB_PATH, "<stdlib>")
        else:
            # os.path.relpath was introduced in python 2.5
            relative = os.path.relpath(filename)
            if len(relative) < len(filename):
                filename = relative
    # using str on filename to make Jython (default string is unicode)
    # consistent with CPython
    return str(filename)


def format_variable(key, value, indent=4, prefix="", print_width=DEFAULT_WIDTH):

    separator = " = "

    vtype = type(value)
    try:
        pvalue = pprint.pformat(value, indent=0)
    except:
        pvalue = "<unprintable %s object>" % vtype.__name__

    base_size = indent + len(prefix) + len(key) + len(separator)

    if base_size + len(pvalue) > print_width:
        reformat = REFORMAT.get(vtype)
        if reformat is None:
            # truncate long strings - minus 3 for the ellipsis
            pvalue = pvalue[:print_width - base_size - 3] + "..."
        else:
            start, end = reformat
            lines = map(str.strip,
                        pvalue.lstrip(start).rstrip(end).splitlines())
            sub_indent = "\n" + " " * (indent + 4)
            pvalue = "".join((start, sub_indent, sub_indent.join(lines),
                              ",", sub_indent, end))

    return "".join((" " * indent, prefix, key, separator, pvalue))
