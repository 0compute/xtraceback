import inspect
import os
import pprint
import sys
import traceback

import pygments
from pygments.formatters.terminal import TerminalFormatter

from xtraceback.frame import Frame
from xtraceback.lexer import PythonXTracebackLexer

    
class XTraceback(object):
    """
    An extended traceback formatter
    """
    
    TERMINAL_WIDTH = 80
    
    REFORMAT = {
        dict : ("{", "}"),
        list : ("[", "]"),
        tuple : ("(", ")"),
        set : ("set([", "])"),
        frozenset : ("frozenset([", "])"),
        }
    
    stdlib_path = os.path.dirname(os.__file__)
    
    def __init__(self, offset=0, context=5, color=None, compact=True,
                 show_globals=False, globals_module_include=None,
                 lexer=None, formatter=None):
        
        self.offset = offset
        self.context = context
        self.color = color
        self.compact = compact
        self.show_globals = show_globals
        self.globals_module_include = globals_module_include
        
        self.lexer = lexer or PythonXTracebackLexer()
        self.formatter = formatter or TerminalFormatter()
        
        self._entered = False 
        self._patch_stack = []
        self._patch_targets = {}
        
    def _patch(self, target, member, patch):
        current = getattr(target, member)
        self._patch_stack.append((target, member, current))
        setattr(target, member, patch)
        self._patch_targets[hash(target) + hash(member)] = current
    
    def __enter__(self):
        
        if self._entered:
            raise RuntimeError("Cannot reenter %r " % self)
        self._entered = True
        
        # patch traceback module
        for func in ("format_tb", "format_exception", "format_exception_only",
                     "print_tb", "print_exception"):
            self._patch(traceback, func, getattr(self, func))
        
        # auto set color if it is None
        if self.color is None:
            color = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
            self._patch(self, "color", color)
        
        return self

    def __exit__(self, etype, value, tb):
        
        if not self._entered:
            raise RuntimeError("Cannot exit %r without entering first" % self)
        self._entered = False
        
        # restore patched objects
        while self._patch_stack:
            target, member, patch = self._patch_stack.pop()
            setattr(target, member, patch)
            del self._patch_targets[hash(target) + hash(member)]
    
    def highlight(self, string, color=True):
        if color:
            try:
                return pygments.highlight(string, self.lexer, self.formatter)
            except KeyboardInterrupt:
                # let the user abort
                return string
        return string
    
    def _patched_function(self, target, member, *args, **kwargs):
        function = self._patch_targets[hash(target) + hash(member)]
        return function(*args, **kwargs)
    
    def _assert_entered(self):
        if not self._entered:
            raise RuntimeError("%r has not been entered" % self)
        
    def format_filename(self, filename):
        if self.compact:
            if filename.startswith(self.stdlib_path):
                filename = filename.replace(self.stdlib_path, "<stdlib>")
            else:
                relative = os.path.relpath(filename)
                if len(relative) < len(filename):
                    filename = relative
        return filename
        
    def format_variable(self, key, value, indent=4, prefix="", separator=" = "):
        pvalue = pprint.pformat(value, indent=0)
        line_size = indent + len(prefix) + len(key) + len(separator) + len(pvalue)
        if line_size > self.TERMINAL_WIDTH:
            reformat = self.REFORMAT.get(type(value))
            if reformat is not None:
                start, end =  reformat
                lines = map(str.strip, pvalue.lstrip(start).rstrip(end).splitlines())
                sub_indent = "\n" + " " * (indent+4)
                pvalue = "".join((start, sub_indent, sub_indent.join(lines),
                                  ",", sub_indent, end))
        return "".join((" " * indent, prefix, key, separator, pvalue))
    
    def format_tb(self, tb, limit=None, color=None):
        
        self._assert_entered()
        
        if color is None:
            color = self.color
        
        frames = []
        number_padding = 0
        
        # extract the traceback frames and work out number padding
        i = 0
        while tb is not None and (limit is None or i < limit):
            if i >= self.offset:
                frame_info = inspect.getframeinfo(tb, self.context)
                frames.append((tb.tb_frame, frame_info, i))
                number_padding = max(len(str(frame_info.lineno)), number_padding)
            tb = tb.tb_next
            i += 1
        
        # format the frames
        seen = {} 
        lines = []
        for frame, frame_info, i in frames:
            frame = Frame(self, frame, frame_info, seen, number_padding, i)
            lines.append(self.highlight(frame.format(), color))
        
        return lines
    
    def format_exception_only(self, etype, value):
        self._assert_entered()
        return self._patched_function(traceback, "format_exception_only", etype, value)
        
    def format_exception(self, etype, value, tb, limit=None, color=None):
        self._assert_entered()
        if color is None:
            color = self.color
        lines = []
        if tb:
            tb_lines = self.format_tb(tb, limit, color)
            if tb_lines:
                lines.append(self.highlight("Traceback (most recent call last):\n", color))
                lines.extend(tb_lines)
        lines.append(self.highlight("".join(self.format_exception_only(etype, value)), color))
        return lines
    
    def __call__(self, *args, **kwargs):
        return "".join(self.format_exception(*args, **kwargs))
    
    def _stream_defaults(self, limit, stream, color):
        if limit is None and hasattr(sys, "tracebacklimit"):
            limit = sys.tracebacklimit
        if stream is None:
            stream = sys.stderr
        if color is None:
            color = False if not hasattr(stream, "isatty") else stream.isatty()
        return limit, stream, color
    
    def print_tb(self, tb, limit=None, file=None, color=None):
        limit, stream, color = self._stream_defaults(limit, file, color)
        stream.write("".join(self.format_tb(tb, limit, color)))
        
    def print_exception(self, etype, value, tb, limit=None, file=None, color=None):
        limit, stream, color = self._stream_defaults(limit, file, color)
        stream.write(self(etype, value, tb, limit, color))


_active_instance = None


def activate(*args, **kwargs):
    global _active_instance
    if _active_instance is not None:
        raise RuntimeError("Cannot activate - already active with %r"
                           % _active_instance)
    _active_instance = XTraceback(*args, **kwargs)
    # patch sys.excepthook - this can't work as a context manager because the
    # sys.excepthook context is always outside of it
    _active_instance._patch(sys, "excepthook", _active_instance.print_exception)
    return _active_instance.__enter__()

def deactivate(etype=None, value=None, tb=None):
    global _active_instance
    if _active_instance is None:
        raise RuntimeError("Cannot deactivate - no active instance")
    _active_instance.__exit__(etype, value, tb)
    _active_instance = None
