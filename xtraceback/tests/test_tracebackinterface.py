from __future__ import with_statement

import sys
import traceback

from .cases import XTracebackStdlibTestCase
from .config import EXTENDED_TEST, SIMPLE_TRACEBACK


class TestTracebackInterface(XTracebackStdlibTestCase):

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
