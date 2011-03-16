# -*- coding: utf-8 -*-
# Copyright (c) 2011, Sebastian Wiesner <lunaryorn@googlemail.com>
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


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from datetime import date

import pytest

kde = pytest.importorskip('synaptiks.kde')

from PyKDE4.kdecore import ki18n

from synaptiks import ISSUE_TRACKER_URL, WEBSITE_URL, __version__


def pytest_funcarg__description(request):
    return ki18n('spam with eggs')


def pytest_funcarg__about_data(request):
    description = request.getfuncargvalue('description')
    return kde.make_about_data(description)


def test_make_about_data_name(about_data):
    assert unicode(about_data.programName()) == 'synaptiks'
    assert unicode(about_data.appName()) == 'synaptiks'
    assert unicode(about_data.productName()) == 'synaptiks'


def test_make_about_data_version(about_data):
    assert unicode(about_data.version()) == __version__


def test_make_about_data_description(about_data):
    assert unicode(about_data.shortDescription()) == 'spam with eggs'


def test_make_about_data_license(about_data):
    licenses = about_data.licenses()
    assert len(licenses) == 1
    license = licenses[0]
    assert license.key() == about_data.License_BSD
    short_name = unicode(about_data.licenseName(about_data.ShortName))
    assert short_name == 'BSD License'


def test_make_about_data_copyright(about_data):
    copyright_statement = unicode(about_data.copyrightStatement())
    assert 'Sebastian Wiesner' in copyright_statement
    this_year = date.today().year
    assert all(unicode(y) in copyright_statement
               for y in range(2009, this_year + 1))


def test_make_about_data_homepage(about_data):
    assert unicode(about_data.homepage()) == WEBSITE_URL


def test_make_about_data_domain(about_data):
    assert unicode(about_data.organizationDomain()) == 'lunaryorn.de'


def test_make_about_data_custom_author_text(about_data):
    assert ISSUE_TRACKER_URL in unicode(about_data.customAuthorPlainText())
    assert ISSUE_TRACKER_URL in unicode(about_data.customAuthorRichText())
