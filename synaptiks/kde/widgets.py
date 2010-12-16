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

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
from PyQt4.uic import loadUi
from PyQt4.QtGui import QWidget
from PyKDE4.kdecore import i18nc
from PyKDE4.kdeui import KIconLoader


PACKAGE_DIRECTORY = os.path.dirname(__file__)


class _DynamicUserInterfaceMixin(object):
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



class TouchpadInformationWidget(QWidget, _DynamicUserInterfaceMixin):
    """
    A widget which shows some information about a touchpad.

    This currently includes:

    - the device name of the touchpad,
    - what physical buttons, the touchpad has,
    - how many fingers it can detect,
    - and whether it supports two-finger emulation.
    """

    def __init__(self, touchpad, parent=None):
        """
        Create a new information widget for the given ``touchpad``.

        ``touchpad`` is a :class:`~synaptiks.touchpad.Touchpad`
        object. ``parent`` is the parent :class:`~PyQt4.QtGui.QWidget` (can be
        ``None``).
        """
        QWidget.__init__(self, parent)
        self._load_userinterface()
        self.show_touchpad(touchpad)

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
