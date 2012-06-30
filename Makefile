###############################################################################
# Setup {{{
###

# using BASH_ENV to activate the virtualenv; this file is sourced on
# non-interactive startup
SHELL = /bin/bash
export BASH_ENV = $(VENV_ACTIVATE)

# development environment uses python 2.7, this variable is overriden using
# recursive make testing other pythons
PYTHON = python2.7
ifeq ($(shell which $(PYTHON) 2>/dev/null || echo x),x)
$(error $(PYTHON) not available)
endif

# these are the pythons we support
PYTHONS = jython python2.5 python2.6 python2.7

# build directory
BUILD_DIR = .build
$(BUILD_DIR):
	mkdir $@

# set pip download cache if not set already otherwise each test env will
# re-download
ifndef PIP_DOWNLOAD_CACHE
export PIP_DOWNLOAD_CACHE = $(shell mktemp -d)
endif

# }}}

###############################################################################
# Virtualenv {{{
###

VIRTUALENV_RELEASE = 1.7.2
VIRTUALENV_DIR = virtualenv-$(VIRTUALENV_RELEASE)
VIRTUALENV_BUILD_DIR = $(BUILD_DIR)/$(VIRTUALENV_DIR)
VIRTUALENV_ARCHIVE = $(VIRTUALENV_DIR).tar.gz
VIRTUALENV_BUILD_ARCHIVE = $(BUILD_DIR)/$(VIRTUALENV_ARCHIVE)
VIRTUALENV_URL = http://pypi.python.org/packages/source/v/virtualenv/$(VIRTUALENV_ARCHIVE)

VIRTUALENV = $(PYTHON) $(VIRTUALENV_BUILD_DIR)/virtualenv.py $(VIRTUALENV_ARGS)

VENV_ROOT ?= .venv
VENV_PATH = $(VENV_ROOT)/$(PYTHON)
VENV_ACTIVATE = $(VENV_PATH)/bin/activate

VENV_SITE = $(VENV_PATH)/lib/$(PYTHON)/site-packages
ifeq ($(PYTHON),jython)
# XXX: jython has a different site-packages - is there a portable way to get
# this from python itself?
VENV_SITE = $(VENV_PATH)/Lib/site-packages
endif

VENV_REQUIREMENTS = development

$(VIRTUALENV_BUILD_ARCHIVE): | $(BUILD_DIR)
	cd $(BUILD_DIR) && curl -O $(VIRTUALENV_URL)

$(VIRTUALENV_BUILD_DIR): | $(VIRTUALENV_BUILD_ARCHIVE)
	tar -C $(BUILD_DIR) -zxf $|

$(VENV_ACTIVATE): | $(VIRTUALENV_BUILD_DIR)
	$(VIRTUALENV) $(abspath $(VENV_PATH))
	pip install --editable=.

$(VENV_SITE)/%.pipreq: requirements/%.pipreq
	pip install --requirement=$<
	cp $< $@

.PHONY: virtualenv
ifeq ($(VENV_REQUIREMENTS),)
virtualenv: $(VENV_ACTIVATE)
else
virtualenv: $(VENV_ACTIVATE) $(VENV_SITE)/$(VENV_REQUIREMENTS).pipreq
endif

# }}}

###############################################################################
# Basic Test {{{
###

# this is used in setup.py to indicate that the nose entry point should not be
# installed - if it is installed for test it screws up coverage because the
# xtraceback module gets imported too early
export XTRACEBACK_NO_NOSE = 1

# nose test runner
NOSETESTS = nosetests

# args passed to nose test
NOSE_ARGS ?=

# under jenkins write out a xunit report and supress nose failure since this is
# (likely) about a failing test not a failing build
ifdef JENKINS_HOME
NOSE_ARGS += --with-xunit --xunit-file=$(BUILD_DIR)/nosetests-$@.xml
NOSETESTS := -$(NOSETESTS)
endif

