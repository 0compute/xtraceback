from StringIO import StringIO
import sys
import traceback

from xtraceback import compat

from .cases import XTracebackTestCase
from .test_xtraceback import BASIC_TEST, SIMPLE_EXCEPTION, SIMPLE_EXCEPTION_NO_TB, SIMPLE_TRACEBACK


SIMPLE_EXCEPTION_ONEFRAME = \
"""%s
Exception: exc
""" % "\n".join(SIMPLE_TRACEBACK.splitlines()[0:3])


class TestCompat(XTracebackTestCase):
    
    def test_format_tb(self):
        tb = self._get_exc_info(BASIC_TEST)[2]
        lines = compat.format_tb(tb, **self.XTB_DEFAULTS)
        self._assert_tb_lines(lines, SIMPLE_TRACEBACK)
    
    def test_print_tb(self):
        tb = self._get_exc_info(BASIC_TEST)[2]
        stream = StringIO()
        compat.print_tb(tb, file=stream, **self.XTB_DEFAULTS)
        self._assert_tb_str(stream.getvalue(), SIMPLE_TRACEBACK)
    
    def test_print_tb_no_file(self):
        stream = StringIO()
        stderr = sys.stderr
        sys.stderr = stream
        try:
            tb = self._get_exc_info(BASIC_TEST)[2]
            compat.print_tb(tb, **self.XTB_DEFAULTS)
            self._assert_tb_str(stream.getvalue(), SIMPLE_TRACEBACK)
        finally:
            sys.stderr = stderr
    
    def test_format_exception_only(self):
        etype, value = self._get_exc_info(BASIC_TEST)[:-1]
        lines = compat.format_exception_only(etype, value, **self.XTB_DEFAULTS)
        self._assert_tb_lines(lines, SIMPLE_EXCEPTION_NO_TB)
    
    def test_format_exception(self):
        exc_info = self._get_exc_info(BASIC_TEST)
        lines = compat.format_exception(*exc_info, **self.XTB_DEFAULTS)
        self._assert_tb_lines(lines, SIMPLE_EXCEPTION)
    
    def test_print_exception(self):
        stream = StringIO()
        exc_info = self._get_exc_info(BASIC_TEST)
        compat.print_exception(*exc_info, file=stream, **self.XTB_DEFAULTS)
        self._assert_tb_str(stream.getvalue(), SIMPLE_EXCEPTION)
    
    def test_print_exception_sys_tracebacklimit(self):
        tracebacklimit = getattr(sys, "tracebacklimit", 1000)
        sys.tracebacklimit = 100
        try:
            stream = StringIO()
            compat.print_exception(*self._get_exc_info(BASIC_TEST), file=stream, **self.XTB_DEFAULTS)
            self._assert_tb_str(stream.getvalue(), SIMPLE_EXCEPTION)
            sys.tracebacklimit = 1
            stream = StringIO()
            compat.print_exception(*self._get_exc_info(BASIC_TEST), file=stream, **self.XTB_DEFAULTS)
            self._assert_tb_str(stream.getvalue(), SIMPLE_EXCEPTION_NO_TB)
            sys.tracebacklimit = 2
            stream = StringIO()
            compat.print_exception(*self._get_exc_info(BASIC_TEST), file=stream, **self.XTB_DEFAULTS)
            self._assert_tb_str(stream.getvalue(), SIMPLE_EXCEPTION_ONEFRAME)
        finally:
            sys.tracebacklimit = tracebacklimit
    
    def test_format_exc(self):
        try:
            exec BASIC_TEST in {}
        except:
            lines = compat.format_exc(**self.XTB_DEFAULTS)
        else:
            self.fail("Should have raised exception")
        self._assert_tb_lines(lines, SIMPLE_EXCEPTION)
    
    def test_print_exc(self):
        stream = StringIO()
        try:
            exec BASIC_TEST in {}
        except:
            compat.print_exc(file=stream, **self.XTB_DEFAULTS)
        else:
            self.fail("Should have raised exception")
        self._assert_tb_str(stream.getvalue(), SIMPLE_EXCEPTION)

    def test_install(self):
        excepthook = sys.excepthook
        compat.install(**self.XTB_DEFAULTS)
        try:
            self.assertEqual(sys.excepthook, compat.print_exception)
            try:
                exec BASIC_TEST in {}
            except:
                exc_info = self._get_exc_info(BASIC_TEST)
                lines = traceback.format_exception(*exc_info, **self.XTB_DEFAULTS)
                self._assert_tb_lines(lines, SIMPLE_EXCEPTION)
            else:
                self.fail("Should have raised exception")
        finally:
            compat.uninstall()
        self.assertEqual(sys.excepthook, excepthook)
#        
#    def test_double_activate(self):
#        excepthook = sys.excepthook
#        xtraceback.activate()
#        try:
#            nose.tools.assert_raises(RuntimeError, xtraceback.activate)
#        finally:
#            xtraceback.deactivate()
#        self.assertEqual(sys.excepthook, excepthook)
#        
#    def test_double_deactivate(self):
#        excepthook = sys.excepthook
#        xtraceback.activate()
#        xtraceback.deactivate()
#        nose.tools.assert_raises(RuntimeError, xtraceback.deactivate)
#        self.assertEqual(sys.excepthook, excepthook)
#        
