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

    >>> 
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
    
In a python sitecustomize.py file::

    import xtraceback
    xtraceback.compat.install()
    
Then tell python to use the startup file::

    export PYTHONSTARTUP=/path/to/startup.py

Configuration
-------------

Options are passed as keyword arguments to the XTraceback constructor.
 
 - offset=0 - Traceback offset
 - limit=None - Traceback limit  
 - context=5 - Number of lines of context to show 
 - show_args=True - Show frame args
 - show_locals=True - Show line locals
 - show_globals=False - Show globals
 - qualify_method_names=True - Qualify method names with the name of the owning class
 - shorten_filenames=True - Shorten filenames where possible
 - color=None - Whether to use color output
 
Installation
------------

The package is on PyPI::
    
    pip install xtraceback

Nose plugin
-----------

The nose plugin is enabled with the `--with-xtraceback` flag. See `nose --help`
for other options.
