Summary: Monitoring scripts for OpenShift
Name: nagios-plugins-openshift
Version: 0.10.0
Release: 1
License: BSD-3-Clause
Source: .
URL: https://git.vshn.net/vshn/nagios-plugins-openshift
Vendor: VSHN AG
Packager: Michael Hanselmann <hansmi@vshn.ch>
BuildRequires: python34-devel

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
* Tue Jan 3 2017 Michael Hanselmann <hansmi@vshn.ch> 0.10.0-1
- Initial release for RedHat (only the Icinga configuration works)
