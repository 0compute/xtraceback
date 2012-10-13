import functools
import sys
import traceback

from stacked import Stacked

from .xtraceback import XTraceback


class TracebackCompat(Stacked):
    """
    A context manager that patches the stdlib traceback module

    Functions in the traceback module that exist as a method of this class are
    replaced with equivalents that use XTraceback.

    :cvar NOPRINT: Exception types that we don't print for (includes None)
    :type NOPRINT: tuple

    :ivar defaults: Default options to apply to XTracebacks created by this
                    instance
    :type defaults: dict
    """

    NOPRINT = (None, KeyboardInterrupt)

    def __init__(self, **defaults):
        super(TracebackCompat, self).__init__()
        self.defaults = defaults
        # register patches for methods that wrap traceback functions
        for key in dir(traceback):
            if hasattr(self, key):
                self._register_patch(traceback, key, getattr(self, key))

    #def __exit__(self, etype, evalue, tb):
        #if etype not in self.NOPRINT:
            #self.print_exception(etype, evalue, tb)
        #super(TracebackCompat, self).__exit__(etype, evalue, tb)

    def _factory(self, etype, value, tb, limit=None, **options):
        options["limit"] = \
            getattr(sys, "tracebacklimit", None) if limit is None else limit
        _options = self.defaults.copy()
        _options.update(options)
        return XTraceback(etype, value, tb, **_options)

    def _print_factory(self, etype, value, tb, limit=None, file=None,
                       **options):
        # late binding here may cause problems where there is no sys i.e. on
        # google app engine but it is required for cases where sys.stderr is
        # rebound i.e. under nose
        if file is None and hasattr(sys, "stderr"):
            file = sys.stderr
        options["stream"] = file
        return self._factory(etype, value, tb, limit, **options)

    @functools.wraps(traceback.format_tb)
    def format_tb(self, tb, limit=None, **options):
        xtb = self._factory(None, None, tb, limit, **options)
        return xtb.format_tb()

    @functools.wraps(traceback.format_exception_only)
    def format_exception_only(self, etype, value, **options):
        xtb = self._factory(etype, value, None, **options)
        return xtb.format_exception_only()

    @functools.wraps(traceback.format_exception)
    def format_exception(self, etype, value, tb, limit=None, **options):
        xtb = self._factory(etype, value, tb, limit, **options)
        return xtb.format_exception()

    @functools.wraps(traceback.format_exc)
    def format_exc(self, limit=None, **options):
        options["limit"] = limit
        return "".join(self.format_exception(*sys.exc_info(), **options))

    @functools.wraps(traceback.print_tb)
    def print_tb(self, tb, limit=None, file=None, **options):
        xtb = self._print_factory(None, None, tb, limit, file, **options)
        xtb.print_tb()

    @functools.wraps(traceback.print_exception)
    def print_exception(self, etype, value, tb, limit=None, file=None,
                        **options):
        xtb = self._print_factory(etype, value, tb, limit, file, **options)
        xtb.print_exception()

    @functools.wraps(traceback.print_exc)
    def print_exc(self, limit=None, file=None, **options):
        options["limit"] = limit
        options["file"] = file
        self.print_exception(*sys.exc_info(), **options)
