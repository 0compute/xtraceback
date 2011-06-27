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
    """
    Provides interface compatibility with the stdlib traceback module
    
    :ivar defaults: Options to apply to XTracebacks created by this instance
    :type defaults: dict
    :ivar color: Whether to use color or not
    :type color: bool or None
    """
    
    __metaclass__ = TracebackCompatMeta
    
    _patch_stack = []
    _traceback_patch_functions = []

    def __init__(self, color=None, **defaults):
        """
        :param color: Whether to use color or not
        :type color: bool or None
        :param defaults: Default options for XTraceback instances created by
                         this instance
        :type defaults: dict
        """
        self.color = color
        self.defaults = defaults
        self._entered = False
        
    def update_defaults(self, color=None, **defaults):
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
        if self._entered:
            raise RuntimeError("Cannot reenter %r " % self)
        self._entered = True
        for func_name in self._traceback_patch_functions:
            self._patch(traceback, func_name, getattr(self, func_name))
        return self

    def __exit__(self,  *exc_info):
        if not self._entered:
            raise RuntimeError("Cannot exit %r without entering first" % self)
        self._entered = False
        while self._patch_stack:
            target, member, patch = self._patch_stack.pop()
            setattr(target, member, patch)
    
    def _factory(self, etype, value, tb, limit=None, **_options):
        options = self.defaults.copy()
        options.update(_options)
        if limit is not None:
            options["limit"] = limit
        return XTraceback(etype, value, tb, **options)
    
    def format_tb(self, tb, limit=None, color=None, **options):
        xtb = self._factory(None, None, tb, limit, **options)
        return xtb.format_tb(self.color if color is None else color)
    
    def format_exception_only(self, etype, value, color=None, **options):
        xtb = self._factory(etype, value, None, **options)
        return xtb.format_exception_only(self.color if color is None else color)
    
    def format_exception(self, etype, value, tb, limit=None, color=None, **options):
        xtb = self._factory(etype, value, tb, limit, **options)
        return xtb.format_exception(self.color if color is None else color)
    
    def format_exc(self, limit=None, color=None, **options):
        return self.format_exception(*sys.exc_info(), limit=limit,
                                     color=color, **options)
    
    def print_tb(self, tb, limit=None, file=None, color=None, **options):
        xtb = self._factory(None, None, tb, limit, **options)
        xtb.print_tb(file, color)
        
    def print_exception(self, etype, value, tb, limit=None, file=None,
                        color=None, **options):
        xtb = self._factory(etype, value, tb, limit, **options)
        xtb.print_exception(file, color)
    
    def print_exc(self, limit=None, file=None, color=None, **options):
        self.print_exception(*sys.exc_info(), limit=limit, file=file,
                             color=color, **options)
