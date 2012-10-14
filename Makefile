###############################################################################
# Setup {{{
###

# these are the pythons we support
SUPPORTED_PYTHONS = python2.7 python2.6 python2.5 python3.1 python3.2 python3.3
ifndef FAST
# jython startup is not quick
SUPPORTED_PYTHONS += jython
endif

# reduce SUPPORTED_PYTHONS to PYTHONS by skipping unavailable interpreters
$(foreach python, $(SUPPORTED_PYTHONS), \
	$(if $(shell which $(python) 2>/dev/null && echo x), \
		$(eval PYTHONS += $(python))))
ifeq ($(PYTHONS),)
$(error No python interpreters available - supported are $(SUPPORTED_PYTHONS))
endif

# default for development
PYTHON_DEFAULT = python2.7

# this is the python interpreter used in this make invocation - it is overriden
# using recursive make when testing multiple python versions
PYTHON ?= $(PYTHON_DEFAULT)
ifeq ($(shell which $(PYTHON) 2>/dev/null || echo x),x)
$(error $(PYTHON) not available)
endif

# the environments that we test; the extras are tests for behaviour in the
# abscence of optional thirdparty libraries - they are not interpreter-specific
TEST_ENVS = $(PYTHONS) nopygments nonose

# set pip download cache if not already set so as to minimize network activity
export PIP_DOWNLOAD_CACHE ?= $(shell mktemp -d)

# where we put build artefacts
BUILD_DIR = .build

# this is used in setup.py to indicate that the nose entry point should not be
# installed - if it is installed for test it screws up coverage because the
# xtraceback module gets imported too early
export XTRACEBACK_NO_NOSE = 1

# using BASH_ENV to activate the virtualenv; this file is sourced on
# non-interactive startup meaning that every shell command runs inside the
# virtualenv (except when it is not yet created)
SHELL = /bin/bash
export BASH_ENV = $(VENV_ACTIVATE)

# }}}

###############################################################################
# Virtualenv {{{
###

VIRTUALENV_RELEASE = 1.7.2
VIRTUALENV_DIR = virtualenv-$(VIRTUALENV_RELEASE)
VIRTUALENV_ARCHIVE = $(VIRTUALENV_DIR).tar.gz
VIRTUALENV_URL = http://pypi.python.org/packages/source/v/virtualenv/$(VIRTUALENV_ARCHIVE)

# the downloaded virtualenv archive
VIRTUALENV_BUILD_ARCHIVE = $(BUILD_DIR)/$(VIRTUALENV_ARCHIVE)
$(VIRTUALENV_BUILD_ARCHIVE): | $(BUILD_DIR)
	cd $(BUILD_DIR) && curl -O $(VIRTUALENV_URL)

# the extracted virtualenv archive
VIRTUALENV_BUILD_DIR = $(BUILD_DIR)/$(VIRTUALENV_DIR)
$(VIRTUALENV_BUILD_DIR): | $(VIRTUALENV_BUILD_ARCHIVE)
	tar -C $(BUILD_DIR) -zxf $|

# the virtualenv script
VIRTUALENV = $(PYTHON_DEFAULT) $(VIRTUALENV_BUILD_DIR)/virtualenv.py --python=$(PYTHON)

# root path for virtualenvs
VENV_ROOT ?= .venv

# name of the virtualenv - this defaults to $(PYTHON) and is overridden for the
# non-interpreter tests
VENV_NAME ?= $(PYTHON)

# path to the virtualenv
VENV_PATH = $(VENV_ROOT)/$(VENV_NAME)

# virtualenv activate script
VENV_ACTIVATE = $(VENV_PATH)/bin/activate
$(VENV_ACTIVATE): | $(VIRTUALENV_BUILD_DIR)
	$(VIRTUALENV) $(abspath $(VENV_PATH))
	echo >> $@
	echo >> $@ '# xtraceback venv support used in Makefile'
	echo >> $@ export PYTHON=$(PYTHON)
	echo >> $@ export VENV_NAME=$(VENV_NAME)
	pip install --editable=.

# the virtualenv's site directory - jython has a different layout
ifeq ($(PYTHON),jython)
VENV_SITE = $(VENV_PATH)/Lib/site-packages
else
VENV_SITE = $(VENV_PATH)/lib/$(PYTHON)/site-packages
endif

# a pip requirements file
$(VENV_SITE)/%.pipreq:: requirements/%.pipreq $(VENV_ACTIVATE)
	pip install --requirement=$<
	cp $< $@

# the base requirements for the venv - anything that needs the venv must depend
# on this
VENV_REQUIREMENTS = $(VENV_SITE)/$(VENV_NAME).pipreq

# the virtualenv - this builds a virtualenv with "." installed and installs
# requirements for $(VENpython2.7V_NAME) if present
.PHONY: virtualenv
virtualenv:: $(VENV_REQUIREMENTS)

# the development environment
.PHONY: develop
develop: $(VENV_REQUIREMENTS) $(VENV_SITE)/development.pipreq

# }}}

###############################################################################
# Test Commands {{{
###

# the nonose test doesn't use nose so the test is just the below module
ifeq ($(VENV_NAME),nonose)

TEST_COMMAND = xtraceback/tests/test_plugin_import.py
COVERAGE_COMMAND = coverage run $(TEST_COMMAND)

else

# default test uses the nose test runner
TEST_COMMAND = $(PYTHON) $(VENV_PATH)/bin/nosetests

# fast excludes the below stdlib test because it has a 4 second sleep
ifdef FAST
TEST_COMMAND += --exclude=test_bug737473
endif

