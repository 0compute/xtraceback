import struct
import traceback
import warnings

try:
    basestring
except NameError:
    # python 3
    basestring = str

try:
    import fcntl
except ImportError:
    fcntl = None
else:
    import termios

try:
    import pygments
except ImportError:
    pygments = None
else:
    from pygments.formatters.terminal import TerminalFormatter
    from pygments.styles import default
    from .lexer import PythonXTracebackLexer

from .defaults import DEFAULT_WIDTH
from .xtracebackoptions import XTracebackOptions
from .xtracebackexc import XTracebackExc


class XTraceback(object):
    """
    An extended traceback formatter

    """

    def __init__(self, etype, value, tb, **options):
        """
        :param etype: The exception type
        :type etype: type
        :param value: The exception instance
        :type value: Exception
        :param tb: The traceback instance
        :type tb: traceback
        :param options: Options for this instance
        :type options: dict
        """

        #: Options for xtraceback
        self.options = XTracebackOptions(**options)

        #: The exception type
        self.etype = etype

        #: The exception value (instance)
        self.value = value

        #: The list of exceptions and tracebacks
        if self.options.chain and self.value is not None \
                and hasattr(traceback, "_iter_chain"):
            # python 3
            values = list(traceback._iter_chain(value, tb))
            # traceback._iter_chain pulls tb from the exception instance and so
            # does not use the tb argument to this method for the last (root)
            # exception; normally this would not matter as the two are the same
            # but it falls over when tb is None so we replace the last tb in
            # the values list with tb from args
            values[-1] = (values[-1][0], tb)
        else:
            values = [(value, tb)]

        #: Used in XTracebackFrame to determine indent
        self.number_padding = 0

        # build list of exceptions
        self.exceptions = []
        for value, tb in values:
            if not isinstance(self.etype, basestring) \
                    and isinstance(value, basestring):
                exc_type = value
                value = None
            else:
                exc_type = etype if value == self.value else type(value)
            exc = XTracebackExc(exc_type, value, tb, self)
            self.exceptions.append(exc)
            self.number_padding = max(exc.number_padding, self.number_padding)

        # placeholders
        self._lexer = None
        self._formatter = None

        # work out print width
        if self.options.print_width is not None:
            self.print_width = self.options.print_width
        elif fcntl is not None and self.tty_stream:
            self.print_width = struct.unpack(
                'HHHH',
                fcntl.ioctl(self.options.stream,
                            termios.TIOCGWINSZ,
                            struct.pack('HHHH', 0, 0, 0, 0)),
            )[1]
        else:
            self.print_width = DEFAULT_WIDTH

    @property
    def tty_stream(self):
        """
        Whether or not our stream is a tty
        """
        return hasattr(self.options.stream, "isatty") \
            and self.options.stream.isatty()

    @property
    def color(self):
        """
        Whether or not color should be output
        """
        return self.tty_stream if self.options.color is None \
            else self.options.color

    def __str__(self):
        return self._str_lines(self._format_exception())

    # { Line formatting

    def _highlight(self, string):
        if pygments is None:
            warnings.warn("highlighting not available - pygments is required")
        else:
            if self._lexer is None:
                self._lexer = PythonXTracebackLexer()
            if self._formatter is None:
                # passing style=default here is the same as passing no
                # arguments - the reason for doing it is that if we don't the
                # style gets imported at runtime which under some restricted
                # environments (appengine) causes a problem - all of the
                # imports must be done before appengine installs its import
                # hook
                self._formatter = TerminalFormatter(style=default)
            try:
                return pygments.highlight(string, self._lexer, self._formatter)
            except KeyboardInterrupt:
                # let the user abort highlighting if problematic
                pass
        return string

    def _str_lines(self, lines):
        exc_str = "".join(lines)
        if self.color:
            exc_str = self._highlight(exc_str)
        return exc_str

    def _format_lines(self, lines):
        # XXX: This is doing the highlight line by line
        return map(self._highlight, lines) if self.color else lines

    def _print_lines(self, lines):
        if self.options.stream is None:
            raise RuntimeError("Cannot print - %r has None stream" % self)
        self.options.stream.write(self._str_lines(lines))

    # { Traceback format - these return lines terminated with "\n"

    def _format_tb(self):
        lines = []
        for exc in self.exceptions:
            lines.extend(exc.format_tb())
        return lines

    def _format_exception_only(self):
        return self.exceptions[-1].format_exception_only()

    def _format_exception(self):
        lines = []
        for exc in self.exceptions:
            lines.extend(exc.format_exception())
        return lines

    # { Interface - this is compatible with the stdlib's traceback module

    def format_tb(self):
        return self._format_lines(self._format_tb())

    def format_exception_only(self):
        return self._format_lines(self._format_exception_only())

    def format_exception(self):
        return self._format_lines(self._format_exception())

    def print_tb(self):
        self._print_lines(self._format_tb())

    def print_exception(self):
        self._print_lines(self._format_exception())

    # }
