from .stdlibcompat import StdlibCompat
from .xtraceback import XTraceback

__version__ = "0.3.3"

compat = StdlibCompat()
__enter__ = compat.__enter__
__exit__ = compat.__exit__
