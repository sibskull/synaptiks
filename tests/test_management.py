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

    def test_initial_state(self, qtapp, manager, touchpad):
        manager.start()
        while not manager.current_state:
            qtapp.processEvents()
        assert manager.current_state_name == 'on'
        assert not touchpad.off

    def test_keyboard_activity(self, qtapp, manager, touchpad):
        manager.start()
        while manager.current_state_name != 'temporarily_off':
            manager.keyboard_monitor.typingStarted.emit()
            qtapp.processEvents()
        assert touchpad.off
        while manager.current_state_name != 'on':
            manager.keyboard_monitor.typingStopped.emit()
            qtapp.processEvents()
        assert not touchpad.off

    def test_mouse_plugging(self, qtapp, manager, touchpad, mouse_device):
        manager.start()
        while manager.current_state_name != 'off':
            manager.mouse_manager.firstMousePlugged.emit(mouse_device)
            qtapp.processEvents()
        assert touchpad.off
        while manager.current_state_name != 'on':
            manager.mouse_manager.lastMouseUnplugged.emit(mouse_device)
            qtapp.processEvents()
        assert not touchpad.off
