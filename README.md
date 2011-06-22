XTraceback
==========

An extended Python traceback formatter.

    from xtraceback import XTraceback
    
    # as a context manager
    xtraceback = XTraceback()
    with xtraceback:
        # ... do your thing
    
    # process-wide
    xtraceback.push()

The formatter patches the stdlib's traceback module replacing `print_tb` and
`format_tb`.
