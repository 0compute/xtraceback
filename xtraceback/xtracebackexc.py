import inspect
import sys

from .formatting import format_filename

from .xtracebackframe import XTracebackFrame


class XTracebackExc(object):

    def __init__(self, etype, value, tb, xtb):
        """
        :param value: The exception instance
        :type value: Exception
        :param tb: The traceback instance
        :type tb: traceback
        :param xtb: the xtraceback instance
        :type xtb: XTraceback
        """

        self.etype = etype

        #: The exception instance
        self.value = value

        #: The XTraceback instance
        self.xtb = xtb

        #: Used in XTracebackFrame to determine indent
        self.number_padding = 0

        #: List of XTracebackFrame
        self.frames = []

        i = 0
        while tb is not None and (self.xtb.options.limit is None
                                  or i < self.xtb.options.limit):
            if i >= self.xtb.options.offset:
                try:
                    frame_info = inspect.getframeinfo(tb,
                                                      self.xtb.options.context)
                except KeyError:  # pragma: no cover - defensive
                    # <stdlib>/inspect.py line 506 - there may be no __main__
                    # XXX: This can't be right - frame_info needs to be defined
                    # in order to construct the XTracebackFrame below.
                    pass
                frame = XTracebackFrame(self, tb.tb_frame, frame_info, i)
                if not frame.exclude:
                    self.frames.append(frame)
                    self.number_padding = max(len(str(frame.lineno)),
                                              self.number_padding)
            tb = tb.tb_next
            i += 1

    # { Traceback format - these return lines that should be joined with ""

    def format_tb(self):
        return ["%s\n" % frame for frame in self.frames]

    def format_exception_only(self):

        lines = []

        if self.value is None:
            value_str = ""
        elif isinstance(self.value, SyntaxError):
            # taken from traceback.format_exception_only
            try:
                msg, (filename, lineno, offset, badline) = self.value.args
            except:
                pass
            else:
                filename = filename and format_filename(self.xtb.options,
                                                        filename) or "<string>"
                filename = filename or "<string>"
                lines.append('  File "%s", line %d\n' % (filename, lineno))
                if badline is not None:
                    lines.append('    %s\n' % badline.strip())
                    if offset is not None:
                        caretspace = badline.rstrip('\n')[:offset].lstrip()
                        # non-space whitespace (likes tabs) must be kept for
                        # alignment
                        caretspace = ((c.isspace() and c or ' ')
                                      for c in caretspace)
                        # only three spaces to account for offset1 == pos 0
                        lines.append('   %s^\n' % ''.join(caretspace))
                    value_str = msg
        else:
            try:
                value_str = str(self.value)
            except Exception:
                try:
                    value_str = unicode(self.value).encode("ascii",
                                                           "backslashreplace")
                except Exception:
                    value_str = "<unprintable %s object>" \
                        % type(self.value).__name__

        # format last line
        if isinstance(self.etype, type):
            stype = self.etype.__name__
            # not using namedtuple to get major version as this is for >= py27
            if sys.version_info[0] == 3:
                # python 3 uses fully-qualified names
                smod = self.etype.__module__
                if smod not in ("__main__", "builtins"):
                    stype = smod + '.' + stype
        else:
            stype = str(self.etype)
        lines.append("%s%s\n" % (stype,
                                 value_str and ": %s" % value_str or ""))

        return lines

    def format_exception(self):
        lines = list(self.format_tb())
        if lines:
            lines.insert(0, "Traceback (most recent call last):\n")
        lines.extend(self.format_exception_only())
        return lines
