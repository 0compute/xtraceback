import os


if not hasattr(os.path, "relpath"):
    
    # adapted from http://jimmyg.org/work/code/barenecessities/

    try:

        import posixpath

        def relpath(path, start=posixpath.curdir):
            """Return a relative version of a path"""
            if not path:
                raise ValueError("no path specified")
            start_list = posixpath.abspath(start).split(posixpath.sep)
            path_list = posixpath.abspath(path).split(posixpath.sep)
            # Work out how much of the filepath is shared by start and path.
            i = len(posixpath.commonprefix([start_list, path_list]))
            rel_list = [posixpath.pardir] * (len(start_list)-i) + path_list[i:]
            if not rel_list:
                return posixpath.curdir
            return posixpath.join(*rel_list)

        os.path.relpath = relpath

    except ImportError:
        pass
