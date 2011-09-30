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
    synaptiks.monitors.mouses
    =========================

    Implementation of mouse monitoring.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from collections import namedtuple
from itertools import ifilter

import pyudev
from pyudev.pyqt4 import QUDevMonitorObserver
from PyQt4.QtCore import QObject, pyqtSignal

from synaptiks.monitors.power import create_resume_monitor


__all__ = ['MouseDevicesManager', 'MouseDevicesMonitor', 'MouseDevice']


def _is_mouse(device):
    return (device.sys_name.startswith('event') and
            device.get('ID_INPUT_MOUSE') == '1' and
            not device.get('ID_INPUT_TOUCHPAD') == '1')


class MouseDevice(namedtuple('_MouseDevice', ['serial', 'name'])):
    """
    A :func:`~collections.namedtuple()` representing a mouse device.

    A mouse device currently has two attributes, the order corresponds to the
    tuple index:

    - :attr:`serial`
    - :attr:`name`
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

    #: Qt signal, which is emitted, when a mouse is plugged.  The slot gets a
    #: single argument of :class:`MouseDevice`, which represents the plugged
    #: mouse device
    mousePlugged = pyqtSignal(MouseDevice)
    #: Qt signal, which is emitted, when a mouse is unplugged.  The slot gets a
    #: single argument of type :class:`MouseDevice`, which represents the
    #: unplugged mouse device
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
        An iterator over all currently plugged mouse devices as
        :class:`MouseDevice` objects.
        """
        devices = self._udev.list_devices(
            subsystem='input', ID_INPUT_MOUSE=True)
        for device in ifilter(_is_mouse, devices):
            yield MouseDevice.from_udev(device)

    def _handle_udev_event(self, evt, device):
        signal = self._event_signal_map.get(unicode(evt))
        if signal and _is_mouse(device):
            signal.emit(MouseDevice.from_udev(device))


class MouseDevicesManager(MouseDevicesMonitor):
    """
    Manage mouse devices.

    This class derives from :class:`MouseDevicesMonitor` to provide more
    advanced monitoring of mouse devices.  In addition to the basic monitoring
    provided by :class:`MouseDevicesMonitor` this class keeps a record of
    currently plugged devices, and thus also informs about the *first* mouse
    plugged, and the *last* mouse unplugged.
    """

    #: Qt signal, which is emitted if the first mouse is plugged.  The slot :
    #: gets a single argument, which is the plugged :class:`MouseDevice`.
    firstMousePlugged = pyqtSignal(MouseDevice)
    #: Qt signal, which is emitted if the last mouse is unplugged.  The slot :
    #: gets a single argument, which is the plugged :class:`MouseDevice`.
    lastMouseUnplugged = pyqtSignal(MouseDevice)

    def __init__(self, parent=None):
        """
        Create a new manager.

        ``parent`` is the parent ``QObject``.
        """
        MouseDevicesMonitor.__init__(self, parent)
        self._resume_monitor = create_resume_monitor(self)
        self._mouse_registry = set()
        self._ignored_mouses = frozenset()
        self.is_running = False

    def start(self):
        """
        Start to observe mouse devices.

        Does nothing, if the manager is already running.
        """
        if not self.is_running:
            self.mousePlugged.connect(self._register_mouse)
            self.mouseUnplugged.connect(self._unregister_mouse)
            if self._resume_monitor:
                self._resume_monitor.resuming.connect(self._reset_registry)
            self._reset_registry()
        self.is_running = True

    def stop(self):
        """
        Stop to observe mouse devices.

        Does nothing, if the manager is not running.
        """
        if self.is_running:
            self.mousePlugged.disconnect(self._register_mouse)
            self.mouseUnplugged.disconnect(self._unregister_mouse)
            if self._resume_monitor:
                self._resume_monitor.resuming.disconnect(self._reset_registry)
            self._clear_registry()
        self.is_running = False

    def _unregister_mouse(self, device):
        """
        Unregister the given mouse ``device``.  If this is the last plugged
        mouse, :attr:`lastMouseUnplugged` is emitted with the given ``device``.
        """
        try:
            self._mouse_registry.remove(device)
        except KeyError:
            pass
        else:
            if not self._mouse_registry:
                self.lastMouseUnplugged.emit(device)

    def _register_mouse(self, device):
        """
        Register the given mouse ``device``.  If this is the first plugged
        mouse, :attr:`firstMousePlugged` is emitted with the given ``device``.
        """
        if device.serial not in self._ignored_mouses:
            if not self._mouse_registry:
                self.firstMousePlugged.emit(device)
            self._mouse_registry.add(device)

    def _reset_registry(self):
        """
        Re-register all plugged mouses.
        """
        self._clear_registry()
        for device in self.plugged_devices:
            self._register_mouse(device)

    def _clear_registry(self):
        """
        Clear the registry of plugged mouse devices.
        """
        for device in list(self._mouse_registry):
            self._unregister_mouse(device)

    @property
    def ignored_mouses(self):
        """
        The list of ignored mouses.

        This property holds a list of serial numbers.  Mouse devices with these
        serial numbers are simply ignored when plugged or unplugged.

        Modifying the returned list in place does not have any effect, assign
        to this property to change the list of ignored devices.  You may also
        assign a list of :class:`~synaptiks.monitors.MouseDevice` objects.
        """
        return list(self._ignored_mouses)

    @ignored_mouses.setter
    def ignored_mouses(self, devices):
        devices = set(d if isinstance(d, basestring) else d.serial
                      for d in devices)
        if self._ignored_mouses != devices:
            self._ignored_mouses = devices
            if self.is_running:
                self._reset_registry()
