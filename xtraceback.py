import functools
import pprint
import inspect
import os
import sys
import traceback

from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexer import bygroups, using
from pygments.lexers.agile import PythonLexer, PythonTracebackLexer
from pygments.token import Text, Comment, Operator, Name, Number, Generic, Other


class StackReference(object):
    
    def __init__(self, index, path, lineno, varname):
        self.index = index
        self.path = path
        self.lineno = lineno
        self.varname = varname

    def marker(self, index):
        return StackReferenceMarker(self, index)


class StackReferenceMarker(object):
    
    def __init__(self, ref, index):
        self.ref = ref
        self.index = index
        self.offset = self.ref.index - self.index
        
    def __repr__(self):
        return "<stackref pos=%d loc=%s:%s name=%s>" \
            % (self.offset, self.ref.path, self.ref.lineno, self.ref.varname)


class StackFrame(object):
    
    EXCLUDE = ("__builtins__",)
    
    def __init__(self, seen, number_padding, index, compact, frame, path,
                 lineno, func_name, context, context_index):
        
        self.seen = seen
        self.number_padding = number_padding
        self.index = index
        self.compact = compact
        self.frame = frame
        self.path = path
        self.lineno = lineno
        self.func_name = func_name
        self.context = context
        self.context_index = context_index
        
        # if path is a real path then try to make it relative
        if os.path.exists(self.path):
            self.path = os.path.abspath(self.path)
            relpath = os.path.relpath(self.path)
            if len(relpath) < len(self.path):
                self.path = relpath
        
        # get frame arguments and filter locals
        self.args, self.varargs, self.varkw, locals = inspect.getargvalues(frame)
        self.locals = self._filter(locals)
        
        # keep a dictionary of the frame's arguments so we don't repeat them
        # in local lines
        self.argdict = {}
        for arg in self.args:
            self.argdict[arg] = self.locals[arg]
        if self.varargs:
            self.argdict[self.varargs] = self.locals[self.varargs]
        if self.varkw:
            self.argdict[self.varkw] = self.locals[self.varkw]
        
    def _filter(self, fdict):
        fdict = fdict.copy()
        for key, value in fdict.items():
            if key in self.EXCLUDE:
                del fdict[key]
            elif isinstance(value, dict):
                if self.compact:
                    # if we are being compact then replace dictionary references
                    # from further up the stack with a StackReferenceMarker
                    oid = id(value)
                    stack_ref = self.seen.get(oid)
                    if stack_ref is not None:
                        marker = stack_ref.marker(self.index)
                        if marker.offset != 0:
                            value = marker
                    else:
                        self.seen[oid] = StackReference(self.index,
                                                        self.path,
                                                        self.lineno,
                                                        key)
                if not isinstance(value, StackReferenceMarker):
                    value = self._filter(value)
                fdict[key] = value                                        
        return fdict
    
    def _pformat(self, key, value, indent="    "):
        value_indent = "\n%s%s" % (indent, " " * (len(key) + 3))
        pvalue = pprint.pformat(value).replace("\n", value_indent)
        return "%s%s = %s" % (indent, key, pvalue)
    
    def _get_local_lines(self, indent="    "):
        lines = []
        for key, value in self.locals.items():
            # do not show values that have not changed from the frame's scope
            if key not in self.argdict or self.argdict[key] != value:
                lines.append(self._pformat(key, value, indent))
        return sorted(lines)
            
    def format(self):
        
        # push path
        lines = ['  File "%s", in %s' % (self.path, self.func_name)]
        
        # push frame args
        for arg in self.args:
            lines.append(self._pformat(arg, self.locals[arg]))
        if self.varargs:
            lines.append(self._pformat("*%s" % self.varargs,
                                       self.locals[self.varargs]))
        if self.varkw:
            lines.append(self._pformat("**%s" % self.varkw,
                                       self.locals[self.varkw]))
        
        # push context lines
        if self.context is not None:

            context_lineno = self.lineno - self.context_index
            
            # work out how much we need to dedent
            dedent = float("inf")
            for line in self.context:
                if not line.strip():
                    continue
                dedent = min(dedent, len(line) - len(line.lstrip()))
            
            for line in self.context:
                
                line = line[dedent:].rstrip()
                numbered_line = "    %s" % "%*s %s" % (self.number_padding,
                                                       context_lineno,
                                                       line)
                
                if context_lineno == self.lineno:
                    
                    # push the numbered line with a marker
                    dedented_line = numbered_line.lstrip()
                    marker_padding = len(numbered_line) - len(dedented_line) -2
                    lines.append("%s> %s" % ("-" * marker_padding, dedented_line))
                    
                    # push locals below lined up with the start of code
                    padding = self.number_padding + len(line) - len(line.lstrip()) + 1
                    indent = "    %s" % (" " * padding)
                    lines.extend(self._get_local_lines(indent))
                    
                else:
                    
                    # push the numbered line
                    lines.append(numbered_line)
                    
                context_lineno += 1
        
        else:
            # no context so we are execing
            lines.extend(self._get_local_lines())
            
        return "\n".join(lines) + "\n"


