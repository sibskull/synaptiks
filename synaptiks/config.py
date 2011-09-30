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
    touchpad manager.  These configuration classes are just mappings with some
    convenience methods to load/save the configuration, and to handle default
    values.

    Configuration is saved in JSON files (to retain type information) in the
    configuration directory (see :func:`get_configuration_directory()`).

    Handling of default values
    --------------------------

    Configuration mappings provided by this module provide their default values
    through a ``defaults`` property, see :attr:`TouchpadConfiguration.defaults`
    and :attr:`ManagerConfiguration.defaults`.

    In case of :class:`ManagerConfiguration` these are explicit default values,
    which do not change.  :class:`TouchpadConfiguration` however uses the
    defaults provided by the touchpad driver.

    Unfortunately the touchpad driver does not provide special access to these
    default values.  To work around this restriction, **synaptiks** saves the
    touchpad configuration to disc right after session startup (through an
    autostart command ``synaptikscfg init``, see :ref:`script_usage`), before
    loading the actual configuration.  At this point, the driver properties
    haven't yet been modified, and thus still contain the default values.
    These dumped defaults can later be loaded through
    :meth:`TouchpadConfiguration.defaults()`.

    .. _script_usage:

    Script usage
    ------------

    .. program:: synaptikscfg

    This module is usable as script, available also as :program:`synaptikscfg`
    in the ``$PATH``.  It provides three different actions, of which ``load``
    and ``save`` are really self-explanatory. ``init`` however deserves some
    detailled explanation.

    The `init` action is supposed to run automatically as script during session
    startup.  To do this, the installation script installs an autostart entry
    (as specified by the `XDG Desktop Application Autostart Specification`_) to
    execute ``synaptikscfg init`` at session startup.  This action first dumps
    the default settings from the touchpad driver as described above, and then
    loads and applies the actual touchpad configuration stored on disk.

    The command line parsing of the script is implemented with :mod:`argparse`,
    so you can expected standard semantics, and an extensive ``--help`` option.

    .. _XDG Desktop Application Autostart Specification: http://standards.freedesktop.org/autostart-spec/autostart-spec-latest.html

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

    Raise :exc:`~exceptions.EnvironmentError`, if the creation of the
    configuration directory fails.

    .. _`XDG base directory specification`: http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html
    """
    xdg_config_home = os.environ.get('XDG_CONFIG_HOME')
    if not xdg_config_home:
        xdg_config_home = os.path.expandvars(os.path.join('$HOME', '.config'))
    return ensure_directory(os.path.join(xdg_config_home, 'synaptiks'))


class AbstractConfiguration(dict):

    @classmethod
    def default_filename(cls):
        """
        Get the default filename for this configuration.

        Return the filename as string.
        """
        raise NotImplementedError()

    @classmethod
    def defaults(cls):
        """
        Get the default configuration.
        """
        return cls()

    @classmethod
    def load(cls, filename=None):
        """
        Load the configuration from disc.

        If no ``filename`` is given, the configuration is loaded from the
        default configuration file as returned by :meth:`default_filename()`.
        Otherwise the configuration is loaded from the given file.

        The configuration is initialized with the defaults provided by
        :meth:`defaults()`.

        Return the configuration object.  Raise
        :exc:`~exceptions.EnvironmentError`, if the file could not be loaded,
        but *not* in case of a non-existing file.
        """
        if not filename:
            filename = cls.default_filename()
        config = cls()
        config.update(cls.defaults())
        config.update(load_json(filename, default={}))
        return config

    def save(self, filename=None):
        """
        Save the configuration.

        If no ``filename`` is given, the configuration is saved to the default
        configuration file as returned by :meth:`default_filename()`.
        Otherwise the configuration is saved to the given file.

        ``filename`` is either ``None`` or a string containing the path to a
        file.

        Raise :exc:`~exceptions.EnvironmentError`, if the file could not be
        written.
        """
        if not filename:
            filename = self.default_filename()
        save_json(filename, dict(self))

    def apply_to(self, target):
        """
        Apply this configuration to the given target.

        Default implementation raises :exc:`~exceptions.NotImplementedError()`.
        """
        raise NotImplementedError()


class TouchpadConfiguration(AbstractConfiguration):
    """
    Touchpad configuration.
    """

    CONFIGURABLE_TOUCHPAD_PROPERTIES = frozenset([
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

    @staticmethod
    def default_filename():
        return os.path.join(get_configuration_directory(),
                            'touchpad-config.json')

    @staticmethod
    def defaults_file():
        return os.path.join(get_configuration_directory(),
                            'touchpad-defaults.json')

    @classmethod
    def defaults(cls):
        """
        Load the default touchpad configuration.

        The default touchpad configuration is dumped to disk as session
        startup, and can be loaded by this method.

        Return a :class:`TouchpadConfiguration` object with the default
        configuration.
        """
        return cls(load_json(cls.defaults_file(), default={}))

    @classmethod
    def load_from_touchpad(cls, touchpad, filename=None):
        """
        Load configuration and initialize it with the state of the given
        ``touchpad``.

        ``touchpad`` is a :class:`~synaptiks.touchpad.Touchpad` object.
        ``filename`` is a string with the filename to load.  If unset, the
        default configuration file is loaded.

        Return a :class:`TouchpadConfiguration` which resembles the sate of the
        given ``touchpad``.
        """
        config = cls.load(filename=filename)
        config.update_from_touchpad(touchpad)
        return config

    def save_as_defaults(self):
        """
        Save this configuration as default.

        Raise :attr:`~exceptions.EnvironmentError`, if saving failed.
        """
        self.save(self.defaults_file())

    def update_from_touchpad(self, touchpad):
        """
        Update this configuration with the state of the given ``touchpad``.

        ``touchpad`` is a :class:`~synaptiks.touchpad.Touchpad` object.
        """
        for key in self.CONFIGURABLE_TOUCHPAD_PROPERTIES:
            value = getattr(touchpad, key)
            if isinstance(value, float):
                # round floats to make comparison safe
                value = round(value, 5)
            self[key] = value

    def apply_to(self, touchpad):
        """
        Apply this configuration to of the given ``touchpad``.

        ``touchpad`` is a :class:`~synaptiks.touchpad.Touchpad` object.
        """
        for key in self.CONFIGURABLE_TOUCHPAD_PROPERTIES:
            setattr(touchpad, key, self[key])

    def get_configured_touchpad(self, display):
        from synaptiks.touchpad import Touchpad, NoTouchpadError
        try:
            return Touchpad.find_first(display)
        except NoTouchpadError:
            from synaptiks.touchpad import FakeTouchpad
            fake_touchpad_name = self.get('fake_touchpad_name')
            if fake_touchpad_name is None:
                raise
            fake_touchpad = next(FakeTouchpad.find_devices_by_name(
                display, fake_touchpad_name), None)
            if fake_touchpad is None:
                raise
            return fake_touchpad


class ManagerConfiguration(AbstractConfiguration):
    """
    A mutable mapping class representing the configuration of a touchpad
    manager.
    """

    #: A mapping with the default values for all configuration keys
    _DEFAULTS = {'monitor_mouses': False, 'ignored_mouses': [],
                'monitor_keyboard': False, 'idle_time': 2.0,
                'keys_to_ignore': 2}

    @staticmethod
    def default_filename():
        return os.path.join(get_configuration_directory(), 'management.json')

    @classmethod
    def defaults(cls):
        """
        Return the default configuration as :class:`ManagerConfiguration`
        object.
        """
        return cls(cls._DEFAULTS)

    def apply_to(self, manager):
        """
        Apply the configuration to the given ``manager``.

        ``manager`` is a :class:`~synaptiks.management.TouchpadManager`.
        """
        manager.mouse_manager.ignored_mouses = self['ignored_mouses']
        for key in ('idle_time', 'keys_to_ignore'):
            setattr(manager.keyboard_monitor, key, self[key])
        for key in ('monitor_mouses', 'monitor_keyboard'):
            setattr(manager, key, self[key])


def main():
    from argparse import ArgumentParser

    from synaptiks import __version__
    from synaptiks.x11 import Display, DisplayError
    from synaptiks.touchpad import Touchpad, NoTouchpadError

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
        with Display.from_name() as display:
            touchpad = Touchpad.find_first(display)

            if args.action == 'init':
                driver_defaults = TouchpadConfiguration()
                driver_defaults.update_from_touchpad(touchpad)
                driver_defaults.save(TouchpadConfiguration.defaults_file())
            if args.action in ('init', 'load'):
                config = TouchpadConfiguration.load(filename=args.filename)
                config.apply_to(touchpad)
            if args.action == 'save':
                current_config = TouchpadConfiguration.load_from_touchpad(
                    touchpad)
                current_config.save(filename=args.filename)
    except DisplayError:
        parser.error('could not connect to X11 display')
    except NoTouchpadError:
        parser.error('no touchpad found')


if __name__ == '__main__':
    main()
