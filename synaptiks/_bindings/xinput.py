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


from ctypes import CDLL, POINTER, Structure, c_int, c_char_p
from ctypes.util import find_library

from synaptiks._bindings.xlib import Display_p
from synaptiks._bindings.util import add_foreign_signatures


c_int_p = POINTER(c_int)


class XIAnyClassInfo(Structure):
    pass


XIAnyClassInfo_p = POINTER(XIAnyClassInfo_p)


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


SIGNATURES = dict(
    XIQueryVersion=([Display_p, c_int_p, c_int_p], c_int, None),
    XIQueryDevice=([Display_p, c_int, c_int_p], XIDeviceInfo_p, None),
    XIFreeDeviceInfo=([XIDeviceInfo_p], None, None),
    )


libXi = add_foreign_signatures(CDLL(find_library('Xi')), SIGNATURES)
