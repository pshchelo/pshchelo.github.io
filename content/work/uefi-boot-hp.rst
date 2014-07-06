UEFI boot order on dualbooted HP EliteBook 840
##############################################

:date: 2014-04-14
:tags: hp, dualboot, uefi
:category: work
:slug: uefi-boot-hp
:summary: setting up dualbooted HP notebook in UEFI mode

Problem
=======

Using UEFI+SecureBoot, dual boot Windows 8.1 / Ubuntu 13.10. Boot order
can be configured in BIOS per device (HDD/ODD/PXI/USB etc) but there is
no way to specify boot order of systems present on HDD. UEFI boot loader
finds both Windows (present as ``OS Manager``) and Ubuntu (as
``ubuntu``), but always uses ``OS Manager`` first. As I intend to use
Ubuntu most of the time, I need a way to make booting Ubuntu the default
option.

Research
========

According to *teh Internets* such problems seem to occur reasonably
often, when vendors "under-implement" UEFI on their products. One
commonly proposed solution is using recent versions of ``boot-repair``
Ubuntu package (a really nice piece of engineering, saved my ass couple
of times in the past). What it does is it substitutes (with backup of
course) the windows *efi* file with accordingly renamed Ubuntu *efi*
file, thus loading GRUB automatically, and from there user can choose
what system to boot. But I find such solution a bit too risky, so I want
something more native.

Another program that is related is ``efibootmgr``

::

    sudo apt-get install efibootmgr

It has the option to modify boot order of *efi* files with
``efibootmgr -o``, but at least on my particular HP notebook it has no
effect, and system boots to Windows by default despite any changes in
the boot order introduced by ``efibootmgr``. Strangely though, the
option to force the boot order only on next reboot (``efibootmgr -n``)
is working alright. So, here comes the solution I figured out with the
help of `this Ubuntu Forums
thread <http://ubuntuforums.org/showthread.php?t=2173267>`__

Solution
========

My current EFI setup looks like following

::

    shell$: sudo efibootmgr 
    BootCurrent: 0001
    Timeout: 0 seconds
    BootOrder: 0001,0002
    Boot0001* ubuntu
    Boot0002* Windows Boot Manager

So I 've placed the following line in ``/etc/rc.local`` (before the
final ``exit 0`` line):

::

    /bin/efibootmgr -n 0001

This forces next default boot to be Ubuntu on every boot of Ubuntu. The
dark side - after booting to Windows, this setting naturally disappears,
so the next booted by default system after Windows boot is Windows
again. But actually this is **exactly what I want** - it sort of
replicates ``GRUB_SAVE_DEFAULT`` feature which I was always using
before, so that every next boot by default is the same as previous boot.
Installing zero delay on UEFI bootloader (there is still couple of
seconds to press F9 and go into UEFI boot menu manually), and very short
delay on GRUB (2 sec just for an emergency need to boot not into
standard Ubuntu) gives me a system that's fast enough to boot in
unattended mode.

Update
======

After living with this configuration for several months I realized two things:

#. I do not use Windows more than once a month;
#. Using hibernate via TuxOnIce has some problems.


The last one is due to rc.local not being processed on resume from hibernate,
and unfortunately I failed to configure TuxOnIce to execute the ``efibootmgr``
properly on resume.

I again turned to BIOS settings and this time noticed that I can 
in fact configure "Custom" boot section and make it the first one to boot.
So now I have Ubuntu booting by default, and from Grub I can start Windows 
if I need, and also I can safely use SAVE_DEFAULT option of Grub. 
For those times when Windows *has* to be booted directly from EFI,
there is still possibility to override first boot option during POST.
