#!/usr/bin/python2
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


import sys
from codecs import open

from setuptools import setup

import synaptiks
from synaptiks.setup import kde, l10n


if sys.version_info[0] >= 3:
    sys.exit('Python 3 is not yet supported.  Try "python2".')


requirements = ['pyudev>=0.6']
if sys.version_info[:2] < (2, 7):
    requirements.append('argparse>=1.1')

with open('README.rst', encoding='utf-8') as stream:
    long_description = stream.read()


cmdclass = dict(kde.CMDCLASS)
cmdclass.update(l10n.CMDCLASS)

setup(
    distclass=kde.Distribution,
    cmdclass=cmdclass,
    name='synaptiks',
    version=str(synaptiks.__version__),
    url=str(synaptiks.WEBSITE_URL),
    author='Sebastian Wiesner',
    author_email='lunaryorn@googlemail.com',
    description='A KDE touchpad configuration and management tool',
    long_description=long_description,
    platforms='X11',
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: KDE',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Desktop Environment :: K Desktop Environment (KDE)',
        'Topic :: System :: Hardware',
        'Topic :: Utilities',
        ],
    packages=['synaptiks', 'synaptiks.kde', 'synaptiks.kde.widgets',
              'synaptiks.monitors', 'synaptiks._bindings'],
    package_data={
        'synaptiks.kde.widgets': ['ui/*.ui'],
        },
    entry_points={
        'gui_scripts': ['synaptiks = synaptiks.kde.trayapplication:main'],
        'console_scripts': ['synaptikscfg = synaptiks.config:main']},
    zip_safe=False,
    install_requires=requirements,
    kde_handbook = 'doc/handbook/index.docbook',
    kde_files={
        'xdgdata-apps': ['synaptiks.desktop'],
        'services': ['services/kcm_synaptiks.desktop'],
        'appdata': ['services/kcm_synaptiks.py', 'synaptiks.notifyrc'],
        'xdgconf-autostart': ['autostart/synaptiks_init_config.desktop'],
        'autostart': ['autostart/synaptiks_autostart.desktop']},
    kde_icons=[
        kde.ThemeIcon('hicolor', 'scalable', 'apps', 'pics/synaptiks.svgz'),
        kde.StandAloneIcon('pics/off-overlay.svgz')]
    )
