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

from synaptiks import ISSUE_TRACKER_URL
from synaptiks.touchpad import NoTouchpadError
from synaptiks.xinput import XInputVersionError
from synaptiks.kde.error import get_localized_error_message


def test_get_localized_error_message_no_touchpad():
    msg = unicode(get_localized_error_message(NoTouchpadError()))
    assert 'No touchpad found' in msg
    assert ISSUE_TRACKER_URL in msg
    assert 'synaptics' in msg


def test_get_localized_error_message_xinput_version():
    error = XInputVersionError((20, 20), (10, 10))
    msg = unicode(get_localized_error_message(error))
    assert 'Version error' in msg
    assert 'XInput extension' in msg
    assert 'Version 10.10 was found' in msg
    assert 'at least version 20.20 is required' in msg


def test_get_localized_error_message_unexpected_error():
    error = ValueError('spam with eggs')
    msg = unicode(get_localized_error_message(error))
    print(msg)
    assert 'Unexpected error occurred' in msg
    assert ISSUE_TRACKER_URL in msg
    assert 'spam with eggs' in msg
