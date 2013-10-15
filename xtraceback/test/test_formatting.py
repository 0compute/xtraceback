from . import config
from . import thing
from .cases import XTracebackTestCase, skipIfNoPygments

from ..defaults import DEFAULT_WIDTH
from ..formatting import format_variable


class TestFormatting(XTracebackTestCase):

    def test_format_variable_bad_repr(self):
        class X(object):
            def __repr__(self):
                raise Exception("repr fail")
        obj = X()
        result = format_variable("a", obj)
        self.assertEqual(result, "    a = <unprintable X object>")

    def test_format_long_string(self):
        long_str = "a" * (DEFAULT_WIDTH + 1)
        formatted_str = format_variable("a", long_str)
        self.assertTrue(formatted_str.endswith("..."))
        self.assertEqual(len(formatted_str), DEFAULT_WIDTH)

    def test_format_long_repr(self):
        class X(object):
            def __repr__(self):
                return "<" + "x" * DEFAULT_WIDTH + ">"
        obj = X()
        formatted_str = format_variable("o", obj)
        self.assertTrue(formatted_str.endswith("..."))
        self.assertEqual(len(formatted_str), DEFAULT_WIDTH)

    def test_reformat_variable(self):
        value = dict()
        for i in range(0, 10):
            value["a%s" % i] = i
        formatted_str = format_variable("a", value)
        self.assertTrue(formatted_str.startswith("    a = {"))
        self.assertTrue(formatted_str.endswith("}"))
