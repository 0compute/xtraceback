from xtraceback import XTracebackOptions

from .cases import XTracebackTestCase


class TestXTracebackOptions(XTracebackTestCase):

    def test_unsupported_options(self):
        self.assertRaises(TypeError, XTracebackOptions, bad_option=True)
