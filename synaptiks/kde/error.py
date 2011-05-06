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
    synaptiks.kde.error
    ===================

    KDE-specific error handling functions.

    This module provides functions to convert common touchpad exceptions into
    human-readable, localized and informative error messages.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from PyKDE4.kdecore import ki18nc

from synaptiks import ISSUE_TRACKER_URL


NO_TOUCHPAD_ERROR_MESSAGE = ki18nc(
    '@info NoTouchpadError error message',
    '<title>No touchpad found</title>'
    '<para>No touchpad was found in this system.  If the system has a '
    'touchpad, please make sure, that the '
    '<application>synaptics</application> driver is properly installed and '
    'configured.</para>'
    '<para>If your touchpad is not found, though the driver is installed and '
    'configured correctly, please compile detailed information about your '
    'touchpad hardware and report this issue to the '
    '<link url="%1">issue tracker</link>.</para>').subs(ISSUE_TRACKER_URL)


VERSION_ERROR_MESSAGE = ki18nc(
    '@info XInputVersionError error message',
    '<title>Version error</title>'
    '<para>The version of the XInput extension installed on your system is '
    'too old.  Version %1 was found, but at least version %2 is required.'
    '</para>'
    '<para>If you want to be able to configure your touchpad, you have to '
    'upgrade your system to a recent release of the Xorg display server.  '
    'This may likely involve a complete upgrade of your system.  Please '
    'excuse this inconvenience, but there is no way to make touchpad '
    'configuration work on systems as old as yours.</para>')


UNEXPECTED_ERROR_MESSAGE = ki18nc(
    '@info error message for unexpected errors',
    '<title>Unexpected error occurred</title>'
    '<para>An unexpected error occurred: <message>%2</message></para>'
    '<para>Please report this issue to the '
    '<link url="%1">issue tracker</link>.</para>').subs(ISSUE_TRACKER_URL)


def get_localized_error_message(error):
    """
    Try to find a localized, user-readable error description corresponding to
    the given :exc:`~exceptions.Exception` object.

    This function needs a existing application object and proper locale
    configuration in order to work correctly.  Do not use before creating a
    :class:`~PyKDE4.kdeui.KApplication` object!

    ``error`` is a subclass of :class:`~exceptions.Exception`.  Of course, not
    all possible subclasses are handled by this function, however all
    touchpad-related error classes defined in the synaptiks modules are
    supported.

    Return a :func:`unicode` object containing the localized error message.
    """
    from synaptiks.touchpad import NoTouchpadError
    from synaptiks.x11.input import XInputVersionError
    if isinstance(error, NoTouchpadError):
        return NO_TOUCHPAD_ERROR_MESSAGE.toString()
    elif isinstance(error, XInputVersionError):
        actual = str(error.actual_version)
        expected = str(error.expected_version)
        return VERSION_ERROR_MESSAGE.subs(actual).subs(expected).toString()
    else:
        return UNEXPECTED_ERROR_MESSAGE.subs(unicode(error)).toString()
