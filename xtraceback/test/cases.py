import re
import sys
import unittest

from xtraceback import XTraceback


ID_PATTERN = re.compile("0[xX][a-fA-F0-9]+")
    
TB_DEFAULTS = dict(address="0x123456789")

    
class XTracebackTestCase(unittest.TestCase):
    
    XTB_DEFAULTS = dict(offset=1)
    
    def _get_exc_info(self, exec_str, **namespace):
        try:
            exec exec_str in namespace
        except:
            return sys.exc_info()
        else:
            self.fail("Should have raised exception")
        
    def _assert_tb_str(self, exc_str, expect_exc_str):
        exc_str = ID_PATTERN.sub(TB_DEFAULTS["address"], exc_str)
        print "want:\n%s" % expect_exc_str
        print "-" * 80
        print "got:\n%s" % exc_str
        print "-" * 80
        self.assertEqual(exc_str, expect_exc_str)
    
    def _assert_tb_lines(self, exc_lines, expect_exc_str):
        self._assert_tb_str("".join(exc_lines), expect_exc_str)
        
    def _check_tb_str(self, exec_str, expect_exc_str, **namespace):
        exc_info = self._get_exc_info(exec_str, **namespace)
        xtb = XTraceback(*exc_info, **self.XTB_DEFAULTS)
        self._assert_tb_str(xtb.formatted_exception_string, expect_exc_str)
    