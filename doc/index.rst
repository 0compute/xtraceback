XTraceback
==========

XTraceback is an extended Python traceback formatter with support for variable
expansion and syntax highlighting. It is intended both as a development tool
and as an aide to post-mortem debugging.

.. warning::

    XTraceback is not tested on Windows systems (patches very welcome).

Installation
------------

.. pypi-release:: xtraceback
      :prefix: The package is on PyPI

To install using :pypi:`pip`::

    pip install xtraceback

To install with syntax highlighting provided by :pypi:`Pygments`::

    pip install "xtraceback[syntax]"

Documentation
-------------

.. toctree::
    :maxdepth: 2

    stdlibcompat
    configuration
    examples
    api
    nose

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
