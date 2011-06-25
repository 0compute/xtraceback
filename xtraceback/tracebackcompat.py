import sys
import traceback

from .xtraceback import XTraceback


class TracebackCompatMeta(type):

    def __init__(self, name, bases, dict_):
        for key in dict_.keys():
            if hasattr(traceback, key):
                self._traceback_patch_functions.append(key)
        super(TracebackCompatMeta, self).__init__(name, bases, dict_)


class TracebackCompat(object):
    
    __metaclass__ = TracebackCompatMeta
    
    _patch_stack = []
    _traceback_patch_functions = []

    def __init__(self,  **defaults):
        self.defaults = defaults
    
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
    
    def _with_newlines(self,  lines):
        return [l + "\n" for l in lines]
    
    def _get_options(self, override, limit=None):
        options = self.defaults.copy()
        options.update(override)
        if limit is not None:
            options["limit"] = limit
        return options
    
    def format_tb(self, tb, limit=None, **options):
        options = self._get_options(options, limit)
        xtb = XTraceback(None, None, tb, **options)
        return self._with_newlines(xtb.formatted_tb)
    
    def print_tb(self, tb, limit=None, file=None, **options):
        options = self._get_options(options, limit)
        xtb = XTraceback(None, None, tb, **options)
        xtb.print_tb(file)
    
    def format_exception_only(self, etype, value, **options):
        options = self._get_options(options)
        xtb = XTraceback(etype, value, None, **options)
        return self._with_newlines(xtb.formatted_exception_only)
    
    def format_exception(self, etype, value, tb, limit=None, **options):
        options = self._get_options(options, limit)
        xtb = XTraceback(etype, value, tb, **options)
        return self._with_newlines(xtb.formatted_exception)
    
    def print_exception(self, etype, value, tb, limit=None, file=None, **options):
        options = self._get_options(options, limit)
        xtb = XTraceback(etype, value, tb, **options)
        xtb.print_exception(file)
    
    def format_exc(self, limit=None, **options):
        return self.format_exception(*sys.exc_info(), limit=limit, **options)
    
    def print_exc(self, limit=None, file=None, **options):
        self.print_exception(*sys.exc_info(), limit=limit, file=file, **options)
