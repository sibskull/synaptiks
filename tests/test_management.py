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

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import time

import mock
from PyQt4.QtCore import QSignalTransition

from synaptiks.management import TouchpadManager


def pytest_funcarg__touchpad(request):
    touchpad = mock.Mock(name='touchpad', spec_set=['off'])
    touchpad.off = False
    return touchpad


def pytest_funcarg__mouse_device(request):
    from synaptiks.monitors import MouseDevice
    return MouseDevice('serial', 'dummy')


def pytest_funcarg__manager(request):
    touchpad = request.getfuncargvalue('touchpad')
    # make sure, that we have a QApplication object before creating the manager
    request.getfuncargvalue('qtapp')
    manager = TouchpadManager(touchpad)
    request.addfinalizer(manager.stop)
    return manager


class TestTouchpadManager(object):

    def _loop_until(self, qtapp, cond_func):
        while not cond_func():
            qtapp.processEvents()
            time.sleep(0.1)

    def _wait_until_state(self, qtapp, manager, state_name):
        self._loop_until(
            qtapp, lambda: manager.current_state_name == state_name)

    def _wait_until_started(self, qtapp, manager):
        self._loop_until(qtapp, lambda: bool(manager.current_state))

    def _start(self, qtapp, manager):
        manager.start()
        self._wait_until_started(qtapp, manager)

    def _stop(self, qtapp, manager):
        manager.stop()
        self._loop_until(qtapp, lambda: not manager.isRunning())

    def test_keyboard_monitor(self, manager):
        assert manager.keyboard_monitor is manager._monitors['keyboard']

    def test_mouse_manager(self, manager):
        assert manager.mouse_manager is manager._monitors['mouses']

    def test_touchpad(self, manager, touchpad):
        assert manager.touchpad is touchpad

    def test_states(self, manager):
        assert set(manager.states) == set(['off', 'on', 'temporarily_off'])

    def test_all_transitions_present(self, manager):
        assert set(manager.transitions) == set([
            ('on', 'off'), ('temporarily_off', 'off'), ('off', 'on'),
            ('on', 'temporarily_off'), ('temporarily_off', 'on')])

    def test_mouse_transitions_present(self, manager):
        on_off = manager.transitions[('on', 'off')][0]
        temp_off_off = manager.transitions[('temporarily_off', 'off')][0]
        off_on = manager.transitions[('off', 'on')][0]
        for transition in (on_off, temp_off_off, off_on):
            assert isinstance(transition, QSignalTransition)
            assert transition.senderObject() is manager.mouse_manager
        for transition in (on_off, temp_off_off):
            assert 'firstMousePlugged' in str(transition.signal())
        assert 'lastMouseUnplugged' in off_on.signal()

    def test_keyboard_transitions_present(self, manager):
        on_temp_off = manager.transitions[('on', 'temporarily_off')][0]
        temp_off_on = manager.transitions[('temporarily_off', 'on')][0]
        for transition in (on_temp_off, temp_off_on):
            assert isinstance(transition, QSignalTransition)
            assert transition.senderObject() is manager.keyboard_monitor
        assert 'typingStarted' in str(on_temp_off.signal())
        assert 'typingStopped' in str(temp_off_on.signal())

    def test_monitoring_enabled(self, qtapp, manager):
        assert not manager.monitor_mouses
        assert not manager.monitor_keyboard
        manager.monitor_mouses = True
        manager.monitor_keyboard = True
        assert manager.monitor_mouses
        assert manager.monitor_keyboard

    def test_monitor_start_stop(self, qtapp, manager):
        manager.monitor_mouses = True
        manager.monitor_keyboard = True
        self._start(qtapp, manager)
        assert manager.isRunning()
        assert manager.monitor_keyboard
        assert manager.monitor_mouses
        assert manager.keyboard_monitor.is_running
        assert manager.mouse_manager.is_running
        self._stop(qtapp, manager)
        assert not manager.keyboard_monitor.is_running
        assert not manager.mouse_manager.is_running
        assert manager.monitor_keyboard
        assert manager.monitor_mouses

    def test_initial_state(self, qtapp, manager, touchpad):
        self._start(qtapp, manager)
        assert manager.current_state_name == 'on'
        assert not touchpad.off

    def test_keyboard_activity(self, qtapp, manager, touchpad):
        self._start(qtapp, manager)
        manager.keyboard_monitor.typingStarted.emit()
        self._wait_until_state(qtapp, manager, 'temporarily_off')
        assert touchpad.off
        manager.keyboard_monitor.typingStopped.emit()
        self._wait_until_state(qtapp, manager, 'on')
        assert not touchpad.off

    def test_mouse_plugging(self, qtapp, manager, touchpad, mouse_device):
        self._start(qtapp, manager)
        manager.mouse_manager.firstMousePlugged.emit(mouse_device)
        self._wait_until_state(qtapp, manager, 'off')
        assert touchpad.off
        manager.mouse_manager.lastMouseUnplugged.emit(mouse_device)
        self._wait_until_state(qtapp, manager, 'on')
        assert not touchpad.off

    def test_mouse_plugged_after_keyboard_activity(self, qtapp, manager,
                                                   touchpad, mouse_device):
        self._start(qtapp, manager)
        manager.keyboard_monitor.typingStarted.emit()
        self._wait_until_state(qtapp, manager, 'temporarily_off')
        assert touchpad.off
        manager.mouse_manager.firstMousePlugged.emit(mouse_device)
        self._wait_until_state(qtapp, manager, 'off')
        assert touchpad.off
