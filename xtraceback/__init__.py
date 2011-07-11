from .stdlibcompat import StdlibCompat
from .xtraceback import XTraceback

compat = StdlibCompat()
__enter__ = compat.__enter__
__exit__ = compat.__exit__