# specify tests to run using a make variable
ifdef TESTS
TEST_COMMAND += --tests=$(TESTS)
endif

# under jenkins write out a xunit report and supress nose failure since this is
# (likely) about a failing test not a failing build
ifdef JENKINS_HOME
TEST_COMMAND := -$(TEST_COMMAND) -v --with-xunit \
	--xunit-file=$(BUILD_DIR)/nosetests-$(VENV_NAME).xml
endif

# under travis the only thing we're doing is testing so a failing test is it
ifdef TRAVIS_PYTHON_VERSION
TEST_COMMAND += -v
else
# this controls a patch in xtraceback.tests.monkeypatch that disables the
# printing of a report after a test run - the report is not wanted anywhere
# except under travis
export COVER_NO_REPORT = 1
endif

COVERAGE_COMMAND = $(TEST_COMMAND) --with-coverage

endif

# add in user-supplied arguments for test command
ifdef ARGS
TEST_COMMAND += $(ARGS)
endif

# used to transform paths in .coverage files between relative and absolute
COVERAGE_TRANSFORM = $(PYTHON) xtraceback/tests/coverage_transform.py

# }}}

###############################################################################
# Test Execution {{{
###

.DEFAULT_GOAL = test
.PHONY: test
test: $(VENV_REQUIREMENTS)
	$(TEST_COMMAND)

# execute the coverage command then transform the latest .coverage file to
# relative paths - this is so that tests can be executed in different places
# with the coverage later combined
.PHONY: coverage
coverage: $(VENV_REQUIREMENTS)
	$(COVERAGE_COMMAND)
# FIXME: This is ugly and doesn't work in parallel
	$(COVERAGE_TRANSFORM) rel $$(ls -t .coverage.* | head -1)

# }}}

###############################################################################
# Metrics {{{
###

.PHONY: coverage-report
coverage-report: $(VENV_REQUIREMENTS)
	$(COVERAGE_TRANSFORM) abs .coverage.*
	coverage combine
	coverage html
ifdef JENKINS_HOME
	coverage xml -o$(BUILD_DIR)/coverage.xml
endif

.PHONY: metrics .metrics
metrics: coverage-report $(VENV_SITE)/metrics.pipreq $(BUILD_DIR)/clonedigger
	-pylint --rcfile=.pylintrc -f parseable xtraceback > $(BUILD_DIR)/pylint
	-pep8 --repeat xtraceback > $(BUILD_DIR)/pep8
	clonedigger -o $(BUILD_DIR)/clonedigger/index.html xtraceback > /dev/null 2>&1
ifdef JENKINS_HOME
	clonedigger --cpd-output -o $(BUILD_DIR)/clonedigger.xml xtraceback > /dev/null
endif
ifeq ($(shell which sloccount && echo x),x)
	sloccount --wide --details xtraceback > $(BUILD_DIR)/sloccount
endif

# }}}

###############################################################################
# Docs {{{
###

DOCS := $(shell find doc -type f)

$(BUILD_DIR)/doc/index.html: $(VENV_REQUIREMENTS) $(VENV_SITE)/docs.pipreq $(DOCS)
	sphinx-build -W -b doctest doc $(BUILD_DIR)/doc
	-sphinx-build -W -b spelling doc $(BUILD_DIR)/doc
	sphinx-build -W -b coverage doc $(BUILD_DIR)/doc
	sphinx-build -W -b linkcheck doc $(BUILD_DIR)/doc
	sphinx-build -W -b html doc $(BUILD_DIR)/doc

.PHONY: doc
doc: $(BUILD_DIR)/doc/index.html

# }}}

###############################################################################
# Recursive Virtualenv {{{
###

vmake_args = VENV_NAME=$(1) $(if $(findstring ython,$(1)),PYTHON=$(1))

# command for recursive make
SUBMAKE = @+$(MAKE) --no-print-directory

.PHONY: test-%
test-%:
	$(SUBMAKE) test $(call vmake_args,$*)

.PHONY: coverage-%
coverage-%:
	$(SUBMAKE) coverage $(call vmake_args,$*)

# execute all tests/coverages; errors are ignored in order that all
# environments are executed and this is suitable for parallel make
.PHONY: tests coverages
tests coverages: SUBMAKE := -$(SUBMAKE)
tests: $(addprefix test-,$(TEST_ENVS))
coverages: $(addprefix coverage-,$(TEST_ENVS))

# }}}

###############################################################################
# Developer {{{
###

# this is a safe operation and will only remove things ignored by git
.PHONY: clean
clean:
	git clean -fdX

.PHONY: printvars
printvars:
	$(foreach V,$(sort $(.VARIABLES)), \
		$(if $(filter-out environment% default automatic, $(origin $V)), \
			$(warning $V=$($V) ($(value $V)))))

# }}}

###############################################################################
# Release Management {{{
###

# TODO: this should all be handled by git
#CURRENT_VERSION = $(shell $(PYTHON) -c "import xtraceback; print xtraceback.__version__")

.PHONY: release
release:
	$(if $(VERSION),,$(error VERSION not set))
	git flow release start $(VERSION)
	sed -e "s/$(CURRENT_VERSION)/$(VERSION)/" -i setup.py xtraceback/__init__.py
	git commit -m "release $(VERSION)" setup.py xtraceback/__init__.py
	git flow release finish $(VERSION)
	git push --all
	git push --tags

.PHONY: publish
publish: doc
	./setup.py sdist register upload upload_sphinx

# }}}

# catchall for build directories
$(BUILD_DIR) $(BUILD_DIR)/%:
	mkdir $@
