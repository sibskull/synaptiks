# -*- coding: utf-8 -*-
# Copyright (C) 2010 Sebastian Wiesner <lunaryorn@googlemail.com>
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
    synaptiks._bindings.xinput
    ==========================

    ctypes-based libXi binding.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


from ctypes import CDLL, POINTER, Structure, byref, c_int, c_char_p
from ctypes.util import find_library

from synaptiks._bindings import xlib
from synaptiks._bindings.util import add_foreign_signatures


c_int_p = POINTER(c_int)


# XInput types

class XIAnyClassInfo(Structure):
    pass


XIAnyClassInfo_p = POINTER(XIAnyClassInfo)


class XIDeviceInfo(Structure):
    _fields_ = [
        ('deviceid', c_int),
        ('name', c_char_p),
        ('use', c_int),
        ('attachment', c_int),
        ('enabled', c_int),
        ('num_classes', c_int),
        ('classes', POINTER(XIAnyClassInfo_p))]


XIDeviceInfo_p = POINTER(XIDeviceInfo)

# XInput defines as python constants
ALL_DEVICES = 0


SIGNATURES = dict(
    XIQueryVersion=([xlib.Display_p, c_int_p, c_int_p], c_int, None),
    XIQueryDevice=([xlib.Display_p, c_int, c_int_p], XIDeviceInfo_p, None),
    XIFreeDeviceInfo=([XIDeviceInfo_p], None, None),
    )


libXi = add_foreign_signatures(CDLL(find_library('Xi')), SIGNATURES)

# add libXi functions under pythonic names and with pythonic api to
# top-level namespace
def query_version(display, expected_version):
    """
    Query the server-side XInput version.

    ``display`` is a :class:`Display_p` providing the server connection,
    ``expected_version`` a tuple ``(major, minor)`` with the expected
    version.  Both components are integers.

    Return a tuple ``(matched, actual_version)``.  ``matched`` is ``True``,
    if the server-side version is at least the ``expected_version``,
    ``False`` otherwise.  ``actual_version`` is a ``(major, minor)`` tuple
    containing the actual version on the server side.
    """
    major, minor = map(c_int, expected_version)
    state = libXi.XIQueryVersion(display, byref(major), byref(minor))
    return (state == xlib.SUCCESS, (major.value, minor.value))


def query_device(display, deviceid):
    """
    Query the device with the given ``deviceid``.

    ``display`` is a :class:`Display_p` providing the server connection.
    ``deviceid`` is an integer with a device id, or :data:`ALL_DEVICES` to
    query all devices.

    Return a tuple ``(number_of_devices, devices)``.  ``number_of_devices``
    is an integer with the number of devices, ``devices`` is a
    :class:`XIDeviceInfo_p` to a C array of :class:`XIDeviceInfo` objects.
    This array is to be freed using :func:`free_device_info`.

    It is recommended, that you wrap the ``devices`` pointer into
    :func:`~synaptiks._bindings.util.scoped_pointer` and use a ``with``
    block to make sure, that the allocated memory is freed.
    """
    number_of_devices = c_int(0)
    devices = libXi.XIQueryDevice(display, deviceid,
                                  byref(number_of_devices))
    return (number_of_devices.value, devices)


free_device_info = libXi.XIFreeDeviceInfo
