import sys

HEX_ID_LENGTH = len(hex(id(__file__))) - 2

TB_DEFAULTS = dict(address="0x%s" % ("a" * HEX_ID_LENGTH,))

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
thing = Thing()
thing.one()
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

SIMPLE_EXCEPTION_ONEFRAME = \
"""Traceback (most recent call last):
%s
Exception: exc
""" % "\n".join(SIMPLE_TRACEBACK.splitlines()[0:2])

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
    g:raise_exception = <function raise_exception at %(address)s>
  File "<string>", line 4, in raise_exception
    recursion_level = 2
    g:one = 1
    g:raise_exception = <function raise_exception at %(address)s>
    dummy = 2
  File "<string>", line 4, in raise_exception
    recursion_level = 1
    g:one = 1
    g:raise_exception = <function raise_exception at %(address)s>
    dummy = 1
  File "<string>", line 6, in raise_exception
    recursion_level = 0
    g:one = 1
    g:raise_exception = <function raise_exception at %(address)s>
Exception: exc
""" % TB_DEFAULTS

EXTENDED_EXCEPTION = \
"""Traceback (most recent call last):
  File "<string>", line 3, in <module>
    g:Thing = <class 'xtraceback.test.thing.Thing'>
    g:thing = <xtraceback.test.thing.Thing object at %(address)s>
  File "xtraceback/test/thing.py", line 13, in Thing.one
    self = <xtraceback.test.thing.Thing object at %(address)s>
    g:Other = <class 'xtraceback.test.other.Other'>
    g:Thing = <class 'xtraceback.test.thing.Thing'>
    g:logging = <package 'logging' from='<stdlib>/logging'>
    g:os = <module 'os' from='<stdlib>/os.py'>
    g:sys = <module 'sys' (built-in)>
    11 def one(self):
    12     sugar = max(1, 2)
--> 13     self.two(sugar)
           sugar = 2
    14
    15 def two(self, sugar):
  File "xtraceback/test/thing.py", line 18, in Thing.two
    self = <xtraceback.test.thing.Thing object at %(address)s>
    sugar = 2
    g:Other = <class 'xtraceback.test.other.Other'>
    g:Thing = <class 'xtraceback.test.thing.Thing'>
    g:logging = <package 'logging' from='<stdlib>/logging'>
    g:os = <module 'os' from='<stdlib>/os.py'>
    g:sys = <module 'sys' (built-in)>
    14
    15 def two(self, sugar):
    16     long = "y" * 67
    17     obj = Other()
--> 18     obj.one(long)
           long = 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy...
           obj = <xtraceback.test.other.Other object at %(address)s>
  File "xtraceback/test/other.py", line 8, in Other.one
    self = <xtraceback.test.other.Other object at %(address)s>
    long = 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy'
    g:Other = <class 'xtraceback.test.other.Other'>
     6     number = 1
     7     result = number * 10
---> 8     self.b(number, long)
           number = 1
           result = 10
     9
    10 def b(self, number, long):
  File "xtraceback/test/other.py", line 11, in Other.b
    self = <xtraceback.test.other.Other object at %(address)s>
    number = 1
    long = 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy'
    g:Other = <class 'xtraceback.test.other.Other'>
     9
    10 def b(self, number, long):
--> 11     self.c("arg1", "arg2", a_kw_arg=1)
    12
    13 def c(self, *args, **kwargs):
  File "xtraceback/test/other.py", line 14, in Other.c
    self = <xtraceback.test.other.Other object at %(address)s>
    *args = ('arg1', 'arg2')
    **kwargs = {'a_kw_arg': 1}
    g:Other = <class 'xtraceback.test.other.Other'>
    12
    13 def c(self, *args, **kwargs):
--> 14     self.d()
    15
    16 def d(self):
  File "xtraceback/test/other.py", line 17, in Other.d
    self = <xtraceback.test.other.Other object at %(address)s>
    g:Other = <class 'xtraceback.test.other.Other'>
    15
    16 def d(self):
--> 17     self.e()
    18
    19 def e(self):
  File "xtraceback/test/other.py", line 20, in Other.e
    self = <xtraceback.test.other.Other object at %(address)s>
    g:Other = <class 'xtraceback.test.other.Other'>
    16 def d(self):
    17     self.e()
    18
    19 def e(self):
--> 20     raise Exception("exc")
Exception: exc
""" % TB_DEFAULTS

# jython prints syntax errors differently to CPython
if sys.platform.startswith("java"):
    SYNTAX_EXCEPTION = \
"""  File "<string>", line 1
    if:
     ^
SyntaxError: no viable alternative at input ':'
"""
else:
    SYNTAX_EXCEPTION = \
"""  File "<string>", line 1
    if:
      ^
SyntaxError: invalid syntax
"""
