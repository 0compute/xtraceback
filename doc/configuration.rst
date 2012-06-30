Configuration
=============

For options and their defaults see :py:class:`xtraceback.XTracebackOptions`.
When using stdlib compatibility the :py:class:`xtraceback.StdlibCompat`
`defaults` dictionary should be updated with your overrides - the default
instance exists at :py:obj:`xtraceback.compat`::

    xtraceback.compat.defaults.update(option=value[, ...])
