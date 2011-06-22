#!/usr/bin/env python

from setuptools import setup

setup(name="xtraceback",
      version="0.1",
      description="An extended traceback formatter.",
      author="Ischium",
      author_email="support@ischium.net",
      url="http://www.ischium.net/",
      install_requires=("pygments",),
      entry_points={
          "nose.plugins" : ("xtraceback=xtraceback:NoseXTraceback",),
          },
      )
