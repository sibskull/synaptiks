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
    synaptiks.kde.widgets.config
    ============================

    Generic configuration widgets.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from functools import partial

from PyQt4.QtCore import QRegExp, QString
from PyQt4.QtGui import QWidget


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
        return unicode(widget.objectName()[len(self.NAME_PREFIX) + 1:])

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
        can have an arbitrary type.  ``key`` is the configuration key as
        string.

        The default implementation does nothing.

        Return the converted ``value``.
        """
        if isinstance(value, QString):
            return unicode(value)
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
        return self.__config != self._get_mapping_from_widgets()

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
        self.__config.update(self._get_mapping_from_widgets())
        self.configurationChanged.emit(self.is_configuration_changed)
