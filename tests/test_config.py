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

import os
import json
from contextlib import contextmanager

import mock
import pytest
import py.path

from synaptiks import config
from synaptiks.management import TouchpadManager


@contextmanager
def config_home(tmpdir):
    """
    A context manager, in whose block ``$XDG_CONFIG_HOME`` is set to
    ``<tmpdir>/config``.  Once the block is left, ``$XDG_CONFIG_HOME`` is
    reset.

    Upon entry, the context manager returns the new path of
    ``$XDG_CONFIG_HOME`` as :class:`py.path.local` object.
    """
    config_home = tmpdir.join('config')
    with mock.patch.dict(os.environ, {'XDG_CONFIG_HOME': str(config_home)}):
        yield config_home


def assert_config_file_path(file_path, name):
    __tracebackhide__ = True
    if isinstance(file_path, basestring):
        file_path = py.path.local(file_path)
    assert file_path.check(exists=False)
    assert file_path.basename == name
    assert file_path.dirpath() == py.path.local(
        config.get_configuration_directory())
    assert file_path.dirpath().check(dir=True, exists=True)



def test_get_configuration_directory_default():
    directory = config.get_configuration_directory()
    assert os.path.normpath(directory) == os.path.normpath(
        os.path.expanduser(os.path.join('~', '.config', 'synaptiks')))


def test_get_configuration_directory_nondefault(tmpdir):
    with config_home(tmpdir) as config_home_dir:
        assert config_home_dir.check(exists=False)
        config_directory = py.path.local(config.get_configuration_directory())
        assert config_directory == config_home_dir.join('synaptiks')
        assert config_directory.check(exists=True, dir=True)


class DummyConfig(config.AbstractConfiguration):

    @staticmethod
    def default_filename():
        directory = config.get_configuration_directory()
        return os.path.join(directory, 'dummy.json')

    @staticmethod
    def defaults():
        return {'spam': 'yes'}


class TestAbstractConfiguration(object):
    cls = DummyConfig

    def test_load_without_filename_non_existing(self, tmpdir):
        with config_home(tmpdir):
            assert self.cls.load() == {'spam': 'yes'}

    def test_load_without_filename_existing(self, tmpdir):
        with config_home(tmpdir) as config_dir:
            config_file = config_dir.join('synaptiks').join('dummy.json')
            config_file.ensure(file=True)
            config_file.write(json.dumps({'spam': 'eggs'}))
            assert self.cls.load() == {'spam': 'eggs'}

    def test_load_with_filename_non_existing(self, tmpdir):
        config_file = tmpdir.join('test.json')
        assert config_file.check(exists=False)
        assert self.cls.load() == {'spam': 'yes'}

    def test_load_with_filename_existing(self, tmpdir):
        config_file = tmpdir.join('test.json')
        config_file.ensure(file=True)
        config_file.write(json.dumps({'spam': 'eggs'}))
        assert self.cls.load(str(config_file)) == {'spam': 'eggs'}

    def test_save_without_filename(self, tmpdir):
        config = self.cls(spam='eggs')
        with config_home(tmpdir) as config_dir:
            config.save()
            contents = config_dir.join('synaptiks', 'dummy.json').read()
            assert json.loads(contents) == {'spam': 'eggs'}

    def test_save_with_filename(self, tmpdir):
        config = self.cls(spam='eggs')
        config_file = tmpdir.join('test.json')
        config.save(str(config_file))
        assert json.loads(config_file.read()) == {'spam': 'eggs'}



def _find_touchpad_properties_to_configure():
    properties = set()
    from synaptiks.touchpad import Touchpad, device_property
    for attr, obj in vars(Touchpad).iteritems():
        if isinstance(obj, device_property) and attr != 'off':
            properties.add(attr)
    return properties


TOUCHPAD_PROPERTIES = _find_touchpad_properties_to_configure()


