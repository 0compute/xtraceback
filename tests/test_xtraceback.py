import re
from StringIO import StringIO
import sys
import traceback
import unittest

import nose

import xtraceback

import something


ID_PATTERN = re.compile(" at 0[xX][a-fA-F0-9]+")
TB_DEFAULTS = dict(address="0x123456789")

TEST_FUNCTION = \
"""def raise_exception(recursion_level=2):
    if recursion_level:
        dummy = recursion_level
        raise_exception(recursion_level-1)
    else:
        raise Exception("exc")
"""

BASIC_TEST = \
"""%s
raise_exception()
""" % TEST_FUNCTION

EXTENDED_TEST = \
"""
something = Something()
something.one()
"""

SIMPLE_TRACEBACK = \
"""  File "<string>", line 8, in <module>
    g:raise_exception = <function raise_exception at %(address)s>
  File "<string>", line 4, in raise_exception
    recursion_level = 2
    dummy = 2
  File "<string>", line 4, in raise_exception
    recursion_level = 1
    dummy = 1
  File "<string>", line 6, in raise_exception
    recursion_level = 0
""" % TB_DEFAULTS

SIMPLE_EXCEPTION = \
"""Traceback (most recent call last):
%sException: exc
""" % SIMPLE_TRACEBACK

SIMPLE_EXCEPTION_ONEFRAME = \
"""Traceback (most recent call last):
%s
Exception: exc
""" % "\n".join(SIMPLE_TRACEBACK.splitlines()[0:2])

SIMPLE_EXCEPTION_NO_TB = \
"""Exception: exc
"""

WITH_GLOBALS_EXCEPTION = \
"""Traceback (most recent call last):
  File "<string>", line 8, in <module>
    g:one = 1
    g:raise_exception = <function raise_exception at %(address)s>
  File "<string>", line 4, in raise_exception
    recursion_level = 2
    dummy = 2
  File "<string>", line 4, in raise_exception
    recursion_level = 1
    dummy = 1
  File "<string>", line 6, in raise_exception
    recursion_level = 0
Exception: exc
""" % TB_DEFAULTS

WITH_SHOW_GLOBALS_EXCEPTION = \
"""Traceback (most recent call last):
  File "<string>", line 8, in <module>
    g:one = 1
    g:raise_exception = <function raise_exception at 0x123456789>
  File "<string>", line 4, in raise_exception
    recursion_level = 2
    g:one = 1
    g:raise_exception = <function raise_exception at 0x123456789>
    dummy = 2
  File "<string>", line 4, in raise_exception
    recursion_level = 1
    g:one = 1
    g:raise_exception = <function raise_exception at 0x123456789>
    dummy = 1
  File "<string>", line 6, in raise_exception
    recursion_level = 0
    g:one = 1
    g:raise_exception = <function raise_exception at 0x123456789>
Exception: exc
"""

EXTENDED_EXCEPTION = \
"""Traceback (most recent call last):
  File "<string>", line 3, in <module>
    g:Something = <class tests.something.Something>
    g:something = <tests.something.Something object at 0x123456789>
  File "tests/something.py", line 12, in Something.one
    self = <tests.something.Something object at 0x123456789>
    10 def one(self):
    11     sugar = max(1, 2)
--> 12     self.two(sugar)
           sugar = 2
    13 
    14 def two(self, sugar):
  File "tests/something.py", line 17, in Something.two
    self = <tests.something.Something object at 0x123456789>
    sugar = 2
    13 
    14 def two(self, sugar):
    15     long = "y" * 67
    16     obj = SomethingElse()
--> 17     obj.one(long)
           long = 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy'
           obj = <tests.somethingelse.SomethingElse object at 0x123456789>
  File "tests/somethingelse.py", line 7, in SomethingElse.one
    self = <tests.somethingelse.SomethingElse object at 0x123456789>
    long = <ref offset=-1>
     5     number = 1
     6     result = number * 10
---> 7     self.b(number, long)
           number = 1
           result = 10
     8 
     9 def b(self, number, long):
  File "tests/somethingelse.py", line 10, in SomethingElse.b
    self = <tests.somethingelse.SomethingElse object at 0x123456789>
    number = 1
    long = <ref offset=-2>
     8 
     9 def b(self, number, long):
--> 10     self.c("arg1", "arg2", a_kw_arg=1)
    11 
    12 def c(self, *args, **kwargs):
  File "tests/somethingelse.py", line 13, in SomethingElse.c
    self = <tests.somethingelse.SomethingElse object at 0x123456789>
    *args = ('arg1', 'arg2')
    **kwargs = {'a_kw_arg': 1}
    11 
    12 def c(self, *args, **kwargs):
--> 13     self.d()
    14 
    15 def d(self):
  File "tests/somethingelse.py", line 16, in SomethingElse.d
    self = <tests.somethingelse.SomethingElse object at 0x123456789>
    14 
    15 def d(self):
--> 16     self.e()
    17 
    18 def e(self):
  File "tests/somethingelse.py", line 19, in SomethingElse.e
    self = <tests.somethingelse.SomethingElse object at 0x123456789>
    15 def d(self):
    16     self.e()
    17 
    18 def e(self):
--> 19     raise Exception("exc")
Exception: exc
"""

