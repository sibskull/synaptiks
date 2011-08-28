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
    synaptiks._bindings.xlib
    ========================

    Incomplete binding to libX11 atop of :mod:`ctypes`.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from collections import namedtuple
from itertools import islice, izip
from ctypes import (Structure, POINTER, string_at, create_string_buffer,
                    c_uint32, c_int, c_void_p, c_char_p, c_char, c_ubyte,
                    c_ulong)

from synaptiks._bindings.util import load_library, scoped_pointer

c_ubyte_p = POINTER(c_ubyte)

# X11 types
Atom = c_ulong
Atom_p = POINTER(Atom)
Bool = c_int
Status = c_int
Time = c_ulong
KeyCode = c_ubyte
KeyCode_p = c_ubyte_p
XPointer = c_char_p
XID = c_uint32


class Display(Structure):
    pass

Display_p = POINTER(Display)


class XModifierKeymap(Structure):
    _fields_ = [
        ('max_keypermod', c_int),
        ('modifiermap', KeyCode_p)
        ]

XModifierKeymap_p = POINTER(XModifierKeymap)

# Some constants from the libX11 headers
#: :class:`Status` value indicating a successful operation
SUCCESS = 0
#: A non-existing :class:`Atom`
NONE = 0
#: :class:`Atom` for an Atom type
ATOM = 4
#: :class:`Atom` for an Integer type
INTEGER = 19
#: :class:`Atom` for a String type
STRING = 31

# event constants
#: type code for key press event
KEY_PRESS = 2
#: type code for key release event
KEY_RELEASE = 3


def _convert_x11_char_p(c_string, function, args):
    """
    Convert a X11-allocated ``c_string`` return by ``function`` to a Python
    string.  Intended for use as ``errcheck`` attribute of foreign
    functions.

    ``c_string`` is expected to be an integer with a memory address, or a
    :obj:`~ctypes.c_void_p`.  ``function`` is a foreign function object,
    which returned ``c_string``.  ``args`` is a tuple containing the
    arguments passed to the function call.  The two latter arguments are
    present to comply with the ``errcheck`` signature, and are actually
    unused.

    The contents of the C string are copied into a python string, afterwards
    the C string is freed using ``XFree()``.

    Return a python byte string with the contents of ``c_string``, or
    ``None``, if ``c_string`` is a ``NULL`` pointer.
    """
    if c_string:
        python_string = string_at(c_string)
        free(c_string)
        return python_string
    else:
        return None


SIGNATURES = dict(
    XFree=([c_void_p], c_int),
    XOpenDisplay=([c_char_p], Display_p),
    XCloseDisplay=([Display_p], c_int),
    XInternAtom=([Display_p, c_char_p, Bool], Atom),
    XGetAtomName=([Display_p, Atom], c_void_p, _convert_x11_char_p),
    XQueryKeymap=([Display_p, c_char * 32], c_int),
    XGetModifierMapping=([Display_p], XModifierKeymap_p),
    XFreeModifiermap=([XModifierKeymap_p], c_int),
    )


libX11 = load_library('X11', SIGNATURES)


open_display = libX11.XOpenDisplay
close_display = libX11.XCloseDisplay


# add libX11 functions to top-level namespace under pythonic names
def free(ptr):
    """
    Free the given pointer using ``XFree``.

    Unlike ``XFree`` this function is safe for use with a ``NULL`` pointer.
    """
    if ptr:
        libX11.XFree(ptr)


intern_atom = libX11.XInternAtom
get_atom_name = libX11.XGetAtomName


def query_keymap(display):
    """
    Query the current state of the keyboard.

    ``display`` is a :class:`Display_p` providing the server connection.

    Return a tuple ``(state, keymap)``, where ``state`` is an integer with the
    error code of the underlying C function, and ``keymap`` is a byte string
    with the keymap.  This byte string has excatly 32 bytes.  Each bit in this
    byte string corresponds to a single key.  If the key is currently pressed,
    the bit is set, otherwise it is unset.
    """
    buffer = create_string_buffer(32)
    state = libX11.XQueryKeymap(display, buffer)
    return state, buffer.raw


ModifierMap = namedtuple(
    'ModifierMap', 'shift lock control mod1 mod2 mod3 mod4 mod5')


def get_modifier_mapping(display):
    """
    Get the modifier mapping.

    ``display`` is a :class:`Display_p` providing the server connection.

    Return a :class:`ModifierMap` tuple, where each element is another plain
    tuple which contains :data:`KeyCode` objects (which are basically just
    bytes).  Zero keycodes are meaningless in all these tuples.
    """
    modifier_map = libX11.XGetModifierMapping(display)
    with scoped_pointer(modifier_map, libX11.XFreeModifiermap):
        keys_per_modifier = modifier_map.contents.max_keypermod
        keycodes = [modifier_map.contents.modifiermap[i]
                    for i in xrange(8 * keys_per_modifier)]
        modifier_keys = izip(*[islice(keycodes, i, None, keys_per_modifier)
                               for i in xrange(keys_per_modifier)])
        return ModifierMap(*modifier_keys)
