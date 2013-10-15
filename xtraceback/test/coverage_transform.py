#!/usr/bin/env python

"""
A utility that transforms paths in .coverage data files
"""

import os
import sys

from coverage import CoverageData

# import this so we get our monkey patching done which is needed for
# os.path.relpath on python2.5
import xtraceback


def transform_data(data, transform):
    result = dict()
    for path, value in data.items():
        result[transform(path)] = value
    return result


if __name__ == "__main__":

    transform = getattr(os.path, "%spath" % sys.argv[1])
    paths = sys.argv[2:]
    assert paths

    for path in paths:
        data = CoverageData(path)
        data.read()
        for field in ("lines", "arcs"):
            field_data = getattr(data, field)
            assert field_data
            setattr(data, field,
                    transform_data(field_data, transform))
        data.write()
