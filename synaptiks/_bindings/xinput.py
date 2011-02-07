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
    synaptiks._bindings.xinput
    ==========================

    ctypes-based libXi binding.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from ctypes import (CDLL, POINTER, Structure, byref, string_at, cast,
                    c_int, c_char_p, c_long, c_ulong, c_byte)
from ctypes.util import find_library

from synaptiks._bindings import xlib
from synaptiks._bindings.util import add_foreign_signatures, scoped_pointer


c_int_p = POINTER(c_int)
c_ulong_p = POINTER(c_ulong)
c_byte_p = POINTER(c_byte)


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
#: a "magic" device id, identifying all devices in :func:`query_device`
ALL_DEVICES = 0
ANY_PROPERTY_TYPE = 0
PROP_MODE_REPLACE = 0


SIGNATURES = dict(
    XIQueryVersion=([xlib.Display_p, c_int_p, c_int_p], xlib.Status, None),
    XIQueryDevice=([xlib.Display_p, c_int, c_int_p], XIDeviceInfo_p, None),
    XIFreeDeviceInfo=([XIDeviceInfo_p], None, None),
    XIListProperties=([xlib.Display_p, c_int, c_int_p], xlib.Atom_p, None),
    XIGetProperty=([xlib.Display_p, c_int, xlib.Atom, c_long, c_long,
                    xlib.Bool, xlib.Atom, xlib.Atom_p, c_int_p,
                    c_ulong_p, c_ulong_p, POINTER(c_byte_p)],
                   xlib.Status, None),
    XIChangeProperty=([xlib.Display_p, c_int, xlib.Atom, xlib.Atom,
                       c_int, c_int, c_byte_p, c_int], None, None),
    )


libXi = add_foreign_signatures(CDLL(find_library('Xi')), SIGNATURES)


# add libXi functions under pythonic names and with pythonic api to
# top-level namespace
def query_version(display, expected_version):
    """
    Query the server-side XInput version.

    ``display`` is a :class:`~synaptiks._bindings.xlib.Display_p` providing the
    server connection, ``expected_version`` a tuple ``(major, minor)`` with the
    expected version.  Both components are integers.

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

    ``display`` is a :class:`~synaptiks._bindings.xlib.Display_p` providing the
    server connection.  ``deviceid`` is an integer with a device id, or
    :data:`ALL_DEVICES` to query all devices.

    Return a tuple ``(number_of_devices, devices)``.  ``number_of_devices``
    is an integer with the number of devices, ``devices`` is a
    :class:`XIDeviceInfo_p` to a C array of :class:`XIDeviceInfo` objects.
    This array is to be freed using :func:`free_device_info`.

    It is recommended, that you wrap the ``devices`` pointer into
    :func:`~synaptiks._bindings.util.scoped_pointer()` and use a ``with``
    block to make sure, that the allocated memory is freed.
    """
    number_of_devices = c_int(0)
    devices = libXi.XIQueryDevice(display, deviceid,
                                  byref(number_of_devices))
    return (number_of_devices.value, devices)


free_device_info = libXi.XIFreeDeviceInfo


def list_properties(display, deviceid):
    """
    Query all properties of the device with the given ``device_id``.

    The properties are returned as C array of X11 Atoms.  Use
    :func:`~synaptiks._bindings.xlib.get_atom_name` to retrieve the name of
    these properties.

    ``display`` is a :class:`~synaptiks._bindings.xlib.Display_p` providing the
    server connection.  ``deviceid`` is an integer with a device id.

    Return a tuple ``(number_of_properties, property_atoms)``.
    ``number_of_properties`` is an integer with the number of properties.
    ``property_atoms`` is :class:`~synaptiks._bindings.xlib.Atom_p` to a C
    array of :class:`~synaptiks._bindings.xlib.Atom` objects.  This array is
    to be freed using :func:`synaptiks._bindings.xlib.free`.

    It is recommended, that you wrap the ``property_atoms`` pointer into
    :func:`~synaptiks._bindings.util.scoped_pointer()` and use a ``with``
    block to make sure, that the allocated memory is freed.
    """
    number_of_properties = c_int(0)
    property_atoms = libXi.XIListProperties(display, deviceid,
                                            byref(number_of_properties))
    return (number_of_properties.value, property_atoms)


def get_property(display, deviceid, property):
    """
    Get the given ``property`` from the device with the given id.

    ``display`` is a :class:`~synaptiks._bindings.xlib.Display_p` providing the
    server connection, ``deviceid`` is an integer with a device id.
    ``property`` is a :class:`~synaptiks._bindings.xlib.Atom` with the X11 atom
    of the property to get.

    Return a tuple ``(type, format, data)``.  ``type`` and ``format`` are
    integers, ``data`` is a byte string.  If the property exists on the
    device, ``type`` contains the type atom, ``format`` the format of the
    property (on of ``8``, ``16`` or ``32``) and ``data`` the property
    contents as bytes.  Otherwise ``type`` is
    :data:`~synaptiks._bindings.xlib.NONE` and ``format`` is ``0``.
    ``data`` contains an empty string.
    """
    length = 1
    while True:
        type_return = xlib.Atom(0)
        format_return = c_int(0)
        num_items_return = c_ulong(0)
        bytes_after_return = c_ulong(0)
        data = c_byte_p()

        state = libXi.XIGetProperty(
            display, deviceid, property, 0, length, False,
            ANY_PROPERTY_TYPE, byref(type_return), byref(format_return),
            byref(num_items_return), byref(bytes_after_return), byref(data))

        with scoped_pointer(data, xlib.free):
            if state != xlib.SUCCESS:
                # XXX: better diagnostics
                raise EnvironmentError()
            if bytes_after_return.value == 0:
                # got all bytes now, handle them
                format = format_return.value
                type = type_return.value
                number_of_items = num_items_return.value
                byte_length = number_of_items * format // 8
                return (type, format, string_at(data, byte_length))
            else:
                # get some more bytes and try again
                length += 1


def change_property(display, deviceid, property, type, format, data):
    """
    Change the given ``property`` on the device with the given id.

    Properties store binary ``data``.  For the X server to correctly interpret
    the data correctly, it must be assigned a matching ``type`` and ``format``.

    ``display`` is a :class:`~synaptiks._bindings.xlib.Display_p` providing the
    server connection, ``deviceid`` is an integer with a device id.
    ``property`` is a :class:`~synaptiks._bindings.xlib.Atom` with the X11 atom
    of the property to change.  ``type`` is the
    :class:`~synaptiks._bindings.xlib.Atom` describing the type of the
    property, mostly either :data:`~synaptiks._bindings.xlib.INTEGER` or the
    atom for ``'FLOAT'`` (use :class:`~synaptiks._bindings.xlib.intern_atom` to
    create get this atom).  ``format`` is an integer describing the format,
    must either 8, 16 or 32.  The format directly corresponds to the number of
    bytes per item in the property.

    Raise :exc:`~exceptions.ValueError`, if ``format`` is anything else than 8,
    16 or 32.
    """
    if format not in (8, 16, 32):
        raise ValueError(format)
    number_of_items = (len(data) * 8) // format
    libXi.XIChangeProperty(
        display, deviceid, property, type, format, PROP_MODE_REPLACE,
        cast(c_char_p(data), c_byte_p), number_of_items)
