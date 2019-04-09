LIBDIR ?= usr/lib
DATADIR ?= usr/share

all:	#nothing to build

install:
	mkdir -p $(DESTDIR)/$(LIBDIR)/nagios-plugins-openshift
	for i in new-app-and-wait; do \
		sed -r \
			-e '1 s|^(#!/usr/bin/python)3$$|\13.4|' \
			< "$$i" \
			> "$(DESTDIR)/$(LIBDIR)/nagios-plugins-openshift/$$(basename "$$i")"; \
	done
	sed -r \
		-e 's#\b(OPENSHIFT_CLIENT_BINARY=)/usr/bin/oc\b#\1$(LIBDIR)/openshift-origin-client-tools/oc#' \
		< utils \
		> "$(DESTDIR)/$(LIBDIR)/nagios-plugins-openshift/utils"
	sed -r \
		-e 's#(^\. )/usr/lib(/nagios-plugins-openshift/utils)$$#\1$(LIBDIR)\2#g' \
		< write-config \
		> "$(DESTDIR)/$(LIBDIR)/nagios-plugins-openshift/write-config"
	chmod +x $(DESTDIR)/$(LIBDIR)/nagios-plugins-openshift/{utils,write-config,new-app-and-wait}
	mkdir -p $(DESTDIR)/$(LIBDIR)/nagios/plugins
	set -e && for i in check_*; do \
		echo "Patching $$i ..." >&2 && \
		sed -r \
			-e '1 s|^(#!/usr/bin/python)3$$|\13.4|' \
			-e 's#(^\. )/usr/lib(/nagios-plugins-openshift/utils)$$#\1$(LIBDIR)\2#g' \
			< "$$i" \
			> "$(DESTDIR)/$(LIBDIR)/nagios/plugins/$$(basename "$$i")"; \
	done
	chmod +x $(DESTDIR)/$(LIBDIR)/nagios/plugins/check_*
	mkdir -p $(DESTDIR)/$(DATADIR)/icinga2/include/plugins-contrib.d
	cp -v openshift*.conf $(DESTDIR)/$(DATADIR)/icinga2/include/plugins-contrib.d
