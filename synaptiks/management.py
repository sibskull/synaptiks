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

from collections import defaultdict

from PyQt4.QtCore import (pyqtSignal, pyqtProperty, QObject,
                          QStateMachine, QState)

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


class TouchpadQtWrapper(QObject):

    def __init__(self, touchpad, parent=None):
        QObject.__init__(self, parent)
        self.touchpad = touchpad

    @pyqtProperty(int)
    def off(self):
        return self.touchpad.off

    @off.setter
    def off(self, value):
        self.touchpad.off = value


class TouchpadManager(QStateMachine):
    """
    Manage the touchpad state state.

    Based upon :class:`~PyQt4.QtCore.QStateMachine` this class manages four
    different states of the touchpad.

    - ``on``: The touchpad is currently on.  This is the initial state.
    - ``temporarily_off``: The touchpad is automatically switched off
      temporarily (e.g. by keyboard activity)
    - ``off``: The touchpad is permanently off (e.g. by user interaction, or by
      a plugged mouse device)

    The :attr:`states` mapping represents the states.  It the names of these
    states to :class:`~PyQt4.QtCore.QState` objects, which represent these
    states.  You may freely access these objects, and for instance connect to
    their ``entered()`` signals to display notifications or something like
    this.  The state names are also the object names of the state objects.

    The :attr:`transitions` mapping represents the transitions between these
    states.  It maps pairs of state names in the form ``(source, destination)``
    to a list of :class:`~PyQt4.QtCore.QAbstractTransition`-derived objects,
    each of which represents a single transition from the ``source`` state to
    the ``destination`` state.
    """

    _STATE_NAMES = dict(on=False, temporarily_off=True, off=True)

    def __init__(self, touchpad, parent=None):
        QStateMachine.__init__(self, parent)
        self.touchpad = touchpad
        self._touchpad_wrapper = TouchpadQtWrapper(self.touchpad, self)
        # setup monitoring objects
        self.mouse_manager = MouseDevicesManager(self)
        self.keyboard_monitor = PollingKeyboardMonitor(self)
        # setup the states
        self.states = {}
        for name, touchpad_off in self._STATE_NAMES.iteritems():
            state = QState(self)
            state.setObjectName(name)
            state.assignProperty(self._touchpad_wrapper, 'off', touchpad_off)
            self.states[name] = state
        # setup the initial state
        self.setInitialState(self.states['on'])
        # setup the transitions
        self.transitions = defaultdict(list)
        # mouse management transitions
        for state in ('on', 'temporarily_off'):
            self._add_transition(
                state, 'off', self.mouse_manager.firstMousePlugged)
        self._add_transition(
            'off', 'on', self.mouse_manager.lastMouseUnplugged)
        # keyboard management transitions
        self._add_transition('on', 'temporarily_off',
                             self.keyboard_monitor.typingStarted)
        self._add_transition('temporarily_off', 'on',
                             self.keyboard_monitor.typingStopped)

    def _add_transition(self, source, dest, signal):
        if isinstance(source, basestring):
            source = self.states[source]
        if isinstance(dest, basestring):
            dest = self.states[dest]
        transition = source.addTransition(signal, dest)
        source_name = unicode(source.objectName())
        dest_name = unicode(dest.objectName())
        self.transitions[(source_name, dest_name)].append(transition)

    def add_touchpad_switch_action(self, action):
        """
        Add the given ``action`` to switch the touchpad manually.

        Whenever the given ``action`` is triggered, the state machine
        transitions from ``on`` and ``temporarily_off`` to ``off``
        and back from ``off`` to ``on``.
        """
        for state in ('on', 'temporarily_off'):
            self._add_transition(state, 'off', action.triggered)
        self._add_transition('off', 'on', action.triggered)

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
            # start the manager, if the initial state is entered
            self.initialState().entered.connect(self.mouse_manager.start)
            if self.isRunning():
                self.mouse_manager.start()
        elif not enabled and self.monitor_mouses:
            self.mouse_manager.stop()
            self.initialState().entered.disconnect(self.mouse_manager.start)

    @property
    def monitor_keyboard(self):
        """
        ``True``, if the touchpad is temporarily disabled on keyboard activity,
        ``False`` otherwise.
        """
        return self.keyboard_monitor.is_running

    @monitor_keyboard.setter
    def monitor_keyboard(self, enabled):
        if enabled and not self.monitor_keyboard:
            self.started.connect(self.keyboard_monitor.start)
            if self.isRunning():
                self.keyboard_monitor.start()
        elif not enabled and self.monitor_keyboard:
            self.keyboard_monitor.stop()
            self.started.disconnect(self.keyboard_monitor.start)
