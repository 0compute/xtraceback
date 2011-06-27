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
    
    _options = (
        ("globals", "Include globals in tracebacks [%s]", "store_true"),
        ("globals_include", "Include only globals in this namespace [%s]", "store"),
        ("color", "Show color tracebacks - one of on,off,auto (default=auto) [%s]", "store"),
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
        self.color = self.xtraceback_color !="off" \
                         and (self.xtraceback_color == "on" \
                             or (self.xtraceback_color in ("auto", None) \
                                 and hasattr(self.conf.stream, "isatty") \
                                 and self.conf.stream.isatty()))
        
    def begin(self):
        # not importing in global scope because is messes with the coverage
        import xtraceback
        options = dict(show_globals=self.xtraceback_globals,
                       globals_module_include=self.xtraceback_globals_include)
        xtraceback.compat.update_defaults(self.color, **options)
        xtraceback.compat.__enter__()
    
    def finalize(self, result):
        import xtraceback
        xtraceback.compat.__exit__(None, None, None)
    