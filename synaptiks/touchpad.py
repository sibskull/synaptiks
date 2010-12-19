# -*- coding: utf-8 -*-
# Copyright (c) 2010, Sebastian Wiesner <lunaryorn@googlemail.com>
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
    synaptiks.touchpad
    ==================

    This module provides the :class:`Touchpad` class, which provides access to
    the touchpads on this system.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import math
from functools import partial
from collections import namedtuple

from synaptiks.qxinput import InputDevice


PhysicalButtons = namedtuple('PhysicalButtons', 'left middle right')


class device_property(object):
    """
    An attribute mapped to a property of an input device.
    """

    PROPERTY_TYPES = ('int', 'byte', 'float', 'bool')

    def __init__(self, property_name, property_type, item, doc=None):
        """
        ``property_name`` is the property name as string.  ``property_type`` is
        the type of the property as string (one of ``('int', 'byte', 'float',
        'bool')``).  ``item`` is the integral number of the item to access in
        the given property.  ``doc`` is the docstring of the descriptor in the
        owner class.

        Raise :exc:`~exceptions.ValueError`, if ``type`` is an invalid value.
        """
        if property_type not in self.PROPERTY_TYPES:
            raise ValueError('invalid type: {0!r}'.format(type))
        self.property_name = property_name
        self.property_type = property_type
        self.item = item
        self.__doc__ = doc

    def __get__(self, obj, owner=None):
        values = obj[self.property_name]
        if self.property_type == 'bool':
            values = map(bool, values)
        return self.convert_from_property(values[self.item])

    def __set__(self, obj, value):
        values = obj[self.property_name]
        values[self.item] = self.convert_to_property(value)
        set_property = getattr(obj, 'set_{0}'.format(self.property_type))
        set_property(self.property_name, values)

    def convert_from_property(self, value):
        """
        Convert the given ``value`` from the actual property value.
        """
        return value

    def convert_to_property(self, value):
        """
        Convert the given ``value`` to the actual property value.
        """
        return value


