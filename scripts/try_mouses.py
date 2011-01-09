#!/usr/bin/python2
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

from PyQt4.QtGui import QApplication, QMainWindow, QSplitter, QAction, QIcon

from synaptiks.views import MouseDevicesView


def show(label, devices):
    print(label, [unicode(d) for d in devices])


def main():
    app = QApplication(sys.argv)

    window = QMainWindow()
    splitter = QSplitter(window)
    window.setCentralWidget(splitter)
    left_view = MouseDevicesView(window)
    left_view.checkedDevicesChanged.connect(partial(show, 'left:'))
    right_view = MouseDevicesView(window)
    right_view.checkedDevicesChanged.connect(partial(show, 'right:'))
    splitter.addWidget(left_view)
    splitter.addWidget(right_view)

    def _move_checked_state(source, dest):
        checked = source.property('checkedDevices').toPyObject()
        dest.setProperty('checkedDevices', checked)

    toolbar = window.addToolBar('Actions')
    move_selection_left = QAction(
        QIcon.fromTheme('arrow-left'), 'Moved checked state left', window,
        triggered=partial(_move_checked_state, right_view, left_view))
    move_selection_right = QAction(
        QIcon.fromTheme('arrow-right'), 'Moved checked state right', window,
        triggered=partial(_move_checked_state, left_view, right_view))
    toolbar.addAction(move_selection_left)
    toolbar.addAction(move_selection_right)

    window.show()
    app.exec_()


if __name__ == '__main__':
    main()

