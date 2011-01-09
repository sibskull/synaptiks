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
    synaptiks.config
    ================

    General configuration handling for synaptiks.

    If executed as script, the touchpad configuration is loaded and applied.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import os
from collections import MutableMapping

from synaptiks.util import ensure_directory, save_json, load_json_with_default


PACKAGE_DIRECTORY = os.path.dirname(__file__)


def get_configuration_directory():
    """
    Get the configuration directory of synaptiks according to the `XDG base
    directory specification`_ as string.  The directory is guaranteed to exist.

    The configuration directory is a sub-directory of ``$XDG_CONFIG_HOME``
    (which defaults to ``$HOME/.config``).

    .. _`XDG base directory specification`: http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html
    """
    xdg_config_home = os.environ.get('XDG_CONFIG_HOME', os.path.expandvars(
        os.path.join('$HOME', '.config')))
    return ensure_directory(os.path.join(xdg_config_home, 'synaptiks'))


def get_touchpad_config_file_path():
    """
    Get the path to the file which stores the touchpad configuration.
    """
    return os.path.join(get_configuration_directory(), 'touchpad-config.json')


def get_touchpad_defaults_file_path():
    """
    Get the path to the file which stores the default touchpad configuration as
    setup by the touchpad driver.
    """
    return os.path.join(get_configuration_directory(), 'touchpad-defaults.json')


def get_management_config_file_path():
    """
    Get the path to the file which stores the touchpad management configuration.
    """
    return os.path.join(get_configuration_directory(), 'management.json')


def get_touchpad_defaults(filename=None):
    """
    Get the default touchpad settings as :func:`dict` *without* applying it to
    the touchpad.
    """
    if not filename:
        filename = get_touchpad_defaults_file_path()
    return load_json_with_default(filename, {})


class TouchpadConfiguration(MutableMapping):
    """
    A mutable mapping class representing the current configuration of the
    touchpad.
    """

    CONFIG_KEYS = frozenset([
        'minimum_speed', 'maximum_speed', 'acceleration_factor',
        'edge_motion_always', 'fast_taps',
        'rt_tap_action', 'rb_tap_action', 'lt_tap_action', 'lb_tap_action',
        'f1_tap_action', 'f2_tap_action', 'f3_tap_action',
        'tap_and_drag_gesture', 'locked_drags', 'locked_drags_timeout',
        'vertical_edge_scrolling', 'horizontal_edge_scrolling',
        'corner_coasting', 'coasting_speed',
        'vertical_scrolling_distance', 'horizontal_scrolling_distance',
        'vertical_two_finger_scrolling', 'horizontal_two_finger_scrolling',
        'circular_scrolling', 'circular_scrolling_trigger',
        'circular_scrolling_distance', 'circular_touchpad'])

    @classmethod
    def load(cls, touchpad, filename=None):
        """
        Load the configuration for the given ``touchpad`` from disc.

        If no ``filename`` is given, the configuration is loaded from the
        default configuration file as returned by
        :func:`get_touchpad_config_file_path`.  Otherwise the configuration is
        loaded from the given file.  If the file doesn't exist, an empty
        configuration is loaded.

        After the configuration is loaded, it is applied to the given
        ``touchpad``.

        ``touchpad`` is a :class:`~synaptiks.touchpad.Touchpad` object.
        ``filename`` is either ``None`` or a string containing the path to a
        file.

        Return a :class:`TouchpadConfiguration` object.  Raise
        :exc:`~exceptions.EnvironmentError`, if the file could not be loaded,
        but *not* in case of a non-existing file.
        """
        if not filename:
            filename = get_touchpad_config_file_path()
        config = cls(touchpad)
        config.update(load_json_with_default(filename, {}))
        return config

    def __init__(self, touchpad):
        """
        Create a new configuration from the given ``touchpad``.

        ``touchpad`` is a :class:`~synaptiks.touchpad.Touchpad` object.
        """
        self.touchpad = touchpad

    def __contains__(self, key):
        return key in self.CONFIG_KEYS

    def __len__(self):
        return len(self.CONFIG_KEYS)

    def __iter__(self):
        return iter(self.CONFIG_KEYS)

    def __getitem__(self, key):
        if key not in self:
            raise KeyError(key)
        value = getattr(self.touchpad, key)
        if isinstance(value, float):
            # round floats for the sake of comparability and readability
            value = round(value, 5)
        return value

    def __setitem__(self, key, value):
        if key not in self:
            raise KeyError(key)
        setattr(self.touchpad, key, value)

    def __delitem__(self, key):
        raise NotImplementedError

    def save(self, filename=None):
        """
        Save the configuration.

        If no ``filename`` is given, the configuration is saved to the default
        configuration file as returned by
        :func:`get_touchpad_config_file_path`.  Otherwise the configuration is
        saved to the given file.

        ``filename`` is either ``None`` or a string containing the path to a
        file.

        Raise :exc:`~exceptions.EnvironmentError`, if the file could not be
        written.
        """
        if not filename:
            filename = get_touchpad_config_file_path()
        save_json(filename, dict(self))


