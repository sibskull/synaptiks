# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011 Sebastian Wiesner <lunaryorn@googlemail.com>
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

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from itertools import ifilter
from collections import namedtuple
from itertools import izip
from array import array

import pyudev
from pyudev.pyqt4 import QUDevMonitorObserver
from PyQt4.QtCore import QObject, QTimer, QTime, pyqtSignal

from synaptiks.qx11 import QX11Display
from synaptiks._bindings import xlib


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


class PollingKeyboardMonitor(QObject):
    """
    Monitor the keyboard for state changes by constantly polling the keyboard.
    """

    #: default polling interval
    DEFAULT_POLLDELAY = 200
    #: default time span before considering the keyboard inactive again
    DEFAULT_IDLETIME = 2000
    #: size of the X11 keymap array
    _KEYMAP_SIZE = 32

    #: Ignore no keys
    IGNORE_NO_KEYS = 0
    #: Ignore modifier keys alone
    IGNORE_MODIFIER_KEYS = 1
    #: Ignore combinations of modifiers and standard keys
    IGNORE_MODIFIER_COMBOS = 2

    #: emitted if typing is started.  Takes no arguments
    typingStarted = pyqtSignal()
    #: emitted if typing is stopped.  Takes no arguments
    typingStopped = pyqtSignal()

    def __init__(self, parent=None):
        """
        Create a new monitor.

        ``parent`` is the parent :class:`~PyQt4.QtCore.QObject`.
        """
        QObject.__init__(self, parent)
        self._keyboard_was_active = False
        self._old_keymap = array(b'B', b'\0'*32)
        self._keyboard_timer = QTimer(self)
        self._keyboard_timer.timeout.connect(self._check_keyboard_activity)
        self._keyboard_timer.setInterval(self.DEFAULT_POLLDELAY)
        self._activity = QTime()
        self._keys_to_ignore = self.IGNORE_NO_KEYS
        self._keymap_mask = self._setup_mask()
        self._idle_time = self.DEFAULT_IDLETIME

    @property
    def is_active(self):
        """
        ``True``, if the keyboard monitor is currently running, ``False``
        otherwise.
        """
        return self._keyboard_timer.isActive()

    def start(self):
        """
        Start monitoring the keyboard.
        """
        self._keyboard_timer.start()

    def stop(self):
        """
        Stop monitoring the keyboard.
        """
        # since we are not monitoring the keyboard anymore, we assume, that
        # there is no keyboard activity anymore.
        self.typingStopped.emit()
        self._keyboard_timer.stop()

    @property
    def idle_time(self):
        """
        The time to wait before assuming, that the typing has stopped, in
        seconds as float.
        """
        return self._idle_time / 1000

    @idle_time.setter
    def idle_time(self, value):
        self._idle_time = int(value*1000)

    @property
    def keys_to_ignore(self):
        """
        The keys to ignore while observing the keyboard.

        If such a key is pressed, the keyboard will not be considered active,
        the signal :attr:`typingStarted()` will consequently not be emitted.

        Raise :exc:`~exceptions.ValueError` upon assignment, if the given value
        is not one of :attr:`IGNORE_NO_KEYS`, :attr:`IGNORE_MODIFIER_KEYS` or
        :attr:`IGNORE_MODIFIER_COMBOS`.
        """
        return self._keys_to_ignore

    @keys_to_ignore.setter
    def keys_to_ignore(self, value):
        if not (self.IGNORE_NO_KEYS <= value <= self.IGNORE_MODIFIER_COMBOS):
            raise ValueError('unknown constant for keys_to_ignore')
        self._keys_to_ignore = value
        self._keymap_mask = self._setup_mask()

    def _setup_mask(self):
        mask = array(b'B', b'\xff'*32)
        if self._keys_to_ignore >= self.IGNORE_MODIFIER_KEYS:
            modifier_mappings = xlib.get_modifier_mapping(QX11Display())
            for modifier_keys in modifier_mappings:
                for keycode in modifier_keys:
                    mask[keycode // 8] &= ~(1 << (keycode % 8))
        return mask

    @property
    def keyboard_active(self):
        """
        Is the keyboard currently active (with respect to
        :attr:`keys_to_ignore`)?

        ``True``, if the keyboard is currently active, ``False`` otherwise.
        """
        is_active = False

        _, raw_keymap = xlib.query_keymap(QX11Display())
        keymap = array(b'B', raw_keymap)

        is_active = keymap != self._old_keymap
        for new_state, old_state, mask in izip(keymap, self._old_keymap,
                                               self._keymap_mask):
            is_active = new_state & ~old_state & mask
            if is_active:
                break

        if self._keys_to_ignore == self.IGNORE_MODIFIER_COMBOS:
            for state, mask in izip(keymap, self._keymap_mask):
                if state & ~mask:
                    is_active = False
                    break

        self._old_keymap = keymap
        return is_active

    def _check_keyboard_activity(self):
        if self.keyboard_active:
            self._activity.start()
            if not self._keyboard_was_active:
                self._keyboard_was_active = True
                self.typingStarted.emit()
        elif self._activity.elapsed() > self._idle_time and \
                 self._keyboard_was_active:
            self._keyboard_was_active = False
            self.typingStopped.emit()
