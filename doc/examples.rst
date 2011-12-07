Examples
========

.. testsetup::

    import sys
    import traceback
    import xtraceback

As a context manager - the stdlib traceback module is monkey patched.


As a sys.excepthook.

.. doctest::
    :options: +REPORT_UDIFF

    >>> xtraceback.compat.install_sys_excepthook()

In a sitecustomize module.

.. doctest::
    :options: +REPORT_UDIFF

    import xtraceback
    xtraceback.compat.install()
