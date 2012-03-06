Stdlib Compatibility
====================

XTraceback works as a drop-in replacement for the standard library's
:py:mod:`traceback` module and can patch
:py:meth:`logging.LogFormatter.formatException`

XTraceback should be installed as early as possible in your code, or
alternatively in a :py:mod:`site` `sitecustomize` module.

traceback
---------

    >>> import xtraceback
    >>> xtraceback.compat.install()

This installs :py:meth:`xtraceback.StdlibCompat.print_exception` as a
:py:obj:`sys.excepthook` and patches the :py:mod:`traceback` module replacing
the following functions with extended versions from
:py:class:`xtraceback.StdlibCompat`:

 * :py:func:`traceback.format_tb`
 * :py:func:`traceback.format_exception_only`
 * :py:func:`traceback.format_exception`
 * :py:func:`traceback.format_exc`
 * :py:func:`traceback.print_tb`
 * :py:func:`traceback.print_exception`
 * :py:func:`traceback.print_exc`

logging
-------

    >>> import xtraceback
    >>> xtraceback.compat.install_root_logformatter()
