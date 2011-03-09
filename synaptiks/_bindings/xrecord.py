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
    synaptiks._bindings.xrecord
    ===========================

    Incomplete binding to the XRecord extension atop of :mod:`ctypes`.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from ctypes import (POINTER, CFUNCTYPE, Structure, byref, cast,
                    c_int, c_ulong, c_ubyte, c_ushort, c_uint8, c_uint16)
from contextlib import contextmanager

from synaptiks._bindings import xlib
from synaptiks._bindings.util import load_library, scoped_pointer


c_int_p = POINTER(c_int)
c_ubyte_p = POINTER(c_ubyte)

# types and type defs from XRecord
XRecordClientSpec = c_ulong
XRecordContext = c_ulong
XRecordClientSpec_p = POINTER(XRecordClientSpec)

class XRecordRange8(Structure):
    _fields_ = [('first', c_ubyte), ('last', c_ubyte)]

class XRecordRange16(Structure):
    _fields_ = [('first', c_ushort), ('last', c_ushort)]

class XRecordExtRange(Structure):
    _fields_ = [('ext_major', XRecordRange8), ('ext_minor', XRecordRange16)]


class XRecordRange(Structure):
    _fields_ = [
        ('core_requests', XRecordRange8),
        ('core_replies', XRecordRange8),
        ('ext_requests', XRecordExtRange),
        ('ext_replies', XRecordExtRange),
        ('delivered_events', XRecordRange8),
        ('device_events', XRecordRange8),
        ('errors', XRecordRange8),
        ('client_started', xlib.Bool),
        ('client_died', xlib.Bool),
        ]

XRecordRange_p = POINTER(XRecordRange)

class XRecordInterceptData(Structure):
    _fields_ = [
        ('id_base', xlib.XID),
        ('server_time', xlib.Time),
        ('client_seq', c_ulong),
        ('category', c_int),
        ('client_swapped', xlib.Bool),
        ('data', c_ubyte_p),
        ('data_len', c_ulong)]

    @property
    def event(self):
        event = cast(self.data, XEvent_p)
        return (event.contents.type, event.contents.detail)


XRecordInterceptData_p = POINTER(XRecordInterceptData)


class XEvent(Structure):
    _fields_ = [('type', c_uint8), ('detail', c_uint8),
                ('sequenceNumber', c_uint16, 16)]


XEvent_p = POINTER(XEvent)


XRecordInterceptProc = CFUNCTYPE(None, xlib.XPointer, XRecordInterceptData_p)


# Some constants from XRecord
# client specs
#: Record data from all current clients
CURRENT_CLIENTS = 1
#: Record data from all future clients
FUTURE_CLIENTS = 2
#: Record data from all clients
ALL_CLIENTS = 3
# event categories
#: Event originating from server
FROM_SERVER = 0
#: Event originating from client
FROM_CLIENT = 1
#: A client was started
CLIENT_STARTED = 2
#: A client died
CLIENT_DIED = 3
#: Start of data (first event after call to :func:`enable_context`)
START_OF_DATA = 4
#: End of data (last event after call to :func:`disable_context`)
END_OF_DATA = 5


SIGNATURES = dict(
    XRecordQueryVersion=([xlib.Display_p, c_int_p, c_int_p], xlib.Status),
    XRecordAllocRange=([], XRecordRange_p, None),
    XRecordCreateContext=([xlib.Display_p, c_int, XRecordClientSpec_p, c_int,
                           POINTER(XRecordRange_p), c_int], XRecordContext),
    XRecordFreeContext=([xlib.Display_p, XRecordContext], xlib.Status),
    XRecordEnableContext=([xlib.Display_p, XRecordContext,
                           XRecordInterceptProc, xlib.XPointer], xlib.Status),
    XRecordDisableContext=([xlib.Display_p, XRecordContext], xlib.Status),
    XRecordFreeData=([XRecordInterceptData_p], None),
    )


