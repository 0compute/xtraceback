
class XTracebackOptions(object):
    """
    XTraceback options

    :ivar stream: A file-like object that is the default for print_* methods
    :type stream: file
    :ivar color: Flag to force color on or off - if None look to whether the
        `stream` is a tty
    :type color: bool
    :ivar print_width: How many columns wide to print the screen - if None and
        `stream` is a tty on Unix then fill the available width
    :ivar offset: A stack frame offset - defaults to 0
    :type offset: int
    :ivar limit: Stack frame limit - if None the entire stack is returned
    :context: Lines of context that are included in traceback entries
    :type context: int
    """

    # default options
    _options = dict(
        stream=None,
        color=None,
        print_width=None,
        offset=0,
        limit=None,
        context=5,
        globals_module_include=None,
        # python 3
        chain=True,
        )

    # default flags
    _flags = dict(
        show_args=True,
        show_locals=True,
        show_globals=False,
        qualify_methods=True,
        shorten_filenames=True,
        )

    def __init__(self, **options):
        # options
        for key in self._options:
            value = options.pop(key, None)
            if value is None:
                value = self._options[key]
            setattr(self, key, value)
        # flags
        for key in self._flags:
            value = options.pop(key, None)
            if value is None:
                value = self._flags[key]
            else:
                value = bool(value)
            setattr(self, key, value)
        # there should be no more options
        if options:
            raise TypeError("Unsupported options: %r" % options)
