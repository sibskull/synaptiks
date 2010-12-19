# -*- coding: utf-8 -*-
# Copyright (c) 2010, Sebastian Wiesner <lunaryorn@googlemail.com>
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
    synaptiks.daemon
    ================

    Implementation of synaptiks touchpad management daemon.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import os
import sys

import dbus
import dbus.service
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
from PyQt4.QtGui import QApplication
from dbus.mainloop.glib import DBusGMainLoop

from synaptiks.touchpad import Touchpad


class SynaptiksDaemon(QApplication):

    class Proxy(dbus.service.Object):
        def __init__(self, daemon, bus):
            dbus.service.Object.__init__(self, bus, '/Daemon')
            self.daemon = daemon

        @dbus.service.method(dbus_interface='org.kde.synaptiks.Daemon',
                             in_signature='', out_signature='')
        def quit(self):
            self.daemon.quit()

        @dbus.service.method(dbus_interface='org.kde.synaptiks.Daemon',
                             in_signature='', out_signature='b')
        def is_running(self):
            return True

    DAEMON_SERVICE_NAME = 'de.lunaryorn.synaptiks'

    def __init__(self, args):
        QApplication.__init__(self, args)
        self.setOrganizationName('kde.org')
        self.setApplicationName('synaptiks')
        bus = dbus.SessionBus()
        self.busname = dbus.service.BusName(self.DAEMON_SERVICE_NAME, bus)
        self.proxy = self.Proxy(self, bus)
        self.touchpad = Touchpad.find_first()

    @classmethod
    def is_running(cls):
        bus = dbus.SessionBus()
        try:
            obj = bus.get_object(cls.DAEMON_SERVICE_NAME, '/Daemon',
                                 introspect=False)
            interface = dbus.Interface(obj, 'org.kde.synaptiks.Daemon')
            return interface.is_running()
        except dbus.DBusException:
            return False

def main():
    # recent qt releases integrate glib support, so we can just use the glib
    # main loop provided by the dbus module
    dbus.set_default_main_loop(DBusGMainLoop())
    if SynaptiksDaemon.is_running():
        print('synaptiksd is already running')
        return
    if os.fork() == 0:
        daemon = SynaptiksDaemon(sys.argv)
        daemon.exec_()


if __name__ == '__main__':
    main()