libXtst = load_library('Xtst', SIGNATURES)


def query_version(display):
    """
    Query the xrecord version available on the given ``display``.

    ``display`` is an X11 display connection
    (e.g. :class:`~synaptiks._bindings.xlib.Display_p` or
    :class:`~synaptiks.qx11.QX11Display`).

    Return a tuple ``(success, version)``.  ``success`` is a boolean flag
    inidicating, whether XRecord is available on the given display.
    ``version`` is a tuple ``(major, minor)``, where ``major`` and ``minor``
    are integers holding the corresponding component of the XRecord version
    number.
    """
    major = c_int()
    minor = c_int()
    state = libXtst.XRecordQueryVersion(display, byref(major), byref(minor))
    return bool(state), (major.value, minor.value)


alloc_range = libXtst.XRecordAllocRange


@contextmanager
def record_range(device_events=None):
    """
    Create a recording range for the given ``device_events`` and wrap it
    into a context manager.

    ``device_events`` is a two-component tuple ``(first, last)``, where
    ``first`` is the first event to be recorded, and ``last`` is the last
    event.

    Return a :class:`XRecordRange_p` object containing the record range.
    """
    with scoped_pointer(alloc_range(), xlib.free) as record_range_p:
        record_range = record_range_p.contents
        if device_events:
            first, last = device_events
            record_range.device_events.first = first
            record_range.device_events.last = last
        yield record_range_p


def create_context(display, flags, client_spec, range):
    client_spec = XRecordClientSpec(client_spec)
    context = libXtst.XRecordCreateContext(
        display, flags, byref(client_spec), 1, byref(range), 1)
    if not context:
        raise EnvironmentError('Could not create record context')
    return context


free_context = libXtst.XRecordFreeContext


@contextmanager
def context(display, client_spec, device_events=None):
    """
    Create a XRecord context and wrap it into a context manager:

    >>> with context(display, ALL_CLIENTS, (KEY_PRESS, KEY_RELEASE)) as context:
    ...     enable_context(display, context, callback, None)

    ``display`` is an X11 display connection
    (e.g. :class:`~synaptiks._bindings.xlib.Display_p` or
    :class:`~synaptiks.qx11.QX11Display`).  ``client_spec`` is one of
    :data:`CURRENT_CLIENTS`, :data:`FUTURE_CLIENTS` or :data:`ALL_CLIENTS`.
    ``device_events`` is a two-component tuple ``(first, last)``, where
    ``first`` is the first device event to be recorded, and ``last`` is the
    last event.

    Upon entry the context manager yields a :class:`XRecordContext` object,
    which points to the allocated recording context.  The context is freed upon
    exit.
    """
    with record_range(device_events=device_events) as rr:
        context = create_context(display, 0, client_spec, rr)
        yield context
        free_context(display, context)


def enable_context(display, context, callback, closure_p):
    """
    Enable the given ``context`` on the given ``display``.

    ``display`` is an X11 display connection
    (e.g. :class:`~synaptiks._bindings.xlib.Display_p` or
    :class:`~synaptiks.qx11.QX11Display`).  ``context`` is a
    :class:`XRecordContext` object.  ``callback`` is a function, taking two
    arguments:

    - The unchanged ``closure_p`` as first
    - The recorded protocol data as :class:`XRecordInterceptData_p` object.
      This data must be freed using :func:`free_data`

    `closure_p` is a :class:`~synaptiks._bindings.xlib.XPointer` object
    pointing to an arbitrary memory location.  It is passed through to the
    callback.

    Raise :exc:`~exceptions.EnvironmentError`, if the context could not be
    enabled.
    """
    state = libXtst.XRecordEnableContext(
        display, context, XRecordInterceptProc(callback), closure_p)
    if state == 0:
        raise EnvironmentError('Could not enable the context')


disable_context = libXtst.XRecordDisableContext

free_data = libXtst.XRecordFreeData
