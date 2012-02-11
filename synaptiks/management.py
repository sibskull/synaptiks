# -*- coding: utf-8 -*-
# Copyright (c) 2011, 2012, Sebastian Wiesner <lunaryorn@googlemail.com>
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

    This module implements the touchpad management layer of |synaptiks|, the
    central class is :class:`TouchpadManager`.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from collections import defaultdict

from PyQt4.QtCore import pyqtProperty, QObject, QStateMachine, QState

from synaptiks.monitors import MouseDevicesManager, create_keyboard_monitor


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


class _monitor_property(object):
    """
    A property, which controls a monitor object in a :class:`TouchpadManager`
    """

    def __init__(self, monitor_name, doc):
        self.monitor_name = monitor_name
        self.__doc__ = doc

    def __get__(self, obj, owner=None):
        if obj is None:
            return self
        return self.monitor_name in obj._enabled_monitors

    def __set__(self, obj, enabled):
        if enabled:
            obj._enabled_monitors.add(self.monitor_name)
        else:
            obj._enabled_monitors.discard(self.monitor_name)
        obj._start_stop_monitors()


class TouchpadManager(QStateMachine):
    """
    Manage the touchpad state state.

    Based upon :class:`~PyQt4.QtCore.QStateMachine` this class manages three
    different states according to the following state chart:

    .. digraph:: touchpad_states

       rankdir=LR
       node[fontname="Helvetica",fontsize=14]
       edge[fontname="Helvetica",fontsize=10]
       on
       temporarily_off
       off
       on -> temporarily_off [label="typingStarted"]
       temporarily_off -> on [label="typingStopped"]
       on -> off [label="firstMousePlugged"]
       temporarily_off -> off [label="firstMousePlugged"]
       off -> on [label="lastMouseUnplugged"]
       on -> off [label="triggered"]
       temporarily_off -> off [label="triggered"]
       off -> on [label="triggered"]

    The states shown in these diagram have the following effects on the
    touchpad:

    - ``on``: The touchpad is currently on.  This is the initial state.
    - ``temporarily_off``: The touchpad is automatically switched off
      temporarily (e.g. by keyboard activity)
    - ``off``: The touchpad is permanently off (e.g. by user interaction, or by
      a plugged mouse device)

    Access to these states is provided by the :attr:`states` mapping, the
    transitions between states are available in the :attr:`transitions`
    mapping.
    """

    _STATE_NAMES = dict(on=False, temporarily_off=True, off=True)

    def __init__(self, touchpad, parent=None):
        QStateMachine.__init__(self, parent)
        self.touchpad = touchpad
        self._touchpad_wrapper = TouchpadQtWrapper(self.touchpad, self)
        # setup monitoring objects
        self._monitors = {'mouses': MouseDevicesManager(self),
                          'keyboard': create_keyboard_monitor(self)}
        self._enabled_monitors = set()
        # setup the states:
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
                state, 'off', self._monitors['mouses'].firstMousePlugged)
        self._add_transition(
            'off', 'on', self._monitors['mouses'].lastMouseUnplugged)
        # keyboard management transitions
        self._add_transition('on', 'temporarily_off',
                             self._monitors['keyboard'].typingStarted)
        self._add_transition('temporarily_off', 'on',
                             self._monitors['keyboard'].typingStopped)
        # start monitors
        self.initialState().entered.connect(self._start_stop_monitors)
        # stop monitors if the state machine is stopped
        self.stopped.connect(self._stop_all_monitors)

    def _stop_all_monitors(self):
        """
        Unconditionally stop all monitors.
        """
        for monitor in self._monitors.itervalues():
            monitor.stop()

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
    def current_state(self):
        """
        The current state as :class:`~PyQt4.QtCore.QState` object.
        """
        config = self.configuration()
        if config:
            return config[0]
        return None

    @property
    def current_state_name(self):
        """
        The name of the current state as unicode string.
        """
        if self.current_state:
            return unicode(self.current_state.objectName())

    def _start_stop_monitors(self):
        """
        Reconfigure the internal monitoring.

        If the state machine is running, all enabled monitors are started, and
        all disabled monitors are stopped.  Otherwise this method does nothing.
        """
        if not self.isRunning():
            return
        for monitor_name, monitor in self._monitors.iteritems():
            if monitor_name in self._enabled_monitors:
                monitor.start()
            else:
                monitor.stop()

    @property
    def keyboard_monitor(self):
        """
        The keyboard monitor used by this manager (an instance of a subclass of
        :class:`~synaptiks.monitors.AbstractKeyboardMonitor`).
        """
        return self._monitors['keyboard']

    @property
    def mouse_manager(self):
        """
        The :class:`~synaptiks.monitors.MouseDevicesManager` used by this
        manager.
        """
        return self._monitors['mouses']

    monitor_mouses = _monitor_property('mouses', """\
``True``, if the touchpad is to switch, if mouses are plugged or unplugged,
``False`` otherwise.

If ``True``, the state machine will switch the touchpad off, if the first mouse
is plugged, and on again, if the last mouse is unplugged.
""")

    monitor_keyboard = _monitor_property('keyboard', """\
``True``, if the touchpad is temporarily disabled on keyboard activity,
``False`` otherwise.""")
