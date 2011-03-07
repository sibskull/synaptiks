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

from PyQt4.QtGui import (QApplication, QMainWindow, QWidget, QLabel,
                         QVBoxLayout, QComboBox, QAction)

from synaptiks.monitors import AbstractKeyboardMonitor, create_keyboard_monitor


def main():
    app = QApplication(sys.argv)

    window = QMainWindow()
    central_widget = QWidget(window)

    start_action = QAction('Start', window)
    stop_action = QAction('Stop', window)
    toolbar = window.addToolBar('Monitor')
    toolbar.addAction(start_action)
    toolbar.addAction(stop_action)

    central_layout = QVBoxLayout(central_widget)

    monitor_name = QLabel(central_widget)
    central_layout.addWidget(monitor_name)

    state_label = QLabel(central_widget)
    central_layout.addWidget(state_label)

    combo_box = QComboBox(central_widget)
    items = [
        ('No keys', AbstractKeyboardMonitor.IGNORE_NO_KEYS),
        ('Modifiers', AbstractKeyboardMonitor.IGNORE_MODIFIER_KEYS),
        ('Modifier combos', AbstractKeyboardMonitor.IGNORE_MODIFIER_COMBOS)]
    for label, userdata in items:
        combo_box.addItem(label, userdata)

    def _update_ignore_keys(index):
        monitor.keys_to_ignore = combo_box.itemData(index).toPyObject()

    combo_box.currentIndexChanged[int].connect(_update_ignore_keys)
    central_layout.addWidget(combo_box)

    central_widget.setLayout(central_layout)
    window.setCentralWidget(central_widget)

    monitor = create_keyboard_monitor(window)
    monitor_name.setText('Using monitor class {0}'.format(
        monitor.__class__.__name__))
    monitor.typingStarted.connect(partial(state_label.setText, 'typing'))
    monitor.typingStopped.connect(partial(state_label.setText, 'not typing'))
    start_action.triggered.connect(monitor.start)
    stop_action.triggered.connect(monitor.stop)
    stop_action.setEnabled(False)
    monitor.started.connect(partial(start_action.setEnabled, False))
    monitor.started.connect(partial(stop_action.setEnabled, True))
    monitor.stopped.connect(partial(start_action.setEnabled, True))
    monitor.stopped.connect(partial(stop_action.setEnabled, False))
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
