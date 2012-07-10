import logging
from StringIO import StringIO
import sys
import traceback

from xtraceback import StdlibCompat

from .cases import XTracebackTestCase
from .test_xtraceback import BASIC_TEST, SIMPLE_EXCEPTION, \
    SIMPLE_EXCEPTION_NO_TB, SIMPLE_TRACEBACK


SIMPLE_EXCEPTION_ONEFRAME = \
"""Traceback (most recent call last):
%s
Exception: exc
""" % "\n".join(SIMPLE_TRACEBACK.splitlines()[0:2])


class MockLogHandler(logging.Handler):
    """
    Mock logging.Handler for test
    """

    def __init__(self, level=logging.NOTSET):
        logging.Handler.__init__(self, level)
        self.log = dict()

    def emit(self, record):
        self.log.setdefault(record.levelname, []).append(self.format(record))


class TestStdlibCompat(XTracebackTestCase):

    def setUp(self):
        super(TestStdlibCompat, self).setUp()
        self.compat = StdlibCompat(**self.XTB_DEFAULTS)
        self.compat.__enter__()

    def tearDown(self):
        super(TestStdlibCompat, self).tearDown()
        self.compat.__exit__(None, None, None)

    def test_format_tb(self):
        tb = self._get_exc_info(BASIC_TEST)[2]
        lines = traceback.format_tb(tb)
        self._assert_tb_lines(lines, SIMPLE_TRACEBACK)

    def test_print_tb(self):
        tb = self._get_exc_info(BASIC_TEST)[2]
        stream = StringIO()
        traceback.print_tb(tb, file=stream)
        self._assert_tb_str(stream.getvalue(), SIMPLE_TRACEBACK)

    def test_print_tb_no_file(self):
        stream = StringIO()
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
        stream = StringIO()
        exc_info = self._get_exc_info(BASIC_TEST)
        traceback.print_exception(*exc_info, **dict(file=stream))
        self._assert_tb_str(stream.getvalue(), SIMPLE_EXCEPTION)

    def test_print_exception_limited(self):
        stream = StringIO()
        traceback.print_exception(*self._get_exc_info(BASIC_TEST),
                                  **dict(limit=2, file=stream))
        self._assert_tb_str(stream.getvalue(), SIMPLE_EXCEPTION_ONEFRAME)

    def test_format_exc(self):
        try:
            exec BASIC_TEST in {}
        except:
            exc_str = traceback.format_exc()
        else:
            self.fail("Should have raised exception")
        self._assert_tb_str(exc_str, SIMPLE_EXCEPTION)

    def test_print_exc(self):
        stream = StringIO()
        try:
            exec BASIC_TEST in {}
        except:
            traceback.print_exc(file=stream)
        else:
            self.fail("Should have raised exception")
        self._assert_tb_str(stream.getvalue(), SIMPLE_EXCEPTION)

    def test_install_sys_excepthook(self):
        self.compat.install_sys_excepthook()
        self.assertEqual(sys.excepthook, traceback.print_exception)
        try:
            exec BASIC_TEST in {}
        except:
            exc_info = self._get_exc_info(BASIC_TEST)
            lines = traceback.format_exception(*exc_info)
            self._assert_tb_lines(lines, SIMPLE_EXCEPTION)
        else:
            self.fail("Should have raised exception")

    def test_install_logging(self):
        formatter = logging.Formatter()
        handler = MockLogHandler()
        handler.setFormatter(formatter)
        logging.root.addHandler(handler)
        try:
            self.compat.install_logging(handler)
            try:
                exec BASIC_TEST in {}
            except:
                logging.exception("the exc")
                exc_str = formatter.formatException(self._get_exc_info(BASIC_TEST))
                self._assert_tb_str(exc_str, SIMPLE_EXCEPTION)
            else:
                self.fail("Should have raised exception")
                exc_str = "\n".join(handler.log["ERROR"][0].splitlines()[1:])
            self._assert_tb_str(exc_str, SIMPLE_EXCEPTION)
        finally:
            logging.root.removeHandler(handler)


    def test_double_entry(self):
        compat = StdlibCompat(**self.XTB_DEFAULTS)
        compat.__enter__()
        self.assertRaises(RuntimeError, compat.__enter__)
        compat.__exit__(None, None, None)
        self.assertRaises(RuntimeError, compat.__exit__, None, None, None)
