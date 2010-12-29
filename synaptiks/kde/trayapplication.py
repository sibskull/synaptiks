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
    synaptiks.kde.trayapplication
    =============================

    Provides a simple system tray application to configure the touchpad.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import sys

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
from PyQt4.QtGui import QAction
from PyKDE4.kdecore import KCmdLineArgs, ki18nc, i18nc
from PyKDE4.kdeui import (KUniqueApplication, KStatusNotifierItem, KDialog,
                          KStandardAction, KToggleAction, KShortcut, KHelpMenu,
                          KShortcutsDialog, KShortcutsEditor, KNotification,
                          KIconLoader)

from synaptiks.qx11 import QX11Display
from synaptiks.touchpad import Touchpad
from synaptiks.config import TouchpadConfiguration
from synaptiks.kde import make_about_data
from synaptiks.kde.widgets import TouchpadConfigurationWidget


class SynaptiksConfigDialog(KDialog):
    """
    Configuration dialog used by the system tray application.
    """

    def __init__(self, touchpad, parent=None):
        KDialog.__init__(self, parent)
        self.touchpad_config = TouchpadConfiguration(touchpad)
        self.setButtons(KDialog.ButtonCodes(
            KDialog.Ok | KDialog.Cancel | KDialog.Apply | KDialog.Default))
        self.enableButtonApply(False)

        self.touchpad_config_widget = TouchpadConfigurationWidget(
            self.touchpad_config, self)
        self.touchpad_config_widget.configurationChanged.connect(
            self.enableButtonApply)

        self.setMainWidget(self.touchpad_config_widget)

        self.applyClicked.connect(self.apply_settings)
        self.okClicked.connect(self.apply_settings)
        self.defaultClicked.connect(self.touchpad_config_widget.load_defaults)

    def apply_settings(self):
        self.touchpad_config_widget.apply_configuration()
        self.touchpad_config.save()
        self.enableButtonApply(False)


class SynaptiksNotifierItem(KStatusNotifierItem):

    def __init__(self, parent=None):
        KStatusNotifierItem.__init__(self, parent)
        self.setTitle('synaptiks')
        self.setIconByName('synaptiks')
        self.setCategory(KStatusNotifierItem.Hardware)
        self.setStatus(KStatusNotifierItem.Passive)
        self.touchpad = Touchpad.find_first(QX11Display())
        self.setup_actions()

    def setup_actions(self):
        touchpad_on = KToggleAction(
            i18nc('@action:inmenu', 'Touchpad on'), self.actionCollection())
        touchpad_on.setChecked(self.touchpad.off == 0)
        self.actionCollection().addAction('touchpadOn', touchpad_on)
        touchpad_on.setGlobalShortcut(
            KShortcut(i18nc('Touchpad toggle shortcut', 'Ctrl+Alt+T')))
        # very ugly, but without the cast the bool signature of triggered is
        # not found, because KAction re-defines triggered with some other
        # signature.  I consider this an issue in PyQt/PyKDE, and this a dirty
        # workaround.
        sip.cast(touchpad_on, QAction).triggered[bool].connect(
            self.toggle_touchpad)
        self.contextMenu().addAction(touchpad_on)

        self.contextMenu().addSeparator()

        shortcuts = self.actionCollection().addAction(
            KStandardAction.KeyBindings, 'shortcuts')
        shortcuts.triggered.connect(self.show_shortcuts_dialog)
        self.contextMenu().addAction(shortcuts)

        preferences = self.actionCollection().addAction(
            KStandardAction.Preferences, 'preferences')
        preferences.triggered.connect(self.show_configuration_dialog)
        self.contextMenu().addAction(preferences)

        help_menu = KHelpMenu(self.contextMenu(), KCmdLineArgs.aboutData())
        self.contextMenu().addMenu(help_menu.menu())

    def toggle_touchpad(self, on):
        self.touchpad.off = not on
        self.show_touchpad_state()

    def show_touchpad_state(self):
        is_touchpad_on = self.touchpad.off == 0
        notification = KNotification(
            'touchpadOn' if is_touchpad_on else 'touchpadOff')
        notification.setText(
            i18nc('touchpad switched notification', 'Touchpad switched on')
            if is_touchpad_on else
            i18nc('touchpad switched notification', 'Touchpad switched off'))
        notification.setPixmap(
            KIconLoader.global_().loadIcon('synaptiks', KIconLoader.Panel))
        notification.sendEvent()

    def show_shortcuts_dialog(self):
        # The dialog is shown in non-modal form, and consequently must exists
        # even after this method returns.  So we bind the dialog to the
        # instance to keep pythons GC out of business and manually delete the
        # dialog once the user closed it
        self.shortcuts_dialog = KShortcutsDialog(
            KShortcutsEditor.GlobalAction,
            KShortcutsEditor.LetterShortcutsDisallowed)
        self.shortcuts_dialog.addCollection(self.actionCollection())
        # delete the dialog manually once the user closed it, to avoid some
        # mysterious crashes when quitting the application
        self.shortcuts_dialog.finished.connect(
            self.shortcuts_dialog.deleteLater)
        self.shortcuts_dialog.configure()

    def show_configuration_dialog(self):
        # using the same "hack" here as in show_shortcuts_dialog
        self.config_dialog = SynaptiksConfigDialog(self.touchpad)
        self.config_dialog.finished.connect(self.config_dialog.deleteLater)
        self.config_dialog.show()


class SynaptiksApplication(KUniqueApplication):

    _first_instance = True

    def newInstance(self):
        if self._first_instance:
            self.setQuitOnLastWindowClosed(False)
            # create and show the status icon on first startup
            self.icon = SynaptiksNotifierItem()
            self.aboutToQuit.connect(self.icon.deleteLater)
            self._first_instance = False
        else:
            # show the configuration dialog in an already running existing
            # instance
            self.icon.show_configuration_dialog()
        return 0


def main():
    about = make_about_data(ki18nc('tray application description',
                                   'touchpad management application'))

    KCmdLineArgs.init(sys.argv, about)
    KUniqueApplication.addCmdLineOptions()

    if not KUniqueApplication.start():
        return

    app = SynaptiksApplication()
    app.exec_()


if __name__ == '__main__':
    main()
