XTraceback
==========

Extended Python traceback formatter with support for local variable expansion and
syntax highlighting.

The formatter monkey patches the stdlib's traceback module replacing `print_tb`,
`format_tb`, and `format_exception` with XTraceback methods of the same name and
signature. It is intended that these methods are 100% compatible with the functions
they replace.

    from xtraceback import XTraceback

    # process-wide
    xtraceback.push()
    raise Exception()
    xtraceback.pop()
    
    # as a context manager
    xtraceback = XTraceback()
    with xtraceback:
        raise Exception()
        
The difference between `push`/`pop` and the context manager is that `push` sets
sys.excepthook to use `print_exception`. 

## Installation
    
    pip install xtraceback

## Nose plugin

The nose plugin is enabled using `--with-xtraceback`.
