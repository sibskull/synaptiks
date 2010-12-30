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


def find_python_sources(directory):
    for root, dirnames, filenames in os.walk(directory):
        for filename in (os.path.join(root, f) for f in filenames):
            if is_python_file(filename):
                yield filename


class ExtractMessages(BaseCommand):
    description = 'Extract messages from source'

    user_options = [(b'xgettext-exe=', None, 'Path to xgettext'),
                    (b'extractrc-exe=', None, 'Path to extractrc'),
                    (b'output-file=', None, 'Output file'),
                    (b'msgid-bugs-address=', None,
                     'Mail address for bug reports concerning messages')]

    def initialize_options(self):
        self.xgettext_exe = None
        self.extractrc_exe = None
        self.output_file = None
        self.msgid_bugs_address = None

    def finalize_options(self):
        if self.xgettext_exe is None:
            self.xgettext_exe = self._find_executable(
                'xgettext', 'Please install gettext')
        if self.extractrc_exe is None:
            self.extractrc_exe = self._find_executable(
                'extractrc', 'Please install extractrc')
        if self.output_file is None:
            self.output_file = os.path.join(
                'po', self.distribution.metadata.name + '.pot')

    def run(self):
        output_directory = os.path.dirname(self.output_file)
        self.mkpath(output_directory)

        build_py = self.get_finalized_command('build_py')
        extract_rc_command = [
            self.extractrc_exe, '--language', 'Python']
        for _, srcdir, _, filenames in build_py.data_files:
            extract_rc_command.extend(
                os.path.join(srcdir, fn) for fn in filenames
                if is_ui_file(fn))
        rc_data = self.spawn(extract_rc_command, catch_output=True)
        if rc_data:
            with open('rc.py', 'w') as stream:
                stream.write(rc_data)

        xgettext_command = [
            self.xgettext_exe, '-ci18n', '--from-code', 'UTF-8',
            '--language', 'Python', '--no-wrap', '--sort-output',
            '--kde', '--keyword', '--output', self.output_file,
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
        self.spawn(xgettext_command, input=rc_data)

        if os.path.isfile('rc.py'):
            os.unlink('rc.py')


class InitCatalog(BaseCommand):
    description = 'Init a new message catalog'

    user_options = [(b'msginit-exe=', None, 'Path to msginit'),
                    (b'input-file=', None,
                     'Input filename (template catalog)'),
                    (b'output-file=', None, 'Output filename'),
                    (b'locale=', None, 'Locale name')]

    def initialize_options(self):
        self.msginit_exe = None
        self.output_file = None
        self.input_file = None
        self.locale = None

    def finalize_options(self):
        if self.msginit_exe is None:
            self.msginit_exe = self._find_executable(
                'msginit', 'Please install gettext')
        if self.locale is None:
            # find out, what locale the user is currently running on
            old_locale = locale.getlocale()
            try:
                locale.setlocale(locale.LC_ALL, '')
                country_code, _ = locale.getlocale()
            finally:
                # always restore locale
                locale.setlocale(locale.LC_ALL, old_locale)
            lang_code = country_code.split('_')[0]
            self.locale = lang_code
        if self.input_file is None:
            extract_messages = self.get_finalized_command('extract_messages')
            self.input_file = extract_messages.output_file
        if self.output_file is None:
            output_directory = os.path.dirname(self.input_file)
            self.output_file = os.path.join(output_directory,
                                            self.locale + '.po')

    def run(self):
        output_directory = os.path.dirname(self.output_file)
        self.mkpath(output_directory)

        msginit_command = [self.msginit_exe, '--locale', self.locale,
                           '--input', self.input_file,
                           '--output', self.output_file]
        self.spawn(msginit_command)
