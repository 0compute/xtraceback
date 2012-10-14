from .cases import WrappedStdlibTestMixin

from test_support import test_traceback

STDLIB_CASES = (
    "TracebackCases",  # 2
    "TracebackFormatTests",  # >= 2.6
    "SyntaxTracebackCases",  # 3
    "PyExcReportingTests",  # 3
    )

# wrap test cases from stdlib's test.test_traceback so that they execute in
# the contect of TracebackCompat
if test_traceback is not None:

    for case in STDLIB_CASES:
        case_cls = getattr(test_traceback, case, None)
        if case_cls is not None:
            test_name = "TestStdlib%s" % case
            locals()[test_name] = type(test_name,
                                       (WrappedStdlibTestMixin, case_cls),
                                       {})
