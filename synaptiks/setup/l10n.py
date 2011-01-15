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
    synaptiks.setup.i18n
    ====================

    i18n support module

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import os
import locale

from synaptiks.setup import BaseCommand


KEYWORDS = [
    'i18n:1', 'i18nc:1c,2', 'i18np:1,2', 'i18ncp:1c,2,3',
    'ki18n:1', 'ki18nc:1c,2', 'ki18np:1,2', 'ki18ncp:1c,2,3',
    'tr2i18n:1']


def _check_ext(filename, ext):
    return os.path.splitext(filename)[1] == ext

def is_python_file(filename):
    return _check_ext(filename, '.py')

def is_ui_file(filename):
    return _check_ext(filename, '.ui')

def is_po_file(filename):
    return _check_ext(filename, '.po')


def find_python_sources(directory):
    for root, dirnames, filenames in os.walk(directory):
        for filename in (os.path.join(root, f) for f in filenames):
            if is_python_file(filename):
                yield filename


def get_current_locale():
    old_locale = locale.getlocale()
    try:
        locale.setlocale(locale.LC_ALL, '')
        country_code, _ = locale.getlocale()
    finally:
        # always restore locale
        locale.setlocale(locale.LC_ALL, old_locale)
    return country_code.split('_')[0]


class ExtractMessages(BaseCommand):
    description = 'Extract messages from source'

    user_options = [(b'xgettext-exe=', None, 'Path to xgettext'),
                    (b'extractrc-exe=', None, 'Path to extractrc'),
                    (b'directory=', None, 'The locale directory'),
                    (b'msgid-bugs-address=', None,
                     'Mail address for bug reports concerning messages')]

    def initialize_options(self):
        self.xgettext_exe = None
        self.extractrc_exe = None
        self.directory = None
        self.msgid_bugs_address = None

    def finalize_options(self):
        if self.xgettext_exe is None:
            self.xgettext_exe = self._find_executable(
                'xgettext', 'Please install gettext')
        if self.extractrc_exe is None:
            self.extractrc_exe = self._find_executable(
                'extractrc', 'Please install extractrc')
        if self.directory is None:
            self.directory = 'po'
        self.template_file = os.path.join(
            self.directory, self.distribution.metadata.name + '.pot')

    def run(self):
        self.mkpath(self.directory)

        build_py = self.get_finalized_command('build_py')
        extract_rc_command = [
            self.extractrc_exe, '--language', 'Python']
        for _, srcdir, _, filenames in build_py.data_files:
            extract_rc_command.extend(
                os.path.join(srcdir, fn) for fn in filenames
                if is_ui_file(fn))
        rc_data = self.spawn(extract_rc_command, catch_output=True)

        xgettext_command = [
            self.xgettext_exe, '-ci18n', '--from-code', 'UTF-8',
            '--language', 'Python', '--width', '80',
            '--kde', '--keyword', '--output', self.template_file,
            '--foreign-user',
            '--package-name', self.distribution.metadata.name,
            '--package-version', self.distribution.metadata.version]
        if self.msgid_bugs_address:
            xgettext_command.extend(
                ['--msgid-bugs-address', self.msgid_bugs_address])
        xgettext_command.extend(
            '-k{0}'.format(keyword) for keyword in KEYWORDS)
        for package in build_py.packages:
            package_directory = build_py.get_package_dir(package)
            xgettext_command.extend(find_python_sources(package_directory))
        for filenames in self.distribution.kde_files.itervalues():
            xgettext_command.extend(fn for fn in filenames if
                                    is_python_file(fn))
        if rc_data:
            xgettext_command.append('rc.py')
            with open('rc.py', 'w') as stream:
                stream.write(rc_data)

        try:
            self.spawn(xgettext_command)
        finally:
            if os.path.isfile('rc.py'):
                os.unlink('rc.py')


