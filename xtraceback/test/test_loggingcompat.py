from __future__ import with_statement

import logging

from .. import LoggingCompat, TracebackCompat

from .cases import XTracebackTestCase, skipIfNoPygments
from .config import BASIC_TEST, SIMPLE_EXCEPTION, SIMPLE_EXCEPTION_COLOR


class MockLogHandler(logging.Handler):

    def __init__(self, level=logging.NOTSET):
        # like this because logging.Handler in python <= 2.6 is not new-style
        logging.Handler.__init__(self, level)
        self.log = dict()

    def emit(self, record):
        self.log.setdefault(record.levelname, []).append(self.format(record))


class MockLogStreamHandler(MockLogHandler):

    def __init__(self, level=logging.NOTSET, tty=False):
        super(MockLogStreamHandler, self).__init__(level)
        self.stream = self.StringIO()
        self.stream.isatty = lambda: tty


class TestLoggingCompat(XTracebackTestCase):

    def setUp(self):
        super(TestLoggingCompat, self).setUp()
        self.traceback_compat = TracebackCompat(**self.XTB_DEFAULTS)

    def _make_logger(self, handler_cls, **handler_kwargs):
        handler = handler_cls(**handler_kwargs)
        handler.setFormatter(logging.Formatter())
        logger = logging.Logger(name="test")
        logger.addHandler(handler)
        return logger, handler

    def test_simple(self):
        logger, handler = self._make_logger(MockLogHandler)
        logging_compat = LoggingCompat(handler, self.traceback_compat)
        with logging_compat:
            try:
                exec(BASIC_TEST, {})
            except:
                logger.exception("the exc")
            else:
                self.fail("Should have raised exception")
        self.assertTrue(len(handler.log), 1)
        self.assertTrue(len(handler.log["ERROR"]), 1)
        exc_str = "\n".join(handler.log["ERROR"][0].split("\n")[1:])
        self._assert_tb_str(exc_str, SIMPLE_EXCEPTION)

    @skipIfNoPygments
    def test_simple_color(self):
        logger, handler = self._make_logger(MockLogHandler)
        logging_compat = LoggingCompat(handler, self.traceback_compat,
                                       color=True)
        with logging_compat:
            try:
                exec(BASIC_TEST, {})
            except:
                logger.exception("the exc")
            else:
                self.fail("Should have raised exception")
        self.assertTrue(len(handler.log), 1)
        self.assertTrue(len(handler.log["ERROR"]), 1)
        exc_str = "\n".join(handler.log["ERROR"][0].split("\n")[1:])
        self._assert_tb_str(exc_str, SIMPLE_EXCEPTION_COLOR)

    #def test_simple_stream_color(self):
        #logger, handler = self._make_logger(MockLogStreamHandler, tty=True)
        #traceback_compat = TracebackCompat(**self.XTB_DEFAULTS)
        #traceback_compat.stream = handler.stream
        #logging_compat = LoggingCompat(handler, traceback_compat)
        #with logging_compat:
            #try:
                #exec(BASIC_TEST, {})
            #except:
                #logger.exception("the exc")
                #exc_str = handler.formatter.formatException(
                #    self._get_exc_info(BASIC_TEST)
                #)
                #self._assert_tb_str(exc_str, SIMPLE_EXCEPTION_COLOR)
            #else:
                #self.fail("Should have raised exception")
        #self.assertTrue(len(handler.log), 1)
        #self.assertTrue(len(handler.log["ERROR"]), 1)
        #exc_str = "\n".join(handler.log["ERROR"][0].split("\n")[1:])
        #self._assert_tb_str(exc_str, SIMPLE_EXCEPTION_COLOR)
