import sys
import traceback

from .xtraceback import XTraceback


class StdlibCompatMeta(type):

    def __init__(mcs, name, bases, dict_):
        for key in dict_.keys():
            if hasattr(traceback, key):
                mcs._traceback_patch_functions.append(key)
        super(StdlibCompatMeta, mcs).__init__(name, bases, dict_)


class StdlibCompat(object):
    """
    Provides interface compatibility with the stdlib traceback module
    
    :ivar defaults: Default options to apply to XTracebacks created by this instance
    :type defaults: dict
    """

    __metaclass__ = StdlibCompatMeta

    _patch_stack = []
    _traceback_patch_functions = []

    def __init__(self, **defaults):
        self.defaults = defaults
        self._entries = []

    def _patch(self, target, member, patch):
        current = getattr(target, member)
        self._patch_stack.append((target, member, current))
        setattr(target, member, patch)

    def install_excepthook(self):
        self._patch(sys, "excepthook", self.print_exception)

    def __enter__(self):
        if not self._entries:
            # first entry - doing it like this to ease testing
            for func_name in self._traceback_patch_functions:
                self._patch(traceback, func_name, getattr(self, func_name))
        self._entries.append(None)
        return self

    def __exit__(self, *exc_info):
        self._entries.pop()
        if not self._entries:
            while self._patch_stack:
                target, member, patch = self._patch_stack.pop()
                setattr(target, member, patch)

    def __del__(self):
        if self._entries:
            self.__exit__(None, None, None)
        assert not self._entries

    def _factory(self, etype, value, tb, limit=None, file=None, **options):
        if limit is not None:
            options["limit"] = limit
        if file is not None:
            options["stream"] = file
        _options = self.defaults.copy()
        _options.update(options)
        return XTraceback(etype, value, tb, **_options)

    def format_tb(self, tb, limit=None, **options):
        xtb = self._factory(None, None, tb, limit, **options)
        return xtb.format_tb()

    def format_exception_only(self, etype, value, **options):
        xtb = self._factory(etype, value, None, **options)
        return xtb.format_exception_only()

    def format_exception(self, etype, value, tb, limit=None, **options):
        xtb = self._factory(etype, value, tb, limit, **options)
        return xtb.format_exception()

    def format_exc(self, limit=None, **options):
        return self.format_exception(*sys.exc_info(), limit=limit, **options)

    def print_tb(self, tb, limit=None, file=None, **options):
        xtb = self._factory(None, None, tb, limit, file, **options)
        xtb.print_tb()

    def print_exception(self, etype, value, tb, limit=None, file=None, **options):
        xtb = self._factory(etype, value, tb, limit, file, **options)
        xtb.print_exception()

    def print_exc(self, limit=None, file=None, **options):
        self.print_exception(*sys.exc_info(), limit=limit, file=file, **options)