class PythonXTracebackLexer(PythonTracebackLexer):
    """
    Pygments lexer for XTraceback
    """

    tokens = {
        "root": [
            (r"^Traceback \(most recent call last\):\n", Generic.Error, "intb"),
            # SyntaxError starts with this.
            (r'^(?=  File "[^"]+", line \d+)', Generic.Error, "intb"),
            (r"^.*\n", Other),
        ],
        "intb": [
            # file with optional func name
            (r'^(  File )("[^"]+")(, in )(.+)(\n)',
             bygroups(Generic.Error, Name.Builtin, Text, Name.Function, Text)),
            (r'^(  File )("[^"]+")(\n)',
             bygroups(Text, Name.Builtin, Text)),
            # error line
            (r"^([-]+>[ ]+\d+)(.+)(\n)",
             bygroups(Generic.Error, using(PythonLexer), Text)),
            # context line
            (r"^([ ]+)(\d+)(.+)(\n)",
             bygroups(Text, Number, using(PythonLexer), Text)),
            # local variables with class repr
            (r"^([ ]+)(\**[a-zA-Z_][a-zA-Z0-9_]*)( = )(<[^>]+>)(\n)",
             bygroups(Text, Name.Variable, Operator, Name.Class, Text)),
            # local variables
            (r"^([ ]+)(\**[a-zA-Z_][a-zA-Z0-9_]*)( = )(.+)(\n)",
             bygroups(Text, Name.Variable, Operator, using(PythonLexer), Text)),
            # continuation line from local variables with class repr
            (r"^([ ]+)('[^']+': )(<[a-zA-Z_][^>]+>)(.*\n)",
             bygroups(Text, using(PythonLexer), Name.Class, Text)),
            # continuation line from local variables
            (r"^([ ]+)(.+)(\n)",
             bygroups(Text, using(PythonLexer), Text)),
            # doctests
            (r"^([ \t]*)(...)(\n)",
             bygroups(Text, Comment, Text)),
            # exception with message
            (r"^(.+)(: )(.+)(\n)",
             bygroups(Generic.Error, Text, Name.Exception, Text), "#pop"),
            # exception no message
            (r"^([a-zA-Z_][a-zA-Z0-9_]*)(:?\n)",
             bygroups(Generic.Error, Text), "#pop")
        ],
    }


class XTraceback(object):
    """
    An extended traceback formatter
    
    Inspired by the ultraTB module from IPython
    """
    
    _lexer_class = PythonXTracebackLexer
    _formatter_class = TerminalFormatter
    
    def __init__(self, offset=0, context=5, compact=True, color=None):
        
        self.offset = offset
        self.context = context
        self.compact = compact
        self.color = color
        self.lexer = self._lexer_class()
        self.formatter = self._formatter_class()
        
        self._entered = False 
        self._patch_stack = []
    
    def _patch_target(self, target, member, patch):
        if isinstance(target, dict):
            target[member] = patch
        else:
            setattr(target, member, patch)
            
    def _patch(self, target, member, patch):
        if isinstance(target, dict):
            current = target[member]
        else:
            current = getattr(target, member)
        self._patch_stack.append((target, member, current))
        self._patch_target(target, member, patch)
    
    def __enter__(self):
        
        if self._entered:
            raise RuntimeError("Cannot reenter %r " % self)
        self._entered = True
        
        # patch traceback module
        for func in ("print_tb", "format_tb"):
            self._patch(traceback,
                        func,
                        functools.partial(getattr(self.__class__, func), self))
        
        # auto set color if it is None
        if self.color is None:
            color = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
            self._patch(self, "color", color)
        
        return self
    
    def __exit__(self, etype, value, tb):
        
        if not self._entered:
            raise RuntimeError("Cannot exit %r without entering first" % self)
        self._entered = False
        
        while self._patch_stack:
            target, member, patch = self._patch_stack.pop()
            self._patch_target(target, member, patch)
        
    def __getattr__(self, key):
        return getattr(traceback, key)
    
    def highlight_exc_str(self, exc_str):    
        return highlight(exc_str, self.lexer, self.formatter)
    
    def print_tb(self, tb, limit=None, file=None):
        if file is None:
            file = sys.stderr
        if limit is None:
            if hasattr(sys, "tracebacklimit"):
                limit = sys.tracebacklimit
        file.write(self.format_tb(tb, limit))
        
    def format_tb(self, tb, limit = None):
        
        frames = inspect.getinnerframes(tb, self.context)[self.offset:limit]
        
        # work out how much we need to pad line numbers
        number_padding = 0
        for frame in frames:
            number_padding = max(len(str(frame[2])), number_padding)
        
        # loop through each frame building the traceback
        seen = {} 
        lines = []
        for index, args in enumerate(frames):
            frame = StackFrame(seen, number_padding, index, self.compact, *args)
            lines.append(frame.format())
        
        return lines
    
    def __call__(self, etype, value, tb, limit=None):
        exc_str = "".join(self.format_exception(etype, value, tb, limit=None))
        if self.color:
            exc_str = self.highlight_exc_str(exc_str)
        return exc_str
