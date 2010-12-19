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
from PyKDE4.kdecore import KCmdLineArgs, KAboutData, ki18n, i18nc
from PyKDE4.kdeui import (KApplication, KSystemTrayIcon, KDialog,
                          KPageDialog, KIcon,
                          KAction, KStandardAction, KHelpMenu)

import synaptiks
from synaptiks.touchpad import Touchpad
from synaptiks.kde.widgets import (TouchpadInformationWidget,
                                   TouchpadConfigurationWidget)


class SynaptiksConfigDialog(KPageDialog):
    """
    Configuration dialog used by the system tray application.
    """

    def __init__(self, touchpad, parent=None):
        KPageDialog.__init__(self, parent)
        self.touchpad = touchpad
        self.setFaceType(KPageDialog.List)
        self.setButtons(KDialog.ButtonCodes(
            KDialog.Ok | KDialog.Cancel | KDialog.Apply))
        self.enableButtonApply(False)

        self.touchpad_config = TouchpadConfigurationWidget(self.touchpad, self)
        self.touchpad_config.configurationChanged.connect(
            self.enableButtonApply)

        for page, icon_name in [(self.touchpad_config, 'configure')]:
            page_item = self.addPage(page, page.windowTitle())
            page_item.setIcon(KIcon(icon_name))

        self.applyClicked.connect(self.apply_settings)
        self.okClicked.connect(self.apply_settings)

        self.load_settings()

    def load_settings(self):
        self.touchpad_config.load_configuration()

    def apply_settings(self):
        self.touchpad_config.apply_configuration()
        self.enableButtonApply(False)


class SynaptiksTrayIcon(KSystemTrayIcon):
    def __init__(self, parent=None):
        KSystemTrayIcon.__init__(self, parent)
        self.setup_actions()
        self.touchpad = Touchpad.find_first()
        self.setIcon(KSystemTrayIcon.loadIcon('synaptiks'))
        # explicitly delete the tray icon before quitting to avoid some rather
        # mysterious crashes.  Should be considered a really nasty hack.
        self.quitSelected.connect(self.deleteLater)

    def setup_actions(self):
        touchpad_information = KAction(
            i18nc('@action:inmenu', 'Touchpad information ...'),
            self.actionCollection())
        self.actionCollection().addAction('information',
                                          touchpad_information)
        touchpad_information.triggered.connect(
            self.show_touchpad_information_dialog)
        self.contextMenu().addAction(touchpad_information)

        preferences = self.actionCollection().addAction(
            KStandardAction.Preferences, 'preferences')
        preferences.triggered.connect(self.show_configuration_dialog)
        self.contextMenu().addAction(preferences)

        self.contextMenu().addSeparator()

        help_menu = KHelpMenu(self.contextMenu(), KCmdLineArgs.aboutData())
        self.contextMenu().addMenu(help_menu.menu())

    def show_configuration_dialog(self):
        # using the same "hack" here as in show_touchpad_information_dialog
        self.config_dialog = SynaptiksConfigDialog(self.touchpad)
        self.config_dialog.finished.connect(self.config_dialog.deleteLater)
        self.config_dialog.show()

    def show_touchpad_information_dialog(self):
        # The dialog is shown in non-modal form, and consequently must exists
        # even after this method returns.  So we bind the dialog to the
        # instance to keep pythons GC out of business and manually delete the
        # dialog once the user closed it
        self.info_dialog = KDialog()
        # delete the dialog manually once the user closed it
        self.info_dialog.finished.connect(self.info_dialog.deleteLater)
        info_widget = TouchpadInformationWidget(self.touchpad,
                                                self.info_dialog)
        self.info_dialog.setMainWidget(info_widget)
        self.info_dialog.setWindowTitle(info_widget.windowTitle())
        self.info_dialog.resize(info_widget.minimumSize())
        self.info_dialog.show()


def main():
    about = KAboutData(
        b'synaptiks', '', ki18n('synaptiks'), str(synaptiks.__version__),
        ki18n('touchpad management and configuration application'),
        KAboutData.License_BSD,
        ki18n('Copyright (C) 2009, 2010 Sebastian Wiesner'))
    about.addAuthor(ki18n('Sebastian Wiesner'), ki18n('Maintainer'),
                    'lunaryorn@googlemail.com')
    about.addCredit(ki18n('Valentyn Pavliuchenko'),
                    ki18n('Debian packaging, russian translation, '
                          'bug reporting and testing'),
                    'valentyn.pavliuchenko@gmail.com')
    about.setHomepage('http://synaptiks.lunaryorn.de/')
    about.setOrganizationDomain('synaptiks.lunaryorn.de')

    KCmdLineArgs.init(sys.argv, about)
    app = KApplication()
    app.setQuitOnLastWindowClosed(False)
    icon = SynaptiksTrayIcon()
    icon.show()
    app.exec_()


if __name__ == '__main__':
    main()
