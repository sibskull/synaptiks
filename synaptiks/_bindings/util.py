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
    synaptiks._bindings.util
    ========================

    Internal utility functions for bindings

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from ctypes import CDLL
from ctypes.util import find_library
from contextlib import contextmanager


def load_library(name, signatures=None):
    """
    Load the C library with the given ``name``.

    ``name`` is a string containing a generic library name (as for
    :func:`ctypes.util.find_library`).  If ``signatures`` is given, it must be
    a dictionary with signatures of functions of the library, see
    :func:`add_foreign_signatures` for details.

    Return a :class:`ctypes.CDLL` wrapping the library.  Raise
    :exc:`~exceptions.ImportError`, if the library was not found.
    """
    library_name = find_library(name)
    if not library_name:
        raise ImportError('No library named {0}'.format(name))
    library = CDLL(library_name)
    if signatures:
        library = add_foreign_signatures(library, signatures)
    return library


def add_foreign_signatures(library, signatures):
    """
    Add ``signatures`` of a foreign ``library`` to the symbols defined in
    this library.

    ``library`` is a :class:`~ctypes.CDLL` object, wrapping a foreign
    library.  ``signatures`` is a dictionary, which specifies signatures for
    symbols defined in this library.  It maps the name of a function to a
    three element tuple ``(argument_types, return_type, error_checker)``.
    ``argument_types`` is a list of argument types (see
    :attr:`~ctypes._FuncPtr.argtypes`), ``return_type`` is the return type
    (see :attr:`~ctypes._FuncPtr.restype`) and ``error_checker`` is a
    function used as error checker (see :attr:``~ctypes._FuncPtr.errcheck`).
    ``error_checker`` may be ``None``, in which case no error checking
    function is defined.

    Return the ``library`` object again.
    """
    for name, signature in signatures.iteritems():
        function = getattr(library, name)
        argument_types, return_type, error_checker = signature
        function.argtypes = argument_types
        function.restype = return_type
        if error_checker:
            function.errcheck = error_checker
    return library


@contextmanager
def scoped_pointer(pointer, deleter):
    """
    A "scoped pointer" for ctypes for use with the ``with`` statement::

       with scoped_pointer(pointer, free) as pointer:
           do_something(pointer)

    ``pointer`` is any ctypes pointer, ``deleter`` is a callable, which
    accepts this pointer as single argument.  This callable is called when
    leaving the block to free the pointer.
    """
    yield pointer
    deleter(pointer)
