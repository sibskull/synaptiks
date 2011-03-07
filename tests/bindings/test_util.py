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

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from ctypes import CDLL, c_void_p, c_int

import mock
import pytest

from synaptiks._bindings import util


def test_load_library_no_signatures():
    library = util.load_library('X11')
    assert library
    assert isinstance(library, CDLL)


def test_library_with_signatures():
    errcheck = mock.Mock(name='errcheck')
    signatures = dict(XFree=([c_void_p], c_int, errcheck))
    library = util.load_library('X11', signatures)
    assert library
    assert isinstance(library, CDLL)
    assert library.XFree.argtypes == [c_void_p]
    assert library.XFree.restype == c_int
    assert library.XFree.errcheck is errcheck


def test_load_library_not_existing():
    with pytest.raises(ImportError) as exc_info:
        util.load_library('doesNotExist')
    assert str(exc_info.value) == 'No library named doesNotExist'


def test_add_foreign_signatures_errcheck_omitted():
    signatures = dict(spam=(mock.sentinel.argtypes, mock.sentinel.restype))
    library = mock.Mock(name='library')
    library.spam = mock.Mock(name='spam', spec_set=['argtypes', 'restype'])
    assert util.add_foreign_signatures(library, signatures) is library
    assert library.spam.argtypes is mock.sentinel.argtypes
    assert library.spam.restype is mock.sentinel.restype


def test_add_foreign_signatures_errcheck_none():
    signatures = dict(spam=(mock.sentinel.argtypes,
                            mock.sentinel.restype, None))
    library = mock.Mock(name='library')
    library.spam = mock.Mock(name='spam', spec_set=['argtypes', 'restype'])
    assert util.add_foreign_signatures(library, signatures) is library
    assert library.spam.argtypes is mock.sentinel.argtypes
    assert library.spam.restype is mock.sentinel.restype


def test_add_foreign_signatures_errcheck_present():
    signatures = dict(spam=(mock.sentinel.argtypes,
                            mock.sentinel.restype, mock.sentinel.errcheck))
    library = mock.Mock(name='library')
    library.spam = mock.Mock(name='spam', spec_set=['argtypes', 'restype',
                                                    'errcheck'])
    assert util.add_foreign_signatures(library, signatures) is library
    assert library.spam.argtypes is mock.sentinel.argtypes
    assert library.spam.restype is mock.sentinel.restype
    assert library.spam.errcheck is mock.sentinel.errcheck


def test_scoped_pointer():
    deleter = mock.Mock()
    with util.scoped_pointer(mock.sentinel.pointer, deleter) as pointer:
        assert pointer is mock.sentinel.pointer
    deleter.assert_called_with(mock.sentinel.pointer)
