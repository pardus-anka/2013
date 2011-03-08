#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 2.
# See the file http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt

from pisi.actionsapi import pisitools
from pisi.actionsapi import pythonmodules
from pisi.actionsapi import get

def build():
    pythonmodules.compile()

def install():
    pythonmodules.install()

    pisitools.doman("doc/bpython.1", "doc/bpython-config.5")
    pisitools.insinto("/usr/share/pixmaps", "bpython/logo.png", "bpython.png")
    pisitools.dodoc("LICENSE", "CHANGELOG", "README", "sample-config")

