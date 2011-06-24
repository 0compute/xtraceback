from pygments.lexer import bygroups, include, using
from pygments.lexers.agile import PythonLexer, PythonTracebackLexer
from pygments.token import Text, Operator, Name, Number, Generic, String

BASE_NAME = r"[a-zA-Z_][a-zA-Z0-9_]*"


class XPythonLexer(PythonLexer):
    
    tokens = PythonLexer.tokens.copy()
    
    tokens["classname"] = [
            ("[a-zA-Z_][a-zA-Z0-9_.]*", Name.Class, "#pop")
        ]
    
    # Marker __repr__
    ref = r"(<ref offset)(=)(\-\d+)( ?)((?:name)?)(=?)((?:%s)?)(>?)" % BASE_NAME
    tokens["root"].insert(0, (ref, bygroups(Name.Builtin, Operator.Word, Number,
                                            Text, Name.Builtin, Operator.Word,
                                            Name.Variable, Name.Builtin)))


class PythonXTracebackLexer(PythonTracebackLexer):

    tokens = {
        "root": [
            include("entry"),
            include("exception"),
            (r"^.*\n", Generic.Error),
        ],
        "entry" : [
            (r"^Traceback \(most recent call last\):\n", Generic.Error, "frame"),
            (r'^(  File )("[^"]+")(, line )(\d+)(, in )(.+)(\n)',
             bygroups(Generic.Error, Name.Builtin, Generic.Error, Number, Generic.Error, Name.Function, Text), "frame"),
        ],
        "exception" : [
            (r"^(AssertionError: )(.+\n)", bygroups(Generic.Error, using(XPythonLexer))),
            (r"^(%s:?)(.+\n)" % BASE_NAME, bygroups(Generic.Error, String)),
            ],
        "frame": [
            include("entry"),
            include("exception"),
            # line of python code
            (r"^((?:-+>)?)( +)(\d+)(.+\n)",
             bygroups(Generic.Error, Text, Number, using(XPythonLexer))),
            # variable continuation
            (r"^([ ]+)('[^']+')(: )(.*)([,}]?\n)",
             bygroups(Text, String, Operator.Word, using(XPythonLexer), Text)),
            # variable
            (r"^([ ]+)((?:g:)?)(\**%s)( = )(.+\n)" % BASE_NAME,
             bygroups(Text, Name.Builtin, Name.Variable, Operator.Word, using(XPythonLexer))),
            # plain python
            (r"^(    )(.+)(\n)",
             bygroups(Text, using(XPythonLexer), Text)),
        ],
             
    }
