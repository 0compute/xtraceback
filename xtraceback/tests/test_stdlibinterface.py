from __future__ import with_statement

import os
import sys
import traceback

# on debian (and maybe others) the standard python distribution does not
# include a test package so the required test_traceback module is included
# with xtraceback
try:
    # FIXME: mixing python 2 and 3 this is not right - for python 3 this will
    # always raise an import error
    from test.test_traceback import TracebackCases, TracebackFormatTests
except ImportError:  # pragma: no cover - just a hack for testing
    import glob
    version = "%s.%s" % sys.version_info[0:2]
    opd = os.path.dirname
    paths = glob.glob(os.path.join(opd(opd(opd(__file__))),
                                   "test_support", "%s.*" % version))
    assert len(paths) == 1, "test_support for %s not available" % version
    sys.path.insert(0, paths[0])
    try:
        del sys.modules["test"]
    except KeyError:
        pass
    try:
        from test.test_traceback import TracebackCases
    except ImportError:
        # not in python 3
        # TODO: other tests are in python 3 and some should likely be used
        # beyond TracebackFormatTests
        TracebackCases = None
    try:
        from test.test_traceback import TracebackFormatTests
    except ImportError:
        # not present in python 2.5
        TracebackFormatTests = None

from xtraceback import TracebackCompat

from .cases import TestCaseMixin, XTracebackTestCase
from .config import EXTENDED_TEST, SIMPLE_TRACEBACK


SIMPLE_EXCEPTION_ONEFRAME = \
"""Traceback (most recent call last):
%s
Exception: exc
""" % "\n".join(SIMPLE_TRACEBACK.splitlines()[0:2])


class StdlibTestMixin(TestCaseMixin):

    @property
    def compat(self):
        return TracebackCompat(context=1,
                               show_args=False,
                               show_locals=False,
                               show_globals=False,
                               qualify_methods=False,
                               shorten_filenames=False)


class InstalledStdlibTestMixin(StdlibTestMixin):

    def run(self, result=None):
        with self.compat:
            super(InstalledStdlibTestMixin, self).run(result)


if TracebackCases is not None:
    class TestStdlibCases(InstalledStdlibTestMixin, TracebackCases):
        pass


if TracebackFormatTests is not None:
    class TestStdlibFormatTests(InstalledStdlibTestMixin, TracebackFormatTests):
        pass

# otherwise they get run as tests
del TracebackCases, TracebackFormatTests


class TestStdlibInterface(StdlibTestMixin, XTracebackTestCase):

    def test_format_tb(self):
        self.assertTrue(hasattr(self.compat, "format_tb"))
        with self.compat:
            tb = self._get_exc_info(EXTENDED_TEST)[2]
            lines = traceback.format_tb(tb)
        self.assertEqual(traceback.format_tb(tb), lines)

    def test_print_tb(self):
        self.assertTrue(hasattr(self.compat, "print_tb"))
        with self.compat:
            tb = self._get_exc_info(EXTENDED_TEST)[2]
            stream = self.StringIO()
            traceback.print_tb(tb, file=stream)
            exc_str = stream.getvalue()
        stream = self.StringIO()
        traceback.print_tb(tb, file=stream)
        stdlib_exc_str = stream.getvalue()
        self.assertEqual(stdlib_exc_str, exc_str)

    def test_print_tb_no_file(self):
        stderr = sys.stderr
        stream = self.StringIO()
        sys.stderr = stream
        try:
            tb = self._get_exc_info(EXTENDED_TEST)[2]
            with self.compat:  # pragma: no cover - coverage does not see this
                traceback.print_tb(tb)
            exc_str = stream.getvalue()
            stream = self.StringIO()
            sys.stderr = stream
            traceback.print_tb(tb)
            stdlib_exc_str = stream.getvalue()
            self.assertEqual(stdlib_exc_str, exc_str)
        finally:
            sys.stderr = stderr

    def test_format_exception_only(self):
        self.assertTrue(hasattr(self.compat, "format_exception_only"))
        with self.compat:
            etype, value = self._get_exc_info(EXTENDED_TEST)[:-1]
            lines = traceback.format_exception_only(etype, value)
        self.assertEqual(traceback.format_exception_only(etype, value), lines)

    def test_format_exception(self):
        self.assertTrue(hasattr(self.compat, "format_exception"))
        with self.compat:
            exc_info = self._get_exc_info(EXTENDED_TEST)
            lines = traceback.format_exception(*exc_info)
        self.assertEqual(traceback.format_exception(*exc_info), lines)

    def test_print_exception(self):
        self.assertTrue(hasattr(self.compat, "print_exception"))
        exc_info = self._get_exc_info(EXTENDED_TEST)
        with self.compat:
            stream = self.StringIO()
            traceback.print_exception(*exc_info, **dict(file=stream))
            exc_str = stream.getvalue()
        stream = self.StringIO()
        traceback.print_exception(*exc_info, **dict(file=stream))
        stdlib_exc_str = stream.getvalue()
        self.assertEqual(stdlib_exc_str, exc_str)

    def _get_format_exc_lines(self):
        try:
            exec(EXTENDED_TEST, {})
        except:
            return traceback.format_exc()
        else:
            self.fail("Should have raised exception")

    def test_format_exc(self):
        stdlib_lines = self._get_format_exc_lines()
        with self.compat:
            lines = self._get_format_exc_lines()
        self.assertEqual(stdlib_lines, lines)

    def _get_print_exc_str(self):
        stream = self.StringIO()
        try:
            exec(EXTENDED_TEST, {})
        except:
            traceback.print_exc(file=stream)
        else:
            self.fail("Should have raised exception")
        return stream.getvalue()

    def test_print_exc(self):
        self.assertTrue(hasattr(self.compat, "print_exc"))
        stdlib_exc_str = self._get_print_exc_str()
        with self.compat:
            exc_str = self._get_print_exc_str()
        self.assertEqual(stdlib_exc_str, exc_str)
