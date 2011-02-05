# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011 Sebastian Wiesner <lunaryorn@googlemail.com>
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
    synaptiks
    =========

    A touchpad configuration and management application.

    Touchpad access
    ---------------

    The :mod:`~synaptiks.touchpad` module provides the
    :class:`~touchpad.Touchpad` class to access and configured the touchpad.
    This class uses the XInput API provided by Xorg to access the properties of
    the touchpad driver.  This API is wrapped in a pythonic interface by the
    :mod:`~synaptiks.xinput` module.

    Event monitoring
    ----------------

    The :mod:`~synaptiks.monitors` module provides monitor classes, which
    listen for external events.  These monitors are used by **synaptiks** to do
    automatic touchpad management.  Currently it includes classes for mouse
    device and keyboard monitoring.

    Touchpad management
    -------------------

    Atop of :mod:`~synaptiks.touchpad` and :mod:`~synaptiks.monitors` the
    :mod:`~synaptiks.management` module implements a sophisticated automatic
    touchpad management, which enables and disables the touchpad based on
    external events like keyboard activity and plugged mouse devices, which is
    a core feature of **synaptiks**.

    Configuration
    -------------

    **synaptiks** allows to configure both the touchpad and the touchpad
    manager.  The corresponding configuration classes
    :class:`~synaptiks.config.TouchpadConfiguration` and
    :class:`~synaptiks.config.ManagerConfiguration` as well as some
    configuration utilities are provided by :mod:`~synaptiks.config`.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)


__version__ = '0.5.2'

WEBSITE_URL = 'http://synaptiks.lunaryorn.de'
ISSUE_TRACKER_URL = 'https://github.com/lunaryorn/synaptiks/issues'