def pytest_funcarg__mock_touchpad(request):
    touchpad = mock.Mock(name='Touchpad', spec_set=list(TOUCHPAD_PROPERTIES))
    for p in TOUCHPAD_PROPERTIES:
        setattr(touchpad, p, mock.sentinel.value)
    return touchpad


class TestTouchpadConfiguration(object):

    cls = config.TouchpadConfiguration

    def test_default_filename(self, tmpdir):
        with config_home(tmpdir):
            assert_config_file_path(self.cls.default_filename(),
                                    'touchpad-config.json')

    def test_defaults_non_existing(self, tmpdir):
        with config_home(tmpdir):
            assert self.cls.defaults() == {}

    def test_defaults_existing(self, tmpdir):
        with config_home(tmpdir):
            config_dir = py.path.local(config.get_configuration_directory())
            defaults_file = config_dir.join('touchpad-defaults.json')
            defaults_file.write(json.dumps({'spam': 'eggs'}))
            assert defaults_file.check(exists=True, file=True)
            assert self.cls.defaults() == {'spam': 'eggs'}

    def test_load_from_touchpad(self, tmpdir, mock_touchpad):
        with config_home(tmpdir):
            config_file = py.path.local(self.cls.default_filename())
            config_file.write(json.dumps({'spam': 'eggs', 'fast_taps': True}))
            config = self.cls.load_from_touchpad(mock_touchpad)
            expected = dict((p, mock.sentinel.value) for p in TOUCHPAD_PROPERTIES)
            expected.update(spam='eggs')
            assert config == expected

    def test_load_from_touchpad_with_filename(self, tmpdir, mock_touchpad):
        config_file = tmpdir.join('test.json')
        config_file.write(json.dumps({'spam': 'eggs', 'fast_taps': True}))
        config = self.cls.load_from_touchpad(mock_touchpad, str(config_file))
        expected = dict((p, mock.sentinel.value) for p in TOUCHPAD_PROPERTIES)
        expected.update(spam='eggs')
        assert config == expected

    def test_apply_to_incomplete(self):
        config = self.cls()
        with pytest.raises(KeyError):
            config.apply_to(mock.Mock(name='Touchpad'))

    def test_apply_to(self, mock_touchpad):
        config = self.cls((p, mock.sentinel.changed_value)
                          for p in TOUCHPAD_PROPERTIES)
        config.apply_to(mock_touchpad)
        assert all(getattr(mock_touchpad, p) == mock.sentinel.changed_value
                   for p in TOUCHPAD_PROPERTIES)

    def test_update_from_touchpad(self, mock_touchpad):
        config = self.cls()
        config.update_from_touchpad(mock_touchpad)
        expected = dict((p, mock.sentinel.value) for p in TOUCHPAD_PROPERTIES)
        assert config == expected

    def test_touchpad_properties(self):
        assert self.cls.CONFIGURABLE_TOUCHPAD_PROPERTIES == TOUCHPAD_PROPERTIES


class TestManagerConfiguration(object):

    cls = config.ManagerConfiguration

    def test_defaults(self):
        assert self.cls.defaults() == self.cls._DEFAULTS
        assert self.cls.load() == self.cls._DEFAULTS

    def test_apply_to(self):
        manager = mock.Mock(
            name='Manager', spec_set=['keyboard_monitor', 'mouse_manager',
                                      'monitor_mouses', 'monitor_keyboard'])
        manager.keyboard_monitor = mock.Mock(
            name='KeyboardMonitor', spec_set=['idle_time', 'keys_to_ignore'])
        manager.mouse_manager = mock.Mock(
            name='MouseManager', spec_set=['ignored_mouses'])
        config = self.cls.load()
        config.apply_to(manager)
        assert manager.monitor_mouses == False
        assert manager.monitor_keyboard == False
        assert manager.keyboard_monitor.idle_time == 2.0
        assert manager.keyboard_monitor.keys_to_ignore == 2
        assert manager.mouse_manager.ignored_mouses == []
