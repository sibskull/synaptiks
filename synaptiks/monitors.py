# -*- coding: utf-8 -*-
# Copyright (C) 2010 Sebastian Wiesner <lunaryorn@googlemail.com>
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
    synaptiks.monitors
    ==================

    Monitor classes for various external event sources.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from itertools import ifilter
from collections import namedtuple

import pyudev
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
from pyudev.pyqt4 import QUDevMonitorObserver
from PyQt4.QtCore import QObject, pyqtSignal


def _is_mouse(device):
    return (device.sys_name.startswith('mouse') and
            device.get('ID_INPUT_MOUSE') == '1' and
            not device.get('ID_INPUT_TOUCHPAD') == '1')


class MouseDevice(namedtuple('_MouseDevice', ['serial', 'name'])):
    """
    A :class:`~collections.namedtuple` representing a mouse device.

    Currently a mouse device is represented by two attributes (the order
    corresponds to their tuple indexes):

    - ``serial``:  The serial number
    - ``name``:  The product name
    """

    @classmethod
    def from_udev(cls, device):
        """
        Create a :class:`MouseDevice` tuple from a :class:`pyudev.Device`.
        """
        # The name is available from the parent device of the actual event
        # device.  The parent represents the actual physical device.  The name
        # may be decorated with quotation marks, which are removed for the sake
        # of a clean represenation
        return cls(device['ID_SERIAL'], device.parent['NAME'].strip('"'))


class MouseDevicesMonitor(QObject):
    """
    Watch for plugged or unplugged mouse devices.
    """

    #: emitted, when a mouse is plugged.  The slot gets a single argument of
    #: :class:`MouseDevice`, which represent the plugged mouse device
    mousePlugged = pyqtSignal(MouseDevice)
    #: emitted, when a mouse is unplugged.  The slot gets a single argument of
    #: :class:`MouseDevice`, which represent the unplugged mouse device
    mouseUnplugged = pyqtSignal(MouseDevice)

    def __init__(self, parent=None):
        """
        Create a new monitor.

        ``parent`` is the parent :class:`~PyQt4.QtCore.QObject`.
        """
        QObject.__init__(self, parent)
        self._udev = pyudev.Context()
        self._notifier = QUDevMonitorObserver(
            pyudev.Monitor.from_netlink(self._udev), self)
        self._notifier.deviceEvent.connect(self._handle_udev_event)
        self._notifier.monitor.filter_by('input')
        self._notifier.monitor.start()
        self._event_signal_map = dict(
            add=self.mousePlugged, remove=self.mouseUnplugged)

    @property
    def plugged_devices(self):
        """
        An iterator over all plugged mouse devices as :class:`MouseDevice`
        objects.
        """
        devices = self._udev.list_devices().match_subsystem(
            'input').match_property('ID_INPUT_MOUSE', True)
        for device in ifilter(_is_mouse, devices):
            yield MouseDevice.from_udev(device)

    def _handle_udev_event(self, evt, device):
        signal = self._event_signal_map.get(evt)
        if signal and _is_mouse(device):
            signal.emit(MouseDevice.from_udev(device))

