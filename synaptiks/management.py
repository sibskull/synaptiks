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
    synaptiks.management
    ====================

    The state machine for touchpad management and related classes.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from functools import partial

from PyQt4.QtCore import pyqtSignal, QStateMachine, QState

from synaptiks.monitors import (MouseDevicesMonitor, MouseDevice,
                                PollingKeyboardMonitor)


class MouseDevicesManager(MouseDevicesMonitor):
    """
    Manage mouse devices.

    This class watches for mouses, which are plugged or unplugged.  If the
    first mouse is plugged, :attr:`firstMousePlugged` is emitted.  If the last
    mouse is unplugged, :attr:`lastMouseUnplugged` is emitted.
    """

    #: emitted if the first mouse is plugged
    firstMousePlugged = pyqtSignal(MouseDevice)
    #: emitted if the last mouse is unplugged
    lastMouseUnplugged = pyqtSignal(MouseDevice)

    def __init__(self, parent=None):
        """
        Create a new manager.

        ``parent`` is the parent ``QObject``.
        """
        MouseDevicesMonitor.__init__(self, parent)
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


class TouchpadStateMachine(QStateMachine):
    """
    A state machine, which manages the touchpad state.

    This state machine has two states:

    - ``touchpad_on``: The touchpad is currently on
    - ``touchpad_off``: The touchpad is currently off
    """

    def __init__(self, touchpad, parent=None):
        QStateMachine.__init__(self, parent)
        self.touchpad = touchpad
        # setup the states
        self.touchpad_off = QState(self)
        self.touchpad_off.setObjectName('touchpad_off')
        self.touchpad_off.entered.connect(partial(self._set_touchpad_off, 1))
        self.touchpad_not_off = QState(self)
        self.touchpad_not_off.setObjectName('touchpad_not_off')
        self.touchpad_on = QState(self.touchpad_not_off)
        self.touchpad_on.setObjectName('touchpad_on')
        self.touchpad_on.entered.connect(partial(self._set_touchpad_off, 0))
        self.touchpad_temporarily_off = QState(self.touchpad_not_off)
        self.touchpad_temporarily_off.setObjectName('touchpad_temporarily_off')
        self.touchpad_temporarily_off.entered.connect(
            partial(self._set_touchpad_off, 1))
        self.touchpad_not_off.setInitialState(self.touchpad_on)
        # set the initial state to reflect the actual state of the touchpad
        self.setInitialState(
            self.touchpad_off if self.touchpad.off else self.touchpad_not_off)
        # setup a mouse manager
        self.mouse_manager = MouseDevicesManager(self)
        self.touchpad_not_off.addTransition(self.mouse_manager.firstMousePlugged,
                                            self.touchpad_off)
        self.touchpad_off.addTransition(self.mouse_manager.lastMouseUnplugged,
                                        self.touchpad_not_off)
        # setup a keyboard monitor
        self.keyboard_monitor = PollingKeyboardMonitor(self)
        self.touchpad_on.addTransition(self.keyboard_monitor.typingStarted,
                                       self.touchpad_temporarily_off)
        self.touchpad_temporarily_off.addTransition(
            self.keyboard_monitor.typingStopped, self.touchpad_on)

    def add_touchpad_switch_signal(self, signal):
        """
        Transition between the touchpad states on the given ``signal``.

        Whenever the given ``signal`` is emitted, this state machine will
        transition between ``touchpad_on`` and ``touchpad_off``.  Use this to
        switch the touchpad, if UI widgets are clicked or actions are
        triggered::

           state_machine.add_touchpad_switch_signal(act.triggered)

        ``signal`` is a bound PyQt signal.
        """
        self.touchpad_not_off.addTransition(signal, self.touchpad_off)
        self.touchpad_off.addTransition(signal, self.touchpad_not_off)

    def _set_touchpad_off(self, off):
        self.touchpad.off = off

    @property
    def monitor_mouses(self):
        """
        ``True``, if the touchpad is to switch, if mouses are plugged or
        unplugged, ``False`` otherwise.

        If ``True``, the state machine will switch the touchpad off, if the
        first mouse is plugged, and on again, if the last mouse is unplugged.
        """
        return self.mouse_manager.is_running

    @monitor_mouses.setter
    def monitor_mouses(self, enabled):
        if enabled and not self.monitor_mouses:
            self.started.connect(self.mouse_manager.start)
            if self.isRunning():
                self.mouse_manager.start()
        elif not enabled and self.monitor_mouses:
            self.mouse_manager.stop()
            self.started.disconnect(self.mouse_manager.start)

    @property
    def monitor_keyboard(self):
        """
        ``True``, if the touchpad is temporarily disabled on keyboard activity,
        ``False`` otherwise.
        """
        return self.keyboard_monitor.is_active

    @monitor_keyboard.setter
    def monitor_keyboard(self, enabled):
        if enabled and not self.monitor_keyboard:
            self.started.connect(self.keyboard_monitor.start)
            if self.isRunning():
                self.keyboard_monitor.start()
        elif not enabled and self.monitor_keyboard:
            self.keyboard_monitor.stop()
            self.started.disconnect(self.keyboard_monitor.start)
