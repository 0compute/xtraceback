# imported so that they are in the global scope which we check in the tests
import logging
import os
import sys

from .other import Other


class Thing(object):

    def one(self):
        sugar = max(1, 2)
        self.two(sugar)

    def two(self, sugar):
        long = "y" * 67
        obj = Other()
        obj.one(long)
