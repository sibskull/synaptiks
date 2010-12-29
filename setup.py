#!/usr/bin/python2
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


import sys
import os
from subprocess import Popen, PIPE
from collections import namedtuple

from distutils import spawn
from distutils.cmd import Command
from distutils.util import change_root

from setuptools import setup
from setuptools.command.install import install as install_cls

import synaptiks


if sys.version_info[0] >= 3:
    sys.exit('Python 3 is not yet supported.  Try "python2".')


def get_output(command):
    return Popen(command, stdout=PIPE).communicate()[0].strip()


def change_prefix(path, old_prefix, new_prefix):
    old_prefix = os.path.normpath(old_prefix)
    path = os.path.normpath(path)
    unprefixed_path = path[len(old_prefix)+1:]
    return os.path.normpath(os.path.join(new_prefix, unprefixed_path))


class KDE4BaseCmd(Command):
    user_options = [('kde4-config-exe=', None,
                     'Full path to kde4-config executable')]

    def initialize_options(self):
        self.kde4_config_exe = None
        self._outputs = []

    def finalize_options(self):
        if self.kde4_config_exe is None:
            self.announce('Searching kde4-config...')
            self.kde4_config_exe = spawn.find_executable('kde4-config')
            if self.kde4_config_exe is None:
                raise SystemExit('Could not find kde4-config. '
                                 'Is kdelibs properly installed?')
            self.announce(' ...kde4-config found at %s' % self.kde4_config_exe)
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


class InstallKDE4Files(KDE4BaseCmd):
    description = 'Install KDE 4 files'

    def finalize_options(self):
        KDE4BaseCmd.finalize_options(self)
        self.kde4_files = dict(KDE4_FILES)

    def run(self):
        if not self.kde4_files:
            return
        for resource_type, files in self.kde4_files.iteritems():
            install_dir = self._get_install_directory(resource_type)
            self.copy_files(files, install_dir)


class InstallKDE4Icons(KDE4BaseCmd):
    description = 'Install KDE4 icons'

    def finalize_options(self):
        KDE4BaseCmd.finalize_options(self)
        self.kde4_icons = list(KDE4_ICONS)

    def run(self):
        if not self.kde4_icons:
            return
        theme_install_dir = self._get_install_directory('icon')
        standalone_install_dir = os.path.join(
            self._get_install_directory('appdata'), 'pics')
        for icon in self.kde4_icons:
            if isinstance(icon, ThemeIcon):
                dest_dir = os.path.join(theme_install_dir, icon.path)
            elif isinstance(icon, StandAloneIcon):
                dest_dir = standalone_install_dir
            else:
                raise SystemExit('unknown icon type: %r', icon)
            self.copy_files([icon.filename], dest_dir)


install_cls.sub_commands.extend([
    ('install_kde4_files', lambda s: True),
    ('install_kde4_icons', lambda s: True),
    ])


KDE4_FILES={
    'xdgdata-apps': ['synaptiks.desktop'],
    'services': ['services/kcm_synaptiks.desktop'],
    'appdata': ['services/kcm_synaptiks.py', 'synaptiks.notifyrc'],
    'autostart': ['autostart/init_synaptiks_config.desktop',
                  'autostart/synaptiks_autostart.desktop'],
    }


class ThemeIcon(namedtuple('_ThemeIcon', 'theme size category filename')):
    @property
    def path(self):
        return os.path.join(self.theme, self.size, self.category)

StandAloneIcon = namedtuple('StandaloneIcon', 'filename')

KDE4_ICONS = [
    ThemeIcon('hicolor', 'scalable', 'apps', 'pics/synaptiks.svgz'),
    StandAloneIcon('pics/off-overlay.svgz'),
    ]


requirements = []
if sys.version_info[:2] < (2, 7):
    requirements.append('argparse>=1.1')


setup(
    name='synaptiks',
    version=synaptiks.__version__,
    url='http://synaptiks.lunaryorn.de',
    author='Sebastian Wiesner',
    author_email='lunaryorn@googlemail.com',
    description='A KDE touchpad management tool',
    platforms='X11',
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: X11 Applications :: KDE',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2',
        'Topic :: Desktop Environment :: K Desktop Environment (KDE)',
        'Topic :: System :: Hardware',
        'Topic :: Utilities',
        ],
    packages=['synaptiks', 'synaptiks.kde', 'synaptiks._bindings'],
    package_data={
        'synaptiks.kde': ['ui/*.ui'],
        },
    entry_points={
        'gui_scripts': ['synaptiks = synaptiks.kde.trayapplication:main'],
        'console_scripts': ['synaptikscfg = synaptiks.config:main']},
    install_requires=requirements,
    cmdclass={'install_kde4_files': InstallKDE4Files,
              'install_kde4_icons': InstallKDE4Icons},
    )
