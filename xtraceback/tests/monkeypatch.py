# patch nose coverage module to stop it writing a report to screen
try:
    from nose.plugins.cover import Coverage
except ImportError:
    pass
else:
    def report(self, stream):
        self.coverInstance.stop()
        self.coverInstance.save()
    Coverage.report = report

# use unittest2 instead of unitest if its installed
try:
    import unittest2
except ImportError:
    pass
else:
    import sys
    sys.modules["unittest"] = unittest2
