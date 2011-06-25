"""
nose plugin for XTraceback

This module is placed outside of the xtraceback package because we don't want
nose to import the xtraceback package until it has started the coverage plugin.
"""

import sys

try:
    from nose.plugins import Plugin
except ImportError:
    NoseXTraceback = None
else:
    
    class NoseXTraceback(Plugin):
        """Extended traceback for error output."""
        
        name = "xtraceback"
        
        # must be before capture otherwise we don't see the real sys.stdout
        score = 600
        
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
                
        def begin(self):
            import xtraceback
            color = self.xtraceback_color !="off" \
                and (self.xtraceback_color == "on" \
                     or (self.xtraceback_color in ("auto", None) \
                         and hasattr(sys.stderr, "isatty") \
                         and sys.stderr.isatty()))
            options = dict(show_globals=self.xtraceback_globals,
                           globals_module_include=self.xtraceback_globals_include,
                           color=color)
            xtraceback.compat.update_defaults(**options)
            xtraceback.compat.__enter__()
            
        def finalize(self, result):
            import xtraceback
            xtraceback.compat.__exit__(None, None, None)
