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
    synaptiks._qxlib
    ================

    Wrap libX11 functions to a automatically use the Qt X11 display.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from ctypes import cast
from functools import wraps

import sip
from PyQt4.QtGui import QX11Info

from synaptiks._xlib import Display_p, libX11


class QX11Display(object):
    """
    Wrapper around the Qt X11 Display (as returned by
    :meth:`PyQt4.QtGui.QX11Info.display()`) to make the display available as
    argument for ctypes-wrapped foreign functions from Xlib.

    If used as argument to a foreign function, this object is cast into a
    proper Display pointer.
    """

    def __init__(self):
        display = QX11Info.display()
        if not display:
            raise ValueError('A Qt X11 display connection is required. '
                             'Create a QApplication object')
        display_address = sip.unwrapinstance(display)
        self._as_parameter_ = cast(display_address, Display_p)


def _wrap_in_qx11_display(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        return function(QX11Display(), *args, **kwargs)
    return wrapped


#: wrapper around XInternAtom, which implicitly uses :class:`QX11Display`
InternAtom = _wrap_in_qx11_display(libX11.XInternAtom)
#: wrapper around XGetAtomName, which implicitly uses :class:`QX11Display`
GetAtomName = _wrap_in_qx11_display(libX11.XGetAtomName)
