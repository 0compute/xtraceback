from .tracebackcompat import TracebackCompat
from .xtraceback import XTraceback

compat = TracebackCompat()
__enter__ = compat.__enter__
__exit__ = compat.__exit__