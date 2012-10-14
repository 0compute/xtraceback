from __future__ import with_statement

import sys
import traceback

import xtraceback

from .cases import XTracebackTestCase
from .config import BASIC_TEST, SIMPLE_EXCEPTION, \
    SIMPLE_EXCEPTION_NO_TB, SIMPLE_TRACEBACK, SIMPLE_EXCEPTION_ONEFRAME


class TestTracebackCompat(XTracebackTestCase):

    def setUp(self):
        super(TestTracebackCompat, self).setUp()
        self.compat = xtraceback.TracebackCompat(**self.XTB_DEFAULTS)
        self.compat.__enter__()

    def tearDown(self):
        super(TestTracebackCompat, self).tearDown()
        self.compat.__exit__(None, None, None)

    def test_format_tb(self):
        tb = self._get_exc_info(BASIC_TEST)[2]
        lines = traceback.format_tb(tb)
        self._assert_tb_lines(lines, SIMPLE_TRACEBACK)

    def test_print_tb(self):
        tb = self._get_exc_info(BASIC_TEST)[2]
        stream = self.StringIO()
        traceback.print_tb(tb, file=stream)
        self._assert_tb_str(stream.getvalue(), SIMPLE_TRACEBACK)

    def test_print_tb_no_file(self):
        stream = self.StringIO()
        stderr = sys.stderr
        sys.stderr = stream
        try:
            tb = self._get_exc_info(BASIC_TEST)[2]
            traceback.print_tb(tb)
            self._assert_tb_str(stream.getvalue(), SIMPLE_TRACEBACK)
        finally:
            sys.stderr = stderr

    def test_format_exception_only(self):
        etype, value = self._get_exc_info(BASIC_TEST)[:-1]
        lines = traceback.format_exception_only(etype, value)
        self._assert_tb_lines(lines, SIMPLE_EXCEPTION_NO_TB)

    def test_format_exception(self):
        exc_info = self._get_exc_info(BASIC_TEST)
        lines = traceback.format_exception(*exc_info)
        self._assert_tb_lines(lines, SIMPLE_EXCEPTION)

    def test_print_exception(self):
        stream = self.StringIO()
        exc_info = self._get_exc_info(BASIC_TEST)
        traceback.print_exception(*exc_info, **dict(file=stream))
        self._assert_tb_str(stream.getvalue(), SIMPLE_EXCEPTION)

    def test_print_exception_limited(self):
        stream = self.StringIO()
        traceback.print_exception(*self._get_exc_info(BASIC_TEST),
                                  **dict(limit=2, file=stream))
        self._assert_tb_str(stream.getvalue(), SIMPLE_EXCEPTION_ONEFRAME)

    def test_format_exc(self):
        try:
            exec(BASIC_TEST, {})
        except:
            exc_str = traceback.format_exc()
        else:
            self.fail("Should have raised exception")
        self._assert_tb_str(exc_str, SIMPLE_EXCEPTION)

    def test_print_exc(self):
        stream = self.StringIO()
        try:
            exec(BASIC_TEST, {})
        except:
            traceback.print_exc(file=stream)
        else:
            self.fail("Should have raised exception")
        self._assert_tb_str(stream.getvalue(), SIMPLE_EXCEPTION)