# run tests under current virtualenv
.DEFAULT_GOAL := test
.PHONY: test
test: virtualenv
	$(NOSETESTS) $(NOSE_ARGS)

# run coverage under current virtualenv
.PHONY: coverage
coverage: virtualenv
	-$(NOSETESTS) --with-coverage $(NOSE_ARGS)

# }}}

###############################################################################
# Test Environments {{{
###

SUBMAKE = +$(MAKE) --no-print-directory

# test without pygments
.PHONY: nopygments
nopygments:
	$(SUBMAKE) coverage VENV_PATH=$(VENV_ROOT)/nopygments VENV_REQUIREMENTS=nopygments

# test import without nose
.PHONY: nonose
nonose:
	$(SUBMAKE) virtualenv VENV_PATH=$(VENV_ROOT)/nonose VENV_REQUIREMENTS=
	$(PYTHON) -c "import xtraceback.nosextraceback"

# test supported python versions
.PHONY: $(PYTHONS)
$(PYTHONS):
	$(SUBMAKE) coverage PYTHON=$@ VENV_REQUIREMENTS=test

# build up list of all test targets
# appended
TEST_ENVS = nopygments nonose
$(foreach python, $(PYTHONS), \
	$(if $(shell which $(python) 2>/dev/null && echo x), \
		$(eval TEST_ENVS := $(python) $(TEST_ENVS))))

# run all the tests
.PHONY: tests
tests: $(TEST_ENVS)

# }}}

###############################################################################
# Metrics
###

.PHONY: coverage-report
coverage-report: virtualenv
	coverage combine
	coverage html
ifdef JENKINS_HOME
	coverage xml -o$(BUILD_DIR)/coverage.xml
endif

.PHONY: metrics .metrics
metrics: virtualenv
	-pylint --rcfile=.pylintrc -f parseable xtraceback > $(BUILD_DIR)/pylint
	-pep8 --repeat xtraceback > $(BUILD_DIR)/pep8
	mkdir -p $(BUILD_DIR)/clonedigger && clonedigger \
		-o $(BUILD_DIR)/clonedigger/index.html xtraceback > /dev/null 2>&1
ifdef JENKINS_HOME
	clonedigger --cpd-output -o $(BUILD_DIR)/clonedigger.xml xtraceback > /dev/null
endif
ifeq ($(shell which sloccount 2>/dev/null && echo x),x)
	sloccount --wide --details xtraceback > $(BUILD_DIR)/sloccount
endif

# }}}

###############################################################################
# Developer Targets {{{
###

$(BUILD_DIR)/doc/index.html: virtualenv $(shell find doc -type f)
	sphinx-build -W -b doctest doc $(BUILD_DIR)/doc
	sphinx-build -W -b spelling doc $(BUILD_DIR)/doc
	sphinx-build -W -b coverage doc $(BUILD_DIR)/doc
	sphinx-build -W -b linkcheck doc $(BUILD_DIR)/doc
	sphinx-build -W -b html doc $(BUILD_DIR)/doc

.PHONY: doc
doc: $(BUILD_DIR)/doc/index.html

.PHONY: everything
everything: tests coverage-report metrics doc

# TODO: this should all be handled by git
CURRENT_VERSION = $(shell $(PYTHON) -c "import xtraceback; print xtraceback.__version__")

.PHONY: release
release:
	$(if $(VERSION),,$(error VERSION not set))
	git flow release start $(VERSION)
	sed -e "s/$(CURRENT_VERSION)/$(VERSION)/" -i setup.py
	sed -e "s/$(CURRENT_VERSION)/$(VERSION)/" -i xtraceback/__init__.py
	git commit -m "version bump" xtraceback/__init__.py
	git flow release finish $(VERSION)
	git push --all
	git push --tags

.PHONY: publish
publish: doc
	./setup.py sdist register upload upload_sphinx

# this is a safe operation and will only remove things ignored by git
.PHONY: clean
clean:
	git clean -fdX

# }}}