class InitCatalog(BaseCommand):
    description = 'Init a new message catalog'

    user_options = [(b'msginit-exe=', None, 'Path to msginit'),
                    (b'directory=', None, 'The locale directory'),
                    (b'template_file=', None,
                     'Input filename (template catalog)'),
                    (b'locale=', None, 'Locale name')]

    def initialize_options(self):
        self.msginit_exe = None
        self.directory = None
        self.template_file = None
        self.locale = None

    def finalize_options(self):
        if self.msginit_exe is None:
            self.msginit_exe = self._find_executable(
                'msginit', 'Please install gettext')
        if self.locale is None:
            self.locale = get_current_locale()
        extract_messages = self.get_finalized_command('extract_messages')
        if self.directory is None:
            self.directory = extract_messages.directory
        if self.template_file is None:
            self.template_file = extract_messages.template_file
        self.output_file = os.path.join(self.directory, self.locale + '.po')

    def run(self):
        output_directory = os.path.dirname(self.output_file)
        self.mkpath(output_directory)

        msginit_command = [self.msginit_exe, '--locale', self.locale,
                           '--input', self.template_file,
                           '--output', self.output_file]
        self.spawn(msginit_command)


class POWorkerCommand(BaseCommand):

    user_options = [(b'directory=', None, 'The locale directory'),
                    (b'locale=', None, 'Locale name')]

    def initialize_options(self):
        self.directory = None
        self.locale = None

    def finalize_options(self):
        if self.directory is None:
            extract_messages = self.get_finalized_command('extract_messages')
            self.directory = extract_messages.directory

    def _get_catalogs(self):
        if self.locale:
            return [self.locale+'.po']
        else:
            return [fn for fn in os.listdir(self.directory) if is_po_file(fn)]

    def _get_locale(self, catalog):
        return os.path.splitext(catalog)[0]


class UpdateCatalog(POWorkerCommand):
    description = 'Update message catalog(s)'

    user_options = POWorkerCommand.user_options + \
                   [(b'msgmerge-exe=', None, 'Path to msgmerge'),
                    (b'template-file=', None,
                     'Input filename (template catalog)')]

    def initialize_options(self):
        POWorkerCommand.initialize_options(self)
        self.template_file = None
        self.msgmerge_exe = None

    def finalize_options(self):
        POWorkerCommand.finalize_options(self)
        if self.msgmerge_exe is None:
            self.msgmerge_exe = self._find_executable(
                'msgmerge', 'Please install gettext')
        if self.template_file is None:
            extract_messages = self.get_finalized_command('extract_messages')
            self.template_file = extract_messages.template_file

    def run(self):
        for catalog in self._get_catalogs():
            msgmerge_command = [
                self.msgmerge_exe, '--width', '80', '--quiet', '--backup=none',
                '--update', os.path.join(self.directory, catalog),
                self.template_file]
            self.spawn(msgmerge_command)


class CompileCatalog(POWorkerCommand):
    description = 'Compile message catalog(s)'

    user_options = POWorkerCommand.user_options + \
                   [(b'msgfmt-exe=', None, 'Path to msgfmt'),
                    (b'build-dir=', None, 'The build directory')]

    def initialize_options(self):
        POWorkerCommand.initialize_options(self)
        self.msgfmt_exe = None
        self.build_dir = None

    def finalize_options(self):
        POWorkerCommand.finalize_options(self)
        if self.msgfmt_exe is None:
            self.msgfmt_exe = self._find_executable(
                'msgfmt', 'Please install gettext')
        if self.build_dir is None:
            build = self.get_finalized_command('build')
            self.build_dir = os.path.join(build.build_base, 'locale')

    def run(self):
        self.mkpath(self.build_dir)

        for catalog in self._get_catalogs():
            locale = self._get_locale(catalog)
            output_file = os.path.join(self.build_dir, locale + '.mo')
            msgfmt_command = [self.msgfmt_exe, '--check',
                              '--output-file', output_file,
                              os.path.join(self.directory, catalog)]
            self.spawn(msgfmt_command)

#: exported command classes
CMDCLASS = {'extract_messages': ExtractMessages,
            'init_catalog': InitCatalog,
            'compile_catalog': CompileCatalog,
            'update_catalog': UpdateCatalog}
