
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


class ClassShim(Shim):
    
    def __repr__(self):
        return "<class %s.%s>" % (self.target.__module__, self.target.__name__)
    

class ModuleShim(Shim):
    
    def __init__(self, target, xtb):
        super(ModuleShim, self).__init__(target, xtb)
        self.filename = getattr(self.target, "__file__", None)
        if self.filename is not None:
            self.filename = self.xtb.format_filename(self.filename)
            if self.filename.endswith("__init__.pyc"):
                self.filename = self.filename[:-13]
    
    def __repr__(self):
        if self.filename is not None:
            return "<%s '%s' from=%r>" % (self.filename.endswith(".pyc") and "module" or "package",
                                          self.target.__name__,
                                          self.filename)
        return repr(self.target)