Summary: Monitoring scripts for OpenShift
Name: nagios-plugins-openshift
Version: 0.12.0
Release: 1
License: BSD-3-Clause
Source: .
URL: https://github.com/appuio/nagios-plugins-openshift
Vendor: VSHN AG
Packager: Michael Hanselmann <hansmi@vshn.ch>
BuildRequires: python34-devel
Requires: bash
Requires: curl >= 7.21.3
# TODO: daemontools for end-to-end tests (systemd unit?)
Requires: nagios-plugins-dns
Requires: openshift-origin-client-tools >= 3.6
Requires: jq >= 1.5
Requires: python34
Requires: python3-nagiosplugin >= 1.2
Requires: python34-requests >= 2.12
Requires: python34-urllib3 >= 1.13
Requires: python34-dateutil

%package config
Requires: icinga2, sudo
Summary: Icinga2 check command definitions for nagios-plugins-openshift
Group: Applications/System

%description
Nagios-compatible scripts for checking OpenShift

%description config
Icinga2 check command definitions for nagios-plugins-openshift

%prep
%setup -cT
cp -v -R -a %SOURCE0/* .

%build
sed -i -re 's#^(DEFAULT_OC_BINARY[[:blank:]]*=[[:blank:]]*).*$#\1"%{_libdir}/openshift-origin-client-tools/oc"#' \
  vshn_npo/constants.py
%py3_build
make 'LIBDIR=%{_libdir}' 'DATADIR=%{_datadir}'

%install
%py3_install
%make_install 'LIBDIR=%{_libdir}' 'DATADIR=%{_datadir}'

%files
%{_libdir}/nagios-plugins-openshift/*
%{_libdir}/nagios/plugins/check_*
%{python3_sitelib}/*

%files config
%{_datadir}/icinga2/include/plugins-contrib.d/*.conf

%changelog
* Fri Feb 9 2018 Michael Hanselmann <hansmi@vshn.ch> 0.12.0-1
- Initial version with most checks working on CentOS and RHEL.

* Tue Jul 4 2017 Michael Hanselmann <hansmi@vshn.ch> 0.11.4-1
- List remaining days in output of "check_openshift_cert_expiry_report".

* Mon Jul 3 2017 Michael Hanselmann <hansmi@vshn.ch> 0.11.7-1
- Add "check_openshift_cert_expiry_report" to evaluate result of
  openshift-ansible certificate report.

* Tue Jan 3 2017 Michael Hanselmann <hansmi@vshn.ch> 0.10.0-1
- Initial release for RedHat (only the Icinga configuration works)

# vim: set sw=2 sts=2 et :
