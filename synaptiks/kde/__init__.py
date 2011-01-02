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
    synaptiks.kde
    =============

    KDE specific modules of synaptiks.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from PyKDE4.kdecore import KAboutData, ki18nc

import synaptiks


def make_about_data(description):
    """
    Create an about data object describing synaptiks.

    ``description`` is a :class:`~PyKDE4.kdecore.KLocalizedString` containing a
    description for the specific part of synaptiks, the created about data
    object should describe.

    Return a :class:`~PyKDE4.kdecore.KAboutData` object with the given
    ``description``.
    """
    about = KAboutData(
        b'synaptiks', '', ki18nc('Program name', 'synaptiks'),
        str(synaptiks.__version__), description, KAboutData.License_BSD,
        ki18nc('About data copyright',
               # KLocalizedString doesn't deal well with unicode
               b'Copyright © 2009, 2010 Sebastian Wiesner'))
    about.setCustomAuthorText(
        ki18nc('custom author text plain text',
               'Please report bugs to the issue tracker at %1').subs(
            synaptiks.ISSUE_TRACKER_URL),
        ki18nc('custom author text rich text',
               'Please report bugs to the '
               '<a href="%1">issue tracker</a>.').subs(
            synaptiks.ISSUE_TRACKER_URL))
    about.setHomepage(synaptiks.WEBSITE_URL)
    about.setOrganizationDomain('lunaryorn.de')

    about.setTranslator(ki18nc('NAME OF TRANSLATORS', 'Your names'),
                        ki18nc('EMAIL OF TRANSLATORS', 'Your emails'))
    about.addAuthor(ki18nc('author name', 'Sebastian Wiesner'),
                    ki18nc('author task', 'Maintainer'),
                    'lunaryorn@googlemail.com')
    about.addCredit(ki18nc('credit name', 'Valentyn Pavliuchenko'),
                    ki18nc('credit task', 'Debian packaging, russian '
                           'translation, bug reporting and testing'),
                    'valentyn.pavliuchenko@gmail.com')
    return about
