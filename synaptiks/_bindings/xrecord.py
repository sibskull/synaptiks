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

from ctypes import (CDLL, POINTER, CFUNCTYPE, Structure, byref, cast,
                    c_int, c_ulong, c_ubyte, c_ushort, c_uint8, c_uint16)
from ctypes.util import find_library
from contextlib import contextmanager

from synaptiks._bindings import xlib
from synaptiks._bindings.util import add_foreign_signatures, scoped_pointer


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
CURRENT_CLIENTS = 1
FUTURE_CLIENTS = 2
ALL_CLIENTS = 3
FROM_SERVER = 0
FROM_CLIENT = 1
CLIENT_STARTED = 2
CLIENT_DIED = 3
START_OF_DATA = 4
END_OF_DATA = 5


SIGNATURES = dict(
    XRecordQueryVersion=([xlib.Display_p, c_int_p, c_int_p],
                         xlib.Status, None),
    XRecordAllocRange=([], XRecordRange_p, None),
    XRecordCreateContext=([xlib.Display_p, c_int, XRecordClientSpec_p, c_int,
                           POINTER(XRecordRange_p), c_int], XRecordContext,
                          None),
    XRecordFreeContext=([xlib.Display_p, XRecordContext], xlib.Status, None),
    XRecordEnableContext=([xlib.Display_p, XRecordContext,
                           XRecordInterceptProc, xlib.XPointer], xlib.Status,
                          None),
    XRecordDisableContext=([xlib.Display_p, XRecordContext], xlib.Status, None),
    XRecordFreeData=([XRecordInterceptData_p], None, None),
    )


libXtst = add_foreign_signatures(CDLL(find_library('Xtst')), SIGNATURES)


def query_version(display):
    major = c_int()
    minor = c_int()
    state = libXtst.XRecordQueryVersion(display, byref(major), byref(minor))
    return bool(state), (major.value, minor.value)


alloc_range = libXtst.XRecordAllocRange


def record_range():
    return scoped_pointer(alloc_range(), xlib.free)


def create_context(display, flags, client_spec, range):
    client_spec = XRecordClientSpec(client_spec)
    context = libXtst.XRecordCreateContext(
        display, flags, byref(client_spec), 1, byref(range), 1)
    if not context:
        raise EnvironmentError('Could not create record context')
    return context


free_context = libXtst.XRecordFreeContext


@contextmanager
def context(display, flags, client_spec, range):
    context = create_context(display, flags, client_spec, range)
    yield context
    free_context(display, context)


def enable_context(display, context, callback, closure_p):
    state = libXtst.XRecordEnableContext(
        display, context, XRecordInterceptProc(callback), closure_p)
    if state == 0:
        raise EnvironmentError('Could not enable the context')


disable_context = libXtst.XRecordDisableContext

free_data = libXtst.XRecordFreeData
