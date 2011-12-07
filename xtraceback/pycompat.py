import os


def monkeypatch():

    if not hasattr(os.path, "relpath"):

        # taken from py27 posixpath

        try:

            import posixpath as pp

            def relpath(path, start=pp.curdir):
                """Return a relative version of a path"""

                if not path:
                    raise ValueError("no path specified")

                start_list = [x for x in pp.abspath(start).split(pp.sep) if x]
                path_list = [x for x in pp.abspath(path).split(pp.sep) if x]

                # Work out how much of the filepath is shared by start and path.
                i = len(pp.commonprefix([start_list, path_list]))

                rel_list = [pp.pardir] * (len(start_list) - i) + path_list[i:]
                if not rel_list:
                    return pp.curdir
                return pp.join(*rel_list)

            os.path.relpath = relpath

        except ImportError:
            pass
