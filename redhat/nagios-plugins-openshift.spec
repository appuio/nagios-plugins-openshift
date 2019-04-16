Summary: Monitoring scripts for OpenShift
Name: nagios-plugins-openshift
Version: 0.17.6
Release: 1
License: BSD-3-Clause
Source: .
URL: https://github.com/appuio/nagios-plugins-openshift
Vendor: VSHN AG
Packager: Michael Hanselmann <hansmi@vshn.ch>
BuildRequires: python34-devel
Requires: bash
Requires: curl >= 7.21.3
Requires: nagios-plugins-dns
Requires: openshift-origin-client-tools >= 3.7.2
Requires: jq >= 1.5
Requires: python34
Requires: python3-nagiosplugin >= 1.2
Requires: python34-requests >= 2.12
Requires: python34-urllib3 >= 1.13
Requires: python34-dateutil

%define __python3 /usr/bin/python3.4

%package config
Requires: icinga2, nagios-plugins-sudo-config
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
* Tue Apr 16 2019 Michael Hanselmann <hansmi@vshn.ch> 0.17.6-1
- check_openshift_es_stats:
  - Gather cluster-wide statistics and allow application of limits.

* Tue Apr 9 2019 Michael Hanselmann <hansmi@vshn.ch> 0.17.5-2
- Patch Python programs to explicitly invoke "/usr/bin/python3.4" instead of
  "/usr/bin/python3" to handle differences in the installed default Python
  version.

* Fri Mar 29 2019 Michael Hanselmann <hansmi@vshn.ch> 0.17.5-1
- check_openshift_es_stats:
  - Use Elasticsearch instance name as metric suffix.
  - Strip "logging-es-data-master-" and "logging-es-" prefixes from instance
    name.

* Thu Mar 21 2019 Michael Hanselmann <hansmi@vshn.ch> 0.17.4-1
- check_openshift_object_stats:
  - Return "OK" status when there are no metrics.

* Wed Feb 6 2019 Michael Hanselmann <hansmi@vshn.ch> 0.17.3-1
- check_openshift_object_stats:
  - Output only metrics with defined limits or an unhealthy status.

* Tue Feb 5 2019 Michael Hanselmann <hansmi@vshn.ch> 0.17.2-1
- check_openshift_object_stats:
  - Add verbose mode for easier debugging.
  - Compute more statistics for cron jobs.

* Thu Jan 31 2019 Michael Hanselmann <hansmi@vshn.ch> 0.17.1-1
- check_openshift_object_stats: Support additional "-n" parameter to specify
  namespace. By default objects from all namespaces are retrieved.

* Tue Jan 29 2019 Michael Hanselmann <hansmi@vshn.ch> 0.17.0-1
- check_openshift_object_stats: New plugin to compute object statistics based
  on "check_openshift_project_pod_phase". The latter will be removed in an
  upcoming version.

* Mon Dec 17 2018 Michael Hanselmann <hansmi@vshn.ch> 0.16.0-1
- Switch from custom "sudo" check command wrapper to
  "nagios-plugins-sudo-config" package.

* Wed Dec 5 2018 Michael Hanselmann <hansmi@vshn.ch> 0.15.4-1
- new-app-and-wait:
  - Collect more logs on completion (regardless of failure).

- pv_avail:
  - Changed terminology for volumes with undefined storage class from "default
    class" to "without storage class".

* Fri Nov 23 2018 Michael Hanselmann <hansmi@vshn.ch> 0.15.3-1
- pod_node_alloc:
  - Changed decision logic to only complain if either >50% or >3 of pods are on
    a single node. This way three-replica deployments are considered okay if
    they have two pods on a single node.

* Thu Nov 15 2018 Michael Hanselmann <hansmi@vshn.ch> 0.15.2-1
- node_log_heartbeat:
  - Change part of the Elasticsearch filter from "term" to "match" query to
    support differences in fields between OpenShift Origin 3.9 and OpenShift
    Container Platform 3.9.

* Wed Nov 14 2018 Michael Hanselmann <hansmi@vshn.ch> 0.15.1-1
- node_log_heartbeat:
  - Add unit-of-measurement to metrics
  - Emit log timestamps as metrics

* Mon Nov 12 2018 Michael Hanselmann <hansmi@vshn.ch> 0.15.0-1
- Removed "logging-wrapper" script as it didn't work on RHEL/CentOS.
- Added new script named "check_openshift_node_log_heartbeat" to check
  Elasticsearch for recent timestamp written to logs on all nodes.

* Mon Aug 6 2018 Michael Hanselmann <hansmi@vshn.ch> 0.14.3-1
- project_pod_phase:
  - Metric descriptions have been amended with more details.
- new-app-and-wait:
  - Client and server versions are output for logging.
  - Deployment logs are collected before project removal.
  - Avoid triggering deployment explicitly ("oc deploy") and rely on default
    triggers instead.
  - Only projects with configured prefix ("e2e" by default) are removed, not
    all visible to the end-to-end test user.

* Tue Jun 19 2018 Michael Hanselmann <hansmi@vshn.ch> 0.14.2-1
- Fix a bug introduced in version 0.14.1: Selector arguments for check commands
  were silently skipped. Only a warning was logged.

* Mon Jun 18 2018 Michael Hanselmann <hansmi@vshn.ch> 0.14.1-1
- Icinga check command "openshift_node_resources": Replace lambdas in "skip_if"
  with direct access to runtime macros. Now arguments are passed onto the check
  script even if they're not a string.

* Fri May 4 2018 Michael Hanselmann <hansmi@vshn.ch> 0.14.0-1
- check_openshift_pv_avail: The selector options "-l" and "-s" now support an
  optional storage class, separated from the value by a comma. To retain the
  existing selection behaviour they apply to all classes by default. Metrics
  are grouped by storage class and storage classes are included in
  human-readable output.
- check_openshift_pvc_phase: Show the storage class for pending and lost volume
  claims. Fail with a critical state when a claim is older than an hour.
- Fix typo in "openshift_pod_count" command definition: the
  "openshift_pod_count_crit" Icinga2 variable would overwrite the parameter for
  setting the warning limit.

* Fri Apr 27 2018 Michael Hanselmann <hansmi@vshn.ch> 0.13.1-1
- Expose count over all pod phases in "check_openshift_project_pod_phase" as
  Icinga2 variable.

* Thu Apr 26 2018 Michael Hanselmann <hansmi@vshn.ch> 0.13.0-1
- Add "check_openshift_project_pod_phase" script to observe pod phase (pending,
  running, etc.) of all pods on a cluster.

* Wed Apr 4 2018 Michael Hanselmann <hansmi@vshn.ch> 0.12.4-1
- new-app-and-wait: The upstream code for "oc new-app" can leave a clone of the
  application source behind in a temporary directory. Explicitly specify
  a temporary directory which is then removed by the wrapper code.

* Tue Apr 3 2018 Michael Hanselmann <hansmi@vshn.ch> 0.12.3-1
- check_openshift_pvc_phase: Show requested size, volume name and bound
  capacity for pending and lost claims.

* Thu Mar 22 2018 Michael Hanselmann <hansmi@vshn.ch> 0.12.2-1
- Install "new-app-and-wait" script.
- Update openshift-origin-client-tools dependency to require version 3.7.2 or
  newer.

* Mon Mar 5 2018 Michael Hanselmann <hansmi@vshn.ch> 0.12.1-1
- check_openshift_node_fluentd: Check all nodes, not only those marked
  schedulable

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
