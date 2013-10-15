from stacked import Stacked


class LoggingCompat(Stacked):

    def __init__(self, handler, tbcompat, **options):
        super(LoggingCompat, self).__init__()
        self.handler = handler
        self.tbcompat = tbcompat
        self.options = options

        formatter = self.handler.formatter

        # this is shit but we're stuck with the stdlib implementation since
        # it caches the result of formatException which we don't want to do
        # as it will screw up other formatters who are expecting a regular
        # traceback
        _format = formatter.format

        def format(record):
            record.exc_text = None
            formatted = _format(record)
            record.exc_text = None
            return formatted

        self._register_patch(formatter, "format", format)

        self._register_patch(formatter, "formatException",
                             self.formatException)

    def formatException(self, ei):
        return str(self.tbcompat._factory(*ei, **self.options))
