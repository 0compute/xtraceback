import functools
import sys
import traceback

from .xtraceback import XTraceback


__all__ = ("format_tb", "format_exception_only", "format_exception",
           "format_exc", "print_tb", "print_exception", "print_exc")
_patch_stack = []


def _patch(target, member, patch):
    global _patch_stack
    current = getattr(target, member)
    _patch_stack.append((target, member, current))
    setattr(target, member, patch)


def install(**defaults):
    for func_name in __all__:
        method = functools.partial(globals()[func_name], **defaults)
        _patch(traceback, func_name, method)
    _patch(sys, "excepthook", print_exception)


def uninstall():
    global _patch_stack
    while _patch_stack:
        target, member, patch = _patch_stack.pop()
        setattr(target, member, patch) 


def _stream_defaults(limit, stream):
    if limit is None and hasattr(sys, "tracebacklimit"):
        limit = sys.tracebacklimit
    if stream is None:
        stream = sys.stderr
    return limit, stream


def _with_newlines(lines):
    return [l + "\n" for l in lines]


def format_tb(tb, limit=None, **options):
    options["limit"] = limit 
    xtb = XTraceback(None, None, tb, **options)
    return _with_newlines(xtb.formatted_tb)


def print_tb(tb, limit=None, file=None, **options):
    limit, stream = _stream_defaults(limit, file)
    options["limit"] = limit 
    xtb = XTraceback(None, None, tb, **options)
    stream.write(xtb.formatted_tb_string)
    

def format_exception_only(etype, value, **options):
    xtb = XTraceback(etype, value, None, **options)
    return _with_newlines(xtb.formatted_exception_only)


def format_exception(etype, value, tb, limit=None, **options):
    options["limit"] = limit 
    xtb = XTraceback(etype, value, tb, **options)
    return _with_newlines(xtb.formatted_exception)


def print_exception(etype, value, tb, limit=None, file=None, **options):
    limit, stream = _stream_defaults(limit, file)
    options["limit"] = limit 
    xtb = XTraceback(etype, value, tb, **options)
    stream.write(xtb.formatted_exception_string)


def format_exc(limit=None, **options):
    return format_exception(*sys.exc_info(), limit=limit, **options)


def print_exc(limit=None, file=None, **options):
    print_exception(*sys.exc_info(), limit=limit, file=file, **options)
