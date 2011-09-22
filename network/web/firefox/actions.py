#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2005-2011 TUBITAK/BILGEM
# Licensed under the GNU General Public License, version 2.
# See the file http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import shelltools
from pisi.actionsapi import get

WorkDir = "mozilla-release"

locales = ["be", "ca", "de", "es-AR", "es-ES", "fr", "hu", "it", "nl", "pl", "ru", "sv-SE", "tr"]

def setup():
    # Let the lines stay below, we could need them in the future
    # Mozilla uses autoconf 3.13 instead of 2.15. Thus we use own autoconf213
    # Use autoconf-213 which we provide via a hacky pathc to produce configure
    #shelltools.system("/bin/bash ./autoconf-213/autoconf-2.13 --macro-dir=autoconf-213/m4")
    #shelltools.cd("js/src")
    #shelltools.system("/bin/bash ../../autoconf-213/autoconf-2.13 --macro-dir=../../autoconf-213/m4")
    #shelltools.cd("../..") 

    # TODO: Enable PGD
    #pisitools.dosed("memory/jemalloc/Makefile.in", "^NO_PROFILE_GUIDED_OPTIMIZE = 1$", "")

    # Needed for our custom l10n tarball
    shelltools.sym("../l10n", "l10n")

    # There are two entries for turkish, remove one. We have to apply it here 
    # because we have one WorkDir but two different archives
    shelltools.system("patch -Np0 -i %s/fix-double-turkish-option.diff" % get.workDIR())

def build():
    # FIXME: Change library path and version with variables
    shelltools.export("LDFLAGS", "%s -Wl,-rpath,/usr/lib/firefox-6.0.2" % get.LDFLAGS())

    autotools.make("-f client.mk")

    # LOCALE
    # FIXME: Find an elegant solution to create the Makefile from Makefile.in
    # We need to execute configure, otherwise the Makefile in browser/locales doesn't 
    # generate. Don't execute is before "make -f client.mk". Otherwise it's conflicts with
    # mozconfig.
    shelltools.system("./configure --prefix=/usr --libdir=/usr/lib --disable-strip --disable-install-strip")

    # FIXME: nsinstall get installed in the wrong place, fix it
    shelltools.copy("%s/%s/obj-x86_64-unknown-linux-gnu/config/nsinstall" % (get.workDIR(), WorkDir), "%s/%s/config/" % (get.workDIR(), WorkDir))
    for locale in locales:
       autotools.make("-C browser/locales langpack-%s" % locale)

def install():
    autotools.rawInstall("-f client.mk DESTDIR=%s" % get.installDIR())

    # Any reason to do this renaming ?
    realdir = shelltools.ls("%s/usr/lib/firefox-?.?.?" % get.installDIR())[0].replace(get.installDIR(), "")
    pisitools.rename(realdir, "MozillaFirefox")

    pisitools.remove("/usr/bin/firefox") # Additional file will replace that

    #install locales
    for locale in locales:
        pisitools.copytree("dist/xpi-stage/locale-%s" % locale, "%s/usr/lib/MozillaFirefox/extensions/langpack-%s@firefox.mozilla.org" % (get.installDIR(), locale))
        pisitools.removeDir("/usr/lib/MozillaFirefox/extensions/langpack-%s@firefox.mozilla.org/defaults" % locale)
        pisitools.remove("/usr/lib/MozillaFirefox/extensions/langpack-%s@firefox.mozilla.org/chrome/%s/locale/branding/browserconfig.properties" % (locale, locale))
        pisitools.dosym("../../../../../../browserconfig.properties", "/usr/lib/MozillaFirefox/extensions/langpack-%s@firefox.mozilla.org/chrome/%s/locale/branding/browserconfig.properties" % (locale, locale))

    pisitools.dodir("/usr/lib/MozillaFirefox/dictionaries")
    shelltools.touch("%s%s/dictionaries/tr-TR.aff" % (get.installDIR(), "/usr/lib/MozillaFirefox"))
    shelltools.touch("%s%s/dictionaries/tr-TR.dic" % (get.installDIR(), "/usr/lib/MozillaFirefox"))

    # Create profile dir, we'll copy bookmarks.html in post-install script
    pisitools.dodir("/usr/lib/MozillaFirefox/defaults/profile")

    # Install branding icon
    pisitools.insinto("/usr/share/pixmaps", "browser/branding/official/default256.png", "firefox.png")

    # Install docs
    pisitools.dodoc("LEGAL", "LICENSE")
