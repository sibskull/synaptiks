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
    synaptiks.kde.widgets.management
    ================================

    Widgets for touchpad management configuration.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from PyQt4.QtCore import pyqtSignal, QStringList
from PyQt4.QtGui import QWidget

from synaptiks.kde.widgets import DynamicUserInterfaceMixin
from synaptiks.kde.widgets.config import ConfigurationWidgetMixin


class TouchpadManagementWidget(QWidget, ConfigurationWidgetMixin,
                               DynamicUserInterfaceMixin):
    """
    Configuration page for touchpad management.
    """

    configurationChanged = pyqtSignal(bool)

    NAME_PREFIX = 'management'

    PROPERTY_MAP = dict(
        QGroupBox='checked', MouseDevicesView='checkedDevices',
        KDoubleNumInput='value', KComboBox='currentIndex')

    CHANGED_SIGNAL_MAP = dict(
        QGroupBox='toggled', MouseDevicesView='checkedDevicesChanged',
        KDoubleNumInput='valueChanged', KComboBox='currentIndexChanged')

    def __init__(self, config, parent=None):
        QWidget.__init__(self, parent)
        self._load_userinterface()
        self.management_config = config
        self._setup(self.management_config)

    def _convert_to_property(self, key, value):
        if key == 'ignored_mouses':
            return QStringList(value)
        return value

    def _convert_from_property(self, key, value):
        if key == 'ignored_mouses':
            return [unicode(d) for d in value]
        return value

    def _get_defaults(self):
        return self.management_config.DEFAULTS
