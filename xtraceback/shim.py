import os


class Shim(object):

    _instances = {}

    def __init__(self, target, xtb):
        self.target = target
        self.xtb = xtb

    def __repr__(self):
        raise NotImplementedError()

    @classmethod
    def get_instance(cls, target, xtb):
        oid = id(target)
        if oid not in cls._instances:
            cls._instances[oid] = cls(target, xtb)
        return cls._instances[oid]


class ModuleShim(Shim):

    def __init__(self, target, xtb):
        super(ModuleShim, self).__init__(target, xtb)
        self.package = False
        self.filename = getattr(self.target, "__file__", None)
        if self.filename is not None:
            if self.filename.endswith(".pyc"):
                self.filename = self.filename[:-1]
            elif self.filename.endswith("$py.class"):
                self.filename = "%s.py" % self.filename[:-9]
            if os.path.basename(self.filename) == "__init__.py":
                self.package = True
                self.filename = os.path.dirname(self.filename)
            self.filename = self.xtb._format_filename(self.filename)

    def __repr__(self):
        if self.filename is None:
            return repr(self.target)
        return "<%s '%s' from=%r>" % (self.package and "package" or "module",
                                      self.target.__name__,
                                      self.filename)