class ManagementConfiguration(MutableMapping):
    """
    A mutable mapping class representing the current configuration of the
    state machine, which manages the touchpad.
    """

    #: the default values
    DEFAULTS = {'monitor_mouses': False, 'ignored_mouses': []}

    #: config keys to be applied to the mouse_manager
    MOUSE_MANAGER_KEYS = frozenset(['ignored_mouses'])

    @classmethod
    def load(cls, state_machine, filename=None):
        """
        Load the configuration for the given ``state_machine`` from disc.

        If no ``filename`` is given, the configuration is loaded from the
        default configuration file as returned by
        :func:`get_management_config_file_path`.  Otherwise the configuration
        is loaded from the given file.  If the file doesn't exist, the default
        config as given by :attr:`DEFAULTS` is loaded.

        After the configuration is loaded, it is applied to the given
        ``state_machine``.

        ``touchpad`` is a :class:`~synaptiks.management.TouchpadStateMachine`
        object.  ``filename`` is either ``None`` or a string containing the
        path to a file.

        Return a :class:`ManagementConfiguration` object.  Raise
        :exc:`~exceptions.EnvironmentError`, if the file could not be loaded,
        but *not* in case of a non-existing file.
        """
        if not filename:
            filename = get_management_config_file_path()
        config = cls(state_machine)
        # use defaults for all non-existing settings
        loaded_config = dict(cls.DEFAULTS)
        loaded_config.update(load_json_with_default(filename, {}))
        config.update(loaded_config)
        return config

    def __init__(self, state_machine):
        self.state_machine = state_machine

    @property
    def mouse_manager(self):
        return self.state_machine.mouse_manager

    def __contains__(self, key):
        return key in self.DEFAULTS

    def __len__(self):
        return len(self.DEFAULTS)

    def __iter__(self):
        return iter(self.DEFAULTS)

    def __getitem__(self, key):
        if key not in self:
            raise KeyError(key)
        target = self.state_machine
        if key in self.MOUSE_MANAGER_KEYS:
            target = self.mouse_manager
        return getattr(target, key)

    def __setitem__(self, key, value):
        if key not in self:
            raise KeyError(key)
        target = self.state_machine
        if key in self.MOUSE_MANAGER_KEYS:
            target = self.mouse_manager
        setattr(target, key, value)

    def __delitem__(self, key):
        raise NotImplementedError

    def update(self, other):
        if other['monitor_mouses']:
            self.mouse_manager.ignored_mouses = other['ignored_mouses']
            self.state_machine.monitor_mouses = True
        else:
            self.state_machine.monitor_mouses = False
            self.mouse_manager.ignored_mouses = other['ignored_mouses']

    def save(self, filename=None):
        """
        Save the configuration.

        If no ``filename`` is given, the configuration is saved to the default
        configuration file as returned by
        :func:`get_management_config_file_path`.  Otherwise the configuration
        is saved to the given file.

        ``filename`` is either ``None`` or a string containing the path to a
        file.

        Raise :exc:`~exceptions.EnvironmentError`, if the file could not be
        written.
        """
        if not filename:
            filename = get_management_config_file_path()
        save_json(filename, dict(self))


def main():
    from argparse import ArgumentParser

    from synaptiks import __version__
    from synaptiks.touchpad import Touchpad
    from synaptiks._bindings import xlib

    parser = ArgumentParser(
        description='synaptiks touchpad configuration utility',
        epilog="""\
Copyright (C) 2010 Sebastian Wiesner <lunaryorn@googlemail.com>,
distributed under the terms of the BSD License""")
    parser.add_argument('--version', help='Show synaptiks version',
                        action='version', version=__version__)
    actions = parser.add_subparsers(title='Actions')

    init_act = actions.add_parser(
        'init', help='Initialize touchpad configuration.  Should not be '
        'called manually, but automatically at session startup.')
    init_act.set_defaults(action='init')

    load_act = actions.add_parser(
        'load', help='Load the touchpad configuration')
    load_act.add_argument(
        'filename', nargs='?', help='File to load the configuration from.  If '
        'empty, the default configuration file is loaded.')
    load_act.set_defaults(action='load')

    save_act = actions.add_parser(
        'save', help='Save the current touchpad configuration')
    save_act.add_argument(
        'filename', nargs='?', help='File to save the configuration to.  If '
        'empty, the default configuration file is used.')
    save_act.set_defaults(action='save')

    # default filename to load configuration from
    parser.set_defaults(filename=None)

    # we don't have any arguments, but need to make sure, that the builtin
    # arguments (--help mainly) are handled
    args = parser.parse_args()

    with xlib.display() as display:
        touchpad = Touchpad.find_first(display)

        if args.action == 'init':
            driver_defaults = TouchpadConfiguration(touchpad)
            driver_defaults.save(get_touchpad_defaults_file_path())
        if args.action in ('init', 'load'):
            TouchpadConfiguration.load(touchpad, filename=args.filename)
        if args.action == 'save':
            current_config = TouchpadConfiguration(touchpad)
            current_config.save(filename=args.filename)


if __name__ == '__main__':
    main()
