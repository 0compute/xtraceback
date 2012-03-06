import logging
import os
import sys

from .somethingelse import SomethingElse


class Something(object):

    def one(self):
        sugar = max(1, 2)
        self.two(sugar)

    def two(self, sugar):
        long = "y" * 67
        obj = SomethingElse()
        obj.one(long)
