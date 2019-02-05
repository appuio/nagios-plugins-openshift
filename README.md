# Nagios/Icinga plugins for monitoring OpenShift 3.x

This package provides Nagios-compatible plugins to verify the operation of
OpenShift clusters.


## Prerequisites

* Ubuntu 16.04 LTS
* `oc` binary

The plugins are tested with Icinga 2.5 or newer, but they should also work with
other consumers of Nagios-compatible plugins.


## Getting started

Install the plugins from our [Ubuntu
PPA](https://launchpad.net/~vshn/+archive/ubuntu/icinga), or build the Debian
packages from source.


## List of plugins

Each plugin has a list of parameters available using the argument `-h`.

### `check_hawkular_machine_timestamp`

Check whether the monitoring data in Hawkular has been updated recently.


### `check_openshift_cert_expiry_report`

Check status of all certificates managed and reported on by [OpenShift
Ansible](https://github.com/openshift/openshift-ansible/).


### `check_openshift_es_stats`

Collect statistics from Elasticsearch instance (i.e. part of the aggregated
logging system) with optional limits.


### `check_openshift_node`

Check status of a node within a cluster.


### `check_openshift_node_fluentd`

Check whether a [Fluentd](https://www.fluentd.org/) pod is running on every
machine.


### `check_openshift_node_list`

Check whether list of nodes in cluster matches passed list. Reports on
unexpected and missing nodes.


### `check_openshift_node_log_heartbeat`

Query Elasticsearch to determine whether node has recently submitted
timestamped log message to logging component.


### `check_openshift_node_resources`

Check whether node resources (CPU, memory) are within given limits.


### `check_openshift_object_stats`

Compute statistics on a number of cluster objects and apply given limits.


### `check_openshift_pod_count`

Check whether number of running pods for a given namespace and selector is
equal to or larger than expected.


### `check_openshift_pod_cpu_usage`

Retrieve and apply limits to CPU usage by pods. Requires the OpenShift metrics
component.


### `check_openshift_pod_memory`

Retrieve and apply limits to memory usage by pods. Requires the OpenShift
metrics component.


### `check_openshift_pod_node_alloc`

Check whether all pods matching given selector are running on disparate nodes.


### `check_openshift_pod_status_count`

Retrieve metrics over whole cluster for each recognized pod status, i.e.
`Running` or `CrashLoopBackOff`.


### `check_openshift_project_phase`

Check whether all projects are in a healthy status, i.e. `active`.


### `check_openshift_pv_avail`

Apply limits to number of available physical volumes for given selector or
capacity.


### `check_openshift_pvc_phase`

Check for unhealthy persistent volume claims.


## Contributions

Each contribution is very welcome--be it an issue or a pull request. We're
happy to accept pull requests so long as they meet the existing code quality
and design.

1. Fork repository (https://github.com/appuio/nagios-plugins-openshift/fork)
2. Create feature branch (`git checkout -b my-new-feature`)
3. Commit changes (`git commit -av`)
4. Push to branch (`git push origin my-new-feature`)
5. Create a pull request
