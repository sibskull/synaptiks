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
    synaptiks._util
    ===============

    Internal utility functions.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""



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
