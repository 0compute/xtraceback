"""
XTraceback plugin for nose
"""

try:
    from nose.plugins import Plugin
except ImportError:
    pass
else:

    from .tracebackcompat import TracebackCompat

    class NoseXTraceback(Plugin):
        """Extended traceback for error output."""

        name = "xtraceback"

        # must be before capture otherwise we don't see the real sys.stdout
        score = 600

        _options = (
            ("globals",
             "Include globals in tracebacks [%s]",
             "store_true"),
            ("globals_include",
             "Include only globals in this namespace [%s]",
             "store"),
            ("color",
             "Show color tracebacks - one of on,off,auto (default=auto) [%s]",
             "store"),
        )

        def options(self, parser, env):
            super(NoseXTraceback, self).options(parser, env)
            for name, doc, action in self._options:
                env_opt = "NOSE_XTRACEBACK_%s" % name.upper()
                parser.add_option("--xtraceback-%s" % name.replace("_", "-"),
                                  action=action,
                                  dest="xtraceback_%s" % name,
                                  default=env.get(env_opt),
                                  help=doc % env_opt)

        def configure(self, options, conf):
            super(NoseXTraceback, self).configure(options, conf)
            for option in self._options:
                name = "xtraceback_%s" % option[0]
                setattr(self, name, getattr(options, name))
            if self.xtraceback_color is not None:
                if self.xtraceback_color == "on":
                    self.xtraceback_color = True
                else:
                    self.xtraceback_color = False

        def begin(self):
            options = dict(
                color=self.xtraceback_color,
                stream=self.conf.stream,
                show_globals=self.xtraceback_globals,
                globals_module_include=self.xtraceback_globals_include
            )
            self.compat = TracebackCompat(**options)
            self.compat.__enter__()

        def finalize(self, result):
            self.compat.__exit__(None, None, None)
