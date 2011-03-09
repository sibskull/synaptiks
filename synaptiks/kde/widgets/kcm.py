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
    synaptiks.kde.widgets.kcm
    =========================

    System settings widgets.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QHBoxLayout, QLabel, QSizePolicy
from PyKDE4.kdecore import ki18nc, i18nc, KGlobal
from PyKDE4.kdeui import KCModule, KIconLoader

from synaptiks.kde import make_about_data
from synaptiks.kde.widgets.touchpad import TouchpadConfigurationWidget


class SynaptiksKCMBase(KCModule):
    """
    Base class for synaptiks kcm widgets.

    This class sets up about data and l10n for synaptiks kcm widgets.
    """

    def __init__(self, component_data, parent=None):
        KCModule.__init__(self, component_data, parent)
        KGlobal.locale().insertCatalog('synaptiks')
        # keep a reference to the generated about data to prevent it from being
        # deleted by the GC
        self._about = make_about_data(
            ki18nc('kcmodule description', 'Touchpad configuration'))
        self.setAboutData(self._about)
        self.setQuickHelp(i18nc(
            '@info:tooltip synaptiks kcmodule',
            '<title>Touchpad configuration</title>'
            '<para>This module lets you configure your touchpad.</para>'))


class TouchpadErrorKCM(SynaptiksKCMBase):
    """
    KCM widget used to show a touchpad error.
    """

    def __init__(self, error, component_data, parent=None):
        SynaptiksKCMBase.__init__(self, component_data, parent)
        if isinstance(error, basestring):
            error_message = error
        else:
            from synaptiks.kde.error import get_localized_error_message
            error_message = get_localized_error_message(error)
        self.setLayout(QHBoxLayout(self))
        icon = QLabel('foobar', self)
        icon.setPixmap(KIconLoader.global_().loadIcon(
            'dialog-warning', KIconLoader.Desktop, KIconLoader.SizeLarge))
        icon.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        # do not expand the icon horizontally, to avoid a wide empty space
        # between icon and text, and to given as much space as possible to the
        # text contents
        icon.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        self.layout().addWidget(icon)
        message = QLabel(error_message, self)
        message.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        message.setWordWrap(True)
        message.setOpenExternalLinks(True)
        self.layout().addWidget(message)
        self.setButtons(self.Help)


class TouchpadConfigurationKCM(SynaptiksKCMBase):
    """
    Synaptiks system settings module.
    """

    def __init__(self, touchpad_config, component_data, parent=None):
        """
        Create a new synaptiks module.

        ``touchpad_config`` is the
        :class:`synaptiks.config.TouchpadConfiguration`, which is handled by
        this module.  ``component_data`` and ``parent`` come from the
        ``KCModule`` constructor and are passed from the plugin entry point.
        """
        SynaptiksKCMBase.__init__(self, component_data, parent)
        self.touchpad_config = touchpad_config
        self.setLayout(QHBoxLayout(self))
        self.config_widget = TouchpadConfigurationWidget(self.touchpad_config)
        self.config_widget.configurationChanged.connect(
            self.unmanagedWidgetChangeState)
        self.layout().addWidget(self.config_widget)

    def defaults(self, defaults=None):
        """
        Load the default settings into the widgets.

        ``defaults`` is a mapping with the default touchpad configuration, or
        ``None``.  In the latter case, the defaults are implicitly loaded from
        disk.
        """
        self.config_widget.load_defaults(defaults)

    def load(self):
        """
        Load the touchpad configuration into the widgets.
        """
        self.config_widget.load_configuration()

    def save(self):
        """
        Apply and save touchpad configuration.
        """
        self.config_widget.apply_configuration()
        self.touchpad_config.save()


def make_kcm_widget(component_data, parent=None):
    """
    Create a KCModule object to configure the touchpad.

    This function tries to find a touchpad on this system and get the
    configuration of this touchpad.  If this succeeds, a
    :class:`TouchpadConfigurationKCM` is returned, allowing the user to
    configure the touchpad.

    Otherwise a :class:`TouchpadErrorKCM` is returned, which gives the user a
    description of the error and its cause.
    """
    from synaptiks.qx11 import QX11Display
    from synaptiks.touchpad import Touchpad
    from synaptiks.config import TouchpadConfiguration
    try:
        touchpad = Touchpad.find_first(QX11Display())
        config = TouchpadConfiguration(touchpad)
        return TouchpadConfigurationKCM(config, component_data, parent)
    except Exception as error:
        return TouchpadErrorKCM(error, component_data, parent)
