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

    Configuration classes
    ---------------------

    This module provides the configuration classes for the touchpad and the
    touchpad manager.  These configuration classes are simply mappings, which
    expose the *current* state of the associated objects (and *not* the state
    of the configuration on disk).  This allows the user to configure the live
    state of these objects, which is especially important for touchpad
    configuration, which can be changed from outside of **synaptiks** using
    utilities like :program:`xinput`.

    To save the configuration permanently, these mappings, and consequently the
    current configuration state of the associated objects, is simply dumped in
    JSON format to the configuration directory (see
    :func:`get_configuration_directory()`).

    To apply a dumped configuration, it is loaded as standard dict from the
    JSON dump, and then the corresponding configuration mapping is updated with
    this dict.  All configuration mappings provide a convenient
    :meth:`~TouchpadConfiguration.load()` method to create a new configuration
    mapping updated with the dumped configuration.

    Handling of default values
    --------------------------

    The touchpad manager configuration (see :class:`ManagerConfiguration`)
    provides explicit defaults.  The touchpad configuration (see
    :class:`TouchpadConfiguration`) however uses defaults provided by the
    touchpad driver.

    As the touchpad driver doesn't expose special access to the default values,
    **synaptiks** simply creates a :class:`TouchpadConfiguration` after session
    startup, but *before* loading the actual configuration from disk.  At this
    point, the touchpad still uses the driver default setting, which are now
    dumped to a special file in JSON format (see
    :func:`get_touchpad_defaults_file_path()`).  They can later be loaded using
    :func:`get_touchpad_defaults()`.

    Script usage
    ------------

    .. program:: synaptikscfg

    This module is usable as script, available also as :program:`synaptikscfg`
    in the ``$PATH``.  It provides three different, of which ``load`` and
    ``save`` are really self-explanatory. ``init`` however deserves some
    detailled explanation.

    The `init` action is supposed to run automatically as script during session
    startup.  To do this, the installation script installs an autostart entry
    to execute ``synaptikscfg init`` at KDE startup.  This action first dumps
    the default settings from the touchpad driver as described above, and then
    loads and applies the actual touchpad configuration stored on disk.

    The command line parsing of the script is implemented with :mod:`argparse`,
    so you can expected standard semantics, and an extensive ``--help`` option.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import os
from collections import MutableMapping

from synaptiks.util import ensure_directory, save_json, load_json


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
    return os.path.join(get_configuration_directory(),
                        'touchpad-defaults.json')


def get_management_config_file_path():
    """
    Get the path to the file which stores the touchpad management
    configuration.
    """
    return os.path.join(get_configuration_directory(), 'management.json')


def get_touchpad_defaults(filename=None):
    """
    Get the default touchpad settings as :func:`dict` *without* applying it to
    the touchpad.
    """
    if not filename:
        filename = get_touchpad_defaults_file_path()
    return load_json(filename, default={})


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
        config.update(load_json(filename, default={}))
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


class ManagerConfiguration(MutableMapping):
    """
    A mutable mapping class representing the configuration of a
    :class:`~synaptiks.management.TouchpadManager`.
    """

    #: A mapping with the default values for all configuration keys
    DEFAULTS = {'monitor_mouses': False, 'ignored_mouses': [],
                'monitor_keyboard': False, 'idle_time': 2.0,
                'keys_to_ignore': 2}

    #: config keys to be applied to the mouse_manager
    MOUSE_MANAGER_KEYS = frozenset(['ignored_mouses'])
    #: config keys to be applied to the keyboard monitor
    KEYBOARD_MONITOR_KEYS = frozenset(['idle_time', 'keys_to_ignore'])

    @classmethod
    def load(cls, touchpad_manager, filename=None):
        """
        Load the configuration for the given ``touchpad_manager`` from disc.

        If no ``filename`` is given, the configuration is loaded from the
        default configuration file as returned by
        :func:`get_management_config_file_path`.  Otherwise the configuration
        is loaded from the given file.  If the file doesn't exist, the default
        config as given by :attr:`DEFAULTS` is loaded.

        After the configuration is loaded, it is applied to the given
        ``touchpad_manager``.

        ``touchpad_manager`` is a
        :class:`~synaptiks.management.TouchpadManager` object.  ``filename`` is
        either ``None`` or a string containing the path to a file.

        Return a :class:`ManagerConfiguration` object.  Raise
        :exc:`~exceptions.EnvironmentError`, if the file could not be loaded,
        but *not* in case of a non-existing file.
        """
        if not filename:
            filename = get_management_config_file_path()
        config = cls(touchpad_manager)
        # use defaults for all non-existing settings
        loaded_config = dict(cls.DEFAULTS)
        loaded_config.update(load_json(filename, default={}))
        config.update(loaded_config)
        return config

    def __init__(self, touchpad_manager):
        self.touchpad_manager = touchpad_manager

    @property
    def mouse_manager(self):
        return self.touchpad_manager.mouse_manager

    @property
    def keyboard_monitor(self):
        return self.touchpad_manager.keyboard_monitor

    def __contains__(self, key):
        return key in self.DEFAULTS

    def __len__(self):
        return len(self.DEFAULTS)

    def __iter__(self):
        return iter(self.DEFAULTS)

    def __getitem__(self, key):
        if key not in self:
            raise KeyError(key)
        target = self.touchpad_manager
        if key in self.MOUSE_MANAGER_KEYS:
            target = self.mouse_manager
        elif key in self.KEYBOARD_MONITOR_KEYS:
            target = self.keyboard_monitor
        return getattr(target, key)

    def __setitem__(self, key, value):
        if key not in self:
            raise KeyError(key)
        target = self.touchpad_manager
        if key in self.MOUSE_MANAGER_KEYS:
            target = self.mouse_manager
        elif key in self.KEYBOARD_MONITOR_KEYS:
            target = self.keyboard_monitor
        setattr(target, key, value)

    def __delitem__(self, key):
        raise NotImplementedError

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
    from synaptiks.touchpad import Touchpad, NoTouchpadError
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

    try:
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
    except xlib.DisplayError:
        parser.error('could not connect to X11 display')
    except NoTouchpadError:
        parser.error('no touchpad found')


if __name__ == '__main__':
    main()
