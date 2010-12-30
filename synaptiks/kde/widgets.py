# -*- coding: utf-8 -*-
# Copyright (c) 2010, Sebastian Wiesner <lunaryorn@googlemail.com>
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
    synaptiks.kde.widgets
    =====================

    Common KDE widgets for synaptiks.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import os
from functools import partial

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
from PyQt4.uic import loadUi
from PyQt4.QtCore import pyqtSignal, QRegExp
from PyQt4.QtGui import QWidget, QHBoxLayout
from PyKDE4.kdecore import KGlobal, ki18nc, i18nc
from PyKDE4.kdeui import KIconLoader, KTabWidget, KComboBox, KCModule

from synaptiks.config import get_touchpad_defaults
from synaptiks.kde import make_about_data


PACKAGE_DIRECTORY = os.path.dirname(__file__)


class DynamicUserInterfaceMixin(object):
    """
    Mixin class for widgets to load their user interface dynamically from the
    :mod:`synaptiks.kde` package.  It provides a single method
    :meth:`_load_userinterface()`, which loads the user interface into the
    instance.
    """

    def _load_userinterface(self):
        """
        Load the user interface for this object.

        The user interface is loaded from a user interface file with the
        lower-cased class name in ``ui/`` sub-directory of this package.  For
        instance, the user interface file for class ``FooBar`` would be
        ``ui/foobar.ui``.
        """
        ui_description_filename = os.path.join(
            PACKAGE_DIRECTORY, 'ui',
            self.__class__.__name__.lower() + '.ui')
        loadUi(ui_description_filename, self)


class MouseButtonComboBox(KComboBox):
    def __init__(self, parent=None):
        KComboBox.__init__(self, parent)
        self.addItems([
            i18nc('@item:inlistbox mouse button triggered by tapping',
                  'Disabled'),
            i18nc('@item:inlistbox mouse button triggered by tapping',
                  'Left mouse button'),
            i18nc('@item:inlistbox mouse button triggered by tapping',
                  'Middle mouse button'),
            i18nc('@item:inlistbox mouse button triggered by tapping',
                   'Right mouse button')
            ])


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
            self._coasting_speed_value_changed)
        if touchpad.finger_detection >= 2 or touchpad.has_two_finger_emulation:
            two_finger_widgets = self.findChildren(
                QWidget, QRegExp('touchpad_(.*)_two_finger_scrolling'))
            for widget in two_finger_widgets:
                widget.setEnabled(True)

    def _coasting_speed_value_changed(self, value):
        self.touchpad_corner_coasting.setEnabled(value != 0)


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


class TouchpadConfigurationWidget(KTabWidget):
    """
    A tab widget to configure the touchpad properties.

    This basically aggregates all page classes in this module.
    """

    configurationChanged = pyqtSignal(bool)

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

    def __init__(self, config, parent=None):
        """
        Create a new configuration widget for the given ``touchpad``.

        ``config`` is the :class:`~synaptiks.config.TouchpadConfiguration`
        object displayed by this widget.  ``parent`` is the parent
        :class:`~PyQt4.QtGui.QWidget` (can be ``None``).
        """
        KTabWidget.__init__(self, parent)
        self.touchpad_config = config
        self._changed_widgets = set()
        pages = [HardwarePage(self.touchpad, self), MotionPage(self),
                 ScrollingPage(self.touchpad, self),
                 TappingPage(self.touchpad, self)]
        for page in pages:
            self.addTab(page, page.windowTitle())
        self.setWindowTitle(
            i18nc('@title:window', 'Touchpad configuration'))
        self.load_configuration()
        for widget in self._find_touchpad_configuration_widgets():
            signalname = self.CHANGED_SIGNAL_MAP[type(widget).__name__]
            signal = getattr(widget, signalname)
            signal.connect(partial(self._check_for_changes, widget))

    @property
    def touchpad(self):
        """
        The :class:`~synaptiks.touchpad.Touchpad` object associated with this
        widget.
        """
        return self.touchpad_config.touchpad

    @property
    def is_configuration_changed(self):
        """
        ``True``, if the configuration shown in the widgets is different from
        the actual touchpad configuration.  This usually means, that the user
        has changed some setting.
        """
        return bool(self._changed_widgets)

    def _check_for_changes(self, origin, changed_value):
        touchpad_property = self._get_touchpad_property(origin)
        name = origin.objectName()
        current_value = self.touchpad_config[touchpad_property]
        if current_value == changed_value:
            self._changed_widgets.remove(name)
        else:
            self._changed_widgets.add(name)
        self.configurationChanged.emit(self.is_configuration_changed)

    def _get_touchpad_property(self, widget):
        """
        Return the touchpad property name associated with the given ``widget``.
        """
        return widget.objectName()[9:]

    def _find_touchpad_configuration_widgets(self):
        """
        Find all widgets which correspond to a touchpad properties.
        """
        return self.findChildren(QWidget, QRegExp('touchpad_.*'))

    def _update_widgets_from_mapping(self, mapping):
        for widget in self._find_touchpad_configuration_widgets():
            touchpad_property = self._get_touchpad_property(widget)
            value = mapping[touchpad_property]
            widget_property = self.PROPERTY_MAP[type(widget).__name__]
            widget.setProperty(widget_property, value)

    def _get_mapping_from_widgets(self):
        config = dict()
        for widget in self._find_touchpad_configuration_widgets():
            touchpad_property = self._get_touchpad_property(widget)
            widget_property = self.PROPERTY_MAP[type(widget).__name__]
            value = widget.property(widget_property)
            config[touchpad_property] = value
        return config

    def load_defaults(self, defaults=None):
        """
        Load the given default configuration into the configuration widgets.

        If ``defaults`` is ``None``, the default configuration is implicitly
        loaded from disk (see
        :func:`synaptiks.config.get_touchpad_defaults()`).

        ``defaults`` is a mapping with the default touchpad configuration or
        ``None``.
        """
        if defaults is None:
            defaults = get_touchpad_defaults()
        self._update_widgets_from_mapping(defaults)

    def shows_defaults(self, defaults=None):
        """
        Check, if the widgets currently shows the given default settings.

        If ``defaults`` is ``None``, the default configuration is implicitly
        loaded from disk (see
        :func:`synaptiks.config.get_touchpad_defaults()`).

        ``defaults`` is a mapping with the default touchpad configuration or
        ``None``.

        Return ``True``, if the given ``defaults`` are currently shown,
        ``False`` otherwise.
        """
        if defaults is None:
            defaults = get_touchpad_defaults()
        current = self._get_mapping_from_widgets()
        return current == defaults

    def load_configuration(self):
        """
        Load the configuration of the associated touchpad into the
        configuration widgets.
        """
        self._update_widgets_from_mapping(self.touchpad_config)

    def apply_configuration(self):
        """
        Apply the contents of the configuration widgets to the associated
        touchpad.
        """
        config = self._get_mapping_from_widgets()
        self.touchpad_config.update(config)


class TouchpadConfigurationKCM(KCModule):
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
        KCModule.__init__(self, component_data, parent)
        KGlobal.locale().insertCatalog('synaptiks')
        # keep a reference to the generated about data to prevent it from being
        # deleted by the GC
        self._about = make_about_data(
            ki18nc('kcmodule description', 'Touchpad configuration'))
        self.setQuickHelp(i18nc(
            '@info:tooltip synaptiks kcmodule',
            '<title>Touchpad configuration</title>'
            '<para>This module lets you configure your touchpad.</para>'))
        self.setAboutData(self._about)
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
