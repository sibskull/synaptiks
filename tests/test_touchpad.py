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

import math

import pytest

from synaptiks.xinput import InputDevice
from synaptiks.touchpad import Touchpad, NoTouchpadError


def pytest_funcarg__touchpad(request):
    display = request.getfuncargvalue('display')
    return Touchpad.find_first(display)

def pytest_funcarg__touchpad_id(request):
    return request.getfuncargvalue('touchpad').id

def pytest_funcarg__touchpad_name(request):
    devices = request.getfuncargvalue('device_database')
    touchpad_id = request.getfuncargvalue('touchpad_id')
    return devices[touchpad_id].name

def pytest_funcarg__touchpad_properties(request):
    devices = request.getfuncargvalue('device_database')
    touchpad_id = request.getfuncargvalue('touchpad_id')
    return devices[touchpad_id].properties

def pytest_funcarg__touchpad_capabilities(request):
    touchpad_properties = request.getfuncargvalue('touchpad_properties')
    return touchpad_properties['Synaptics Capabilities']


def test_inheritance():
    assert issubclass(Touchpad, InputDevice)


@pytest.mark.skipif(b'config.xinput_has_touchpad')
def test_no_touchpad(display):
    assert not Touchpad.find_all()
    with pytest.raises(NoTouchpadError):
        Touchpad.find_first(display)


