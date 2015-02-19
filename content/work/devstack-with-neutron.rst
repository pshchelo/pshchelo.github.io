How to set DevStack with Neutron
################################

:date: 2014-04-21
:tags: devstack, openstack
:category: work
:slug: devstack-with-neutron
:summary: tips and tricks on setting DevStack

These tips try to solve problems I stumbled upon when starting my work
on OpenStack, Grizzly release at that time. I've tried to accommodate
the solutions for recent DevStack (early Juno as of this
writing), but some things might still be incorrect or already fixed -
YMMV.

All notes are concerning Ubuntu/Debian on an Intel CPU, so for other systems
some changes might be necessary.

Update
  Tried DevStack on fresh Ubuntu 14.04 LTS (Trusty Thar), updated tips.


.. contents::


Install DevStack
================

-  Prepare a VM for DevStack deployment
-  in this VM install ``git``

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

   -  I have a `repo <https://github.com/pshchelo/stackdev>`__ with my
      DevStack customizations, you might want to check it out.

-  install DevStack

   ::

       ./stack.sh

Now you should have a working DevStack installation. You can login into
Horizon, or join the running stack with ``./rejoin_stack.sh`` command
and check console outputs of all the running services for debug and error info.
There are some networks and routers created by default, so you can
start VMs and attach floating IPs to them.


Allow VM Internet connectivity
==============================

You might stumble on networking issues concerning outside access,
like pinging or accessing Internet resources outside of your DevStack.
First you need to change the Security Group settings -
the "default" group created by DevStack seems to allow everything
but in fact I've always had problems with it, so just create your own
security group and assign your VMs to it.
Then you need to configure ``iptables`` to pass through the traffic:

::

    sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

(after this `launchpad question <https://answers.launchpad.net/neutron/+question/208377>`_).


Note on ``unstack.sh`` and rebooting
====================================

As I've found the hard way, if you ever need to reboot your DevStack VM,
**do not** run ``unstack.sh`` before that.
Simply detach from screen and/or reboot as usual.
The unstacking script not only stops the services run in screen,
it also alters some configuration options of your system
that were introduced by running ``stack.sh`` and setting up the DevStack.
Mostly it concerns network bridges from what I have seen.
So if you run ``unstack.sh``, in order to have a working DevStack installation
you have to run ``stack.sh`` after it.
That has a drawback that all your cloud configuration
(e.g. everything stored in DB tables of OpenStack and content of stack-volume-backing-file) will be reset.

Thus, the work flow looks somewhat like this:

#. Start/configure DevStack with ``stack.sh``

#. Join the stack with ``rejoin_stack.sh``

#. Make changes, restarting services affected on per-service basis via screen
   to put your changes in effect.

#. If in need to reboot the DevStack VM, shut it down the usual way,
   and upon restart simply run ``rejoin_stack.sh`` again,
   all services will be started in screen again.

#. Only if you need to change the OpenStack/DevStack configuration,
   then run ``unstack.sh``, make changes in ``local.conf`` / wherever you have to
   and then run ``stack.sh``.


Restore settings after reboot
=============================

After reboot of the DevStack VM the following will be lost:

-  stack volumes (this includes created storage volumes etc.)
-  iptables/NAT setting
-  bridges configurations

Here how to restore these settings or make them permanent:

Update
  Right now it appears to be so involved to cleanly restore all the settings
  lost after reboot that a much safer and easier way is to make peace with
  everything in your OpenStack being lost (all the settings and things
  you've created inside) and just run ``stack.sh`` again (optionally with
  ``OFFLINE = True`` in your ``local.conf`` to keep the code exactly as
  before reboot).


Stack volumes
-------------

**Note** - with ``Swift`` enabled actual loopback device may be other
than ``/dev/loop0``

Check that volumes are created after fresh running of ``./stack.sh``:

::

    sudo losetup -a
    sudo pvs
    sudo vgs

You should see volume group ``stack-volumes`` existing and attached to
``/opt/stack/data/stack-volumes-backing-file`` via ``/dev/loop0``.

After reboot the attachment of the backing file to loopback device will
be lost. To make it permanent add the following line to your
``/etc/rc.local`` file, before ``exit 0`` line:

::

    losetup /dev/loop0 /opt/stack/data/stack-volumes-backing-file


NAT settings
------------

After `this mail-list
post <https://lists.launchpad.net/openstack/msg17016.html>`__

-  permanently enable IP-forwarding

   ::

       sudo sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf

-  permanently set ``iptables`` settings: add to ``/etc/interfaces``

   ::

       post up iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE


Bridges
-------
After `this ghist <https://gist.github.com/charlesflynn/5576114>`_.

Bridge ``br-ex`` has no IP after reboot.
Use the following commands to set bridges according to default settings
of ``stack.sh``:

    ::

        sudo ip addr flush dev br-ex
        sudo ip addr add 172.24.4.1/24 dev br-ex
        sudo ip link set br-ex up
        sudo route add -net 10.0.0.0/24 gw 172.24.4.1



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

Some versions of VirtIO network interface seem not to fill in checksums correctly in UDP
packets (something called checksum offloading), which interferes with
receiving DHCP lease from neutron/nova-network when everything is
running on a single host (e.g. DevStack). To fix this add the following
rule to ``iptables``:

::

    sudo iptables -A POSTROUTING -t mangle -p udp --dport bootpc -j CHECKSUM --checksum-fill


Nested KVM
==========

If you run DevStack as a KVM guest, ensure that your host system has nested KVM enabled -
that will greatly speed up those VMs you run inside your DevStack guest
(of course your CPU has to support virtualization extensions and have them enabled in BIOS).

Check that nested KVM is enabled:

::

    cat /sys/module/kvm_intel/parameters/nested



If it's ``N`` then try to load the module with

::

    modprobe kvm_intel nested=1


If it worked (you get ``Y`` after checking again) to make it permanent
you have to add the following line to some ``.conf`` file in ``/etc/modprobe.d/``:

::

    options kvm-intel nested=1

Reboot and check again.
