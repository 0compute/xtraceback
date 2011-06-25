import inspect
import os
import pprint
import sys

from .xtracebackframe import XTracebackFrame
from .util import cachedproperty
    
    
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
    
    def __init__(self, etype, value, tb, **options):
        
        self.etype = etype
        self.value = value
        self.tb = tb
        
        self.stream = options.pop("stream", sys.stderr)
        self.offset = options.pop("offset", 0)
        self.limit = options.pop("limit", None)
        self.context = options.pop("context", 5)
        self.compact = options.pop("compact", True)
        self.show_globals = options.pop("show_globals", False)
        self.globals_module_include = options.pop("globals_module_include", None)
        
        assert not options, "Unsupported options: %r" % options
        
        # set when frames property is resolved
        self.number_padding = 0
        
        self.seen = {}
    
    def _format_filename(self, filename):
        if self.compact:
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
    
    @cachedproperty
    def tb_frames(self):
        tb_frames = []
        i = 0
        tb = self.tb
        while tb is not None and (self.limit is None or i < self.limit):
            if i >= self.offset:
                frame_info = inspect.getframeinfo(tb, self.context)
                tb_frames.append(XTracebackFrame(self, tb.tb_frame, frame_info, i))
                self.number_padding = max(len(str(frame_info.lineno)), self.number_padding)
            tb = tb.tb_next
            i += 1
        return tb_frames
    
    @cachedproperty
    def formatted_tb(self):
        lines = map(str, self.tb_frames)
        if lines:
            lines.insert(0, "Traceback (most recent call last):")
        return lines 
    
    @cachedproperty
    def formatted_tb_string(self):
        return "\n".join(self.formatted_tb) + "\n"
    
    @cachedproperty
    def formatted_exception_only(self):

        lines = [isinstance(self.etype, type) and self.etype.__name__ or str(self.etype)]
        
        try:
            value_str = str(self.value)
        except:
            value_str = "<unprintable %s object>" % type(self.value).__name__
    
        if isinstance(self.value, SyntaxError):
            # It was a syntax error; show exactly where the problem was found.
            
            try:
                msg, (filename, lineno, offset, badline) = self.value.args
            except Exception:
                pass
            else:
                filename = filename or "<string>"
                lines.append('  File "%s", line %d' % (filename, lineno))
                if badline is not None:
                    lines.append('    %s' % badline.strip())
                    if offset is not None:
                        caretspace = badline[:offset].lstrip()
                        # non-space whitespace (likes tabs) must be kept for alignment
                        caretspace = ((c.isspace() and c or ' ') for c in caretspace)
                        # only three spaces to account for offset1 == pos 0
                        lines.append('   %s^' % ''.join(caretspace))
                    value_str = msg
        
        if value_str:
            lines[0] += ": %s" % value_str
        
        return lines
    
    @cachedproperty
    def formatted_exception(self):
        lines = self.formatted_tb[:]
        lines.extend(self.formatted_exception_only)
        return lines
    
    @cachedproperty
    def formatted_exception_string(self):
        return "\n".join(self.formatted_exception) + "\n"
    
    def __str__(self):
        return self.formatted_exception_string
    
    # }
    