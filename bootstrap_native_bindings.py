#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2010, 2011 Sebastian Wiesner <lunaryorn@googlemail.com>

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


"""
    bootstrap_native_bindings
    =========================

    Bootstrapping script for native bindings used during synaptiks tests.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import sys
import os
import errno
import posixpath
import subprocess
import logging
from multiprocessing import cpu_count
from optparse import OptionParser
from collections import namedtuple


class SubprocessMixin(object):
    def _check_call(self, command, **options):
        self.log.debug('calling %r with options %r', command, options)
        subprocess.check_call(command, **options)


def ensuredirs(*directories):
    for directory in directories:
        try:
            os.makedirs(directory)
        except EnvironmentError as error:
            if error.errno != errno.EEXIST:
                raise


class SourcePackage(namedtuple(
    '_SourcePackage', 'name version buildtype url_template'),
                    SubprocessMixin):

    log = logging.getLogger('bootstrap.source')

    @property
    def url(self):
        return self.url_template.format(**self._asdict())

    def download(self, target_directory):
        filename = posixpath.basename(self.url)
        target = os.path.join(target_directory, filename)
        if not os.path.isfile(target):
            try:
                self.log.info('downloading %s to %s', self.url, target)
                self._check_call(['wget', '-O', target, self.url])
            except:
                if os.path.isfile(target):
                    os.unlink(target)
                raise
        else:
            self.log.info('skipping %s, already downloaded', self.url)
        return target

    def make_build(self, download_directory, target_directory):
        archive = self.download(download_directory)
        self.log.info('extracting %s to %s', archive, target_directory)
        self._check_call(['tar', '-x', '-a', '-f', archive,
                          '-C', target_directory])
        return self.buildtype(os.path.join(
            target_directory, '{0.name}-{0.version}'.format(self)))

    def build(self, download_directory, target_directory):
        self.make_build(download_directory, target_directory).run()


class Build(SubprocessMixin):
    def __init__(self, source_directory):
        self.log = logging.getLogger('bootstrap.builder')
        self.source_directory = source_directory

    @property
    def build_directory(self):
        return self.source_directory

    def initialize(self):
        pass

    def configure(self):
        pass

    def build(self):
        self.log.info('building in %s', self.build_directory)
        number_of_cpus = cpu_count()
        self._check_call(['make', '-j', str(number_of_cpus)],
                         cwd=self.build_directory)

    def install(self):
        self.log.info('installing from %s', self.build_directory)
        self._check_call(['make', 'install'],
                         cwd=self.build_directory)

    def run(self):
        self.initialize()
        self.configure()
        self.build()
        self.install()

    def __call__(self):
        self.run()


class SipBuild(Build):

    configure_options = [
        '--incdir', os.path.join(sys.prefix, 'include', 'sip')]

    def configure(self):
        self.log.info('configuring in %s with %r', self.build_directory,
                      self.configure_options)
        cmd = [sys.executable, 'configure.py']
        cmd.extend(self.configure_options)
        self._check_call(cmd, cwd=self.build_directory)


class PyQtBuild(SipBuild):
    configure_options = ['--confirm-license', '--concatenate',
                         '--enable', 'QtGui', '--no-qsci-api']


RIVERBANK_DOWNLOAD_URL = 'http://www.riverbankcomputing.com/static/Downloads/{0}'

PYQT4_SOURCES = [
    SourcePackage('sip', '4.12.4', SipBuild,
                  RIVERBANK_DOWNLOAD_URL.format(
                      'sip4/{name}-{version}.tar.gz')),
    SourcePackage('PyQt-x11-gpl', '4.8.5', PyQtBuild,
                  RIVERBANK_DOWNLOAD_URL.format(
                      'PyQt4/{name}-{version}.tar.gz'))]


def build_all(sources, download_directory, build_directory):
    for source in sources:
        source.build(download_directory, build_directory)


def import_string(import_name, silent=False):
    """
    Import an object based on a string given by ``import_name``.  An import
    path can be specified either in dotted notation
    (``'xml.sax.saxutils.escape'``) or with a colon as object delimiter
    (``'xml.sax.saxutils:escape'``).

    Return the imported object.  If the import or the attribute access fails
    and ``silent`` is ``True``, ``None`` will be returned.  Otherwise
    :exc:`~exceptions.ImportError` or :exc:`~exceptions.AttributeError` will
    be raised.

    This function was shamelessly stolen from Werkzeug_.  Thanks to Armin
    Ronacher.

    .. _werkzeug: http://werkzeug.pocoo.org
    """
    try:
        if ':' in import_name:
            module, obj = import_name.split(':', 1)
        elif '.' in import_name:
            module, obj = import_name.rsplit('.', 1)
        else:
            return __import__(import_name)
        # to make things run on python 2 and python 3
        obj = str(obj)
        module = str(module)
        return getattr(__import__(module, None, None, [obj]), obj)
    except (ImportError, AttributeError):
        if not silent:
            raise


def have_pyqt4_qtgui(expected_version):
    log = logging.getLogger('pyqt4')
    try:
        QtCore = import_string('PyQt4.QtCore')
        import_string('PyQt4.QtGui')
        log.info('excepted version %s, actual version %s',
                 expected_version, QtCore.PYQT_VERSION_STR)
        return QtCore.PYQT_VERSION_STR == expected_version
    except (ImportError, AttributeError):
        log.exception('QtGui not found')
        return False


def main():
    parser = OptionParser(usage='%prog download_directory build_directory')
    parser.add_option('--debug', action='store_const', dest='loglevel',
                      const=logging.DEBUG)
    parser.add_option('--verbose', action='store_const', dest='loglevel',
                      const=logging.INFO)
    parser.set_defaults(loglevel=logging.WARN)
    opts, args = parser.parse_args()
    if len(args) != 2:
        parser.error('missing arguments')
    logging.basicConfig(level=opts.loglevel)

    try:
        download_directory, build_directory = args
        ensuredirs(download_directory, build_directory)

        if not have_pyqt4_qtgui(PYQT4_SOURCES[1].version):
            build_all(PYQT4_SOURCES, download_directory, build_directory)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