class TestTouchpad(object):
    pytestmark = pytest.mark.skipif(b'not config.xinput_has_touchpad')

    def test_find_all(self, display):
        touchpads = Touchpad.find_all(display)
        assert touchpads
        assert all(isinstance(t, Touchpad) for t in touchpads)
        assert all('Synaptics Off' in t for t in touchpads)

    def test_find_first(self, display):
        touchpad = Touchpad.find_first(display)
        assert touchpad
        assert 'Synaptics Off' in touchpad
        assert isinstance(touchpad, Touchpad)

    def test_off(self, touchpad, touchpad_properties):
        assert isinstance(touchpad.off, int)
        assert 0 <= touchpad.off <= 2
        assert touchpad.off == touchpad_properties['Synaptics Off'][0]

    def test_move_speed(self, touchpad, touchpad_properties):
        minimum, maximum, accel, trackstick = touchpad_properties[
            'Synaptics Move Speed']
        assert isinstance(touchpad.minimum_speed, float)
        assert isinstance(touchpad.maximum_speed, float)
        assert isinstance(touchpad.acceleration_factor, float)
        assert round(touchpad.minimum_speed, 6) == minimum
        assert round(touchpad.maximum_speed, 6) == maximum
        assert round(touchpad.acceleration_factor, 6) == accel

    def test_edge_motion_always(self, touchpad, touchpad_properties):
        assert isinstance(touchpad.edge_motion_always, bool)
        assert touchpad.edge_motion_always == \
               touchpad_properties['Synaptics Edge Motion Always'][0]

    def test_fast_taps(self, touchpad, touchpad_properties):
        assert isinstance(touchpad.fast_taps, bool)
        assert touchpad.fast_taps == \
               touchpad_properties['Synaptics Tap FastTap'][0]

    def test_tap_action(self, touchpad, touchpad_properties):
        rt, rb, lt, lb, f1, f2, f3 = touchpad_properties[
            'Synaptics Tap Action']
        assert isinstance(touchpad.rt_tap_action, int)
        assert isinstance(touchpad.rb_tap_action, int)
        assert isinstance(touchpad.lt_tap_action, int)
        assert isinstance(touchpad.lb_tap_action, int)
        assert isinstance(touchpad.f1_tap_action, int)
        assert isinstance(touchpad.f2_tap_action, int)
        assert isinstance(touchpad.f3_tap_action, int)
        assert touchpad.rt_tap_action == rt
        assert touchpad.rb_tap_action == rb
        assert touchpad.lt_tap_action == lt
        assert touchpad.lb_tap_action == lb
        assert touchpad.f1_tap_action == f1
        assert touchpad.f2_tap_action == f2
        assert touchpad.f3_tap_action == f3

    def test_gestures(self, touchpad, touchpad_properties):
        assert isinstance(touchpad.tap_and_drag_gesture, bool)
        assert touchpad.tap_and_drag_gesture == \
               touchpad_properties['Synaptics Gestures'][0]

    def test_locked_drags(self, touchpad, touchpad_properties):
        assert isinstance(touchpad.locked_drags, bool)
        assert touchpad.locked_drags == \
               touchpad_properties['Synaptics Locked Drags'][0]

    def test_locked_drags_timeout(self, touchpad, touchpad_properties):
        assert isinstance(touchpad.locked_drags_timeout, float)
        assert int(touchpad.locked_drags_timeout * 1000) == \
               touchpad_properties['Synaptics Locked Drags Timeout'][0]

    def test_edge_scrolling(self, touchpad, touchpad_properties):
        vertical, horizontal, corner = touchpad_properties[
            'Synaptics Edge Scrolling']
        assert isinstance(touchpad.vertical_edge_scrolling, bool)
        assert isinstance(touchpad.horizontal_edge_scrolling, bool)
        assert isinstance(touchpad.corner_coasting, bool)
        assert touchpad.vertical_edge_scrolling == vertical
        assert touchpad.horizontal_edge_scrolling == horizontal
        assert touchpad.corner_coasting == corner

    def test_scrolling_distance(self, touchpad, touchpad_properties):
        vertical, horizontal = touchpad_properties[
            'Synaptics Scrolling Distance']
        assert isinstance(touchpad.vertical_scrolling_distance, int)
        assert isinstance(touchpad.horizontal_scrolling_distance, int)
        assert touchpad.vertical_scrolling_distance == vertical
        assert touchpad.horizontal_scrolling_distance == horizontal

    def test_coasting_speed(self, touchpad, touchpad_properties):
        assert isinstance(touchpad.coasting_speed, float)
        assert round(touchpad.coasting_speed, 6) == \
               round(touchpad_properties['Synaptics Coasting Speed'][0], 6)

    def test_two_finger_scrolling(self, touchpad, touchpad_properties):
        vertical, horizontal = touchpad_properties[
            'Synaptics Two-Finger Scrolling']
        assert isinstance(touchpad.vertical_two_finger_scrolling, bool)
        assert isinstance(touchpad.horizontal_two_finger_scrolling, bool)
        assert touchpad.vertical_two_finger_scrolling == vertical
        assert touchpad.horizontal_two_finger_scrolling == horizontal

    def test_circular_scrolling(self, touchpad, touchpad_properties):
        assert isinstance(touchpad.circular_scrolling, bool)
        assert touchpad.circular_scrolling == \
               touchpad_properties['Synaptics Circular Scrolling'][0]

    def test_circular_scrolling_trigger(self, touchpad, touchpad_properties):
        assert isinstance(touchpad.circular_scrolling_trigger, int)
        assert touchpad.circular_scrolling_trigger < 8
        assert touchpad.circular_scrolling_trigger == \
               touchpad_properties['Synaptics Circular Scrolling Trigger'][0]

    def test_circular_scrolling_distance(self, touchpad, touchpad_properties):
        assert isinstance(touchpad.circular_scrolling_distance, float)
        distance = math.degrees(
            touchpad_properties['Synaptics Circular Scrolling Distance'][0])
        assert round(touchpad.circular_scrolling_distance, 4) == \
               round(distance, 4)

    def test_circular_touchpad(self, touchpad, touchpad_properties):
        assert isinstance(touchpad.circular_touchpad, bool)
        assert touchpad.circular_touchpad == \
               touchpad_properties['Synaptics Circular Pad'][0]

    def test_coasting(self, touchpad, touchpad_properties):
        assert isinstance(touchpad.coasting, bool)
        if touchpad_properties['Synaptics Coasting Speed'][0] == 0:
            assert not touchpad.coasting
        else:
            assert touchpad.coasting

    def test_capabilities(self, touchpad, touchpad_capabilities):
        assert all(isinstance(v, bool) for v in touchpad.capabilities)
        assert touchpad.capabilities == touchpad_capabilities

    def test_finger_detection(self, touchpad, touchpad_capabilities):
        assert isinstance(touchpad.finger_detection, int)
        if touchpad_capabilities[4]:
            assert touchpad.finger_detection == 3
        elif touchpad_capabilities[3]:
            assert touchpad.finger_detection == 2
        else:
            assert touchpad.finger_detection == 1

    def test_buttons(self, touchpad, touchpad_capabilities):
        assert touchpad.buttons.left == touchpad_capabilities[0]
        assert touchpad.buttons.middle == touchpad_capabilities[1]
        assert touchpad.buttons.right == touchpad_capabilities[2]

    def test_has_pressure_detection(self, touchpad, touchpad_capabilities):
        assert isinstance(touchpad.has_pressure_detection, bool)
        assert touchpad.has_pressure_detection == touchpad_capabilities[5]

    def test_has_finger_width_detection(self, touchpad, touchpad_capabilities):
        assert isinstance(touchpad.has_finger_width_detection, bool)
        assert touchpad.has_finger_width_detection == touchpad_capabilities[6]

    def test_has_two_finger_emulation(self, touchpad, touchpad_capabilities):
        assert isinstance(touchpad.has_two_finger_emulation, bool)
        assert touchpad.has_two_finger_emulation == \
               all(touchpad_capabilities[5:7])
