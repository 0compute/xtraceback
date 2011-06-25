import sys
import traceback

from .xtraceback import XTraceback


class TracebackCompatMeta(type):

    def __init__(mcs, name, bases, dict_):
        for key in dict_.keys():
            if hasattr(traceback, key):
                mcs._traceback_patch_functions.append(key)
        super(TracebackCompatMeta, mcs).__init__(name, bases, dict_)


class TracebackCompat(object):
    
    __metaclass__ = TracebackCompatMeta
    
    _patch_stack = []
    _traceback_patch_functions = []

    def __init__(self,  **defaults):
        self.color = defaults.pop("color", False)
        self.defaults = defaults
        
    def update_defaults(self,  **defaults):
        color = defaults.pop("color", None)
        if color is not None:
            self.color = color
        self.defaults.update(defaults)
    
    def _patch(self,  target, member, patch):
        current = getattr(target, member)
        self._patch_stack.append((target, member, current))
        setattr(target, member, patch)
    
    def install_excepthook(self):
        self._patch(sys, "excepthook", self.print_exception)
    
    def __enter__(self):
        for func_name in self._traceback_patch_functions:
            self._patch(traceback, func_name, getattr(self, func_name))
        return self

    def __exit__(self,  *exc_info):
        while self._patch_stack:
            target, member, patch = self._patch_stack.pop()
            setattr(target, member, patch)
    
    def _get_options(self, override, limit=None):
        options = self.defaults.copy()
        options.update(override)
        if limit is not None:
            options["limit"] = limit
        return options
    
    def format_tb(self, tb, limit=None, **options):
        color = options.pop("color", self.color)
        options = self._get_options(options, limit)
        xtb = XTraceback(None, None, tb, **options)
        return xtb.format_tb(color)
    
    def format_exception_only(self, etype, value, **options):
        color = options.pop("color", self.color)
        options = self._get_options(options)
        xtb = XTraceback(etype, value, None, **options)
        return xtb.format_exception_only(color)
    
    def format_exception(self, etype, value, tb, limit=None, **options):
        color = options.pop("color", self.color)
        options = self._get_options(options, limit)
        xtb = XTraceback(etype, value, tb, **options)
        return xtb.format_exception(color)
    
    def format_exc(self, limit=None, **options):
        return self.format_exception(*sys.exc_info(), limit=limit, **options)
    
    def _get_print_options(self, stream, color):
        if stream is None:
            stream = sys.stderr
        if color is None:
            color = hasattr(stream, "isatty") and stream.isatty()
        return stream, color
        
    def print_tb(self, tb, limit=None, file=None, **options):
        # intentionally not falling back to self.color if color is not in 
        # options because None here means that we decide based on whether
        # the stream is a tty or not
        stream, color = self._get_print_options(file, options.pop("color", None))
        options = self._get_options(options, limit)
        xtb = XTraceback(None, None, tb, **options)
        stream.write("".join(xtb.format_tb(color)))
        
    def print_exception(self, etype, value, tb, limit=None, file=None, **options):
        stream, color = self._get_print_options(file, options.pop("color", None))
        options = self._get_options(options, limit)
        xtb = XTraceback(etype, value, tb, **options)
        stream.write("".join(xtb.format_exception(color)))
    
    def print_exc(self, limit=None, file=None, **options):
        self.print_exception(*sys.exc_info(), limit=limit, file=file, **options)
