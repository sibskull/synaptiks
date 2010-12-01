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
from functools import partial

import sip
from PyQt4.QtGui import QX11Info

from synaptiks._xlib import Display_p, libX11


class QX11Display(object):
    @property
    def _as_parameter_(self):
        display_address = sip.unwrapinstance(QX11Info.display())
        return cast(display_address, Display_p)


InternAtom = partial(libX11.XInternAtom, QX11Display())
GetAtomName = partial(libX11.XGetAtomName, QX11Display())
