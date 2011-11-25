from __future__ import with_statement

from StringIO import StringIO
import sys
import traceback

from xtraceback import StdlibCompat

from .cases import TestCaseMixin, XTracebackTestCase
from .test_xtraceback import EXTENDED_TEST, SIMPLE_TRACEBACK


SIMPLE_EXCEPTION_ONEFRAME = \
"""Traceback (most recent call last):
%s
Exception: exc
""" % "\n".join(SIMPLE_TRACEBACK.splitlines()[0:2])


class StdlibTestMixin(TestCaseMixin):

    def setUp(self):
        super(StdlibTestMixin, self).setUp()
        # these options should produce tracebacks that the same as from stdlib
        self.compat = StdlibCompat(context=1,
                                   show_args=False,
                                   show_locals=False,
                                   show_globals=False,
                                   qualify_methods=False,
                                   shorten_filenames=False)


class InstalledStdlibTestMixin(StdlibTestMixin):

    def setUp(self):
        super(InstalledStdlibTestMixin, self).setUp()
        self.compat.__enter__()

    def tearDown(self):
        super(InstalledStdlibTestMixin, self).tearDown()
        self.compat.__exit__(None, None, None)


# use the stdlib's traceback test cases
try:
    from test.test_traceback import TracebackCases, TracebackFormatTests
except ImportError:  # pragma: no cover
    # on debian (and maybe others) the stdlib does not have the full
    # test package
    pass
else:

    class TestStdlibBase(InstalledStdlibTestMixin, TracebackCases):
        pass

    class TestStdlibFormat(InstalledStdlibTestMixin, TracebackFormatTests):
        pass

    # otherwise they get run as tests
    del TracebackCases, TracebackFormatTests


class TestStdlibInterface(StdlibTestMixin, XTracebackTestCase):

    def test_format_tb(self):
        with self.compat:
            tb = self._get_exc_info(EXTENDED_TEST)[2]
            lines = traceback.format_tb(tb)
        self.assertEqual(traceback.format_tb(tb), lines)

    def test_print_tb(self):
        with self.compat:
            tb = self._get_exc_info(EXTENDED_TEST)[2]
            stream = StringIO()
            traceback.print_tb(tb, file=stream)
            exc_str = stream.getvalue()
        stream = StringIO()
        traceback.print_tb(tb, file=stream)
        stdlib_exc_str = stream.getvalue()
        self.assertEqual(stdlib_exc_str, exc_str)

    def test_print_tb_no_file(self):
        stderr = sys.stderr
        stream = StringIO()
        sys.stderr = stream
        try:
            tb = self._get_exc_info(EXTENDED_TEST)[2]
            with self.compat:  # pragma: no cover - coverage does not see this
                traceback.print_tb(tb)
            exc_str = stream.getvalue()
            stream = StringIO()
            sys.stderr = stream
            traceback.print_tb(tb)
            stdlib_exc_str = stream.getvalue()
            self.assertEqual(stdlib_exc_str, exc_str)
        finally:
            sys.stderr = stderr

    def test_format_exception_only(self):
        with self.compat:
            etype, value = self._get_exc_info(EXTENDED_TEST)[:-1]
            lines = traceback.format_exception_only(etype, value)
        self.assertEqual(traceback.format_exception_only(etype, value), lines)

    def test_format_exception(self):
        with self.compat:
            exc_info = self._get_exc_info(EXTENDED_TEST)
            lines = traceback.format_exception(*exc_info)
        self.assertEqual(traceback.format_exception(*exc_info), lines)

    def test_print_exception(self):
        exc_info = self._get_exc_info(EXTENDED_TEST)
        with self.compat:
            stream = StringIO()
            traceback.print_exception(*exc_info, **dict(file=stream))
            exc_str = stream.getvalue()
        stream = StringIO()
        traceback.print_exception(*exc_info, **dict(file=stream))
        stdlib_exc_str = stream.getvalue()
        self.assertEqual(stdlib_exc_str, exc_str)

    def test_format_exc(self):
        with self.compat:
            try:
                exec EXTENDED_TEST in {}
            except:
                lines = traceback.format_exc()
            else:
                self.fail("Should have raised exception")
        self.assertEqual(traceback.format_exc(), lines)

    def test_print_exc(self):
        with self.compat:
            stream = StringIO()
            try:
                exec EXTENDED_TEST in {}
            except:
                traceback.print_exc(file=stream)
            else:
                self.fail("Should have raised exception")
            exc_str = stream.getvalue()
        stream = StringIO()
        traceback.print_exc(file=stream)
        stdlib_exc_str = stream.getvalue()
        self.assertEqual(stdlib_exc_str, exc_str)
