import inspect
import os
import pprint
import sys
import warnings

try:
    import pygments
except ImportError:
    pygments = None
    
from .xtracebackframe import XTracebackFrame
    
    
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
    
    if pygments is not None:
        from pygments.formatters.terminal import TerminalFormatter
        from .lexer import PythonXTracebackLexer
        _formatter = TerminalFormatter()
        _lexer = PythonXTracebackLexer()
    
    def __init__(self, etype, value, tb, **options):
        
        self.etype = etype
        self.value = value
        
        # set options
        self.offset = options.pop("offset", 0)
        self.limit = options.pop(
            "limit",
            hasattr(sys, "tracebacklimit") and sys.tracebacklimit or None,
            )
        self.context = options.pop("context", 5)
        self.show_args = options.pop("show_args", True)
        self.show_locals = options.pop("show_locals", True)
        self.show_globals = options.pop("show_globals", False)
        self.qualify_method_names = options.pop("qualify_method_names", True)
        self.shorten_filenames = options.pop("shorten_filenames", True)
        self.globals_module_include = options.pop("globals_module_include", None)
        assert not options, "Unsupported options: %r" % options
        
        # keep track of objects we've seen
        self.seen = {}
        
        # get the traceback frames and work out number padding
        self.tb_frames = []
        self.number_padding = 0
        i = 0
        while tb is not None and (self.limit is None or i < self.limit):
            if i >= self.offset:
                frame_info = inspect.getframeinfo(tb, self.context)
                frame = XTracebackFrame(self, tb.tb_frame, frame_info, i)
                if not frame.exclude:
                    self.tb_frames.append(frame)
                    self.number_padding = max(len(str(frame_info.lineno)), self.number_padding)
            tb = tb.tb_next
            i += 1
    
    def _format_filename(self, filename):
        if self.shorten_filenames:
            if filename.startswith(self.stdlib_path):
                filename = filename.replace(self.stdlib_path, "<stdlib>")
            else:
                relative = os.path.relpath(filename)
                if len(relative) < len(filename):
                    filename = relative
        return filename
        
    def _format_variable(self, key, value, indent=4, prefix="", separator=" = "):
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
    
    def highlight(self, string):
        if pygments is None:
            warnings.warn("highlighting disabled - pygments is not available")
        else:
            try:
                return pygments.highlight(string, self._lexer, self._formatter)
            except KeyboardInterrupt:
                # let the user abort a long-running highlight
                return string
    
    def format_tb(self, color=False):
        lines = []
        for frame in self.tb_frames:
            frame_str = str(frame)
            if color:
                frame_str = self.highlight(frame_str)
            lines.append(frame_str + "\n")
        return lines
    
    def format_exception_only(self, color=False):

        lines = []
        
        value_str = str(self.value)
        
        if isinstance(self.value, SyntaxError):
            msg, (filename, lineno, offset, badline) = self.value.args
            # taken from traceback.format_exception_only
            filename = filename and self._format_filename(filename) or "<string>"
            filename = filename or "<string>"
            lines.append('  File "%s", line %d\n' % (filename, lineno))
            if badline is not None:
                lines.append('    %s\n' % badline.strip())
                if offset is not None:
                    caretspace = badline[:offset].lstrip()
                    # non-space whitespace (likes tabs) must be kept for alignment
                    caretspace = ((c.isspace() and c or ' ') for c in caretspace)
                    # only three spaces to account for offset1 == pos 0
                    lines.append('   %s^\n' % ''.join(caretspace))
                value_str = msg
        
        exc_line = isinstance(self.etype, type) and self.etype.__name__ or str(self.etype)
        if value_str:
            exc_line += ": %s" % value_str
        lines.insert(0, exc_line + "\n")
        
        if color:
            for i, line in enumerate(lines):
                lines[i] = self.highlight(line)
                
        return lines
    
    def format_exception(self, color=False):
        lines = self.format_tb()
        if lines:
            lines.insert(0, "Traceback (most recent call last):\n")
        lines.extend(self.format_exception_only())
        if color:
            for i, line in enumerate(lines):
                lines[i] = self.highlight(line)
        return lines
    
    def __str__(self):
        return "".join(self.format_exception())
