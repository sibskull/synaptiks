# -*- coding: utf-8 -*-
# Copyright (c) 2010, 2011, Sebastian Wiesner <lunaryorn@googlemail.com>
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

from PyQt4.QtCore import pyqtSignal, Qt, QRegExp
from PyQt4.QtGui import QWidget, QHBoxLayout, QLabel, QSizePolicy
from PyKDE4.kdecore import KGlobal, ki18nc, i18nc
from PyKDE4.kdeui import KIconLoader, KTabWidget, KComboBox, KCModule

from synaptiks.config import get_touchpad_defaults
from synaptiks.kde import make_about_data
from synaptiks.kde.uic import loadUi


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


class ConfigurationWidgetMixin(object):
    """
    Mixin class for configuration widgets.

    This class is a mixin for any widget, which corresponds to a configuration
    stored as mapping.  This mixin considers all ``QWidget``-derived children
    of the current object, whose name starts with ``<prefix>_``, as
    configuration widget.  These correspond directly to keys in the
    configuration mapping.  For all these widgets the mixin automatically does
    all the configuration management (applying and loading configuration,
    checking for default settings, checking if the user changed some settings
    and so on).

    To do so, it needs to now the ``<prefix>``.  Classes deriving from this
    mixin must therefore define a ``NAME_PREFIX`` attribute at class or
    instance scope, which holds this prefix.  Moreover it needs to mappings
    called ``PROPERTY_MAP`` and ``CHANGED_SIGNAL_MAP`` at class or instance
    scope, which map class names to properties, which are considered the
    configuration properties, and to a signal, which is emitted, whenever this
    property changes.

    Whenever values are moved between the configuration mapping and the
    widgets, this class can do type conversion from and to Qt objects if
    necessary.  To do so, reimplement :meth:`_convert_to_property()` and
    :meth:`_convert_from_property()`.  The default implementations do not
    perform any conversion.

    An at last, classes deriving from this mixin, must define a
    ``configurationChanged(bool)`` signal, and a :meth:`_get_defaults()`, which
    returns default values for all configuration keys.

    See :class:`TouchpadConfigurationWidget` for an example.
    """

    def _setup(self, config):
        """
        Setup the mixin with the given ``config`` mapping.

        Call this in ``__init__()`` of your configuration widget.
        """
        self.__config = config
        self.__changed_keys = set()
        for widget in self._find_configuration_widgets():
            signalname = self._get_signal_name_for_widget(widget)
            signal = getattr(widget, signalname)
            signal.connect(partial(self._check_for_changes, widget))
        self.load_configuration()

    def _check_for_changes(self, sender, changed_value):
        """
        Used as slot for changed signals of configuration widgets.

        The widget, which was changed, is available in ``sender``, the new
        value in ``changed_value``.
        """
        config_key = self._get_config_key_for_widget(sender)
        current_value = self.__config[config_key]
        if current_value == changed_value:
            self.__changed_keys.discard(config_key)
        else:
            self.__changed_keys.add(config_key)
        self.configurationChanged.emit(self.is_configuration_changed)

    def _find_configuration_widgets(self):
        """
        Find all widgets, which correspond to configuration keys.
        """
        pattern = QRegExp('{0}_.*'.format(self.NAME_PREFIX))
        return self.findChildren(QWidget, pattern)

    def _get_config_key_for_widget(self, widget):
        """
        Get the configuration key for the given widget as string.
        """
        return unicode(widget.objectName()[len(self.NAME_PREFIX)+1:])

    def _get_property_name_for_widget(self, widget):
        """
        Get the configuration property name for the given object.
        """
        return self.PROPERTY_MAP[type(widget).__name__]

    def _get_signal_name_for_widget(self, widget):
        """
        Get the name of the signal, which is emitted whenever the configuration
        property of the given widget is changed.
        """
        return self.CHANGED_SIGNAL_MAP[type(widget).__name__]

    def _convert_to_property(self, key, value):
        """
        Convert the given ``value`` for the given ``key`` to a type suitable
        for the corresponding widget.

        ``value`` comes from the internal configuration mapping, and can
        consequently have an arbitrary type.  ``key`` is a string with the
        configuration key (*not* the property name!).

        The default implementation does nothing.

        Return the converted ``value``.
        """
        return value

    def _convert_from_property(self, key, value):
        """
        Convert the given ``value`` to a type suitable as value for the given
        ``key`` in the configuration mapping.

        ``value`` is the value of the corresponding property in the widget and
        can have an arbitrary type.  ``key`` is the configuration key as string.

        The default implementation does nothing.

        Return the converted ``value``.
        """
        return value

    def _update_widgets_from_mapping(self, mapping):
        """
        Update all configuration widgets to represent the given ``mapping``.
        """
        for widget in self._find_configuration_widgets():
            config_key = self._get_config_key_for_widget(widget)
            value = mapping[config_key]
            widget_property = self._get_property_name_for_widget(widget)
            widget.setProperty(widget_property,
                               self._convert_to_property(config_key, value))

    def _get_mapping_from_widgets(self):
        """
        Get a configuration mapping, which holds the current values of all
        configuration widgets.
        """
        config = dict()
        for widget in self._find_configuration_widgets():
            config_key = self._get_config_key_for_widget(widget)
            widget_property = self._get_property_name_for_widget(widget)
            value = widget.property(widget_property).toPyObject()
            config[config_key] = self._convert_from_property(config_key, value)
        return config

    @property
    def is_configuration_changed(self):
        """
        ``True``, if the contents of the configuration widgets is different
        from the actual configuration.  This usually means, that the user has
        changed some setting in the widget.
        """
        return bool(self.__changed_keys)

    def load_defaults(self, defaults=None):
        """
        Load the default values in the ``defaults`` mapping.

        If ``defaults`` is ``None``, use the standard defaults provided by this
        widget.
        """
        if defaults is None:
            defaults = self._get_defaults()
        self._update_widgets_from_mapping(defaults)

    def shows_defaults(self, defaults=None):
        """
        Check, if the configuration widgets currently show the default values
        given by the ``defaults`` mapping.

        If ``defaults`` is ``None``, use the standard defaults provided by this
        widget (see :meth:`_get_defaults()`).

        Return ``True``, if the given defaults are contained in the widgets, or
        ``False`` otherwise.
        """
        if defaults is None:
            defaults = self._get_defaults()
        current = self._get_mapping_from_widgets()
        return current == defaults

    def load_configuration(self):
        """
        Load the configuration into the configuration widgets.
        """
        self._update_widgets_from_mapping(self.__config)

    def apply_configuration(self):
        """
        Apply the contents of all configuration widgets to the internal
        configuration mapping.
        """
        config = self._get_mapping_from_widgets()
        self.__config.update(config)
        self.__changed_keys.clear()
        self.configurationChanged.emit(self.is_configuration_changed)


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

    def __init__(self, config, parent=None):
        """
        Create a new configuration widget for the given ``touchpad``.

        ``config`` is the :class:`~synaptiks.config.TouchpadConfiguration`
        object displayed by this widget.  ``parent`` is the parent
        :class:`~PyQt4.QtGui.QWidget` (can be ``None``).
        """
        KTabWidget.__init__(self, parent)
        self.touchpad_config = config
        pages = [HardwarePage(self.touchpad, self), MotionPage(self),
                 ScrollingPage(self.touchpad, self),
                 TappingPage(self.touchpad, self)]
        for page in pages:
            self.addTab(page, page.windowTitle())
        self.setWindowTitle(
            i18nc('@title:window', 'Touchpad configuration'))
        self._setup(self.touchpad_config)

    @property
    def touchpad(self):
        """
        The :class:`~synaptiks.touchpad.Touchpad` object associated with this
        widget.
        """
        return self.touchpad_config.touchpad

    def _get_defaults(self):
        return get_touchpad_defaults()


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
