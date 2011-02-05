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


def pytest_generate_tests(metafunc):
    if metafunc.cls == TestTouchpadConfiguration:
        if 'key' in metafunc.funcargnames:
            for key in config.TouchpadConfiguration.CONFIG_KEYS:
                metafunc.addcall(funcargs=dict(key=key), id=key)


def pytest_funcarg__touchpad_config(request):
    keys = config.TouchpadConfiguration.CONFIG_KEYS
    touchpad = mock.Mock(name='Touchpad', spec_set=list(keys))
    return config.TouchpadConfiguration(touchpad)


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


def test_get_touchpad_config_file_path(tmpdir):
    with config_home(tmpdir):
        assert_config_file_path(config.get_touchpad_config_file_path(),
                                'touchpad-config.json')


def test_get_touchpad_defaults_file_path(tmpdir):
    with config_home(tmpdir):
        assert_config_file_path(config.get_touchpad_defaults_file_path(),
                                'touchpad-defaults.json')


def test_get_management_config_file_path(tmpdir):
    with config_home(tmpdir):
        assert_config_file_path(config.get_management_config_file_path(),
                                'management.json')


def test_get_touchpad_defaults_non_existing_with_filename(tmpdir):
    test_file = tmpdir.join('test.json')
    assert test_file.check(exists=False)
    assert config.get_touchpad_defaults(str(test_file)) == {}


def test_get_touchpad_defaults_non_existing_without_filename(tmpdir):
    with config_home(tmpdir) as config_home_dir:
        assert config.get_touchpad_defaults() == {}
        assert config_home_dir.check(exists=True, dir=True)


def test_get_touchpad_defaults_existing_with_filename(tmpdir):
    test_file = tmpdir.join('test.json')
    data = {'spam': 'eggs'}
    test_file.write(json.dumps(data))
    assert test_file.check(exists=True, file=True)
    assert config.get_touchpad_defaults(str(test_file)) == data


def test_get_touchpad_defaults_existing_without_filename(tmpdir):
    with config_home(tmpdir):
        defaults_file = py.path.local(config.get_touchpad_defaults_file_path())
        data = {'spam': 'eggs'}
        defaults_file.write(json.dumps(data))
        assert defaults_file.check(exists=True, file=True)
        assert config.get_touchpad_defaults() == data


class TestTouchpadConfiguration(object):

    def test_load_without_filename_non_existing(self, tmpdir):
        with config_home(tmpdir):
            touchpad = mock.Mock(name='touchpad', spec_set=[])
            # due to the empty spec set, this will raise exceptions, if any
            # attributes are set on the touchpad mock
            touchpad_config = config.TouchpadConfiguration.load(touchpad)
            assert touchpad_config.touchpad is touchpad

    def test_load_without_filename_existing(self, tmpdir):
        with config_home(tmpdir):
            config_file = py.path.local(config.get_touchpad_config_file_path())
            keys = config.TouchpadConfiguration.CONFIG_KEYS
            config_file.write(json.dumps(dict((k, 'eggs') for k in keys)))
            touchpad = mock.Mock(name='Touchpad', spec_set=list(keys))
            touchpad_config = config.TouchpadConfiguration.load(touchpad)
            assert touchpad_config.touchpad is touchpad
            assert all(getattr(touchpad, k) == 'eggs' for k in keys)

    def test_load_with_filename_non_existing(self, tmpdir):
        config_file = tmpdir.join('test.json')
        assert config_file.check(exists=False)
        touchpad = mock.Mock(name='touchpad', spec_set=[])
        # due to the empty spec set, this will raise exceptions, if any
        # attributes are set on the touchpad mock
        touchpad_config = config.TouchpadConfiguration.load(
            touchpad, str(config_file))
        assert touchpad_config.touchpad is touchpad

    def test_load_with_filename_existing(self, tmpdir):
        config_file = tmpdir.join('test.json')
        keys = config.TouchpadConfiguration.CONFIG_KEYS
        config_file.write(json.dumps(dict((k, 'eggs') for k in keys)))
        touchpad = mock.Mock(name='Touchpad', spec_set=list(keys))
        touchpad_config = config.TouchpadConfiguration.load(
            touchpad, str(config_file))
        assert touchpad_config.touchpad is touchpad
        assert all(getattr(touchpad, k) == 'eggs' for k in keys)

    def test_init(self):
        cfg = config.TouchpadConfiguration(mock.sentinel.touchpad)
        assert cfg.touchpad is mock.sentinel.touchpad

    def test_contains(self, key, touchpad_config):
        assert key in touchpad_config

    def test_iter(self, touchpad_config):
        assert set(touchpad_config) == config.TouchpadConfiguration.CONFIG_KEYS

    def test_len(self, touchpad_config):
        assert len(touchpad_config) == \
               len(config.TouchpadConfiguration.CONFIG_KEYS)

    def test_getitem(self, touchpad_config, key):
        setattr(touchpad_config.touchpad, key, mock.sentinel.value)
        assert touchpad_config[key] is mock.sentinel.value

    def test_getitem_float(self, touchpad_config, key):
        setattr(touchpad_config.touchpad, key, 5.2500000125)
        assert getattr(touchpad_config.touchpad, key) != 5.25
        assert touchpad_config[key] == 5.25

    def test_getitem_wrong_key(self, touchpad_config):
        with pytest.raises(KeyError):
            touchpad_config['spam']

    def test_setitem(self, touchpad_config, key):
        touchpad_config[key] = mock.sentinel.value
        assert getattr(touchpad_config.touchpad, key) is mock.sentinel.value

    def test_setitem_wrong_key(self, touchpad_config):
        with pytest.raises(KeyError):
            touchpad_config['spam'] = mock.sentinel.value

    def test_delitem(self, touchpad_config, key):
        with pytest.raises(NotImplementedError):
            del touchpad_config[key]


class TestManagerConfiguration(object):
    pass
