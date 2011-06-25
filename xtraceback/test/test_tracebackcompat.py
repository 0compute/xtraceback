from StringIO import StringIO
import sys
import traceback

from xtraceback.tracebackcompat import TracebackCompat

from .cases import XTracebackTestCase
from .test_xtraceback import BASIC_TEST, SIMPLE_EXCEPTION, SIMPLE_EXCEPTION_NO_TB, SIMPLE_TRACEBACK


SIMPLE_EXCEPTION_ONEFRAME = \
"""%s
Exception: exc
""" % "\n".join(SIMPLE_TRACEBACK.splitlines()[0:3])


class TestTracebackCompat(XTracebackTestCase):
    
    def setUp(self):
        super(TestTracebackCompat, self).setUp()
        self.compat = TracebackCompat(**self.XTB_DEFAULTS)
        self.compat.__enter__()
        
    def tearDown(self):
        super(TestTracebackCompat, self).tearDown()
        self.compat.__exit__(None, None, None)  
    
    def test_format_tb(self):
        with self.compat:
            tb = self._get_exc_info(BASIC_TEST)[2]
            lines = traceback.format_tb(tb, **self.XTB_DEFAULTS)
            self._assert_tb_lines(lines, SIMPLE_TRACEBACK)
    
    def test_print_tb(self):
        with self.compat:
            tb = self._get_exc_info(BASIC_TEST)[2]
            stream = StringIO()
            traceback.print_tb(tb, file=stream, **self.XTB_DEFAULTS)
            self._assert_tb_str(stream.getvalue(), SIMPLE_TRACEBACK)
    
    def test_print_tb_no_file(self):
        with self.compat:
            stream = StringIO()
            stderr = sys.stderr
            sys.stderr = stream
            try:
                tb = self._get_exc_info(BASIC_TEST)[2]
                traceback.print_tb(tb, **self.XTB_DEFAULTS)
                self._assert_tb_str(stream.getvalue(), SIMPLE_TRACEBACK)
            finally:
                sys.stderr = stderr
    
    def test_format_exception_only(self):
        with self.compat:
            etype, value = self._get_exc_info(BASIC_TEST)[:-1]
            lines = traceback.format_exception_only(etype, value, **self.XTB_DEFAULTS)
            self._assert_tb_lines(lines, SIMPLE_EXCEPTION_NO_TB)
    
    def test_format_exception(self):
        with self.compat:
            exc_info = self._get_exc_info(BASIC_TEST)
            lines = traceback.format_exception(*exc_info, **self.XTB_DEFAULTS)
            self._assert_tb_lines(lines, SIMPLE_EXCEPTION)
    
    def test_print_exception(self):
        with self.compat:
            stream = StringIO()
            exc_info = self._get_exc_info(BASIC_TEST)
            traceback.print_exception(*exc_info, file=stream, **self.XTB_DEFAULTS)
            self._assert_tb_str(stream.getvalue(), SIMPLE_EXCEPTION)
    
    def test_print_exception_limited(self):
        with self.compat:
            stream = StringIO()
            traceback.print_exception(*self._get_exc_info(BASIC_TEST), limit=2, file=stream, **self.XTB_DEFAULTS)
            self._assert_tb_str(stream.getvalue(), SIMPLE_EXCEPTION_ONEFRAME)
        
    def test_format_exc(self):
        with self.compat:
            try:
                exec BASIC_TEST in {}
            except:
                lines = traceback.format_exc(**self.XTB_DEFAULTS)
            else:
                self.fail("Should have raised exception")
            self._assert_tb_lines(lines, SIMPLE_EXCEPTION)
    
    def test_print_exc(self):
        with self.compat:
            stream = StringIO()
            try:
                exec BASIC_TEST in {}
            except:
                traceback.print_exc(file=stream, **self.XTB_DEFAULTS)
            else:
                self.fail("Should have raised exception")
            self._assert_tb_str(stream.getvalue(), SIMPLE_EXCEPTION)
    
    def test_excepthook(self):
        excepthook = sys.excepthook
        with self.compat as compat:
            compat.install_excepthook()
            self.assertEqual(sys.excepthook, traceback.print_exception)
            try:
                exec BASIC_TEST in {}
            except:
                exc_info = self._get_exc_info(BASIC_TEST)
                lines = traceback.format_exception(*exc_info, **self.XTB_DEFAULTS)
                self._assert_tb_lines(lines, SIMPLE_EXCEPTION)
            else:
                self.fail("Should have raised exception")
        self.assertEqual(sys.excepthook, excepthook)
        