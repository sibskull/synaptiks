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
    synaptiks.management
    ====================

    The state machine for touchpad management and related classes.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from functools import partial

from PyQt4.QtCore import QStateMachine, QState


class TouchpadStateMachine(QStateMachine):
    """
    A state machine, which manages the touchpad state.

    This state machine has two states:

    - ``touchpad_on``: The touchpad is currently on
    - ``touchpad_off``: The touchpad is currently off
    """

    def __init__(self, touchpad, parent=None):
        QStateMachine.__init__(self, parent)
        self.touchpad = touchpad
        self.touchpad_off = QState(self)
        self.touchpad_off.setObjectName('touchpad_off')
        self.touchpad_off.entered.connect(partial(self._set_touchpad_off, 1))
        self.touchpad_on = QState(self)
        self.touchpad_on.setObjectName('touchpad_on')
        self.touchpad_on.entered.connect(partial(self._set_touchpad_off, 0))
        self.setInitialState(self.touchpad_on if self.touchpad.off == 0
                             else self.touchpad_off)

    def add_touchpad_switch_transition(self, signal):
        """
        Transition between the touchpad states on the given ``signal``.

        Whenever the given ``signal`` is emitted, this state machine will
        transition between ``touchpad_on`` and ``touchpad_off``.

        ``signal`` is a bound PyQt signal.
        """
        self.touchpad_on.addTransition(signal, self.touchpad_off)
        self.touchpad_off.addTransition(signal, self.touchpad_on)

    def _set_touchpad_off(self, off):
        self.touchpad.off = off
