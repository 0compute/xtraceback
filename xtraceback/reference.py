import sys
import pprint


class Reference(object):

    def __init__(self, tb_index, varname, target):
        self.tb_index = tb_index
        self.varname = varname
        self.target = target

    def marker(self, xtb, tb_index, key):
        return Marker(self, xtb, tb_index, key)


class Marker(object):

    def __init__(self, reference, xtb, tb_index, key):
        self.reference = reference
        self.xtb = xtb
        self.tb_index = tb_index
        self.key = key
        self.tb_offset = self.reference.tb_index - self.tb_index

    def __repr__(self):
        frame = sys._getframe(1)
        while frame:
            try:
                code = self.xtb._format_variable.func_code
            except AttributeError:
                # python 3
                code = self.xtb._format_variable.__code__
            if frame.f_code == code:
                indent = frame.f_locals["indent"] + 4
                break
            frame = frame.f_back
        else:  # pragma: no cover - defensive
            raise RuntimeError("Expecting to be called with "
                               "XTraceback._format_variable in stack")
        pretty_repr = pprint.pformat(self.reference.target)
        if indent + len(self.key) + len(pretty_repr) > self.xtb.print_width \
            or pretty_repr.find("\n") > 0:
            name = "" if self.reference.varname == self.key \
                       else " name=%s" % self.reference.varname
            pretty_repr = "<ref offset=%d%s>" % (self.tb_offset, name)
        return pretty_repr
