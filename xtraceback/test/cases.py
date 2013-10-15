from __future__ import with_statement

import copy
import difflib
import re
import sys
import unittest

try:
    from StringIO import StringIO
except ImportError:
    # python 3
    from io import StringIO

try:
    import pygments
except ImportError:
    pygments = None
skipIfNoPygments = unittest.skipIf(pygments is None, "pygments not available")

from .. import TracebackCompat, XTraceback

from .config import TB_DEFAULTS

ID_PATTERN = re.compile("(0[xX][a-fA-F0-9]+)")
TRAILING_WHITESPACE_PATTERN = re.compile(" \n")


class TestCaseMixin(object):

    def __str__(self):  # pragma: no cover - test util only
        # so that you can copy/paste the test name to rerun
        return "%s:%s.%s" % (self.__class__.__module__,
                             self.__class__.__name__,
                             self._testMethodName)


class StdlibTestMixin(TestCaseMixin):
    """
    Mixin for stdlib tests

    Provides a TracebackCompat with options set to mimick stdlib behaviour
    """

    @property
    def compat(self):
        return TracebackCompat(context=1,
                               show_args=False,
                               show_locals=False,
                               show_globals=False,
                               qualify_methods=False,
                               shorten_filenames=False)


class WrappedStdlibTestMixin(StdlibTestMixin):
    """
    Mixin for wrapping stdlib tests

    Tests are executed in the context of self.compat
    """

    def run(self, result=None):
        with self.compat:
            super(WrappedStdlibTestMixin, self).run(result)


class XTracebackTestCase(TestCaseMixin, unittest.TestCase):

    XTB_DEFAULTS = dict(offset=1)

    # keep a reference to this for subclasses
    StringIO = StringIO

    def _factory(self, *exc_info, **options):
        _options = copy.deepcopy(self.XTB_DEFAULTS)
        _options.update(options)
        return XTraceback(*exc_info, **_options)

    def _get_exc_info(self, exec_str, **namespace):
        try:
            exec(exec_str, namespace)
        except:
            return sys.exc_info()
        else:
            self.fail("Should have raised exception")

    def _assert_tb_str(self, exc_str, expect_exc_str):
        exc_str = ID_PATTERN.sub(
            lambda m: TB_DEFAULTS["address"][0:len(m.group(0))],
            exc_str)
        # stripping trailing whitespace that gets added when we have an empty
        # line
        exc_str = TRAILING_WHITESPACE_PATTERN.sub("\n", exc_str)
        if exc_str != expect_exc_str:  # pragma: no cover for obvious reasons
            diff = difflib.unified_diff(expect_exc_str.splitlines(True),
                                        exc_str.splitlines(True),
                                        "expected", "actual")
            print("".join(diff))
            self.fail("traceback is not as expected")

    def _assert_tb_lines(self, exc_lines, expect_lines):
        self._assert_tb_str("".join(exc_lines), "".join(expect_lines))

    def _check_tb_str(self, exec_str, expect_exc_str, **namespace):
        exc_info = self._get_exc_info(exec_str, **namespace)
        xtb = self._factory(*exc_info)
        self._assert_tb_str(str(xtb), expect_exc_str)


class XTracebackStdlibTestCase(StdlibTestMixin, XTracebackTestCase):
    pass
