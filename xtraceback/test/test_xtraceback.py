from . import config
from . import thing
from .cases import XTracebackTestCase, skipIfNoPygments


class TestXTraceback(XTracebackTestCase):

    def test_simple(self):
        self._check_tb_str(config.BASIC_TEST, config.SIMPLE_EXCEPTION)

    def test_simple_str(self):
        exc_info = self._get_exc_info(config.BASIC_TEST)
        xtb = self._factory(*exc_info)
        self._assert_tb_str(str(xtb), config.SIMPLE_EXCEPTION)

    @skipIfNoPygments
    def test_simple_str_color(self):
        exc_info = self._get_exc_info(config.BASIC_TEST)
        xtb = self._factory(*exc_info, **dict(color=True))
        self._assert_tb_str("".join(xtb.format_exception()),
                            config.SIMPLE_EXCEPTION_COLOR)

    def test_simple_no_tb(self):
        etype, value = self._get_exc_info(config.BASIC_TEST)[:-1]
        xtb = self._factory(etype, value, None)
        self._assert_tb_str(str(xtb), config.SIMPLE_EXCEPTION_NO_TB)

    def test_with_globals(self):
        self._check_tb_str(config.BASIC_TEST, config.WITH_GLOBALS_EXCEPTION,
                           one=1)

    def test_with_show_globals(self):
        exc_info = self._get_exc_info(config.BASIC_TEST, one=1)
        xtb = self._factory(show_globals=True, *exc_info)
        self._assert_tb_str(str(xtb), config.WITH_SHOW_GLOBALS_EXCEPTION)

    def test_extended(self):
        exc_info = self._get_exc_info(config.EXTENDED_TEST,
                                      Thing=thing.Thing)
        xtb = self._factory(show_globals=True, *exc_info)
        self._assert_tb_str(str(xtb), config.EXTENDED_EXCEPTION)

    def test_syntax(self):
        self._check_tb_str(config.SYNTAX_TEST, config.SYNTAX_EXCEPTION)

    def test_print_width_fixed(self):
        print_width = 100
        xtb = self._factory(None, None, None, print_width=print_width)
        self.assertEqual(xtb.print_width, print_width)
