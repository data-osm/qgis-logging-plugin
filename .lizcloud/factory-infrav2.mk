#
# Makefile for building/packaging qgis for lizmap hosting infra v2
#

ifndef FABRIC
FABRIC:=$(shell [ -e .fabricrc ] && echo "fab -c .fabricrc" || echo "fab")
endif

VERSION=$(shell ./metadata_key ../metadata.txt version)

main:
	echo "Makefile for packaging infra components: select a task"

PACKAGE=qgis3_logger
FILES = ../*.py ../metadata.txt ../README.md
PACKAGEDIR=qgis_logger

buildv2/$(PACKAGEDIR):
	@rm -rf buildv2/$(PACKAGEDIR)
	@mkdir -p buildv2/$(PACKAGEDIR)


.PHONY: package
package: build/$(PACKAGEDIR)
	@echo "Building package $(PACKAGE)"
	@cp -rLp $(FILES) buildv2/$(PACKAGEDIR)/
	$(FABRIC) package:qgis3_logger,versiontag=$(VERSION),files="qgis_logger",directory=./buildv2
