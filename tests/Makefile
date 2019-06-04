.PHONY: test
SHELL:=bash
#
# test plugin makefile
#

COMMITID=$(shell git rev-parse --short HEAD)

ifdef REGISTRY_URL
REGISTRY_PREFIX=$(REGISTRY_URL)/
endif

# Qgis version flavor
FLAVOR:=ltr

BECOME_USER:=$(shell id -u)

QGIS_IMAGE=$(REGISTRY_PREFIX)qgis-platform:$(FLAVOR)

LOCAL_HOME ?= $(shell pwd)

TITLE=qgis_logger

test:
	mkdir -p $$(pwd)/.local $(LOCAL_HOME)/.cache
	@echo PWD=$$(pwd)
	ls -al $$(pwd)
	docker run --rm --name $(TITLE)-test-$(COMMITID) -w /src \
		-u $(BECOME_USER) \
		-v $$(pwd):/src   \
		-v $$(realpath ..):/plugins/$(TITLE) \
		-v $$(pwd)/.local:/.local \
		-v $(LOCAL_HOME)/.cache:/.cache \
		-e PIP_CACHE_DIR=/.cache \
		-e PYTEST_ADDOPTS="$(PYTEST_ADDOPTS)" \
		$(QGIS_IMAGE) /src/run-tests.sh --qgis-plugins=/plugins

