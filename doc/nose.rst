Nose plugin ===========

The plugin is enabled with the `--with-xtraceback` flag. See `nosetests --help`
for other options.

The plugin will not work in conjunction with other plugins that patch nose or
stdlib hence a second plugin named `yanc <https://github.com/ischium/yanc>`_
which colorizes nose output without resorting to monkey patching.
