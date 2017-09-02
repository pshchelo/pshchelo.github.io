#################################################################
Performance testing of Ansible-deploy driver for OpenStack Ironic
#################################################################

.. |date| date::

:date: 2017-09-01
:modified: |date|
:tags: ironic,ansible,deploy,testing
:category: openstack
:slug: ansible-deploy-perf
:lang: en
:authors: pas-ha
:summary: Comparative performance testing of ansible-deploy and agent ironic drivers
:status: draft

What and why are we testing
===========================

For more than a year me and my colleagues are developing and promoting a new
deploy driver interface for OpenStack ironic service.
Contrary to the standard ``direct`` or ``iscsi`` deploy interfaces that depend
on ``ironic-python-agent`` service (IPA) running in the deploy ramdisk,
this new ``ansible`` deploy interface is using Ansible to provision the node,
with the steps to execute during provisioning or cleaning defined as Ansible
playbooks/roles/tasks *etc*.

The current version of this driver interface is available as part of
``ironic-staging-driver`` project.
We are currently proposing to include this interface to the ironic project
itself.

One of the topics raised during discussions is a performance of this new driver
interface.
Different to the ``direct`` deploy interface that offloads most of the work
to be executed by IPA that runs on the node being provisioned,
this new interface involves executing code on the side of ironic-conductor
service, thus we were asked to show that the ``ansible`` deploy interface
can cope with deploying several node in parallel (50 at least) without severe
performance degradation on the side of ironic-conductor service.

Testbed
=======

We have deployed a minimal single host ironic installation as of 7.0.2 version
(Ocata release) using Mirantis Cloud Platform 1.1.
The Ansible-deploy interface was taken from ``ironic-staging-drivers`` project
as of stable/ocata branch.
The deployment also included OpenStack Identity (keystone)
and Networking (neutron) services, also of Ocata release.

The lab consisted of 4 baremetal nodes with the following relevant stats:

1x ironic node
  **CPU**: Intel(R) Xeon(R) CPU E5-2620, 32 cores,
  **RAM**: 32GB

3x enrolled into ironic
  **CPU**: Intel(R) Xeon(R) CPU E5-2650, 32 cores
  **RAM**: 64GB

We enrolled the 3 slave baremetal nodes in ironic,
deployed them with Ubuntu Xenial image,
created 100 VMs on each of them, and enrolled those to ironic using
``virtualbmc`` utility to simulate IPMI-capable hardware nodes.
This effectively gave us 300 ironic nodes to test deployment on.

Overall order of the test was the following:

#. ``pxe_ipmitool_ansible`` driver, deploy 50 nodes, repeat 3 times
#. ``agent_ipmitool driver``, deploy 50 nodes, repeat 3 times
#. ``agent_ipmitool driver``, deploy 100 nodes, repeat 3 times
#. ``pxe_ipmitool_ansible`` driver, deploy 100 nodes, repeat 3 times

Concurrent deployment was done via trivial bash script calling ironic client
commands in a ``for`` loop.
For each iteration "virtual" nodes to be provisioned were chosen
to be equally distributed between real baremetal nodes
to decrease possible congestion.

Monitoring was performed with Cacti, with results presented and discussed below.

Results and discussion
======================

Nodes per driver
----------------

These graphs simply show the number of nodes registered per each driver
to set time frame reference for further graphs.

.. image:: {filename}/images/ansible-deploy-performance/node-by-driver.png
   :align: center
   :alt: Nodes per driver, batches of 50

.. image:: {filename}/images/ansible-deploy-performance/node-by-driver100.png
   :align: center
   :alt: Nodes per driver, total (batches of 50 and 100)

And we immediately see one of the troubles we stumbled upon - the dips in the
second graph around 10:35 and 11:30.
These graphs were plotted by Cacti periodically polling the ironic API
for number of nodes - and at these points requests simply timed out.
It happened for both drivers, so we tend to attribute this to the fact that
ironic API was running as the **eventlet sever** instead of WSGI behind a more
robust webserver (Note that running ironic as WSGI app was not yet officially
supported in Ocata release).

Number of active nodes
------------------------

.. image:: {filename}/images/ansible-deploy-performance/ironic-nodes.png
   :align: center
   :alt: Active vs being deployed nodes, batches of 50

.. image:: {filename}/images/ansible-deploy-performance/ironic-nodes100.png
   :align: center
   :alt: Active vs being deployed nodes, total (batches of 50 and 100)

Ironic host performance stats
-----------------------------

Batches of 50
~~~~~~~~~~~~~

CPU usage
   .. image:: {filename}/images/ansible-deploy-performance/cpu-usage.png
      :align: center
      :alt: CPU usage, batches of 50

Load average
   .. image:: {filename}/images/ansible-deploy-performance/load-average.png
      :align: center
      :alt: System load, batches of 50

Memory usage
   .. image:: {filename}/images/ansible-deploy-performance/memory-usage.png
      :align: center
      :alt: Memory usage, batches of 50

TCP counters
   .. image:: {filename}/images/ansible-deploy-performance/tcp-counters.png
      :align: center
      :alt: TCP counters, batches of 50



Overall test (both 50 and 100 batches)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
CPU usage
   .. image:: {filename}/images/ansible-deploy-performance/cpu-usage100.png
      :align: center
      :alt: CPU usage, total (batches of 50 and 100)

Load average
   .. image:: {filename}/images/ansible-deploy-performance/load-average100.png
      :align: center
      :alt: System load, total (batches of 50 and 100)

Memory usage
   .. image:: {filename}/images/ansible-deploy-performance/memory-usage100.png
      :align: center
      :alt: Memory usage, total (batches of 50 and 100)

TCP counters
   .. image:: {filename}/images/ansible-deploy-performance/tcp-counters100.png
      :align: center
      :alt: TCP counters, total (batches of 50 and 100)

Conclusion
==========
