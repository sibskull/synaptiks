# -*- coding: utf-8 -*-
# Copyright (c) 2011, Sebastian Wiesner <lunaryorn@googlemail.com>
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
    synaptiks.monitors.power
    ========================

    Implementation of Power monitoring.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from PyQt4.QtCore import QObject, pyqtSignal
try:
    import dbus
    from  dbus.mainloop.glib import DBusGMainLoop
except ImportError:
    dbus = None


__all__ = ['create_resume_monitor', 'AbstractResumeMonitor',
           'UPowerResumeMonitor']


class AbstractResumeMonitor(QObject):
    """
    Abstract base class for suspend monitors.

    This class defines the interface for classes, which monitor the systems
    power state and emit :attr:`resuming`, whenever the system resumes from a
    sleep state.

    Use :func:`create_resume_monitor()` to create an instance of the "best"
    implementation of this class.
    """

    #: Qt signal, emitted whenever the system resumes from a sleep state.  Has
    #: no arguments.
    resuming = pyqtSignal()


class UPowerResumeMonitor(AbstractResumeMonitor):
    """
    Implementation of :class:`AbstractResumeMonitor`, which uses UPower_ to
    monitor the system's power state.

    .. _UPower: http://upower.freedesktop.org
    """

    UPOWER_SERVICE_NAME = 'org.freedesktop.UPower'
    UPOWER_INTERFACE = 'org.freedesktop.UPower'
    UPOWER_OBJECT_PATH = '/org/freedesktop/UPower'

    def __init__(self, parent=None):
        AbstractResumeMonitor.__init__(self, parent)
        self._bus = dbus.SystemBus(mainloop=DBusGMainLoop())
        self._bus.add_signal_receiver(
            self.resuming.emit, 'Resuming', self.UPOWER_SERVICE_NAME,
            self.UPOWER_INTERFACE, self.UPOWER_OBJECT_PATH)


def create_resume_monitor(parent=None):
    """
    Create a new resume monitor:

    >>> monitor = create_resume_monitor(parent)
    >>> monitor.resuming.connect(lambda: print('system is resuming'))

    This function automatically chooses the "best" available implementation.
    Currently this means, that a :class:`UPowerResumeMonitor` is created, if
    UPower is installed and working.  Otherwise ``None`` is returned.

    .. note::

       This should actually be the task of KDEs hardware abstraction library
       Solid.  It indeed provides this functionality through the
       ``Solid::PowerManagement::Notifier::resumingFromSuspend`` signal, but
       unfortunately the ``Notifier`` class is not wrapped by PyKDE.

    Return an implementation of :class:`AbstractResumeMonitor`, or ``None``, if
    this system does not support monitoring of power state.
    """
    if dbus:
        bus = dbus.SystemBus(mainloop=DBusGMainLoop())
        activatable_names = bus.list_activatable_names()
        if 'org.freedesktop.UPower' in activatable_names:
            # UPower is available on the system bus
            return UPowerResumeMonitor(parent)
    # no power state monitoring available
    return None
