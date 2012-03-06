#!/usr/bin/env python

import os

from setuptools import setup

import xtraceback

README = open(os.path.join(os.path.dirname(__file__), "README.rst")).read()

# under test we do not want the nose entry point
if "XTRACEBACK_NO_NOSE" in os.environ:
    entry_points = None
else:
    entry_points = {
        "nose.plugins" : ("xtraceback=xtraceback.nosextraceback:NoseXTraceback",),
        }

setup(name="xtraceback",
      version=xtraceback.__version__,
      description="An extended traceback formatter",
      long_description=README,
      license="MIT",
      keywords="traceback exception nose",
      author="Ischium",
      author_email="support@ischium.net",
      url="https://github.com/ischium/xtraceback",
      packages=("xtraceback",),
      extras_require=dict(syntax=("pygments")),
      tests_require=("nose", "pygments", "yanc"),
      test_suite="nose.collector",
      entry_points=entry_points,
      )
