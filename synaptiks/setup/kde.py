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
    synaptiks.setup.kde
    ===================

    KDE4-specific distutils extension code.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import os
import sys
from glob import glob
from collections import namedtuple
from itertools import chain

from distutils import log
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
        self.kde_handbook = None
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

    def _get_install_directory(self, resource_type, with_root=True):
        if resource_type == 'appdata':
            tail_path = self.distribution.metadata.name
            resource_type = 'data'
        else:
            tail_path = None

        # manually handle KDE and XDG autostart resources, because kde4-config
        # doesn't provide the install path for this resource type
        if resource_type == 'autostart':
            install_directory = os.path.join(
                self.kde4_prefix, 'share', 'autostart')
        elif resource_type == 'xdgconf-autostart':
            root = '/'
            real_prefix = getattr(sys, 'real_prefix', None)
            if real_prefix is not None and sys.prefix != real_prefix:
                # we are installing into a virtualenv for testing purposes, so
                # adjust the prefix
                root = sys.prefix
            # the system-wide autostart directory is given by the XDG autostart
            # spec
            install_directory = os.path.join(root, 'etc/xdg/autostart')
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
        if with_root and install_cmd.root:
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


class ThemeIcon(namedtuple('_ThemeIcon', 'theme size category filename')):
    @property
    def path(self):
        return os.path.join(self.theme, self.size, self.category)

StandAloneIcon = namedtuple('StandaloneIcon', 'filename')


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


class InstallMessages(KDEBaseCmd):
    description = 'Install KDE message catalogs'

    def finalize_options(self):
        KDEBaseCmd.finalize_options(self)
        compile_catalog = self.get_finalized_command('compile_catalog')
        self.build_dir = compile_catalog.build_dir
        domain = self.distribution.metadata.name
        self.catalog_name = domain + '.mo'

    def install_catalog(self, catalog):
        locale = os.path.splitext(catalog)[0]
        target_tail = os.path.join(locale, 'LC_MESSAGES')
        target_directory = os.path.join(
            self._get_install_directory('locale'), target_tail)
        self.mkpath(target_directory)
        target_file = os.path.join(target_directory, self.catalog_name)
        source_file = os.path.join(self.build_dir, catalog)
        destname, _ = self.copy_file(source_file, target_file)
        self._outputs.append(destname)

    def run(self):
        self.run_command('compile_catalog')
        compiled_catalogs = os.listdir(self.build_dir)
        for catalog in compiled_catalogs:
            self.install_catalog(catalog)


class BuildHandbook(BaseCommand):
    user_options = [
        (b'meinproc4-exe=', None, 'Full path to meinproc4 executable'),
        (b'build-dir=', None, 'Build directory')]

    def initialize_options(self):
        self.meinproc4_exe = None
        self.build_dir = None

    def finalize_options(self):
        if self.meinproc4_exe is None:
            self.meinproc4_exe = self._find_executable(
                'meinproc4', 'Please install kdelibs')
        if self.build_dir is None:
            build = self.get_finalized_command('build')
            self.build_dir = os.path.join(build.build_base, 'handbook')
        self.handbook = self.distribution.kde_handbook
        self.handbook_directory = os.path.dirname(self.handbook)

    def run(self):
        self.mkpath(self.build_dir)
        docbook_files = glob(os.path.join(
            self.handbook_directory, '*.docbook'))
        image_files = glob(os.path.join(self.handbook_directory, '*.png'))
        for filename in chain(docbook_files, image_files):
            self.copy_file(filename, self.build_dir)
        # build the index cache
        cache_file = os.path.join(self.build_dir, 'index.cache.bz2')
        self.spawn([self.meinproc4_exe, '--check', '--cache', cache_file,
                   self.handbook])


class InstallHandbook(KDEBaseCmd):
    description = 'Install a KDE handbook'

    user_options = KDEBaseCmd.user_options + [
        (b'build-dir=', None, 'Build directory')]

    def initialize_options(self):
        KDEBaseCmd.initialize_options(self)
        self.build_dir = None

    def finalize_options(self):
        KDEBaseCmd.finalize_options(self)
        if self.build_dir is None:
            build = self.get_finalized_command('build_kde_handbook')
            self.build_dir = build.build_dir
        self.name = self.distribution.metadata.name

    def symlink(self, source, dest):
        if self.verbose >= 1:
            log.info('symbolically linking %s -> %s', source, dest)
        if self.dry_run:
            return (dest, True)
        if os.path.isdir(dest):
            dest = os.path.join(dest, os.path.basename(source))
        # for now, simply ignore existing symlinks, not really the way to go,
        # see below
        if not os.path.islink(dest):
            os.symlink(source, dest)
        # do *not* add symlink dest to outputs here due to a bug in pip 0.8.2
        # (and possibly other versions):  "pip install" removes the whole
        # directory pointed to and leaves the symlink, instead of leaving the
        # directory untouched and removing the symlink.
        # self._outputs.append(dest)
        return (dest, True)

    def run(self):
        files = [os.path.join(self.build_dir, fn)
                 for fn in os.listdir(self.build_dir)]
        handbook_install_directory = os.path.join(
            self._get_install_directory('html'), 'en', self.name)
        self.copy_files(files, handbook_install_directory)
        html_directory = self._get_install_directory('html', with_root=False)
        self.symlink(os.path.join(html_directory, 'en', 'common'),
                     os.path.join(handbook_install_directory))


from setuptools.command.install import install as install_cls
install_cls.sub_commands.extend([
    ('install_kde_files', lambda s: True),
    ('install_kde_icons', lambda s: True),
    ('install_kde_messages', lambda s: True),
    ('install_kde_handbook', lambda s: True),
    ])

from distutils.command.build import build as build_cls
build_cls.sub_commands.append(('build_kde_handbook', lambda s: True))


CMDCLASS = {'install_kde_files': InstallFiles,
            'install_kde_icons': InstallIcons,
            'install_kde_messages': InstallMessages,
            'build_kde_handbook': BuildHandbook,
            'install_kde_handbook': InstallHandbook,
            }
