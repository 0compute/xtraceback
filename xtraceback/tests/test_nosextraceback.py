import re
import unittest

from nose.plugins import PluginTester

from xtraceback.nosextraceback import NoseXTraceback

from .cases import XTracebackTestCase


EXCEPTION = \
"""E
======================================================================
ERROR: runTest (xtraceback.tests.test_nosextraceback.TC)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "xtraceback/tests/test_nosextraceback.py", line 45, in TC.runTest
    self = <xtraceback.tests.test_nosextraceback.TC testMethod=runTest>
    43 class TC(unittest.TestCase):
    44     def runTest(self):
--> 45         raise ValueError("xxx")
    46 return unittest.TestSuite([TC()])
    47
ValueError: xxx

----------------------------------------------------------------------
Ran 1 test in 0.001s

FAILED (errors=1)
"""

TIME_PATTEN = re.compile("\d+\.\d+s")


class TestNoseXTraceback(PluginTester, XTracebackTestCase):

    activate = '--with-xtraceback'
    args = ('--xtraceback-color=off',)

    plugins = [NoseXTraceback()]

    def makeSuite(self):
        class TC(unittest.TestCase):
            def runTest(self):
                raise ValueError("xxx")
        return unittest.TestSuite([TC()])

    def test_active(self):
        exc_str = TIME_PATTEN.sub("0.001s", str(self.output))
        self._assert_tb_str(exc_str, EXCEPTION)
