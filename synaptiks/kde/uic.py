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
    synaptiks.kde.uic
    =================

    Fixup PyQt4.uic to respect comments

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from PyQt4 import QtCore, QtGui
from PyQt4.uic.Loader.loader import DynamicUILoader
from PyQt4.uic.properties import Properties
from PyKDE4.kdecore import tr2i18n


class PyKDEProperties(Properties):
    def _string(self, prop, notr=None):
        text = prop.text
        if prop.get('notr', notr) == 'true':
            return text
        if text:
            text = unicode(text).encode('utf-8')
        comment = prop.attrib.get('comment', None)
        if comment:
            comment = unicode(comment).encode('utf-8')
        return tr2i18n(text, comment)


class PyKDELoader(DynamicUILoader):
    def __init__(self):
        DynamicUILoader.__init__(self)
        self.wprops = PyKDEProperties(self.factory, QtCore, QtGui)


def loadUi(uifile, baseinstance=None):
    return PyKDELoader().loadUi(uifile, baseinstance)
