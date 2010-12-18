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

from synaptiks.qxinput import InputDevice


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

    TYPESCHEME = {
        'Synaptics Edges': ('int', 4),
        'Synaptics Finger': ('int', 3),
        'Synaptics Tap Time': ('int', 1),
        'Synaptics Tap Move': ('int', 1),
        'Synaptics Tap Durations': ('int', 3),
        'Synaptics Tap FastTap': ('bool', 1),
        'Synaptics Middle Button Timeout': ('int', 1),
        'Synaptics Two-Finger Pressure': ('int', 1),
        'Synaptics Two-Finger Width': ('int', 1),
        'Synaptics Scrolling Distance': ('int', 2),
        'Synaptics Edge Scrolling': ('bool', 3),
        'Synaptics Two-Finger Scrolling': ('bool', 2),
        'Synaptics Move Speed': ('float', 4),
        'Synaptics Edge Motion Pressure': ('int', 2),
        'Synaptics Edge Motion Speed': ('int', 2),
        'Synaptics Edge Motion Always': ('bool', 1),
        'Synaptics Off': ('byte', 1),
        'Synaptics Locked Drags': ('bool', 1),
        'Synaptics Locked Drags Timeout': ('int', 1),
        'Synaptics Tap Action': ('byte', 7),
        'Synaptics Click Action': ('byte', 3),
        'Synaptics Circular Scrolling': ('bool', 1),
        'Synaptics Circular Scrolling Distance': ('float', 1),
        'Synaptics Circular Scrolling Trigger': ('byte', 1),
        'Synaptics Circular Pad': ('byte', 1),
        'Synaptics Palm Detection': ('byte', 1),
        'Synaptics Palm Dimensions': ('int', 2),
        'Synaptics Coasting Speed': ('float', 2),
        'Synaptics Pressure Motion': ('int', 2),
        'Synaptics Pressure Motion Factor': ('float', 2),
        'Synaptics Grab Event Device': ('bool', 1),
        'Synaptics Gestures': ('bool', 1),
        }


    def __init__(self, id):
        InputDevice.__init__(self, id)
        self.typescheme = dict(self.TYPESCHEME)

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
        """
        return self.capabilities[0:3]

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


class TouchpadConfig(dict):
    """
    Touchpad configuration class.

    This class provides an easier interface to touchpad configuration than the
    touchpad properties themselves.
    """

    #: Map touchpad properties to configuration keys.  The values in this
    #: dictionary are tuples containing configuration keys, in the order they
    #: appear in the property (which is the key)
    PROPERTY_CONFIG_MAP = {
        'Synaptics Move Speed': ('minimum_speed', 'maximum_speed',
                                 'acceleration_factor'),
        'Synaptics Edge Motion Always': ('edge_motion_always',),
        }

    @classmethod
    def from_touchpad(cls, touchpad):
        """
        Extract the touchpad configuration from the given ``touchpad`` device.

        ``touchpad`` is a :class:`Touchpad` object.

        Return a :class:`TouchpadConfig` object.
        """
        config = cls()
        for property, item_names in cls.PROPERTY_CONFIG_MAP.iteritems():
            values = touchpad[property]
            config.update(zip(item_names, values))
        return config
