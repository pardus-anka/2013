#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2005-2010 TUBITAK/UEKAE
# Licensed under the GNU General Public License, version 2.
# See the file http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import shelltools
from pisi.actionsapi import get

import os

snapshot = False

if snapshot:
    verMajor, verMinor = get.srcVERSION().replace("pre", "").split("_", 1)
    WorkDir = "gcc-4.5-%s" % verMinor
else:
    verMajor = get.srcVERSION()

arch = get.ARCH().replace("x86_64", "x86-64")

opt_unwind = "--with-system-libunwind" if get.ARCH() == "x86_64" else "--without-system-libunwind"
opt_arch = "--with-arch_32=i686" if get.ARCH() == "x86_64" else "--with-arch=i686"

# WARNING: even -fomit-frame-pointer may break the build, stack protector, fortify source etc. are off limits
cflags = "-O2 -g -pipe"

def removePardusSection(_dir):
    for k in shelltools.ls(_dir):
        if k.startswith("crt") and k.endswith(".o"):
            i = os.path.join(_dir, k)
            shelltools.system('objcopy -R ".comment.PARDUS.OPTs" %s' % i)

def exportFlags():
    # we set real flags with new configure settings, these are just safe optimizations
    shelltools.export("CFLAGS", cflags)
    shelltools.export("CXXFLAGS", cflags)
    # shelltools.export("LDFLAGS", "")

    # FIXME: this may not be necessary for biarch
    shelltools.export("CC", "gcc")
    shelltools.export("CXX", "g++")
    shelltools.export("LC_ALL", "en_US.UTF-8")

def setup():
    exportFlags()
    # Maintainer mode off, do not force recreation of generated files
    # shelltools.system("contrib/gcc_update --touch")

    shelltools.makedirs("build")
    shelltools.cd("build")

    shelltools.system('../configure \
                       --prefix=/usr \
                       --bindir=/usr/bin \
                       --libdir=/usr/lib \
                       --libexecdir=/usr/lib \
                       --includedir=/usr/include \
                       --mandir=/usr/share/man \
                       --infodir=/usr/share/info \
                       --with-gxx-include-dir=/usr/include/c++ \
                       --build=%s \
                       --disable-libgcj \
                       --disable-multilib \
                       --disable-nls \
                       --disable-mudflap \
                       --disable-libmudflap \
                       --disable-libunwind-exceptions \
                       --enable-checking=release \
                       --enable-clocale=gnu \
                       --enable-__cxa_atexit \
                       --enable-languages=c,c++,fortran,objc,obj-c++,lto \
                       --enable-libstdcxx-allocator=new \
                       --disable-libstdcxx-pch \
                       --enable-shared \
                       --enable-ssp \
                       --disable-libssp \
                       --enable-plugin \
                       --enable-threads=posix \
                       --without-included-gettext \
                       %s \
                       %s \
                       --with-tune=generic \
                       --with-system-zlib \
                       --with-tune=generic \
                       --with-pkgversion="Pardus Linux" \
                       --with-bugurl=http://bugs.pardus.org.tr' % (get.HOST(), opt_arch, opt_unwind))
                       # FIXME: this is supposed to be detected automatically
                       #--enable-long-long \
                       # --enable-gnu-unique-object \  enable with binutils > 2.20.51.0.2
                       # --disable-libunwind-exceptions  # experiment with libunwind >= 0.99


def build():
    exportFlags()

    shelltools.cd("build")
    autotools.make('BOOT_CFLAGS="%s" profiledbootstrap' % cflags)

def install():
    shelltools.cd("build")
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    for header in ["limits.h","syslimits.h"]:
        pisitools.insinto("/usr/lib/gcc/%s/%s/include" % (get.HOST(), verMajor) , "gcc/include-fixed/%s" % header)

    # Not needed
    pisitools.removeDir("/usr/lib/gcc/*/*/include-fixed")
    pisitools.removeDir("/usr/lib/gcc/*/*/install-tools")

    # This one comes with binutils
    pisitools.remove("/usr/lib*/libiberty.a")

    # cc symlink
    pisitools.dosym("/usr/bin/gcc" , "/usr/bin/cc")

    # /lib/cpp symlink for legacy X11 stuff
    pisitools.dosym("/usr/bin/cpp", "/lib/cpp")

    # Remove our options section from crt stuff
    removePardusSection("%s/usr/lib/gcc/%s/%s/" % (get.installDIR(), get.HOST(), verMajor))

    # autoload gdb pretty printers
    gdbpy_dir = "/usr/share/gdb/auto-load/usr/lib/"
    pisitools.dodir(gdbpy_dir)

    gdbpy_files = shelltools.ls("%s/usr/lib/libstdc++*gdb.py*" % get.installDIR())
    for i in gdbpy_files:
        pisitools.domove("/usr/lib/%s" % shelltools.baseName(i), gdbpy_dir)


