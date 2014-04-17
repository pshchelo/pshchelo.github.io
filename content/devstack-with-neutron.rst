How to set DevStack with Neutron
################################

:date: 2014-04-15
:tags: devstack, openstack
:category: work
:slug: devstack-with-neutron
:summary: tips and tricks on setting DevStack

These tips try to solve problems I stumbled upon when starting my work
on OpenStack, Grizzly release at that time. I've tried to accommodate
the solutions for recent DevStack (late Icehouse/early Juno as of this
writing), but some things might still be incorrect or already fixed -
YMMV.

Install DevStack
================

-  Prepare a VM for DevStack deployment (e.g. Ubuntu 12.04 LTS server)
-  in this VM install ``git`` (assuming Ubuntu/Debian)

   ::

       sudo apt-get install git

-  clone DevStack repo

   ::

       git clone https://github.com/openstack-dev/devstack.git

-  create ``local.conf`` file in the ``devstack`` folder to enable
   Neutron and set some passwords (choose your own if you wish)

   ::

       [[local|localrc]]
       DATABASE_PASSWORD=password
       RABBIT_PASSWORD=password
       SERVICE_TOKEN=password
       SERVICE_PASSWORD=password
       ADMIN_PASSWORD=password
       disable_service n-net
       enable_service q-svc q-agt q-dhcp q-l3 q-meta neutron

   -  I have a `repo <https://github.com/pshchelo/stackdev>`__ with some
      standard DevStack customizations ready, you migh want to check it
      out too.

-  install DevStack

   ::

       ./stack.sh

Now you should have a working DevStack installation. You can login into
Horizon, or join the runnig stack with ``./rejoin_stack.sh`` command.
There are some networks and routers pre-created by DevStack, so you can
start VMs and attach floating IPs to them.

You can ping VMs from DevStack host by both their private and public
IPs, and ping between VMs inside one tenant (probably you have to edit
security groups first to allow ICMP traffic).

The only problem - your launched VMs might not access wide Internet or
be accessed from Internet.

Allow VM Internet connectivity
==============================

after `this launchpad
question <https://answers.launchpad.net/neutron/+question/208377>`__

-  enable ipv4 forwarding

   ::

       sudo sysctl net.ipv4.ip_forward = 1

-  configure ``iptables`` to pass through the traffic

   ::

       sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

-  Manually assign public bridge to public interface (assuming it is
   ``eth0``):

   -  get the ip address of the eth0

      ::

          ip addr show eth0

   -  flush the IP on this interface

      ::

          sudo ip addr flush dev eth0

   -  flush the IP on the public bridge (assuming it is ``br-ex``)

      ::

          sudo ip addr flush dev br-ex

   -  bring up the public bridge

      ::

          sudo ip link set br-ex up

   -  assign the public IP to the public bridge

      ::

          sudo ip addr add $PUBLIC_IP dev br-ex

   -  attach the public interface to the public bridge

      ::

          sudo ovs-vsctl add-port br-ex eth0

Permanent settings
==================

After reboot of the DevStack VM the following will be lost:

-  iptables NAT setting
-  stack volume (this includes created storage volumes etc)

Here how to make these settings permanent:

NAT settings
------------

after `this mail-list
post <https://lists.launchpad.net/openstack/msg17016.html>`__

-  permanently enable ip-forwarding

   ::

       sudo sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf

-  permanently set ``iptables`` settings: add to ``/etc/interfaces``

   ::

       post up iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

Stack volume
------------

**Note** - with ``Swift`` enabled actual loopback device may be other
than ``/dev/loop0``

Check that volumes are created:

::

    sudo losetup -a
    sudo pvs
    sudo vgs

you should see volume group ``stack-volumes`` existing and attached to
``/opt/stack/data/stack-volumes-backing-file`` via ``/dev/loop0``.

After reboot the attachment of the backing file to loopback device will
be lost. To make it permanent add the following line to your
``/etc/rc.local`` file, before ``exit 0`` line:

::

    losetup /dev/loop0 /opt/stack/data/stack-volumes-backing-file

Sharing files between your physical machine and DevStack host
=============================================================

As I use ``vim`` as my Python IDE I personally prefer to work directly
in the console of the guest DevStack instance, but if you prefer GUI IDE
(like PyCharm) you might want to have access to the code on the DevStack
guest right from your host. One rather straightforward possibility is
``sshfs``, but as it is usually pretty slow, you might want to try NFS.

The following is adopted from `this post by
radix <http://radix.twistedmatrix.com/2013/06/complete-guide-to-setting-up-openstack.html>`__

First, install the ``nfs-kernel-server`` package on the host system and
then edit ``/etc/exports`` to add the following line:

::

    full_path_to_project_on_host    *(rw,async,root_squash,no_subtree_check)

Then in the DevStack guest install ``nfs-common`` and add the following
line to ``/etc/fstab``:

::

    address_of_host:full_path_to_project_on_host    full_path_to_project_on_guest    nfs

Don't forget to ``mkdir full_path_to_project_on_guest`` in the guest.
You can then reboot the DevStack guest or just mount
``full_path_to_project_on_guest``.

Problems with receiving IPs for VMs
===================================

VirtIO network interface seems not to fill in checksums correctly in UDP
packets (something called checksum offloading), which interferes with
receiving DHCP lease from neutron/nova-network when everything is
running on a single host (i.e. DevStack). To fix this add the following
rule to ``iptables``:

::

    iptables -A POSTROUTING -t mangle -p udp --dport bootpc -j CHECKSUM --checksum-fill

