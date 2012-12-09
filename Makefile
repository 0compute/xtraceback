MAKEENV_MODULES = *
include .makeenv/makeenv.mak

ENVIRONMENTS += nopygments nonose

ifdef FAST
# jython startup is not quick
# FIXME: see end of multienv makefile
SUPPORTED_PYTHONS := $(subst jython,,$(SUPPORTED_PYTHONS))
# fast excludes the below stdlib test because it has a 4 second sleep
TEST_COMMAND += --exclude=test_bug737473
endif

# jython may be a shell script wrapper that uses unset variables
ifeq ($(PYTHON),jython)
	SHELLOPTS := $(subst,:nounset,,$(SHELLOPTS))
endif

# the nonose test doesn't use nose (obviously?) so we override the test and
# coverage commands
ifeq ($(VIRTUAL_ENV_NAME),nonose)
TEST_COMMAND = xtraceback/tests/test_plugin_import.py
COVERAGE_COMMAND = $(COVERAGE_CLI) run $(TEST_COMMAND)
else
# xtraceback is added by makeeenv to the test command options but we don't
# want to use it for self
TEST_COMMAND := $(subst --with-xtraceback,,$(TEST_COMMAND))
endif

# this is used in setup.py to indicate that the nose entry point should not be
# installed - if it is installed for test it screws up coverage because the
# xtraceback module gets imported too early
export XTRACEBACK_NO_NOSE = 1
