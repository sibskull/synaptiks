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

import errno
import json

import pytest

from synaptiks import util


def pytest_funcarg__json_file(request):
    tmpdir = request.getfuncargvalue('tmpdir')
    return tmpdir.join('test.json')


def pytest_funcarg__json_obj(request):
    return {'foo': 'bar', 'spam': 10, 'eggs': 5.0}


def test_ensure_byte_string():
    assert isinstance(util.ensure_byte_string('foo'), bytes)
    assert util.ensure_byte_string('foo') == b'foo'
    s = b'foo'
    assert util.ensure_byte_string(s) is s


def test_ensure_unicode_string():
    assert isinstance(util.ensure_unicode_string(b'foo'), unicode)
    assert util.ensure_unicode_string(b'foo') == 'foo'
    s = 'foo'
    assert util.ensure_unicode_string(s) is s


def test_ensure_directory(tmpdir):
    directory = tmpdir.join('directory')
    assert not directory.check(dir=True)
    util.ensure_directory(str(directory))
    assert directory.check(dir=True)
    # check that invocation on an existing directory doesn't fail with EEXIST
    util.ensure_directory(str(directory))


def test_ensure_directory_no_perms(tmpdir):
    """
    Test, that other exceptions than EEXIST are handed up to the caller
    """
    tmpdir.chmod(550)
    directory = tmpdir.join('directory')
    with pytest.raises(EnvironmentError) as excinfo:
        util.ensure_directory(str(directory))
    assert excinfo.value.filename == str(directory)
    assert excinfo.value.errno == errno.EACCES


def test_save_json(json_file, json_obj):
    assert not json_file.check(file=True, exists=True)
    util.save_json(str(json_file), json_obj)
    assert json_file.check(file=True)
    assert json.loads(json_file.read()) == json_obj


def test_save_json_no_perms(tmpdir, json_file, json_obj):
    tmpdir.chmod(550)
    with pytest.raises(EnvironmentError) as excinfo:
        util.save_json(str(json_file), json_obj)
    assert excinfo.value.filename == str(json_file)
    assert excinfo.value.errno == errno.EACCES


def test_load_json_no_default(json_file, json_obj):
    json_file.write(json.dumps(json_obj))
    assert util.load_json(str(json_file)) == json_obj


def test_load_json_default_ignored(json_file, json_obj):
    json_file.write(json.dumps(json_obj))
    assert util.load_json(str(json_file), default='default') == json_obj


def test_load_json_default_used(json_file):
    assert util.load_json(str(json_file), default='default') == 'default'


def test_load_json_non_existing_no_default(json_file):
    with pytest.raises(EnvironmentError) as excinfo:
        util.load_json(str(json_file))
    assert excinfo.value.filename == str(json_file)
    assert excinfo.value.errno == errno.ENOENT


def test_load_json_no_default_no_perms(json_file, json_obj):
    json_file.write(json.dumps(json_obj))
    json_file.chmod(200)
    with pytest.raises(EnvironmentError) as excinfo:
        util.load_json(str(json_file))
    assert excinfo.value.filename == str(json_file)
    assert excinfo.value.errno == errno.EACCES


def test_load_json_with_default_no_perms(json_file, json_obj):
    json_file.write(json.dumps(json_obj))
    json_file.chmod(200)
    with pytest.raises(EnvironmentError) as excinfo:
        util.load_json(str(json_file), default='default')
    assert excinfo.value.filename == str(json_file)
    assert excinfo.value.errno == errno.EACCES
