XTraceback is an extended Python traceback formatter with support for variable
expansion and syntax highlighting. It is intended both as a development tool
and for post-mortem debugging of live applications.

It works as a drop-in replacement for the standard library's
:py:mod:`traceback` module and has support for the :py:mod:`logging` package.

To use XTraceback you need to have the following as early as possible in your
code, or alternatively in a :py:mod:`site` `sitecustomize` module.

    >>> import xtraceback
    >>> xtraceback.compat.install()

This will patch the :py:mod:`traceback` module replacing the following
functions with extended versions from :py:class:`xtraceback.StdlibCompat`:

 * :py:func:`traceback.format_tb`
 * :py:func:`traceback.format_exception_only`
 * :py:func:`traceback.format_exception`
 * :py:func:`traceback.format_exc`
 * :py:func:`traceback.print_tb`
 * :py:func:`traceback.print_exception`
 * :py:func:`traceback.print_exc`

It will also install :py:meth:`xtraceback.StdlibCompat.print_exception` as a
:py:obj:`sys.excepthook`.
