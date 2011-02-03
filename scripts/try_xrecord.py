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

import signal

from synaptiks._bindings import xlib, xrecord
from synaptiks._bindings.util import scoped_pointer


def handle_event(_, data):
    with scoped_pointer(data, xrecord.free_data):
        if data.contents.category != xrecord.FROM_SERVER:
            return
        print('keyboard active')


def disable_context_handler(context):
    def handler(signum, frame):
        with xlib.display() as dpy:
            xrecord.disable_context(dpy, context)
    return handler


def main():
    with xlib.display() as display:
        with xrecord.record_range() as record_range:
            record_range.contents.device_events.first = xlib.KEY_PRESS
            record_range.contents.device_events.last = xlib.KEY_RELEASE
            with xrecord.context(display, 0, xrecord.ALL_CLIENTS,
                                 record_range) as context:
                disable = disable_context_handler(context)
                signal.signal(signal.SIGINT, disable)
                signal.signal(signal.SIGTERM, disable)
                xrecord.enable_context(display, context, handle_event, None)


if __name__ == '__main__':
    main()
