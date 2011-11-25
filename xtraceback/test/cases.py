import difflib
import re
import sys
import unittest

from xtraceback import XTraceback


ID_PATTERN = re.compile("0[xX][a-fA-F0-9]+")
TRAILING_WHITESPACE_PATTERN = re.compile(" \n")

TB_DEFAULTS = dict(address="0x123456789")


class TestCaseMixin(object):

    def __str__(self):  # pragma: no cover - test util only
        # so that you can copy/paste the test name to rerun
        return "%s:%s.%s" % (self.__class__.__module__,
                             self.__class__.__name__,
                             self._testMethodName)


class XTracebackTestCase(TestCaseMixin, unittest.TestCase):

    XTB_DEFAULTS = dict(offset=1)

    def _factory(self, *exc_info, **options):
        _options = self.XTB_DEFAULTS.copy()
        _options.update(options)
        return XTraceback(*exc_info, **_options)

    def _get_exc_info(self, exec_str, **namespace):
        try:
            exec exec_str in namespace
        except:
            return sys.exc_info()
        else:
            self.fail("Should have raised exception")

    def _assert_tb_str(self, exc_str, expect_exc_str):
        exc_str = ID_PATTERN.sub(TB_DEFAULTS["address"], exc_str)
        # stripping trailing whitespace that gets added when we have an empty
        # line
        exc_str = TRAILING_WHITESPACE_PATTERN.sub("\n", exc_str)
        if exc_str != expect_exc_str:  # pragma: no cover for obvious reasons
            diff = difflib.ndiff(exc_str.splitlines(True),
                                 expect_exc_str.splitlines(True))
            #print "-" * 70
            #print "want:"
            #print expect_exc_str
            #print "-" * 70
            #print "got:"
            #print exc_str
            #print "-" * 70
            print "diff:"
            print "".join(diff)
            self.fail("different")

    def _assert_tb_lines(self, exc_lines, expect_lines):
        self._assert_tb_str("".join(exc_lines), "".join(expect_lines))

    def _check_tb_str(self, exec_str, expect_exc_str, **namespace):
        exc_info = self._get_exc_info(exec_str, **namespace)
        xtb = self._factory(*exc_info)
        self._assert_tb_str(str(xtb), expect_exc_str)
