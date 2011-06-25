"""
nose plugin for XTraceback

This module is placed outside of the xtraceback package because we don't want
nose to import the xtraceback package until it has started the coverage plugin.
"""
import sys

try:
    from nose.plugins import Plugin
except ImportError:
    nose_xtraceback = None
else:
    
    class nose_xtraceback(Plugin):
        """Extended traceback for error output"""
        
        name = "xtraceback"
        
        _options = (
            ("color", "Show color tracebacks [%s]", "store_true"),
            ("globals", "Include globals in tracebacks [%s]", "store_true"),
            ("globals_include", "Include only globals in this namespace [%s]", "store")
            )
        
        def options(self, parser, env):
            super(nose_xtraceback, self).options(parser, env)
            for name, help, action in self._options:
                env_opt = "NOSE_XTRACEBACK_%s" % name.upper()
                parser.add_option("--xtraceback-%s" % name.replace("_", "-"),
                                  action=action,
                                  dest="xtraceback_%s" % name,
                                  default=env.get(env_opt),
                                  help=help % env_opt)
            
        
        def configure(self, options, conf):
            super(nose_xtraceback, self).configure(options, conf)
            for name, help, action in self._options:
                name = "xtraceback_%s" % name
                setattr(self, name, getattr(options, name))
                
        def begin(self):
            from xtraceback import TracebackCompat
            options = dict(show_globals=self.xtraceback_globals,
                           globals_module_include=self.xtraceback_globals_include,
                           color=self.xtraceback_color,)
            self._xtraceback_compat = TracebackCompat(**options)
            self._xtraceback_compat.__enter__()
            
        def finalize(self, result):
            self._xtraceback_compat.__exit__(None, None, None)