#!/usr/bin/env python

import os

from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), "README.md")).read()

setup(name="xtraceback",
      version="0.1",
      description="An extended traceback formatter",
      long_description=README,
      license="MIT",
      keywords="traceback exception",
      author="Ischium",
      author_email="support@ischium.net",
      url="https://github.com/ischium/xtraceback",
      py_modules=("xtraceback",),
      install_requires=("pygments",),
      entry_points={
          "nose.plugins" : ("xtraceback=xtraceback:NoseXTraceback",),
          },
      )
