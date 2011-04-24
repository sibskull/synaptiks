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
    synaptiks.xlib
    ==============

    X11 API used by synaptiks

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from ctypes import cast

from synaptiks._bindings import xlib
from synaptiks.util import ensure_byte_string


class DisplayError(EnvironmentError):
    """
    Raised on failure to connect to a X11 display.
    """
    pass


class Display(object):
    """
    A X11 display connection.

    This class supports the context manager protocol.  Upon context exit, it
    closes the display connection::

       with Display.from_name() as display:
           assert display
           # work with the display here
       assert not display

    As you can see above, a :class:`Display` object is ``True`` in a boolean
    context, if and only if it represents an open connection.  You can
    explicitly check, whether the display is open using :attr:`open`.

    A :class:`Display` object can be passed directly to any ctypes-wrapped
    function as ``Display*`` argument.
    """

    def __init__(self, display_pointer):
        if not display_pointer:
            raise DisplayError()
        self._as_parameter_ = display_pointer

    @classmethod
    def from_name(cls, name=None):
        """
        Connect to the display with the given ``name``.

        ``name`` is a byte or unicode string containing the name of a display
        (e.g. ``':0'``).  If ``name`` is ``None``, the value of ``$DISPLAY`` is
        used.

        If ``name`` refers to a non-existing display, or if ``name`` is empty
        and ``$DISPLAY`` is empty or refers to a non-existing display, the
        display connection fails, and :exc:`DisplayError` is raised.

        Return a :class:`Display` object representing the connection to the
        display.  Raise :exc:`DisplayError`, if no display could be opened.
        """
        if name is not None:
            name = ensure_byte_string(name)
        return cls(xlib.open_display(name))

    @classmethod
    def from_qt(cls):
        """
        Create and return a :class:`Display` object from the Qt display
        connection, as available in :meth:`PyQt4.QtGui.QX11Info.display()`.

        Raise :exc:`~exceptions.DisplayError`, if no Qt display connection
        is available.  Raise :exc:`~exceptions.ImportError`, if either
        :mod:`sip` or :mod:`PyQt4.QtGui` are not available.
        """
        import sip
        from PyQt4.QtGui import QX11Info

        display = QX11Info.display()
        if not display:
            raise DisplayError()
        display_address = sip.unwrapinstance(display)
        return cls(cast(display_address, xlib.Display_p))

    def close(self):
        """
        Close this display connection.
        """
        if self:
            xlib.close_display(self)
        self._as_parameter_ = None

    @property
    def open(self):
        """
        ``True``, if this display connection is open, ``False`` otherwise.
        """
        return bool(self._as_parameter_)

    def __nonzero__(self):
        return self.open

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback):
        self.close()
