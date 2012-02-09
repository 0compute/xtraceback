all: metrics docs

DIRS := .build .build/clonedigger
$(DIRS):
	mkdir -p $@

DEV_ENV = dev
DEV_ENV_PATH = .tox/$(DEV_ENV)
DEV_ENV_ACTIVATE = . $(DEV_ENV_PATH)/bin/activate

VENV_PATH = $(PWD)/$(DEV_ENV_PATH)
include Makefile.virtualenv

VENV_POST_CREATE = $(TOX) -e $(DEV_ENV)

TOX = tox --develop
TOX_ARGS = -- --stop

TEST_ENVS = $(shell grep envlist tox.ini | awk -F= '{print $$2}' | tr -d ,)

.PHONY: $(TEST_ENVS)
$(TEST_ENVS): .build
	$(TOX) -e $@ $(TOX_ARGS)

.PHONY: test
test: $(TEST_ENVS)

.PHONY: metrics
metrics: test $(VENV_ACTIVATE)
	$(call vmake,.metrics)

.PHONY: .metrics
.metrics: .build/clonedigger
	$(call assert-vmake)
	coverage combine
	coverage xml -o.build/coverage.xml
	coverage html
	-pylint --rcfile=.pylintrc -f parseable xtraceback > .build/pylint
	-pep8 --repeat xtraceback > .build/pep8
	clonedigger --cpd-output -o .build/clonedigger.xml xtraceback
	clonedigger -o .build/clonedigger/index.html xtraceback
	sloccount --wide --details xtraceback > .build/sloccount

.PHONY: doc
doc: .build/doc/index.html

.build/doc/index.html: $(VENV_ACTIVATE) $(shell find doc -type f)
	$(call vmake,.vdoc)

.vdoc:
	$(call assert-vmake)
	sphinx-build -W -b doctest doc .build/doc
#	sphinx-build -W -b spelling doc .build/doc
	sphinx-build -W -b coverage doc .build/doc
#	sphinx-build -W -b linkcheck doc .build/doc
	sphinx-build -W -b html doc .build/doc

.PHONY: publish
publish: doc
	 ./setup.py sdist register upload upload_sphinx

.PHONY: clean
clean:
	git clean -fdX
