# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011 Sebastian Wiesner <lunaryorn@googlemail.com>
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
    synaptiks.util
    ==============

    General utilities used throughout synaptiks.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import os
import sys
import errno
import json


def assert_byte_string(s):
    """
    Convert ``s`` to a byte string.

    If ``s`` is already a byte string, it is returned unchanged.  If ``s``
    is a unicode string, it is converted according to
    :func:`sys.getfilesystemencoding()`.
    """
    if isinstance(s, unicode):
        return s.encode(sys.getfilesystemencoding())
    return s


def assert_unicode_string(s):
    """
    Convert ``s`` to a unicode string.

    If ``s`` is already a unicode string, it is returned unchanged.  If
    ``s`` is a byte string, it is converted according to
    :func:`sys.getfilesystemencoding()`.
    """
    if isinstance(s, str):
        return s.decode(sys.getfilesystemencoding())
    return s


def ensure_directory(directory):
    """
    Ensure, that the given ``directory`` exists.  If the ``directory`` does not
    yet exist, it is created.

    Return ``directory`` again.

    Raise :exc:`~exceptions.EnvironmentError`, if directory creation fails.
    """
    try:
        os.makedirs(directory)
        return directory
    except EnvironmentError as error:
        if error.errno == errno.EEXIST:
            return directory
        else:
            raise


def save_json(filename, obj):
    """
    Save the given ```obj`` in JSON format to the given ``filename``.

    ``obj`` must either be a primitive type such as integer or string, or a
    list or a dict.  Any other type will raise a :exc:`~exceptions.TypeError`.
    ``filename`` is a string containing the path to the file to which the
    object is saved.

    Raise :exc:`~exceptions.TypeError`, if ``obj`` has an unsupported path.
    Raise :exc:`~exceptions.EnvironmentError`, if ``filename`` could not be
    opened or not be written to.
    """
    with open(filename, 'w') as stream:
        json.dump(obj, stream, indent=2)


def load_json(filename, default=None):
    """
    Load the given JSON file.

    If the given file does not exist and ``default`` is not ``None``, then the
    given ``default`` is returned.

    Raise :exc:`~exceptions.EnvironmentError`, if the file could not be read,
    or if ``default`` is ``None`` and the file was not found.
    """
    try:
        with open(filename, 'r') as stream:
            return json.load(stream)
    except EnvironmentError as error:
        if default is not None and error.errno == errno.ENOENT:
            return default
        raise
