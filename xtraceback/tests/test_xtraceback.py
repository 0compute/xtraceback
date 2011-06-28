import re

from . import something
from .cases import XTracebackTestCase

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

SYNTAX_TEST = \
"""if:
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

SIMPLE_EXCEPTION_COLOR = \
"""[31;01mTraceback (most recent call last):[39;49;00m
[31;01m  File [39;49;00m[36m"<string>"[39;49;00m[31;01m, line [39;49;00m[34m8[39;49;00m[31;01m, in [39;49;00m[32m<module>[39;49;00m
    [39;49;00m[36mg:[39;49;00m[31mraise_exception[39;49;00m = [39;49;00m<[39;49;00mfunction[39;49;00m [39;49;00mraise_exception[39;49;00m [39;49;00mat[39;49;00m [39;49;00m[34m%(address)s[39;49;00m>[39;49;00m
[31;01m  File [39;49;00m[36m"<string>"[39;49;00m[31;01m, line [39;49;00m[34m4[39;49;00m[31;01m, in [39;49;00m[32mraise_exception[39;49;00m
    [39;49;00m[31mrecursion_level[39;49;00m = [39;49;00m[34m2[39;49;00m
    [39;49;00m[31mdummy[39;49;00m = [39;49;00m[34m2[39;49;00m
[31;01m  File [39;49;00m[36m"<string>"[39;49;00m[31;01m, line [39;49;00m[34m4[39;49;00m[31;01m, in [39;49;00m[32mraise_exception[39;49;00m
    [39;49;00m[31mrecursion_level[39;49;00m = [39;49;00m[34m1[39;49;00m
    [39;49;00m[31mdummy[39;49;00m = [39;49;00m[34m1[39;49;00m
[31;01m  File [39;49;00m[36m"<string>"[39;49;00m[31;01m, line [39;49;00m[34m6[39;49;00m[31;01m, in [39;49;00m[32mraise_exception[39;49;00m
    [39;49;00m[31mrecursion_level[39;49;00m = [39;49;00m[34m0[39;49;00m
[31;01mException:[39;49;00m[33m exc[39;49;00m
""" % TB_DEFAULTS

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
    g:Something = <class 'xtraceback.tests.something.Something'>
    g:something = <xtraceback.tests.something.Something object at 0x123456789>
  File "xtraceback/tests/something.py", line 12, in Something.one
    self = <xtraceback.tests.something.Something object at 0x123456789>
    g:Something = <class 'xtraceback.tests.something.Something'>
    g:SomethingElse = <class 'xtraceback.tests.somethingelse.SomethingElse'>
    g:logging = <package 'logging' from='<stdlib>/logging'>
    g:os = <module 'os' from='<stdlib>/os.pyc'>
    g:sys = <module 'sys' (built-in)>
    10 def one(self):
    11     sugar = max(1, 2)
--> 12     self.two(sugar)
           sugar = 2
    13 
    14 def two(self, sugar):
  File "xtraceback/tests/something.py", line 17, in Something.two
    self = <xtraceback.tests.something.Something object at 0x123456789>
    sugar = 2
    g:Something = <class 'xtraceback.tests.something.Something'>
    g:SomethingElse = <class 'xtraceback.tests.somethingelse.SomethingElse'>
    g:logging = <package 'logging' from='<stdlib>/logging'>
    g:os = <module 'os' from='<stdlib>/os.pyc'>
    g:sys = <module 'sys' (built-in)>
    13 
    14 def two(self, sugar):
    15     long = "y" * 67
    16     obj = SomethingElse()
--> 17     obj.one(long)
           long = 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy'
           obj = <xtraceback.tests.somethingelse.SomethingElse object at 0x123456789>
  File "xtraceback/tests/somethingelse.py", line 7, in SomethingElse.one
    self = <xtraceback.tests.somethingelse.SomethingElse object at 0x123456789>
    long = <ref offset=-1>
    g:SomethingElse = <class 'xtraceback.tests.somethingelse.SomethingElse'>
     5     number = 1
     6     result = number * 10 #@UnusedVariable
---> 7     self.b(number, long)
           number = 1
           result = 10
     8 
     9 def b(self, number, long):
  File "xtraceback/tests/somethingelse.py", line 10, in SomethingElse.b
    self = <xtraceback.tests.somethingelse.SomethingElse object at 0x123456789>
    number = 1
    long = <ref offset=-2>
    g:SomethingElse = <class 'xtraceback.tests.somethingelse.SomethingElse'>
     8 
     9 def b(self, number, long):
--> 10     self.c("arg1", "arg2", a_kw_arg=1)
    11 
    12 def c(self, *args, **kwargs):
  File "xtraceback/tests/somethingelse.py", line 13, in SomethingElse.c
    self = <xtraceback.tests.somethingelse.SomethingElse object at 0x123456789>
    *args = ('arg1', 'arg2')
    **kwargs = {'a_kw_arg': 1}
    g:SomethingElse = <class 'xtraceback.tests.somethingelse.SomethingElse'>
    11 
    12 def c(self, *args, **kwargs):
--> 13     self.d()
    14 
    15 def d(self):
  File "xtraceback/tests/somethingelse.py", line 16, in SomethingElse.d
    self = <xtraceback.tests.somethingelse.SomethingElse object at 0x123456789>
    g:SomethingElse = <class 'xtraceback.tests.somethingelse.SomethingElse'>
    14 
    15 def d(self):
--> 16     self.e()
    17 
    18 def e(self):
  File "xtraceback/tests/somethingelse.py", line 19, in SomethingElse.e
    self = <xtraceback.tests.somethingelse.SomethingElse object at 0x123456789>
    g:SomethingElse = <class 'xtraceback.tests.somethingelse.SomethingElse'>
    15 def d(self):
    16     self.e()
    17 
    18 def e(self):
--> 19     raise Exception("exc")
Exception: exc
"""

SYNTAX_EXCEPTION = \
"""  File "<string>", line 1
    if:
      ^
SyntaxError: invalid syntax
"""

class TestXTraceback(XTracebackTestCase):

    def test_simple(self):
        self._check_tb_str(BASIC_TEST, SIMPLE_EXCEPTION)

    def test_simple_str(self):
        exc_info = self._get_exc_info(BASIC_TEST)
        xtb = self._factory(*exc_info)
        self._assert_tb_str(str(xtb), SIMPLE_EXCEPTION)

    def test_simple_str_color(self):
        exc_info = self._get_exc_info(BASIC_TEST)
        xtb = self._factory(*exc_info, color=True)
        self._assert_tb_str("".join(xtb.format_exception()), SIMPLE_EXCEPTION_COLOR)

    def test_simple_no_tb(self):
        etype, value = self._get_exc_info(BASIC_TEST)[:-1]
        xtb = self._factory(etype, value, None)
        self._assert_tb_str(str(xtb), SIMPLE_EXCEPTION_NO_TB)

    def test_with_globals(self):
        self._check_tb_str(BASIC_TEST, WITH_GLOBALS_EXCEPTION, one=1)

    def test_with_show_globals(self):
        exc_info = self._get_exc_info(BASIC_TEST, one=1)
        xtb = self._factory(show_globals=True, *exc_info)
        self._assert_tb_str(str(xtb), WITH_SHOW_GLOBALS_EXCEPTION)

    def test_extended(self):
        exc_info = self._get_exc_info(EXTENDED_TEST, Something=something.Something)
        xtb = self._factory(show_globals=True, *exc_info)
        self._assert_tb_str(str(xtb), EXTENDED_EXCEPTION)

    def test_syntax(self):
        self._check_tb_str(SYNTAX_TEST, SYNTAX_EXCEPTION)
