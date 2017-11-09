#
# Makefile for building/packaging qgis infra components
#

ifndef FABRIC
FABRIC:=$(shell [ -e .fabricrc ] && echo "fab -c .fabricrc" || echo "fab") 
endif

VERSION=$(shell python metadata.py src/qgis_logger/metadata.txt version)

main:
	echo "Makefile for packaging infra components: select a task"

FILES=qgis_logger wfsOutputExtension

package:
	$(FABRIC) package:qgis_logger,versiontag=$(VERSION),files="$(FILES)",directory=./src 

