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
    synaptiks.x11
    =============

    X11 API used by synaptiks

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from ctypes import cast

from synaptiks._bindings import xlib
from synaptiks.util import ensure_byte_string, ensure_unicode_string


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
        self._atom_cache = {}
        self.types = StandardTypes(self)

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

    def intern_atom(self, name, only_if_exists=True):
        """
        Create a new X11 atom with the given ``name``.

        ``name`` is a byte or unicode string with the name of the atom.  If
        ``only_if_exists`` is ``True``, the atom is only created, if it already
        exists.  If it does not exist, ``None`` is returned.

        Return an :class:`Atom` with the given ``name``, or ``None``, if the
        ``only_if_exists`` was ``True`` and the atom did not exist.
        """
        name = ensure_byte_string(name)
        atom = self._atom_cache.get(name)
        if atom:
            return atom
        atom = xlib.intern_atom(self, ensure_byte_string(name), only_if_exists)
        if atom == xlib.NONE:
            return None
        return self._atom_cache.setdefault(name, Atom(self, atom))

    def is_atom_defined(self, name):
        """
        Check, if the atom with the given ``name`` is defined on this display.

        ``name`` is a byte or unicode string with the name of the atom.

        Return ``True``, if the atom is defined, ``False`` otherwise.
        """
        return self.intern_atom(name) is not None

    def __nonzero__(self):
        return self.open

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback):
        self.close()


class StandardTypes(object):
    """
    Standard type atoms defined on all X11 displays.
    """

    def __init__(self, display):
        self.display = display
        self.string = Atom(display, xlib.STRING)
        self.integer = Atom(display, xlib.INTEGER)
        self.float = display.intern_atom('FLOAT')
        self.atom = Atom(display, xlib.ATOM)


class Atom(object):
    """
    An xlib atom.

    Atoms are unique internal, display-specific identifiers in the X11
    protocol.  They are created by :meth:`Display.intern_atom()`.

    Atoms are hashable and comparable to other atoms and to integers.
    """

    def __init__(self, display, value):
        """
        Create a new atom on the given ``display`` with the given atom ``value``.

        ``display`` is a :class:`Display`.  ``value`` is an integral atom
        value.

        Normally you should create atoms by :meth:`Display.intern_atom`.  Use
        this only to wrap integral atoms you retrieve from other xlib
        functions.
        """
        self.display = display
        self._as_parameter_ = value

    @property
    def value(self):
        """
        The integral value of this atom.
        """
        return self._as_parameter_

    @property
    def name(self):
        """
        The name of this atom as unicode string.
        """
        return ensure_unicode_string(xlib.get_atom_name(self.display, self))

    def __unicode__(self):
        return self.name

    def __str__(self):
        return ensure_byte_string(self.name)

    def __repr__(self):
        return '{0!r} ({1})'.format(self.name, self.value)

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        if isinstance(other, Atom):
            other = other._as_parameter_
        return self._as_parameter_ == other

    def __ne__(self, other):
        return not (self == other)
