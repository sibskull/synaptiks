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

from functools import partial

from synaptiks._bindings import xlib, xrecord


def pytest_funcarg__record_range(request):
    return request.cached_setup(xrecord.alloc_range, xlib.free,
                                scope='function')


def pytest_funcarg__context(request):
    record_range = request.getfuncargvalue('record_range')
    display = request.getfuncargvalue('display')
    record_range.contents.device_events.first = xlib.KEY_PRESS
    record_range.contents.device_events.last = xlib.KEY_RELEASE
    return request.cached_setup(
        partial(xrecord.create_context, display, 0, xrecord.ALL_CLIENTS,
                record_range), partial(xrecord.free_context, display),
        scope='function')


def test_query_version(display):
    success, version = xrecord.query_version(display)
    assert success
    assert version >= (1, 13)


def test_alloc_range():
    r = xrecord.alloc_range()
    assert r
    xlib.free(r)


def test_create_context(display):
    record_range = xrecord.alloc_range()
    record_range.contents.device_events.first = xlib.KEY_PRESS
    record_range.contents.device_events.last = xlib.KEY_RELEASE
    context = None
    try:
        context = xrecord.create_context(
            display, 0, xrecord.ALL_CLIENTS, record_range)
        assert context
    finally:
        if context:
            assert xrecord.free_context(display, context)
