from .stdlibcompat import StdlibCompat
from .xtraceback import XTraceback, XTracebackOptions

from . import pycompat
del pycompat

__version__ = "0.4.0-dev"

compat = StdlibCompat()
__enter__ = compat.__enter__
__exit__ = compat.__exit__
