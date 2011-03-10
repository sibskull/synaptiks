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

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QWidget, QHBoxLayout, QCheckBox, QLineEdit

from synaptiks.kde.widgets.config import ConfigurationWidgetMixin


class DummyConfigWidget(QWidget, ConfigurationWidgetMixin):

    NAME_PREFIX = 'dummy'
    PROPERTY_MAP = dict(QCheckBox='checked', QLineEdit='text')
    CHANGED_SIGNAL_MAP = dict(QCheckBox='toggled', QLineEdit='textChanged')

    configurationChanged = pyqtSignal(bool)

    def __init__(self, config, parent=None):
        QWidget.__init__(self, parent)
        layout = QHBoxLayout(self)
        self.setLayout(layout)
        self.checkbox = QCheckBox(self)
        self.checkbox.setObjectName('dummy_checkbox')
        layout.addWidget(self.checkbox)
        self.lineedit = QLineEdit(self)
        self.lineedit.setObjectName('dummy_lineedit')
        layout.addWidget(self.lineedit)
        self._setup(config)

    def _get_defaults(self):
        return {'lineedit': 'spam', 'checkbox': False}

    def change(self, text, check_state):
        self.lineedit.setText(text)
        self.checkbox.setChecked(check_state)

    def check(self, text, check_state):
        __tracebackhide__ = True
        assert unicode(self.lineedit.text()) == text
        assert self.checkbox.isChecked() == check_state


def pytest_funcarg__config(request):
    return {'lineedit': 'spam', 'checkbox': False}


def pytest_funcarg__config_widget(request):
    return DummyConfigWidget(request.getfuncargvalue('config'))


class TestConfigurationWidgetMixin(object):

    def test_setup(self, config_widget):
        config_widget.check('spam', False)

    def test_configuration_changed(self, config_widget):
        signal_calls = []
        config_widget.configurationChanged.connect(signal_calls.append)
        config_widget.change('eggs', True)
        assert signal_calls == [True, True]
        del signal_calls[:]
        config_widget.apply_configuration()
        signal_calls == [False]
        del signal_calls[:]
        config_widget.load_defaults()
        assert signal_calls == [True, True]
        del signal_calls[:]
        config_widget.load_configuration()
        assert signal_calls == [True, False]

    def test_is_configuration_changed(self, config_widget):
        assert not config_widget.is_configuration_changed
        config_widget.change('eggs', True)
        assert config_widget.is_configuration_changed
        config_widget.apply_configuration()
        assert not config_widget.is_configuration_changed

    def test_load_defaults(self, config_widget):
        config_widget.change('eggs', True)
        assert not config_widget.shows_defaults()
        config_widget.load_defaults()
        assert config_widget.shows_defaults()
        config_widget.check('spam', False)

    def test_shows_defaults(self, config, config_widget):
        assert config_widget.shows_defaults()
        config_widget.change('eggs', True)
        assert not config_widget.shows_defaults()

    def test_load_configuration(self, config, config_widget):
        config['checkbox'] = True
        config['lineedit'] = 'eggs'
        config_widget.load_configuration()
        config_widget.check('eggs', True)

    def test_apply_configuration(self, config, config_widget):
        config_widget.change('eggs', True)
        config_widget.apply_configuration()
        assert config == {'lineedit': 'eggs', 'checkbox': True}
