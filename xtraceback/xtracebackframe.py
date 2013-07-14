import inspect
import os
import textwrap
import types
import warnings

from .reference import Reference
from .shim import ModuleShim


class XTracebackFrame(object):

    FILTER = ("__builtins__", "__all__", "__doc__", "__file__", "__name__",
              "__package__", "__path__", "__loader__", "__cached__",
              "__initializing__")

    FUNCTION_EXCLUDE = ("GeneratorContextManager.__exit__",)

    GLOBALS_PREFIX = "g:"

    def __init__(self, xtb, frame, frame_info, tb_index):

        self.xtb = xtb
        self.frame = frame
        self.frame_info = frame_info
        self.tb_index = tb_index

        (self.filename, self.lineno, self.function,
         self.code_context, self.index) = self.frame_info
        self.args, self.varargs, self.varkw = inspect.getargs(frame.f_code)

        # keep track of what we've formatted in this frame
        self.formatted_vars = {}

        # we use a filtered copy of locals and globals
        self.locals = self._filter(frame.f_locals)
        self.globals = self._filter(frame.f_globals)

        # filter globals
        if self.xtb.options.globals_module_include is not None:
            for key, value in self.globals.items():
                assert key not in self.FILTER
                if isinstance(value, types.ModuleType):
                    module = value.__name__
                elif isinstance(value, types.InstanceType):
                    module = value.__class__.__module__
                else:
                    module = getattr(value, "__module__", None)
                if (module is not None \
                    and not module.startswith(
                        self.xtb.options.globals_module_include
                        )):
                    del self.globals[key]

        # if path is a real path then try to shorten it
        if os.path.exists(self.filename):
            self.filename = self.xtb._format_filename(
                                os.path.abspath(self.filename)
                                )

        # qualify method name with class name
        if self.xtb.options.qualify_methods and self.args:
            try:
                cls = frame.f_locals[self.args[0]]
            except KeyError:  # pragma: no cover - defensive
                # we're assuming that the first argument is in f_locals but
                # it may not be in some cases so this is a defence, see
                # https://github.com/ischium/xtraceback/issues/3 with further
                # detail at http://www.sqlalchemy.org/trac/ticket/2317 and
                # https://dev.entrouvert.org/issues/765
                pass
            except TypeError:  # pragma: no cover - defensive
                # if self.args[0] is a list it is not hashable - inspect.getargs
                # may return nested lists for args
                pass
            else:
                if not isinstance(cls, type):
                    cls = type(cls)
                if hasattr(cls, self.function):
                    for base in inspect.getmro(cls):
                        if self.function in base.__dict__:
                            self.function = base.__name__ + "." + self.function
                            break

        self._formatted = None

    @property
    def exclude(self):
        return self.locals.get("__xtraceback_skip_frame__", False) \
            or self.function in self.FUNCTION_EXCLUDE

    def _filter(self, fdict):
        try:
            fdict = fdict.copy()
        except NotImplementedError:
            # user data types inheriting dict may not have implemented copy
            pass
        else:
            to_remove = []
            for key, value in fdict.items():
                try:
                    if key in self.FILTER:
                        to_remove.append(key)
                        continue
                except:
                    exc_info = sys.exc_info()
                    # the comparison failed for an unknown reason likely a
                    # custom __cmp__ that makes bad assumptions - swallow
                    try:
                        warnings.warn("Could not filter %r: %r" % (key, exc_info[1]))
                    except:
                        warnings.warn("Could not filter and can't say why: %s" % exc_info[1])
                    continue
                else:
                    # replace some values with shim types
                    if isinstance(value, types.ModuleType):
                        value = ModuleShim.get_instance(value, self.xtb)
                    # replace objects from further up the stack with a Marker
                    oid = id(value)
                    stack_ref = self.xtb.seen.get(oid)
                    if stack_ref is not None:
                        marker = stack_ref.marker(self.xtb, self.tb_index, key)
                        if marker.tb_offset != 0:
                            value = marker
                    else:
                        self.xtb.seen[oid] = Reference(self.tb_index, key, value)
                    if isinstance(value, dict):
                        value = self._filter(value)
                    fdict[key] = value
            for key in to_remove:
                del fdict[key]
        return fdict

    def _format_variable(self, lines, key, value, indent=4, prefix=""):
        if value is not self.formatted_vars.get(key):
            self.formatted_vars[key] = value
            if self.globals.get(key) is value:
                prefix = self.GLOBALS_PREFIX + prefix
            lines.append(self.xtb._format_variable(key, value, indent, prefix))

    def _format_dict(self, odict, indent=4):
        lines = []
        for key in sorted(odict.keys()):
            self._format_variable(lines, key, odict[key], indent)
        return lines

    def _format_frame(self):

        lines = ['  File "%s", line %d, in %s' % (self.filename, self.lineno,
                                                  self.function)]

        # push frame args
        if self.xtb.options.show_args:
            for arg in self.args:
                if isinstance(arg, list):
                    # TODO: inspect.getargs arg list may contain nested lists;
                    # skip it for now
                    continue
                self._format_variable(lines, arg, self.locals.get(arg))
            if self.varargs:
                self._format_variable(lines, self.varargs,
                                      self.locals.get(self.varargs), prefix="*")
            if self.varkw:
                self._format_variable(lines, self.varkw,
                                      self.locals.get(self.varkw), prefix="**")

        # push globals
        if self.xtb.options.show_globals:
            lines.extend(self._format_dict(self.globals))

        # push context lines
        if self.code_context is not None:

            lineno = self.lineno - self.index

            dedented = textwrap.dedent("".join(self.code_context))
            for line in dedented.splitlines():

                numbered_line = "    %s" % "%*s %s" % (self.xtb.number_padding,
                                                       lineno,
                                                       line)

                if lineno == self.lineno:

                    if self.xtb.options.context > 1:
                        # push the numbered line with a marker
                        dedented_line = numbered_line.lstrip()
                        marker_padding = len(numbered_line) \
                                             - len(dedented_line) - 2
                        lines.append("%s> %s" % ("-" * marker_padding,
                                                 dedented_line))
                    else:
                        # push the line only
                        lines.append("    " + line)

                    # push locals below lined up with the start of code
                    if self.xtb.options.show_locals:
                        indent = self.xtb.number_padding + len(line) \
                                     - len(line.lstrip()) + 5
                        lines.extend(self._format_dict(self.locals, indent))

                else:

                    # push the numbered line
                    lines.append(numbered_line)

                lineno += 1

        elif self.xtb.options.show_locals:
            # no context so we are execing
            lines.extend(self._format_dict(self.locals))

        return "\n".join(lines)

    def __str__(self):
        if self._formatted is None:
            self._formatted = self._format_frame()
        return self._formatted