class Touchpad(InputDevice):
    """
    A touchpad registered on the X11 server.

    This class is a child of :class:`~synaptiks.qxinput.InputDevice`,
    consequently all of the input device methods are available on this class as
    well.  Additionally this class provides special methods and properties
    specific to touchpads.

    It is recommended, that you use these whenever possible instead of directly
    accessing the device properties.
    """

    def __init__(self, id):
        InputDevice.__init__(self, id)

    @classmethod
    def find_all(cls):
        """
        Find all touchpad devices present in this system.

        Return an iterator over all :class:`Touchpad` objects present on this
        system.

        Raise :exc:`XInputVersionError`, if the XInput version isn't sufficient
        to support input device management.
        """
        return cls.find_devices_with_property('Synaptics Off')

    @classmethod
    def find_first(cls):
        """
        Find the first usable touchpad device on this system.

        Return a :class:`Touchpad` object for this device or ``None``, if
        theere is no touchpad on this system.

        Raise :exc:`XInputVersionError`, if the XInput version isn't sufficient
        to support input device management.
        """
        return next(cls.find_all(), None)

    _move_speed_property = partial(device_property,
                                   'Synaptics Move Speed', 'float')
    minimum_speed = _move_speed_property(
        0, 'The minimum speed of cursor movement as float')
    maximum_speed = _move_speed_property(
        1, 'The maximum speed of cursor movement as float')
    acceleration_factor = _move_speed_property(
        2, 'The acceleration factor of cursor movement as float')

    edge_motion_always = device_property(
        'Synaptics Edge Motion Always', 'bool', 0,
        '``True`` if edge motion is enabled, ``False`` otherwise.')

    fast_taps = device_property(
        'Synaptics Tap FastTap', 'bool', 0,
        '``True`` if edge taps are enabled, ``False`` otherwise.')

    _tap_action_property = partial(device_property,
                                   'Synaptics Tap Action', 'byte')
    rt_tap_action = _tap_action_property(
        0, 'Tap action for the right top corner')
    rb_tap_action = _tap_action_property(
        1, 'Tap action for the right bottom corner')
    lt_tap_action = _tap_action_property(
        2, 'Tap action for the left top corner')
    lb_tap_action = _tap_action_property(
        3, 'Tap action for the left bottom corner')
    f1_tap_action = _tap_action_property(4, 'Action for a one-finger tap')
    f2_tap_action = _tap_action_property(5, 'Action for a two-finger tap')
    f3_tap_action = _tap_action_property(6, 'Action for a three-finger tap')

    tap_and_drag_gesture = device_property(
        'Synaptics Gestures', 'bool', 0,
        '``True``, if the tap and drag gesture is enabled, ``False`` otherwise')

    locked_drags = device_property(
        'Synaptics Locked Drags', 'bool', 0,
        '``True``, if locked drags are enabled, ``False`` otherwise')

    locked_drags_timeout = device_property(
        'Synaptics Locked Drags Timeout', 'int', 0,
        'The timeout of locked drags in seconds as float')
    locked_drags_timeout.convert_from_property = lambda v: v / 1000
    locked_drags_timeout.convert_to_property = lambda v: int(1000*v)

    _edge_scrolling_property = partial(device_property,
                                       'Synaptics Edge Scrolling', 'bool')
    vertical_edge_scrolling = _edge_scrolling_property(
        0, '``True``, if vertical edge scrolling is enabled, ``False`` '
        'otherwise')
    horizontal_edge_scrolling = _edge_scrolling_property(
        1, '``True``, if horizontal edge scrolling is enabled, ``False`` '
        'otherwise')
    corner_coasting = _edge_scrolling_property(
        0, '``True``, if corner coasting is enabled, ``False`` otherwise')

    _scrolling_distance_property = partial(
        device_property, 'Synaptics Scrolling Distance', 'int')
    vertical_scrolling_distance = _scrolling_distance_property(
        0, 'The vertical scrolling distance as int')
    horizontal_scrolling_distance = _scrolling_distance_property(
        1, 'The horizontal scrolling distance as int')

    coasting_speed = device_property(
        'Synaptics Coasting Speed', 'float', 0, 'The coasting speed as float')

    _two_finger_scrolling_property = partial(
        device_property, 'Synaptics Two-Finger Scrolling', 'bool')
    vertical_two_finger_scrolling = _two_finger_scrolling_property(
        0, '``True``, if vertical two-finger scrolling is enabled, ``False`` '
        'otherwise')
    horizontal_two_finger_scrolling = _two_finger_scrolling_property(
        1, '``True``, if horizontal two-finger scrolling is enabled, '
        '``False`` otherwise')

    circular_scrolling = device_property(
        'Synaptics Circular Scrolling', 'bool', 0,
        '``True``, if circular scrolling is enabled, ``False`` otherwise')

    circular_scrolling_trigger = device_property(
        'Synaptics Circular Scrolling Trigger', 'byte', 0,
        'The trigger area for circular scrolling')

    circular_scrolling_distance = device_property(
        'Synaptics Circular Scrolling Distance', 'float', 0,
        'The circular scrolling distance in degrees as float.')
    circular_scrolling_distance.convert_from_property = math.degrees
    circular_scrolling_distance.convert_to_property = math.radians

    @property
    def coasting(self):
        """
        ``True``, if coasting is enabled, ``False`` otherwise.

        Readonly, set :attr:`coasting_speed` to a non-zero value to enable
        coasting.
        """
        return self.coasting_speed != 0

    @property
    def capabilities(self):
        """
        The capabilities of the touchpad.

        This is a list of seven boolean values, indicating the following
        capabilities (in the order of the list items):

        - the touchpad has a left button
        - the touchpad has a middle button
        - the touchpad has a right button
        - the touchpad can detect two fingers
        - the touchpad can detect three fingers
        - the touchpad can detect the pressure of a touch
        - the touchpad can detect the width of a finger
        """
        return map(bool, self['Synaptics Capabilities'])

    @property
    def finger_detection(self):
        """
        The number of fingers, this touchpad can independently detect upon a
        touch, as integer.
        """
        finger_capabilities = self.capabilities[3:5]
        return sum(finger_capabilities, 1)

    @property
    def buttons(self):
        """
        The physical mouse buttons, this touchpad has, as a named tuple with
        the following three components (in corresponding order):

        - ``left``: a physical left button
        - ``middle``: a physical middle button
        - ``right``: a physical right button

        Each component is ``True``, if the touchpad has this physical button,
        or ``False`` otherwise.
        """
        return PhysicalButtons(self.capabilities[0:3])

    @property
    def has_pressure_detection(self):
        """
        ``True``, if this touchpad can detect the pressure of a touch,
        ``False`` otherwise.
        """
        return self.capabilities[5]

    @property
    def has_finger_width_detection(self):
        """
        ``True``, if this touchpad can detect the width of a finger upon touch,
        ``False`` otherwise.
        """
        return self.capabilities[6]

    @property
    def has_two_finger_emulation(self):
        """
        ``True``, if this touchpad supports two finger emulation, ``False``
        otherwise.

        Many older touchpads are unable to detect multiple fingers
        independently, which is required for features like two finger
        scrolling.  Some of these however can at least emulate this by
        detecting the width of a finger and the pressure upon a touch.
        """
        return all(self.capabilities[5:7])
