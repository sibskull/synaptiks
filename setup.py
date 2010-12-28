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

from distutils.core import setup

import synaptiks


if sys.version_info[0] >= 3:
    sys.exit('Python 3 is not yet supported.  Try "python2".')


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
    data_files=[
        ('share/applications/kde4/', ['synaptiks.desktop']),
        ('share/icons/hicolor/scalable/apps/', ['pics/synaptiks.svgz']),
        ('share/kde4/services/', ['kcm_synaptiks.desktop']),
        ('share/apps/synaptiks/', ['kcm_synaptiks.py']),
        ],
    scripts=['scripts/synaptiks'],
    )
