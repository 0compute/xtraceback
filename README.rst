XTraceback is an extended Python traceback formatter with support for variable
expansion and syntax highlighting.

Installation
------------

The package is on PyPI::

    pip install xtraceback

Syntax highlighting depends on `pygments <http://pygments.org/>`_; this can be
installed in one step using::

    pip install "xtraceback[color]"

Configuration
-------------

For options and their defaults see :py:class:`-xtraceback.XTracebackOptions`. When using
stdlib compat the xtraceback.StdlibCompat class has a `defaults` dictionary
which should be updated with your overrides - the default instance exists at
xtraceback.compat::

    xtraceback.compat.defaults.update(option=value[, ...])

Nose plugin
-----------

The nose plugin is enabled with the `--with-xtraceback` flag. See `nosetests
--help` for other options.

The plugin will not work in conjunction with other plugins that patch nose or
stdlib hence a second plugin named `yanc <https://github.com/ischium/yanc>_`
which colorizes nose output without resorting to monkey patching.
