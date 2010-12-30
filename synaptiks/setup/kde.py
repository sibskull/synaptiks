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
    synaptiks.setup.kde
    ===================

    KDE4-specific distutils extension code.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import os
from collections import namedtuple

from distutils.util import change_root
from distutils.errors import DistutilsSetupError
from setuptools import Distribution as _Distribution

from synaptiks.setup import BaseCommand, get_output, change_prefix


class Distribution(_Distribution):
    """
    A setuptools distribution with some extra kde-specific attributes.
    """

    def __init__(self, attrs=None):
        # register kde_* attributes for distutils
        self.kde_files = None
        self.kde_icons = None
        _Distribution.__init__(self, attrs=attrs)


class KDEBaseCmd(BaseCommand):
    user_options = [(b'kde4-config-exe=', None,
                     'Full path to kde4-config executable')]

    def initialize_options(self):
        self.kde4_config_exe = None
        self._outputs = []

    def finalize_options(self):
        if self.kde4_config_exe is None:
            self.kde4_config_exe = self._find_executable(
                'kde4-config', 'Please install kdelibs')
        self.kde4_prefix = get_output([self.kde4_config_exe, '--prefix'])
        if not self.kde4_prefix:
            raise SystemExit('Could not determine KDE4 installation prefix')
        else:
            self.kde4_prefix = os.path.normpath(self.kde4_prefix)

    def _get_install_directory(self, resource_type):
        if resource_type == 'appdata':
            tail_path = self.distribution.metadata.name
            resource_type = 'data'
        else:
            tail_path = None

        if resource_type == 'autostart':
            # manually handle autostart type, because kde4-config doesn't
            # provide the install path for this resource type
            install_directory = os.path.join(
                self.kde4_prefix, 'share', 'autostart')
        else:
            install_directory = get_output(
                [self.kde4_config_exe, '--install', resource_type])
            if not install_directory:
                raise SystemExit('Could not determine install directory '
                                 'for %s' % resource_type)

        # substitute the KDE prefix with the prefix from distutils
        install_cmd = self.get_finalized_command('install')
        actual_install_dir = change_prefix(
            install_directory, self.kde4_prefix, install_cmd.prefix)
        if tail_path:
            actual_install_dir = os.path.join(actual_install_dir, tail_path)
        if install_cmd.root:
            # respect a changed root
            actual_install_dir = change_root(
                install_cmd.root, actual_install_dir)
        return os.path.normpath(actual_install_dir)

    def get_outputs(self):
        return self._outputs

    def copy_files(self, files, install_dir):
        self.mkpath(install_dir)
        for filename in files:
            destname, _ = self.copy_file(filename, install_dir)
            self._outputs.append(destname)


class InstallFiles(KDEBaseCmd):
    description = 'Install KDE 4 files'

    def finalize_options(self):
        KDEBaseCmd.finalize_options(self)
        self.kde_files = self.distribution.kde_files

    def run(self):
        if not self.kde_files:
            return
        for resource_type, files in self.kde_files.iteritems():
            install_dir = self._get_install_directory(resource_type)
            self.copy_files(files, install_dir)


class InstallIcons(KDEBaseCmd):
    description = 'Install KDE icons'

    def finalize_options(self):
        KDEBaseCmd.finalize_options(self)
        self.kde_icons = self.distribution.kde_icons

    def run(self):
        if not self.kde_icons:
            return
        theme_install_dir = self._get_install_directory('icon')
        standalone_install_dir = os.path.join(
            self._get_install_directory('appdata'), 'pics')
        for icon in self.kde_icons:
            if isinstance(icon, ThemeIcon):
                dest_dir = os.path.join(theme_install_dir, icon.path)
            elif isinstance(icon, StandAloneIcon):
                dest_dir = standalone_install_dir
            else:
                raise DistutilsSetupError('unknown icon type: %r' % icon)
            self.copy_files([icon.filename], dest_dir)


class ThemeIcon(namedtuple('_ThemeIcon', 'theme size category filename')):
    @property
    def path(self):
        return os.path.join(self.theme, self.size, self.category)

StandAloneIcon = namedtuple('StandaloneIcon', 'filename')


from setuptools.command.install import install as install_cls
install_cls.sub_commands.extend([
    ('install_kde_files', lambda s: True),
    ('install_kde_icons', lambda s: True),
    ])
