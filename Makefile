TOPDIR := $(shell /bin/pwd)
VERSION := $(shell cat VERSION)
PACKAGENAME = "customproperties"
PACKAGEDIR = "CustomProperties"
distclean:
	find . -iname "*.pyc" -o -iname "*.tar.gz" -o -iname "*~" | xargs -r rm -f

disttarball: distclean
	cd $(TOPDIR)/..; \
	tar cvfz $(TOPDIR)/${PACKAGENAME}-$(VERSION).tar.gz ./${PACKAGEDIR}
