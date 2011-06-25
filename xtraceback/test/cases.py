import difflib
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
        if exc_str != expect_exc_str:
            diff = difflib.ndiff(expect_exc_str.splitlines(True), exc_str.splitlines(True))
            print expect_exc_str
            print exc_str
            print "".join(diff)
            self.fail("different")
    
    def _assert_tb_lines(self, exc_lines, expect_lines):
        if isinstance(expect_lines, str):
            expect_lines = expect_lines.splitlines(True)
        self._assert_tb_str("".join(exc_lines), "".join(expect_lines))
        
    def _check_tb_str(self, exec_str, expect_exc_str, **namespace):
        exc_info = self._get_exc_info(exec_str, **namespace)
        xtb = XTraceback(*exc_info, **self.XTB_DEFAULTS)
        self._assert_tb_str(xtb.formatted_exception_string, expect_exc_str)
    