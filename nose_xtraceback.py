"""
nose plugin for XTraceback

This module is placed outside of the xtraceback package because we don't want
nose to import the xtraceback package until it has started the coverage plugin.
"""
try:
    from nose.plugins import Plugin
except ImportError:
    nose_xtraceback = None
else:
    
    class nose_xtraceback(Plugin):
        """Extended traceback for error output"""
        
        name = "xtraceback"
            
        def options(self, parser, env):
            super(nose_xtraceback, self).options(parser, env)
            env_opt = "NOSE_XTRACEBACK_GLOBALS"
            parser.add_option("--xtraceback-globals",
                              action="store_true",
                              dest="show_globals",
                              default=env.get(env_opt),
                              help="Include globals in tracebacks [%s]" % env_opt)
        
        def configure(self, options, conf):
            super(nose_xtraceback, self).configure(options, conf)
            self.show_globals = options.show_globals
                
        def begin(self):
            from xtraceback import activate
            activate(show_globals=self.show_globals)
        
        def finalize(self, result):
            from xtraceback import deactivate
            deactivate()