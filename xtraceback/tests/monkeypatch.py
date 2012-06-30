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
