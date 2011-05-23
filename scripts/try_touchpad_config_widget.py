#!/usr/bin/python2
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

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import sys
from functools import partial

from PyKDE4.kdecore import KCmdLineArgs, KAboutData, ki18n
from PyKDE4.kdeui import KApplication, KMainWindow

import synaptiks
from synaptiks.x11 import Display
from synaptiks.touchpad import Touchpad
from synaptiks.config import TouchpadConfiguration
from synaptiks.kde.widgets.touchpad import TouchpadConfigurationWidget


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
    window = KMainWindow()
    touchpad = Touchpad.find_first(Display.from_qt())
    config = TouchpadConfiguration(touchpad)
    config_widget = TouchpadConfigurationWidget(config)
    config_widget.configurationChanged.connect(
        partial(print, 'config changed?'))
    window.setCentralWidget(config_widget)
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
