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
    synaptiks._bindings.xlib
    ========================

    ctypes-based xlib binding

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from ctypes import (CDLL, Structure, POINTER, string_at,
                    c_uint, c_int, c_void_p, c_char_p)
from ctypes.util import find_library

from synaptiks._bindings.util import add_foreign_signatures


# X11 types
Atom = c_uint
Atom_p = POINTER(Atom)


class Display(Structure):
    pass

Display_p = POINTER(Display)


# X11 definitions as python constants
SUCCESS = 0
# 0 atom
NONE = 0


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
    XFree=([c_void_p], c_int, None),
    XInternAtom=([Display_p, c_char_p, c_int], Atom, None),
    XGetAtomName=([Display_p, Atom], c_void_p, _convert_x11_char_p),
    )


libX11 = add_foreign_signatures(CDLL(find_library('X11')), SIGNATURES)

# add libX11 functions to top-level namespace under pythonic names
free = libX11.XFree
intern_atom = libX11.XInternAtom
get_atom_name = libX11.XGetAtomName
