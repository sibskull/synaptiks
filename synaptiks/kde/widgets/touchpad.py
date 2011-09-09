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
    synaptiks.kde.widgets.touchpad
    ==============================

    Widgets for touchpad information and configuration

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from PyQt4.QtCore import pyqtSignal, QRegExp
from PyQt4.QtGui import QWidget
from PyKDE4.kdecore import i18nc
from PyKDE4.kdeui import KTabWidget, KIconLoader, KComboBox

from synaptiks.kde.widgets import DynamicUserInterfaceMixin
from synaptiks.kde.widgets.config import ConfigurationWidgetMixin


class TouchpadInformationWidget(QWidget, DynamicUserInterfaceMixin):
    """
    A widget which shows some information about a touchpad.

    This currently includes:

    - the device name of the touchpad,
    - what physical buttons, the touchpad has,
    - how many fingers it can detect,
    - and whether it supports two-finger emulation.
    """

    def __init__(self, parent=None):
        """
        Create a new information widget.
        """
        QWidget.__init__(self, parent)
        self._load_userinterface()

    def show_touchpad(self, touchpad):
        """
        Show information about the given ``touchpad`` in this widget.

        ``touchpad`` is a :class:`~synaptiks.touchpad.Touchpad` object.
        """
        self.nameLabel.setText(i18nc(
            '@info touchpad name', '<title><resources>%1</resource></title>',
            touchpad.name))

        pixmaps = {True: 'dialog-ok', False: 'dialog-cancel'}
        for key in pixmaps:
            pixmaps[key] = KIconLoader.global_().loadIcon(
                pixmaps[key], KIconLoader.Small)

        button_widgets = ('left', 'middle', 'right')
        for widget_name, is_supported in zip(button_widgets, touchpad.buttons):
            widget = getattr(self, '{0}Button'.format(widget_name))
            widget.setPixmap(pixmaps[is_supported])

        self.fingerDetection.setValue(touchpad.finger_detection)

        # disable the emulation box, if the touchpad natively supports two
        # fingers natively.
        if touchpad.finger_detection > 2:
            self.twoFingerEmulationBox.setEnabled(False)
        # nonetheless always assign proper pixmaps
        self.fingerWidthDetection.setPixmap(
            pixmaps[touchpad.has_finger_width_detection])
        self.pressureDetection.setPixmap(
            pixmaps[touchpad.has_pressure_detection])
        self.twoFingerEmulation.setPixmap(
            pixmaps[touchpad.has_two_finger_emulation])


class MotionPage(QWidget, DynamicUserInterfaceMixin):
    """
    Configuration page to configure the settings for cursor motion on the
    touchpad.
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self._load_userinterface()


class ScrollingPage(QWidget, DynamicUserInterfaceMixin):
    """
    Configuration page to configure scrolling.
    """

    def __init__(self, touchpad, parent=None):
        QWidget.__init__(self, parent)
        self._load_userinterface()
        # HACK: the designer is seems unable to set this property, so we set it
        # in code.
        self.touchpad_coasting_speed.setSpecialValueText(
            i18nc('@item coasting speed special value', 'Disabled'))
        self.touchpad_coasting_speed.valueChanged.connect(
            self._coasting_speed_changed)
        self.coasting.toggled.connect(self._coasting_toggled)
        step = self.touchpad_coasting_speed.singleStep()
        value = self.touchpad_coasting_speed.value()
        self._saved_coasting_speed = value or step
        if touchpad.finger_detection >= 2 or touchpad.has_two_finger_emulation:
            two_finger_widgets = self.findChildren(
                QWidget, QRegExp('touchpad_(.*)_two_finger_scrolling'))
            for widget in two_finger_widgets:
                widget.setEnabled(True)

    def _coasting_toggled(self, checked):
        if checked and not self.touchpad_coasting_speed.value():
            self.touchpad_coasting_speed.setValue(self._saved_coasting_speed)
        elif not checked:
            self.touchpad_coasting_speed.setValue(0)

    def _coasting_speed_changed(self, value):
        if value:
            # remember any non-zero value to restore it, when the user
            # re-checks "coasting"
            self._saved_coasting_speed = value
        self.coasting.setChecked(bool(value))


class TappingPage(QWidget, DynamicUserInterfaceMixin):
    """
    Configuration page to configure tapping.
    """

    def __init__(self, touchpad, parent=None):
        QWidget.__init__(self, parent)
        self._load_userinterface()
        finger_tap_actions = self.findChildren(
            KComboBox, QRegExp('touchpad_f[1-3]_tap_action'))

        for widget in finger_tap_actions[touchpad.finger_detection:]:
            self._set_enabled(widget, False)
        if touchpad.has_two_finger_emulation:
            self._set_enabled(self.touchpad_f2_tap_action, True)

    def _set_enabled(self, widget, enabled):
        widget.setEnabled(enabled)
        self.fingerButtonsLayout.labelForField(widget).setEnabled(enabled)


class HardwarePage(QWidget, DynamicUserInterfaceMixin):
    """
    Configuration page for hardware settings.
    """

    def __init__(self, touchpad, parent=None):
        QWidget.__init__(self, parent)
        self._load_userinterface()
        self.information.show_touchpad(touchpad)


class TouchpadConfigurationWidget(KTabWidget, ConfigurationWidgetMixin):
    """
    A tab widget to configure the touchpad properties.

    This basically aggregates all configuration pages in this module and adds
    configuration management.
    """

    configurationChanged = pyqtSignal(bool)

    NAME_PREFIX = 'touchpad'

    PROPERTY_MAP = dict(
        QCheckBox='checked', QRadioButton='checked', QGroupBox='checked',
        MouseButtonComboBox='currentIndex', KComboBox='currentIndex',
        KIntNumInput='value', KDoubleNumInput='value'
        )

    CHANGED_SIGNAL_MAP = dict(
        QCheckBox='toggled', QRadioButton='toggled', QGroupBox='toggled',
        MouseButtonComboBox='currentIndexChanged',
        KComboBox='currentIndexChanged',
        KIntNumInput='valueChanged', KDoubleNumInput='valueChanged'
        )

    def __init__(self, config, touchpad, parent=None):
        """
        Create a new touchpad configuration widget based on given ``config``.

        ``touchpad`` is the touchpad configured by ``config``.  Based it's
        capabilities settings which are not available are disabled.

        ``config`` is the :class:`~synaptiks.config.TouchpadConfiguration`
        object displayed by this widget.  ``touchpad`` is a
        :class:`~synaptiks.touchpad.Touchpad` object.  ``parent`` is the parent
        :class:`~PyQt4.QtGui.QWidget` (can be ``None``).
        """
        KTabWidget.__init__(self, parent)
        self.touchpad_config = config
        self.touchpad = touchpad
        pages = [HardwarePage(self.touchpad, self), MotionPage(self),
                 ScrollingPage(self.touchpad, self),
                 TappingPage(self.touchpad, self)]
        for page in pages:
            self.addTab(page, page.windowTitle())
        self.setWindowTitle(
            i18nc('@title:window', 'Touchpad configuration'))
        self._setup(self.touchpad_config)
