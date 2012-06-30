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
  File "xtraceback/tests/test_nosextraceback.py", line 46, in TC.runTest
    self = <xtraceback.tests.test_nosextraceback.TC testMethod=runTest>
    44 class TC(unittest.TestCase):
    45     def runTest(self):
--> 46         raise ValueError("xxx")
    47 return unittest.TestSuite([TC()])
    48
ValueError: xxx

----------------------------------------------------------------------
Ran 1 test in 0.001s

FAILED (errors=1)
"""

TIME_PATTEN = re.compile("\d+\.\d+s")


class TestNoseXTraceback(PluginTester, XTracebackTestCase):

    activate = '--with-xtraceback'

    plugins = [NoseXTraceback()]

    exc_str = EXCEPTION

    def makeSuite(self):
        class TC(unittest.TestCase):
            def runTest(self):
                raise ValueError("xxx")
        return unittest.TestSuite([TC()])

    def test_active(self):
        exc_str = TIME_PATTEN.sub("0.001s", str(self.output))
        self._assert_tb_str(exc_str, self.exc_str)


EXCEPTION_COLOR = \
"""E
======================================================================
ERROR: runTest (xtraceback.tests.test_nosextraceback.TC)
----------------------------------------------------------------------
[31;01mTraceback (most recent call last):[39;49;00m
[31;01m  File [39;49;00m[35m"xtraceback/tests/test_nosextraceback.py"[39;49;00m[31;01m, line [39;49;00m[34m46[39;49;00m[31;01m, in [39;49;00m[32mTC.runTest[39;49;00m
    [39;49;00m[31mself[39;49;00m = [39;49;00m<[39;49;00mxtraceback[39;49;00m.[39;49;00mtests[39;49;00m.[39;49;00mtest_nosextraceback[39;49;00m.[39;49;00mTC[39;49;00m [39;49;00mtestMethod[39;49;00m=[39;49;00mrunTest[39;49;00m>[39;49;00m
    [39;49;00m[34m44[39;49;00m [39;49;00m[34mclass[39;49;00m [39;49;00m[04m[32mTC[39;49;00m([39;49;00munittest[39;49;00m.[39;49;00mTestCase[39;49;00m)[39;49;00m:[39;49;00m
    [39;49;00m[34m45[39;49;00m     [39;49;00m[34mdef[39;49;00m [39;49;00m[32mrunTest[39;49;00m([39;49;00m[36mself[39;49;00m)[39;49;00m:[39;49;00m
[31;01m-->[39;49;00m [39;49;00m[34m46[39;49;00m         [39;49;00m[34mraise[39;49;00m [39;49;00m[36mValueError[39;49;00m([39;49;00m[33m"[39;49;00m[33mxxx[39;49;00m[33m"[39;49;00m)[39;49;00m
    [39;49;00m[34m47[39;49;00m [39;49;00m[34mreturn[39;49;00m [39;49;00munittest[39;49;00m.[39;49;00mTestSuite[39;49;00m([39;49;00m[[39;49;00mTC[39;49;00m([39;49;00m)[39;49;00m][39;49;00m)[39;49;00m
    [39;49;00m[34m48[39;49;00m [39;49;00m
[31;01mValueError:[39;49;00m[33m xxx[39;49;00m

----------------------------------------------------------------------
Ran 1 test in 0.001s

FAILED (errors=1)
"""

try:
    import pygments
except ImportError:
    pass
else:

    class TestNoseXTracebackColor(TestNoseXTraceback):

        args = ('--xtraceback-color=on',)
        exc_str = EXCEPTION_COLOR
