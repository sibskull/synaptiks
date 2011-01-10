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
    synaptiks.kde.trayapplication
    =============================

    Provides a simple system tray application to configure the touchpad.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import sys
from functools import partial

from PyKDE4.kdecore import KCmdLineArgs, ki18nc, i18nc
from PyKDE4.kdeui import (KUniqueApplication, KStatusNotifierItem,
                          KConfigDialog, KShortcutsDialog, KMessageBox,
                          KShortcutsEditor, KShortcut,
                          KStandardAction, KToggleAction,
                          KHelpMenu, KIcon, KIconLoader,
                          KNotification, KConfigSkeleton)

from synaptiks.qx11 import QX11Display
from synaptiks.touchpad import Touchpad
from synaptiks.management import TouchpadStateMachine
from synaptiks.config import TouchpadConfiguration, ManagementConfiguration
from synaptiks.kde import make_about_data
from synaptiks.kde.widgets.touchpad import TouchpadConfigurationWidget
from synaptiks.kde.widgets.management import TouchpadManagementWidget


class SynaptiksConfigDialog(KConfigDialog):
    """
    Configuration dialog used by the system tray application.
    """

    DIALOG_NAME = 'synaptiks-configuration'

    def __init__(self, touchpad, state_machine, tray_config, parent=None):
        KConfigDialog.__init__(self, parent, self.DIALOG_NAME, tray_config)
        self.touchpad_config = TouchpadConfiguration(touchpad)
        self.management_config = ManagementConfiguration(state_machine)

        self.setFaceType(self.List)

        self.touchpad_config_widget = TouchpadConfigurationWidget(
            self.touchpad_config, self)
        self.management_config_widget = TouchpadManagementWidget(
            self.management_config, self)

        self.config_widgets = [self.touchpad_config_widget,
                               self.management_config_widget]
        for widget in self.config_widgets:
            widget.configurationChanged.connect(self.settingsChangedSlot)

        pages = [(self.management_config_widget, 'configure'),
                 (self.touchpad_config_widget, 'synaptiks')]
        for page_widget, page_icon_name in pages:
            page = self.addPage(page_widget, page_widget.windowTitle())
            page.setIcon(KIcon(page_icon_name))

    def hasChanged(self):
        return (KConfigDialog.hasChanged(self) or
                any(w.is_configuration_changed for w in self.config_widgets))

    def isDefault(self):
        return (KConfigDialog.isDefault(self) or
                any(w.shows_defaults() for w in self.config_widgets))

    def updateWidgetsDefault(self):
        KConfigDialog.updateWidgetsDefault(self)
        for widget in self.config_widgets:
            widget.load_defaults()

    def updateWidgets(self):
        KConfigDialog.updateWidgets(self)
        for widget in self.config_widgets:
            widget.load_configuration()

    def updateSettings(self):
        KConfigDialog.updateSettings(self)
        for widget in self.config_widgets:
            widget.apply_configuration()
        self.touchpad_config.save()
        self.management_config.save()


class SynaptiksTrayConfiguration(KConfigSkeleton):
    """
    Configuration specific for the tray application.
    """

    def __init__(self, parent=None):
        KConfigSkeleton.__init__(self, 'synaptiksrc', parent)
        self.setCurrentGroup('General')
        self.addItemBool('Autostart', False, False)


class SynaptiksNotifierItem(KStatusNotifierItem):

    def __init__(self, parent=None):
        KStatusNotifierItem.__init__(self, parent)
        self.setTitle('synaptiks')
        self.setIconByName('synaptiks')
        self.setCategory(KStatusNotifierItem.Hardware)
        self.setStatus(KStatusNotifierItem.Passive)
        self.setup_actions()

        self._config = SynaptiksTrayConfiguration(self)

        try:
            self.touchpad = Touchpad.find_first(QX11Display())
        except Exception as error:
            # show an error message
            from synaptiks.kde.error import get_localized_error_message
            error_message = get_localized_error_message(error)
            options = KMessageBox.Options(KMessageBox.Notify |
                                          KMessageBox.AllowLink)
            KMessageBox.error(None, error_message, '', options)
            # disable all touchpad related actions
            for act in (self.touchpad_on_action, self.preferences_action):
                act.setEnabled(False)
            # disable synaptiks autostart, the user can still start synaptiks
            # manually again, if the reason of the error is fixed
            self._config.findItem('Autostart').setProperty(False)
            self._config.writeConfig()
        else:
            self.activateRequested.connect(self.show_configuration_dialog)
            # setup the touchpad state machine
            self.touchpad_states = TouchpadStateMachine(self.touchpad, self)
            ManagementConfiguration.load(self.touchpad_states)
            # transition upon touchpad_on_action
            self.touchpad_states.add_touchpad_switch_action(
                self.touchpad_on_action)
            # update checked state of touchpad_on_action
            self.touchpad_states.touchpad_on.assignProperty(
                self.touchpad_on_action, 'checked', True)
            self.touchpad_states.touchpad_manually_off.assignProperty(
                self.touchpad_on_action, 'checked', False)
            # update the overlay icon
            self.touchpad_states.touchpad_on.entered.connect(
                partial(self.setOverlayIconByName, 'touchpad-off'))
            self.touchpad_states.touchpad_on.exited.connect(
                partial(self.setOverlayIconByName, ''))
            self.touchpad_states.start()

    def setup_actions(self):
        self.touchpad_on_action = KToggleAction(
            i18nc('@action:inmenu', 'Touchpad on'), self.actionCollection())
        self.actionCollection().addAction(
            'touchpadOn', self.touchpad_on_action)
        self.touchpad_on_action.setGlobalShortcut(
            KShortcut(i18nc('Touchpad toggle shortcut', 'Ctrl+Alt+T')))
        self.contextMenu().addAction(self.touchpad_on_action)

        self.contextMenu().addSeparator()

        shortcuts = self.actionCollection().addAction(
            KStandardAction.KeyBindings, 'shortcuts')
        shortcuts.triggered.connect(self.show_shortcuts_dialog)
        self.contextMenu().addAction(shortcuts)

        self.preferences_action = self.actionCollection().addAction(
            KStandardAction.Preferences, 'preferences')
        self.preferences_action.triggered.connect(
            self.show_configuration_dialog)
        self.contextMenu().addAction(self.preferences_action)

        help_menu = KHelpMenu(self.contextMenu(), KCmdLineArgs.aboutData())
        self.contextMenu().addMenu(help_menu.menu())

    def notify_touchpad_state(self, is_off=None):
        if is_off is None:
            is_off = self.touchpad.off
        # show a notification
        if is_off:
            event_id = 'touchpadOff'
            text = i18nc('touchpad switched notification',
                         'Touchpad switched off')
        else:
            event_id = 'touchpadOn'
            text = i18nc('touchpad switched notification',
                         'Touchpad switched on')
        icon = KIconLoader.global_().loadIcon('synaptiks', KIconLoader.Panel)
        KNotification.event(event_id, text, icon)

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
        self.config_dialog = SynaptiksConfigDialog(
            self.touchpad, self.touchpad_states, self._config)
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
