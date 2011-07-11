"""
nose plugin for XTraceback

This module is placed outside of the xtraceback package because we don't want
nose to import the xtraceback package until it has started the coverage plugin.
"""

try:
    from nose.plugins import Plugin
except ImportError:
    Plugin = object


class NoseXTraceback(Plugin):
    """Extended traceback for error output."""

    name = "xtraceback"

    # must be before capture otherwise we don't see the real sys.stdout
    score = 600

    _options = (
        ("globals", "Include globals in tracebacks [%s]", "store_true"),
        ("globals_include",
         "Include only globals in this namespace [%s]",
         "store"),
        ("color",
         "Show color tracebacks - one of on,off,auto (default=auto) [%s]",
         "store"),
        )

    def options(self, parser, env):
        super(NoseXTraceback, self).options(parser, env)
        for name, help, action in self._options:
            env_opt = "NOSE_XTRACEBACK_%s" % name.upper()
            parser.add_option("--xtraceback-%s" % name.replace("_", "-"),
                              action=action,
                              dest="xtraceback_%s" % name,
                              default=env.get(env_opt),
                              help=help % env_opt)


    def configure(self, options, conf):
        super(NoseXTraceback, self).configure(options, conf)
        for name, help, dummy in self._options:
            name = "xtraceback_%s" % name
            setattr(self, name, getattr(options, name))
        if self.xtraceback_color is not None:
            if self.xtraceback_color == "on":
                self.xtraceback_color = True
            else:
                self.xtraceback_color = False

    def begin(self):
        # not importing in global scope because it messes with the coverage
        # analysis
        import xtraceback
        options = dict(color=self.xtraceback_color,
                       stream=self.conf.stream,
                       show_globals=self.xtraceback_globals,
                       globals_module_include=self.xtraceback_globals_include)
        xtraceback.compat.defaults.update(**options)
        xtraceback.compat.install()

    def finalize(self, result):
        import xtraceback
        xtraceback.compat.uninstall()
