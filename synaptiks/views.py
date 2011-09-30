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
    synaptiks.views
    ===============

    View classes for synaptiks

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from PyQt4.QtCore import pyqtProperty, pyqtSignal, QStringList
from PyQt4.QtGui import QListView

from synaptiks.x11 import Display
from synaptiks.models import MouseDevicesModel
from synaptiks.touchpad import FakeTouchpad


class MouseDevicesView(QListView):
    """
    A view for :class:`~synaptiks.models.MouseDevicesModel`.

    This allows to use this model in configuration classes.
    """

    #: emitted if the checked devices have changed
    checkedDevicesChanged = pyqtSignal(QStringList)

    def __init__(self, parent=None):
        QListView.__init__(self, parent)
        self.setModel(MouseDevicesModel(self))
        self.model().checkedDevicesChanged.connect(self.checkedDevicesChanged)

    @pyqtProperty(QStringList, notify=checkedDevicesChanged)
    def checkedDevices(self):
        """
        The list of checked devices.
        """
        return self.model().checkedDevices

    @checkedDevices.setter
    def checkedDevices(self, devices):
        self.model().checkedDevices = devices


class FakeTouchpadView(QListView):
    """
    A view which shows all mouse devices which may serve as fake touchpad.
    """

    def __init__(self, parent=None):
        QListView.__init__(self, parent)
        display = Display.from_qt()
        mouse_devices = [d.name for d in FakeTouchpad.find_all(Display.from)]
        model = QStringListModel(self)
