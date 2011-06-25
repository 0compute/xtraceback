XTraceback
----------

Extended Python traceback formatter with support for variable expansion and
syntax highlighting::
    
    import sys
    import traceback
    import xtraceback

    # inline
    try:
        raise Exception()
    except:
        xtb = xtraceback.XTraceback(*sys.exc_info())
        xtb.print_exception()

    # as a context manager - the stdlib traceback module is monkey patched
    with xtraceback.TracebackCompat():
        try:
            raise Exception()
        except:
            traceback.print_exc()
    
    # as a sys.excepthook
    xtb = xtraceback.TracebackCompat()
    xtb.install_excepthook()

Options can be passed as keyword arguments to both XTraceback and
TracebackCompat. The available options are listed below with their default
values:
 
 * offset=0 - Traceback offset
 * limit=None - Traceback limit  
 * context=5 - Number of lines of context to show 
 * show_args=True - Show frame args
 * show_locals=True - Show line locals
 * show_globals=False - Show globals
 * qualify_method_names=True - Qualify method names with the name of the owning class
 * shorten_filenames=True - Shorten filenames where possible
 * color=None - Whether to use color output
 
Installation
------------

Using pip::
    
    pip install xtraceback

Nose plugin
-----------

The nose plugin is enabled with the `--with-xtraceback` flag. See `nose --help`
for other options.

[highlight.js]: http://softwaremaniacs.org/soft/highlight/en/