class TestXTraceback(unittest.TestCase):
    
    _tb_defaults = dict(color=False, offset=1)
    
    def _get_exc_info(self, exec_str, **namespace):
        try:
            exec exec_str in namespace
        except:
            return sys.exc_info()
        else:
            self.fail("Should have raised exception")
    
    def _assert_tb_str(self, exc_str, expect_exc_str):
        exc_str = ID_PATTERN.sub(" at %s" % TB_DEFAULTS["address"], exc_str)
        print "want:\n%s" % expect_exc_str
        print "-" * 80
        print "got:\n%s" % exc_str
        print "-" * 80
        self.assertEqual(exc_str, expect_exc_str)
        
    def _check_tb_str(self, exec_str, expect_exc_str, **namespace):
        etype, value, tb = self._get_exc_info(exec_str, **namespace)
        exc_str = "".join(traceback.format_exception(etype, value, tb))
        self._assert_tb_str(exc_str, expect_exc_str)
            
    def test_simple(self):
        with xtraceback.XTraceback(**self._tb_defaults):
            self._check_tb_str(BASIC_TEST, SIMPLE_EXCEPTION)
            
    def test_simple_no_tb(self):
        with xtraceback.XTraceback(**self._tb_defaults) as xtb:
            etype, value = self._get_exc_info(BASIC_TEST)[:-1]
            exc_str = xtb(etype, value, None)
            self._assert_tb_str(exc_str, SIMPLE_EXCEPTION_NO_TB)
        
    def test_with_globals(self):
        with xtraceback.XTraceback(**self._tb_defaults):
            self._check_tb_str(BASIC_TEST, WITH_GLOBALS_EXCEPTION, one=1)
        
    def test_with_show_globals(self):
        with xtraceback.XTraceback(show_globals=True, **self._tb_defaults):
            self._check_tb_str(BASIC_TEST, WITH_SHOW_GLOBALS_EXCEPTION, one=1)
    
    def test_call(self):
        with xtraceback.XTraceback(**self._tb_defaults) as xtb:
            exc_str = xtb(*self._get_exc_info(BASIC_TEST))
            self._assert_tb_str(exc_str, SIMPLE_EXCEPTION)
    
    def test_print_tb(self):
        stream = StringIO()
        with xtraceback.XTraceback(**self._tb_defaults):
            traceback.print_tb(self._get_exc_info(BASIC_TEST)[2], file=stream)
            self._assert_tb_str(stream.getvalue(), SIMPLE_TRACEBACK)
            
    def test_print_tb_no_file(self):
        stream = StringIO()
        stderr = sys.stderr
        sys.stderr = stream
        try:
            with xtraceback.XTraceback(**self._tb_defaults):
                traceback.print_tb(self._get_exc_info(BASIC_TEST)[2])
                self._assert_tb_str(stream.getvalue(), SIMPLE_TRACEBACK)
        finally:
            sys.stderr = stderr
            
    def test_print_exception(self):
        with xtraceback.XTraceback(**self._tb_defaults):
            stream = StringIO()
            traceback.print_exception(*self._get_exc_info(BASIC_TEST), file=stream)
            self._assert_tb_str(stream.getvalue(), SIMPLE_EXCEPTION)
    
    def test_print_exception_sys_tracebacklimit(self):
        tracebacklimit = getattr(sys, "tracebacklimit", 1000)
        sys.tracebacklimit = 100
        try:
            with xtraceback.XTraceback(**self._tb_defaults):
                stream = StringIO()
                traceback.print_exception(*self._get_exc_info(BASIC_TEST), file=stream)
                self._assert_tb_str(stream.getvalue(), SIMPLE_EXCEPTION)
                sys.tracebacklimit = 1
                stream = StringIO()
                traceback.print_exception(*self._get_exc_info(BASIC_TEST), file=stream)
                self._assert_tb_str(stream.getvalue(), SIMPLE_EXCEPTION_NO_TB)
                sys.tracebacklimit = 2
                stream = StringIO()
                traceback.print_exception(*self._get_exc_info(BASIC_TEST), file=stream)
                self._assert_tb_str(stream.getvalue(), SIMPLE_EXCEPTION_ONEFRAME)
        finally:
            sys.tracebacklimit = tracebacklimit
            
    def test_excepthook(self):
        excepthook = sys.excepthook
        xtraceback.activate(**self._tb_defaults)
        try:
            self.assertEqual(sys.excepthook, xtraceback._active_instance.print_exception)
            self._check_tb_str(BASIC_TEST, SIMPLE_EXCEPTION)
        finally:
            xtraceback.deactivate()
        self.assertEqual(sys.excepthook, excepthook)
        
    def test_double_activate(self):
        excepthook = sys.excepthook
        xtraceback.activate()
        try:
            nose.tools.assert_raises(RuntimeError, xtraceback.activate)
        finally:
            xtraceback.deactivate()
        self.assertEqual(sys.excepthook, excepthook)
        
    def test_double_deactivate(self):
        excepthook = sys.excepthook
        xtraceback.activate()
        xtraceback.deactivate()
        nose.tools.assert_raises(RuntimeError, xtraceback.deactivate)
        self.assertEqual(sys.excepthook, excepthook)
        
    def test_extended(self):
        with xtraceback.XTraceback(show_globals=False, **self._tb_defaults) as xtb:
            exc_str = xtb(*self._get_exc_info(EXTENDED_TEST, Something=something.Something))
            self._assert_tb_str(exc_str, EXTENDED_EXCEPTION)
        