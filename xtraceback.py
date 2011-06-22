import functools
import pprint
import inspect
import os
import sys
import traceback

from nose.plugins import Plugin

import pygments
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexer import bygroups, using
from pygments.lexers.agile import PythonLexer, PythonTracebackLexer
from pygments.token import Text, Comment, Operator, Name, Number, Generic, Other


class Reference(object):
    
    def __init__(self, index, path, lineno, varname):
        self.index = index
        self.path = path
        self.lineno = lineno
        self.varname = varname

    def marker(self, index):
        return ReferenceMarker(self, index)


class ReferenceMarker(object):
    
    def __init__(self, ref, index):
        self.ref = ref
        self.index = index
        self.offset = self.ref.index - self.index
        
    def __repr__(self):
        return "<ref pos=%d loc=%s:%s name=%s>" \
            % (self.offset, self.ref.path, self.ref.lineno, self.ref.varname)


class Frame(object):
    
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
                    # from further up the stack with a ReferenceMarker
                    oid = id(value)
                    stack_ref = self.seen.get(oid)
                    if stack_ref is not None:
                        marker = stack_ref.marker(self.index)
                        if marker.offset != 0:
                            value = marker
                    else:
                        self.seen[oid] = Reference(self.index,
                                                        self.path,
                                                        self.lineno,
                                                        key)
                if not isinstance(value, ReferenceMarker):
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
            # first line
            (r"^Traceback \(most recent call last\):\n", Generic.Error),
            # SyntaxError starts with this.
            (r'^(?=  File "[^"]+", line \d+)', Generic.Error),
            # File ..., in ...
            (r'^(  File )("[^"]+")(, in )(.+)(\n)',
             bygroups(Generic.Error, Name.Builtin, Text, Name.Function, Text), "intb"),
            # File ...
            (r'^(  File )("[^"]+")(\n)',
             bygroups(Text, Name.Builtin, Text), "intb"),
            # exception
            (r"^(.+)(:)(.+\n)", bygroups(Generic.Error, Text, Name.Exception)),
            (r"^.*\n", Other),
            ],
        "intb": [
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
            ],
        }


class XTraceback(object):
    """
    An extended traceback formatter
    """
    
    def __init__(self, offset=0, context=5, color=None, compact=True,
                 lexer=None, formatter=None):
        
        self.offset = offset
        self.context = context
        self.color = color
        self.compact = compact
        
        self.lexer = lexer or PythonXTracebackLexer()
        self.formatter = formatter or TerminalFormatter()
        
        self._entered = False 
        self._patch_stack = []
    
    def _patch(self, target, member, patch):
        self._patch_stack.append((target, member, getattr(target, member)))
        setattr(target, member, patch)
    
    def __enter__(self):
        
        if self._entered:
            raise RuntimeError("Cannot reenter %r " % self)
        self._entered = True
        
        # patch traceback module
        for func in ("print_tb", "format_tb", "format_exception"):
            self._patch(traceback,
                        func,
                        functools.partial(getattr(self.__class__, func), self))
        
        # auto set color if it is None
        if self.color is None:
            color = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
            self._patch(self, "color", color)
        
        return self
    
    push = __enter__

    def __exit__(self, etype, value, tb):
        
        if not self._entered:
            raise RuntimeError("Cannot exit %r without entering first" % self)
        self._entered = False
        
        while self._patch_stack:
            target, member, patch = self._patch_stack.pop()
            setattr(target, member, patch)
    
    def pop(self, *exc_info):
        self.__exit__(*exc_info)

    def __getattr__(self, key):
        return getattr(traceback, key)
    
    def highlight(self, string):
        if self.color:  
            return pygments.highlight(string, self.lexer, self.formatter)
        return string
    
    def print_tb(self, tb, limit=None, file=None):
        if file is None:
            file = sys.stderr
        if limit is None:
            if hasattr(sys, "tracebacklimit"):
                limit = sys.tracebacklimit
        file.write("".join(self.format_tb(tb, limit)))
        
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
            frame = Frame(seen, number_padding, index, self.compact, *args)
            lines.append(self.highlight(frame.format()))
        
        return lines
    
    def format_exception(self, etype, value, tb, limit=None):
        lines = []
        if tb:
            lines.append(self.highlight("Traceback (most recent call last):\n"))
            lines.extend(self.format_tb(tb, limit))
        lines.append(self.highlight("".join(self.format_exception_only(etype, value))))
        return lines

    def __call__(self, etype, value, tb, limit=None):
        return "".join(self.format_exception(etype, value, tb, limit=limit))


class NoseXTraceback(Plugin):
    
    score = 600 # before capture
    env_opt = "NOSE_XTRACEBACK"
    
    def options(self, parser, env):
        parser.add_option(
            "", "--with-xtraceback",
            action="store_true",
            default=env.get("NOSE_XTRACEBACK"),
            dest="xtraceback", help="Enable XTraceback plugin [NOSE_XTRACEBACK]")

    def configure(self, options, conf):
        if not self.can_configure:
            return
        self.enabled = options.xtraceback
        if self.enabled:
            traceback = XTraceback()
            traceback.push()
        self.conf = conf
