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

import os

import mock
import pytest

from synaptiks.x11 import Display, DisplayError


class TestDisplay(object):

    def test_open_close(self):
        display = Display.from_name()
        assert display
        display.close()
        assert not display

    def test_context(self):
        with Display.from_name() as display:
            assert display
        assert not display

    def test_error(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with pytest.raises(DisplayError):
                Display.from_name()

    def test_qt(self, qtapp):
        assert Display.from_qt()

    def test_standard_types(self, display):
        from synaptiks._bindings import xlib
        float_atom = display.intern_atom('FLOAT')
        int_atom = display.intern_atom('INTEGER')
        atom_atom = display.intern_atom('ATOM')
        assert display.types.float == float_atom
        assert display.types.integer == int_atom
        assert display.types.integer == xlib.INTEGER
        assert display.types.atom == atom_atom
        assert display.types.atom == xlib.ATOM

    def test_intern_atom(self, display):
        float_atom = display.intern_atom('FLOAT')
        int_atom = display.intern_atom('INTEGER')
        non_existing_atom = display.intern_atom('non-existing-atom')
        assert float_atom
        assert int_atom
        assert non_existing_atom is None
        assert display._atom_cache[b'FLOAT'] is float_atom
        assert display._atom_cache[b'INTEGER'] is int_atom
        assert b'non-existing_atom' not in display._atom_cache


class TestAtom(object):

    def test_display(self, display):
        float_atom = display.intern_atom('FLOAT')
        assert float_atom.display is display

    def test_value(self, display):
        float_atom = display.intern_atom('FLOAT')
        assert float_atom.value == float_atom._as_parameter_
        int_atom = display.intern_atom('INTEGER')
        from synaptiks._bindings.xlib import INTEGER
        assert int_atom.value == INTEGER

    def test_name(self, display):
        float_atom = display.intern_atom('FLOAT')
        assert isinstance(float_atom.name, unicode)
        assert float_atom.name == 'FLOAT'

    def test_str_unicode(self, display):
        float_atom = display.intern_atom('FLOAT')
        assert str(float_atom) == b'FLOAT'
        assert isinstance(str(float_atom), bytes)
        assert unicode(float_atom) == 'FLOAT'
        assert isinstance(unicode(float_atom), unicode)

    def test_repr(self, display):
        float_atom = display.intern_atom('FLOAT')
        assert repr(float_atom) == "u'FLOAT' ({0})".format(float_atom.value)

    def test_hash(self, display):
        float_atom = display.intern_atom('FLOAT')
        int_atom = display.intern_atom('INTEGER')
        assert hash(int_atom) == hash(int_atom.value)
        from synaptiks._bindings.xlib import INTEGER
        assert hash(int_atom) == hash(INTEGER)
        assert hash(float_atom) == hash(float_atom.value)

    def test_eq(self, display):
        float_atom = display.intern_atom('FLOAT')
        other_atom = display.intern_atom('FLOAT')
        int_atom = display.intern_atom('INTEGER')
        assert not (float_atom == None)
        assert float_atom == float_atom
        assert float_atom == other_atom
        assert not (float_atom == int_atom)

    def test_ne(self, display):
        float_atom = display.intern_atom('FLOAT')
        other_atom = display.intern_atom('FLOAT')
        int_atom = display.intern_atom('INTEGER')
        assert float_atom != None
        assert not (float_atom != float_atom)
        assert not (float_atom != other_atom)
        assert float_atom != int_atom
