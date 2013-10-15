#!/usr/bin/env python

import os

from setuptools import setup

# under test we do not want the nose entry point installed because it screws up
# coverage as the xtraceback module is imported too early
if "XTRACEBACK_NO_NOSE" in os.environ:
    entry_points = None
else:
    entry_points = {
        "nose.plugins": ("xtraceback=xtraceback.nosextraceback:NoseXTraceback",),
    }

README = open(os.path.join(os.path.dirname(__file__), "README.rst"))

setup(name="xtraceback",
      version="0.4.0-rc1",
      description="A verbose traceback formatter",
      long_description="\n".join(README.read().splitlines()[0:3]),
      license="MIT",
      keywords="traceback exception nose",
      author="Arthur Noel",
      author_email="arthur@0compute.net",
      url="https://github.com/0compute/xtraceback",
      packages=("xtraceback",),
      install_requires=("stacked == 0.1.2",),
      extras_require=dict(syntax=("pygments")),
      tests_require=("nose", "pygments", "yanc"),
      test_suite="nose.collector",
      entry_points=entry_points,
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Operating System :: POSIX",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.5",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.2",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: Implementation :: CPython",
          "Programming Language :: Python :: Implementation :: Jython",
      ],
      )
