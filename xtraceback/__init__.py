__version__ = "0.4.0-dev"

from .stdlibcompat import StdlibCompat
from .xtraceback import XTraceback
from .xtracebackoptions import XTracebackOptions

from .pycompat import monkeypatch
monkeypatch()
del monkeypatch

compat = StdlibCompat()
__enter__ = compat.__enter__
__exit__ = compat.__exit__
