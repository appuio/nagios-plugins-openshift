LIBDIR ?= usr/lib
DATADIR ?= usr/share

all:	#nothing to build

install:
	mkdir -p $(DESTDIR)/$(LIBDIR)/nagios-plugins-openshift
	cp new-app-and-wait "$(DESTDIR)/$(LIBDIR)/nagios-plugins-openshift/new-app-and-wait"
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
		sed -re 's#(^\. )/usr/lib(/nagios-plugins-openshift/utils)$$#\1$(LIBDIR)\2#g' \
			< "$$i" \
			> "$(DESTDIR)/$(LIBDIR)/nagios/plugins/$$(basename "$$i")"; \
	done
	chmod +x $(DESTDIR)/$(LIBDIR)/nagios/plugins/check_*
	mkdir -p $(DESTDIR)/$(DATADIR)/icinga2/include/plugins-contrib.d
	cp -v openshift*.conf $(DESTDIR)/$(DATADIR)/icinga2/include/plugins-contrib.d
