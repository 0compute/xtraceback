"""
stdlib test_traceback importer

on debian (and maybe others) the standard python distribution does not
include a test package so the required test_traceback module is included here
"""

import glob
import os
import sys
import warnings

test_traceback = None

try:
    from test import test_traceback
except ImportError:

    platform = sys.platform.startswith("java") and "jython" or "python"
    version = "%s.%s" % sys.version_info[0:2]
    paths = glob.glob(os.path.join(os.path.dirname(__file__),
                                   platform,
                                   "%s.*" % version))
    if not paths:
        warnings.warn("test_support for %s %s not available" % (platform, version))
    else:
        sys.path.insert(0, paths[0])
        try:
            del sys.modules["test"]
        except KeyError:
            pass
        from test import test_traceback
