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
from contextlib import nested

import mock
import pytest

from synaptiks.xlib import Display, DisplayError


def test_display_open_close():
    display = Display.from_name()
    assert display
    display.close()
    assert not display


def test_display_context():
    with Display.from_name() as display:
        assert display
    assert not display


def test_display_error():
    with mock.patch.dict(os.environ, {}, clear=True):
        with pytest.raises(DisplayError):
            Display.from_name()


def test_display_qt(qtapp):
    assert Display.from_qt()


def test_display_mock():
    open_display = 'synaptiks._bindings.xlib.open_display'
    close_display = 'synaptiks._bindings.xlib.close_display'
    with nested(mock.patch(open_display),
                mock.patch(close_display)) as (open_display, close_display):
        with Display.from_name() as display:
            assert display
            open_display.assert_called_with(None)
            assert not close_display.called
        close_display.assert_called_with(display)
