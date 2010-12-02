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
    synaptiks.util
    ==============

    General utilities used throughout synaptiks.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


import sys


def assert_byte_string(s):
    """
    Convert ``s`` to a byte string.

    If ``s`` is already a byte string, it is returned unchanged.  If ``s``
    is a unicode string, it is converted according to
    :func:`sys.getfilesystemencoding()`.
    """
    if isinstance(s, unicode):
        return s.encode(sys.getfilesystemencoding())
    return s


def assert_unicode_string(s):
    """
    Convert ``s`` to a unicode string.

    If ``s`` is already a unicode string, it is returned unchanged.  If
    ``s`` is a byte string, it is converted according to
    :func:`sys.getfilesystemencoding()`.
    """
    if isinstance(s, str):
        return s.decode(sys.getfilesystemencoding())
    return s
