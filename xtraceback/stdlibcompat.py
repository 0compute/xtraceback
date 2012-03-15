import functools
import sys
import traceback

from .xtraceback import XTraceback


class StdlibCompatMeta(type):
    """
    A metaclass for StdlibCompat that collects methods to patch on to the
    `traceback` module
    """

    def __init__(mcs, name, bases, dict_):
        for key in dict_.keys():
            if hasattr(traceback, key):
                mcs.traceback_patch_functions.append(key)
        super(StdlibCompatMeta, mcs).__init__(name, bases, dict_)


class StdlibCompat(object):
    """
    Provides interface compatibility with the stdlib traceback module

    :ivar defaults: Default options to apply to XTracebacks created by this
                    instance
    :type defaults: dict
    """

    __metaclass__ = StdlibCompatMeta

    # a stack of patches that have been applied as (target, member, pre-patch-value)
    _patch_stack = []

    # names of methods in this class that patch functions of the same name in
    # the `traceback` module.
    traceback_patch_functions = []

    def __init__(self, **defaults):
        self.defaults = defaults
        self._entered = False

    def _patch(self, target, member, patch):
        current = getattr(target, member)
        self._patch_stack.append((target, member, current))
        setattr(target, member, patch)

    def install_sys_excepthook(self):
        """
        Patch `sys.excepthook`
        """
        self._patch(sys, "excepthook", self.print_exception)

    def install_traceback(self):
        """
        Patch the stdlib traceback module's top level functions with
        replacements from this class

        The functions patched are named in `traceback_patch_functions`
        """
        for func_name in self.traceback_patch_functions:
            self._patch(traceback, func_name, getattr(self, func_name))

    def install_logging(self, handler, **options):
        """
        Patch a `logging.Handler`'s `formatter` so that it uses XTraceback
        to format exceptions

        :param handler: The handler to patch
        :type handler: logging.Handler
        :param options:
        """

        formatter = handler.formatter

        def formatException(ei):
            return str(self._factory(*ei, **options))

        self._patch(formatter, "formatException", formatException)

        # this is shit but we're stuck with the stdlib implementation since
        # it caches the result of formatException which we don't want to do
        # as it will screw up other formatters who are expecting a regular
        # traceback
        _format = formatter.format

        def format(record):
            record.exc_text = None
            formatted = _format(record)
            record.exc_text = None
            return formatted

        self._patch(formatter, "format", format)

    def install(self):
        self.install_sys_excepthook()
        self.install_traceback()

    def uninstall(self):
        while self._patch_stack:
            target, member, patch = self._patch_stack.pop()
            setattr(target, member, patch)

    def __enter__(self):
        if self._entered:
            raise RuntimeError("Already entered %r" % self)
        self._entered = True
        self.install_traceback()
        return self

    def __exit__(self, *exc_info):
        if not self._entered:
            raise RuntimeError("Not entered %r" % self)
        self.uninstall()
        self._entered = False

    def _factory(self, etype, value, tb, limit=None, **options):
        options["limit"] = getattr(sys, "tracebacklimit", None) \
                               if limit is None else limit
        _options = self.defaults.copy()
        _options.update(options)
        return XTraceback(etype, value, tb, **_options)

    def _print_factory(self, etype, value, tb, limit=None, file=None, **options):
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
