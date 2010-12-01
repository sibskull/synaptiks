#!/usr/bin/python2
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import synaptiks

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
    packages=find_packages(),
    )
