__version__ = "0.4.0-rc1"

from .loggingcompat import LoggingCompat
from .tracebackcompat import TracebackCompat
from .xtraceback import XTraceback
from .xtracebackoptions import XTracebackOptions

from .pycompat import monkeypatch
monkeypatch()
del monkeypatch

compat = TracebackCompat()
