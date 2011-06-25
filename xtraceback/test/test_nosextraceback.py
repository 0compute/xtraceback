import re
import unittest

from nose.plugins import PluginTester

from nosextraceback import NoseXTraceback 

from .cases import XTracebackTestCase


EXCEPTION = \
"""E
======================================================================
ERROR: runTest (xtraceback.test.test_nosextraceback.TC)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "xtraceback/test/test_nosextraceback.py", line 44, in TC.runTest
    self = <xtraceback.test.test_nosextraceback.TC testMethod=runTest>
    42 class TC(unittest.TestCase):
    43     def runTest(self):
--> 44         raise ValueError("xxx")
    45 return unittest.TestSuite([TC()])
    46 
ValueError: xxx

----------------------------------------------------------------------
Ran 1 test in 0.001s

FAILED (errors=1)
"""

TIME_PATTEN = re.compile("\d+\.\d+s")


class TestNoseXTraceback(PluginTester, XTracebackTestCase):
    
    activate = '--with-xtraceback'
    
    plugins = [NoseXTraceback()]
    
    def makeSuite(self):
        class TC(unittest.TestCase):
            def runTest(self):
                raise ValueError("xxx")
        return unittest.TestSuite([TC()])
    
    def test_active(self):
        exc_str = TIME_PATTEN.sub("0.001s", str(self.output))
        self._assert_tb_str(exc_str, EXCEPTION)
