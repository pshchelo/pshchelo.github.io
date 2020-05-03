#################################################
Graphical VNC console in ironic - early prototype
#################################################

:date: 2016-12-12
:tags: ironic, vnc, drac
:category: work
:slug: vnc-in-ironic
:summary: enabling VNC access to nova instances deployed to ironic baremetal nodes

In integrated case (working as part of OpenStack deployment) nova instances
deployed on ironic baremetal nodes have certain limitations compared to
standard virtual machines created by nova.
In particular it is not currently possible to access the graphical console
of such instance for example via horizon Dashboard.

This is about to change with ironic community starting to work [#]_
on introducing a framework for graphical console access for baremetal nodes.
As each hardware vendor implements a different way to provide graphical
console access, the framework is planned to be quite generic,
leaving details of actual graphical console configuration and management
to a proposed GraphicalConsole interface of an ironic driver.

One interesting hardware to consider in this regard is Dell servers supporting
iDRACv7 or newer [#]_.
The iDRAC firmware on such servers supports native access to the server’s
graphical console over OpenVNC-compatible protocol directly,
without a need of proprietary VNC proxies or clients.
An administrator who has appropriate access to the iDRAC configuration can
enable this built-in VNC server and set the password, connection timeout and
SSL encryption options.

In order to test the VNC capabilities of such hardware I have implemented
a prototype [#]_ of a graphical console interface for the DRAC driver.
It uses WS-MAN HTTP API (as the rest of DRAC-specific driver interfaces)
to toggle the VNC server feature on and off and set its properties.
I have also created a prototype [#]_ of ``get_vnc_console`` method for ironic
virt-driver in nova.
As a result, I was able to get access to the graphical console in
horizon Dashboard for the nova instance deployed on top of Dell R630 server
managed by ironic.

.. image:: {static}/images/ironic-vnc-console-files/bm-vnc-console-in-horizon.png
   :align: center
   :width: 100%
   :alt: Screenshot of a VNC console of the baremetal node in horizon Dashboard

Lessons learned
===============

Of course no prototype is complete and without any bugs/problems discovered
during testing.
Here is what I’ve been hitting my head and hacking around while making
this to work:

Prototype limitations
---------------------

* This prototype is done prior to the generic graphical console framework
  implementation done in ironic.
  Thus the prototype implementation is for now overriding the existing serial
  console interface in a specifically created for this purpose ironic driver.
  That means currently it is not possible to have both serial console
  and graphical console.

  Conveniently though, the proposed base GraphicalConsole interface will have
  the same API as the current Console (SerialConsole in the future) interface.
  This means that once the generic framework for graphical console interfaces
  is implemented in ironic, this prototype can be plugged as graphical
  console interface basically as-is.

* The interface implementation is using low-level WS-MAN Python client calls
  for now since support for managing iDracCardService is yet lacking
  from python-dracclient.
  The work to enable this functionality is already ongoing in the community
  though.

* The ironic virt-driver changes are rather specific for this particular case
  to let me quickly test this functionality.
  It will be changed after the generic graphical console is implemented in
  Ironic and required complementary functionality is available in
  python-ironicclient.

iDrac VNC limitations
---------------------

* OpenVNC implementation in iDRAC does not seem to be complete as noVNC can
  not properly connect to it resulting in an apparently connected console
  with no graphical output [#]_.
  A single passed encoding parameter must be disabled in noVNC code.
  I had to resort to noVNC patched accordingly, but the implications of such
  patch on access to standard VM graphical console are yet to be tested.

* Password must be set on the VNC server as noVNC can not connect to it
  otherwise.
  It seems setting the password for the iDRAC VNC server to None/empty string
  still results in VNC server requesting a password on connection,
  but noVNC can not accept an empty password in its password prompt.
  I am not sure if this should be considered a bug in iDRAC VNC server or
  in noVNC.

* I have not tested yet how iDRAC VNC server works with noVNC when SSL is
  enabled in iDRAC VNC Server.

* The iDRAC VNC server is limited to a single VNC session at a time,
  so it is not really multi-user setup.
  On the other hand this still might suffice for undercloud-like use cases
  such as TrippleO.

* Note that in the current prototype, all nodes running nova-novncproxy
  service (or the single one specified as ``vncserver_proxyclient_address``
  in config for nova-compute with ironic virt-driver) must effectively have
  access to the BMC network as the built-in iDRAC VNC server is serving from
  its own BMC IP address.
  Care has to be taken to setup such proxying securely in a clustered nova
  deployment.

Nevertheless, this seems like an interesting and promising development on
the hardware market.
I consider it as yet another small step on the way forward to close the gap
between baremetal and virtual servers in OpenStack and enable a unified user
experience for compute service.

References
----------

.. [#] https://review.openstack.org/#/c/306074/
.. [#] http://en.community.dell.com/cfs-file/__key/telligent-evolution-components-attachments/13-4491-00-00-20-44-10-34/AccessingRemoteDesktop_5F00_using_5F00_VNC_5F00_on_5F00_iDRAC.pdf
.. [#] https://review.openstack.org/#/c/396661/
.. [#] https://review.openstack.org/#/c/398270/
.. [#] https://github.com/kanaka/noVNC/issues/712
