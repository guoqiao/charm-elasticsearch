#!/usr/bin/make
PYTHON := /usr/bin/env python

build: sync-charm-helpers test

lint:
	@flake8 --exclude hooks/charmhelpers --ignore=E125 hooks
	@flake8 --exclude hooks/charmhelpers --ignore=E125 unit_tests
	@charm proof

test:
	@echo Starting unit tests...
	@PYTHONPATH=./hooks $(PYTHON) /usr/bin/nosetests3 --nologcapture unit_tests

deploy:
	@echo Deploying local elasticsearch charm
	@juju deploy --num-units=2 --repository=../.. local:trusty/elasticsearch


# The following targets are used for charm maintenance only.
bin/charm_helpers_sync.py:
	@bzr cat lp:charm-helpers/tools/charm_helpers_sync/charm_helpers_sync.py \
		> bin/charm_helpers_sync.py

sync-charm-helpers: bin/charm_helpers_sync.py
	@$(PYTHON) bin/charm_helpers_sync.py -c charm-helpers.yaml

