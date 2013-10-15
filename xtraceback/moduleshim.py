import inspect
import os

from .formatting import format_filename


class ModuleShim(object):

    def __init__(self, options, target):
        self.options = options
        self.target = target

    def __repr__(self):
        package = False
        try:
            filename = inspect.getsourcefile(self.target)
        except TypeError:
            filename = None
        if filename is not None:
            if os.path.basename(filename) == "__init__.py":
                package = True
                filename = os.path.dirname(filename)
            filename = format_filename(self.options, filename)
        if filename is None:
            return repr(self.target)
        return "<%s '%s' from=%r>" % (package and "package" or "module",
                                      self.target.__name__,
                                      filename)
