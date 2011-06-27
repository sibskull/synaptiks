#!/usr/bin/python2
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
    try_xrecord
    ===========

    Play with xrecord extension.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import signal

from synaptiks.x11 import Display
from synaptiks._bindings import xlib, xrecord
from synaptiks._bindings.util import scoped_pointer


EVENT_NAMES = {xlib.KEY_PRESS: 'KeyPress', xlib.KEY_RELEASE: 'KeyRelease'}


def handle_event(_, data):
    with scoped_pointer(data, xrecord.free_data):
        if data.contents.category != xrecord.FROM_SERVER:
            return
        event_type, keycode = data.contents.event
        event_name = EVENT_NAMES[event_type]
        print('{0}: {1}'.format(event_name, keycode))


def disable_context_handler(context):
    def handler(signum, frame):
        with Display.from_name() as display:
            xrecord.disable_context(display, context)
    return handler


def main():
    with Display.from_name() as display:
        _, xrecord_version = xrecord.query_version(display)
        print('xrecord version:', '.'.join(map(str, xrecord_version)))
        key_events = (xlib.KEY_PRESS, xlib.KEY_RELEASE)
        with xrecord.context(display, xrecord.ALL_CLIENTS,
                             device_events=key_events) as context:
            disable = disable_context_handler(context)
            signal.signal(signal.SIGINT, disable)
            signal.signal(signal.SIGTERM, disable)
            xrecord.enable_context(display, context, handle_event, None)


if __name__ == '__main__':
    main()
