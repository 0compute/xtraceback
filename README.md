XTraceback
==========

Extended Python traceback formatter with support for variable expansion and
syntax highlighting.

The formatter monkey patches the stdlib's traceback module replacing some 
functions with XTraceback methods of the same name and signature. It is intended
that these methods are compatible with the existing interfaces so this package 
can work as a drop-in replacement.

    from xtraceback import XTraceback

    # process-wide
    xtraceback.activate()
    raise Exception()
    xtraceback.deactivate()
    
    # as a context manager
    with XTraceback():
        raise Exception()

## Installation
    
    pip install xtraceback

## Nose plugin

The nose plugin is enabled with the `--with-xtraceback` flag.

[highlight.js]: http://softwaremaniacs.org/soft/highlight/en/