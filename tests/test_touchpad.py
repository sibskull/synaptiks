# -*- coding: utf-8 -*-
# Copyright (c) 2010, Sebastian Wiesner <lunaryorn@googlemail.com>
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


import pytest

from synaptiks.touchpad import Touchpad


def pytest_generate_tests(metafunc):
    if metafunc.function.__name__.startswith('test_typescheme'):
        for property in Touchpad.TYPESCHEME:
            funcargs = dict(property=property)
            if 'number_of_items' in metafunc.funcargnames:
                _, number_of_items = Touchpad.TYPESCHEME[property]
                funcargs['number_of_items'] = number_of_items
            metafunc.addcall(id=property, param=property)


def pytest_funcarg__touchpad(request):
    touchpad = Touchpad.find_first()
    if touchpad is None:
        pytest.skip('No touchpad available')
    return touchpad


def pytest_funcarg__property(request):
    return request.param


def pytest_funcarg__number_of_items(request):
    property = request.getfuncargvalue('property')
    _, number_of_items = Touchpad.TYPESCHEME[property]
    return number_of_items


def test_find_touchpad(touchpad):
    assert touchpad


def test_typescheme_contained(touchpad, property):
    assert property in touchpad


def test_typescheme_length(touchpad, property, number_of_items):
    value = touchpad[property]
    assert value
    assert len(value) == number_of_items


def test_typescheme_roundtrip(touchpad, property):
    value = touchpad[property]
    touchpad[property] = value
