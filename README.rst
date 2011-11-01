XTraceback is an extended Python traceback formatter with support for variable
expansion and syntax highlighting.

Examples
--------

As a context manager - the stdlib traceback module is monkey patched::

    >>> import sys
    >>> import traceback
    >>> import xtraceback
    >>>
    >>> def some_func():
    ...     some_var = 2*2
    ...     raise Exception("exc")
    >>>
    >>> with xtraceback.StdlibCompat():
    ...     try:
    ...         some_func()
    ...     except:
    ...         traceback.print_exc(file=sys.stdout) #doctest: +ELLIPSIS +REPORT_NDIFF
    Traceback (most recent call last):
      File "<doctest README.rst[...]>", line 3, in <module>
        1 with xtraceback.StdlibCompat():
        2     try:
    --> 3         some_func()
                  g:some_func = <function some_func at 0x...>
                  g:sys = <module 'sys' (built-in)>
                  g:traceback = <module 'traceback' from='<stdlib>/traceback.pyc'>
                  g:xtraceback = <package 'xtraceback' from='xtraceback'>
        4     except:
        5         traceback.print_exc(file=sys.stdout) #doctest: +ELLIPSIS +REPORT_NDIFF
      File "<doctest README.rst[...]>", line 3, in some_func
        1 def some_func():
        2     some_var = 2*2
    --> 3     raise Exception("exc")
              some_var = 4
    Exception: exc

As a sys.excepthook::

    >>> xtraceback.compat.install_sys_excepthook()
    >>> print sys.excepthook #doctest: +ELLIPSIS
    <bound method StdlibCompat.print_exception of <xtraceback.stdlibcompat.StdlibCompat object at 0x...>>
    >>> raise Exception("exc") #doctest: +ELLIPSIS
    Traceback (most recent call last):
      File "<stdlib>/doctest.py", line 1231, in __run
        compileflags, 1) in test.globs
      File "<doctest README.rst[...]>", line 1, in <module>
        raise Exception("exc") #doctest: +ELLIPSIS
    Exception: exc

By itself::

    >>> try:
    ...     raise Exception("exc")
    ... except:
    ...     print xtraceback.XTraceback(*sys.exc_info(), color=False) #doctest: +ELLIPSIS
    Traceback (most recent call last):
      File "<doctest README.rst[...]>", line 2, in <module>
        1 try:
    --> 2     raise Exception("exc")
              g:some_func = <function some_func at 0x...>
              g:sys = <module 'sys' (built-in)>
              g:traceback = <module 'traceback' from='<stdlib>/traceback.pyc'>
              g:xtraceback = <package 'xtraceback' from='xtraceback'>
        3 except:
        4     print xtraceback.XTraceback(*sys.exc_info(), color=False) #doctest: +ELLIPSIS
    Exception: exc
    <BLANKLINE>

In a sitecustomize module::

    import xtraceback
    xtraceback.compat.install()

Configuration
-------------

For options and their defaults see `xtraceback.XTraceback`'s constructor. When
using stdlib compat the `xtraceback.StdlibCompat` class has a `defaults`
dictionary which should be updated with your overrides - the default instance
exists at xtraceback.compat::

    xtraceback.compat.defaults.update(option=value[, ...])

Installation
------------

The package is on PyPI::

    pip install xtraceback

Syntax highlighting depends on the pygments library::

    pip install pygments

Nose plugin
-----------

The nose plugin is enabled with the `--with-xtraceback` flag. See `nosetests --help`
for other options.
