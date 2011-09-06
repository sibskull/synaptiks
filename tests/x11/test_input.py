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

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import sys
import re
from itertools import product, repeat
from functools import partial

import pytest

from synaptiks.x11 import input as xinput


def pytest_generate_tests(metafunc):
    if any(a in metafunc.funcargnames for a in ('test_device', 'device',
                                                'device_property')):
        devices = metafunc.config.xinput_device_database
        for device in devices:
            if 'device_property' in metafunc.funcargnames:
                # single test for each property defined on a device
                for property in device.properties:
                    test_id = '{0},id={1},property={2}'.format(
                        device.name, device.id, property)
                    funcargs = dict(device_property=property)
                    metafunc.addcall(param=device, funcargs=funcargs,
                                     id=test_id)
            else:
                test_id = '{0},id={1}'.format(device.name, device.id)
                metafunc.addcall(param=device, id=test_id)
    if metafunc.function.__name__ in ('test_pack_property_data',
                                      'test_unpack_property_data'):
        type_codes = [('B', 1), ('H', 2), ('L', 4), ('f', 4)]
        for type_code, item_size in type_codes:
            funcargs = dict(type_code=type_code, item_size=item_size)
            if type_code == 'f':
                testid = 'float'
            else:
                bit_length = item_size * 8
                testid = 'uint{0}'.format(bit_length)
            metafunc.addcall(funcargs=funcargs, id=testid)


def pytest_funcarg__test_device(request):
    return request.param


def pytest_funcarg__device_property_value(request):
    test_device = request.getfuncargvalue('test_device')
    device_property = request.getfuncargvalue('device_property')
    return test_device.properties[device_property]


def pytest_funcarg__device(request):
    display = request.getfuncargvalue('display')
    test_device = request.getfuncargvalue('test_device')
    return xinput.InputDevice(display, test_device.id)


def pytest_funcarg__test_keyboard(request):
    """
    The virtual testing keyboard as :class:`synaptiks.xinput.InputDevice`.
    """
    display = request.getfuncargvalue('display')
    return next(xinput.InputDevice.find_devices_by_name(
        display, 'Virtual core XTEST keyboard'))


def pytest_funcarg__test_pointer(request):
    """
    The virtual testing pointer as :class:`synaptiks.xinput.InputDevice`.
    """
    display = request.getfuncargvalue('display')
    return next(xinput.InputDevice.find_devices_by_name(
        display, 'Virtual core XTEST pointer'))


def test_assert_xinput_version(display):
    # just check, that no unexpected exception is raised
    try:
        xinput.assert_xinput_version(display)
    except xinput.XInputVersionError:
        # this is an expected exception
        pass


def test_make_struct_format():
    data = xinput._make_struct_format('f', 1)
    assert isinstance(data, str)
    assert data == '=1f'
    assert xinput._make_struct_format('B', 10) == '=10B'


def test_pack_property_data(type_code, item_size):
    data = xinput._pack_property_data(type_code, [10, 20, 30])
    assert isinstance(data, bytes)
    assert len(data) == 3 * item_size


def test_unpack_property_data(type_code, item_size):
    if type_code == 'f':
        pytest.xfail('Floating point packing test not implemented')

    pad_bytes = [b for b in repeat('\x00', item_size - 1)]
    value_byte = '\x01'

    if sys.byteorder == 'little':
        bytes = [value_byte] + pad_bytes
    elif sys.byteorder == 'big':
        bytes = pad_bytes + [value_byte]
    else:
        raise ValueError('Unexpected byte order: {0!r}'.format(sys.byteorder))

    data = ''.join(bytes)
    assert xinput._unpack_property_data(type_code, 1, data) == [1]


def test_make_struct_format_invalid_type_code():
    with pytest.raises(ValueError) as exc_info:
        xinput._make_struct_format('ff', 10)
    assert str(exc_info.value) == 'invalid type code'


class TestXInputVersion(object):

    version = xinput.XInputVersion(2, 3)

    def test_attributes(self):
        assert self.version.major == 2
        assert self.version.minor == 3

    def test_str(self):
        assert str(self.version) == '2.3'


class TestXInputVersionError(object):

    error = xinput.XInputVersionError((2, 3), (1, 0))

    def test_attributes(self):
        assert isinstance(self.error.expected_version, xinput.XInputVersion)
        assert isinstance(self.error.actual_version, xinput.XInputVersion)
        assert self.error.expected_version == (2, 3)
        assert self.error.actual_version == (1, 0)

    def test_str(self):
        assert str(self.error) == 'XInputVersionError: Expected 2.3, got 1.0'


class TestInputDevice(object):

    def test_all_devices_return_type(self, display):
        devices = list(xinput.InputDevice.all_devices(display))
        assert all(isinstance(d, xinput.InputDevice) for d in devices)

    def test_all_devices(self, display, device_database):
        ids = set(d.id for d in device_database)
        all_devices = xinput.InputDevice.all_devices(display)
        assert set(d.id for d in all_devices) == ids

    def test_all_devices_master_only(self, display, device_database):
        master_ids = set(d.id for d in device_database if d.is_master)
        master_devices = xinput.InputDevice.all_devices(
            display, master_only=True)
        assert set(d.id for d in master_devices) == master_ids

    def test_find_devices_by_type_invalid_type(self, display):
        with pytest.raises(ValueError) as excinfo:
            xinput.InputDevice.find_devices_by_type(display, 'foo')
        assert str(excinfo.value) == 'foo'

    def test_find_devices_by_type_keyboard(self, display, device_database):
        keyboard_ids = set(d.id for d in device_database
                           if d.type == 'keyboard')
        keyboards = xinput.InputDevice.find_devices_by_type(
            display, 'keyboard')
        assert set(k.id for k in keyboards) == keyboard_ids

    def test_find_devices_by_type_pointer(self, display, device_database):
        pointer_ids = set(d.id for d in device_database
                           if d.type == 'pointer')
        pointers = xinput.InputDevice.find_devices_by_type(
            display, 'pointer')
        assert set(k.id for k in pointers) == pointer_ids

    def test_find_devices_by_name(self, display, test_device, device_database):
        device_ids = set(d.id for d in device_database
                         if d.name == test_device.name)
        devices = xinput.InputDevice.find_devices_by_name(
            display, test_device.name)
        assert set(d.id for d in devices) == device_ids

    def test_find_devices_with_property(self, display, device_property):
        devices = xinput.InputDevice.find_devices_with_property(
            display, device_property)
        assert all(device_property in d for d in devices)

    def test_find_devices_with_property_non_defined(self, display):
        devices = list(xinput.InputDevice.find_devices_with_property(
            display, 'a undefined property'))
        assert not devices

    def test_find_devices_by_name_non_existing(self, display):
        name = 'a non-existing device'
        devices = list(xinput.InputDevice.find_devices_by_name(display, name))
        assert not devices

    def test_find_devices_by_name_existing_devices_regex(self, display):
        pattern = re.compile('.*XTEST.*')
        devices = list(xinput.InputDevice.find_devices_by_name(display,
                                                               pattern))
        assert devices
        assert all('XTEST' in d.name for d in devices)

    def test_display(self, display, device):
        assert device.display is display

    def test_name(self, device, test_device):
        assert device.name == test_device.name

    def test_is_master(self, device, test_device):
        assert device.is_master == test_device.is_master

    def test_type(self, device, test_device):
        assert device.type == test_device.type

    def test_attachment_device(self, device, test_device):
        if test_device.type == 'floating':
            assert device.attachment_device is None
        else:
            assert isinstance(device.attachment_device, xinput.InputDevice)
            assert device.attachment_device.id == test_device.attachment
            assert device.attachment_device.is_master
            if not test_device.is_master:
                assert device.attachment_device.type == device.type
            else:
                inverse = {'keyboard': 'pointer', 'pointer': 'keyboard'}
                assert device.attachment_device.type == inverse[device.type]

    def test_self_identity(self, device):
        assert device == device
        assert not (device != device)

    def test_eq_ne(self, display, device_database):
        all_ids = set(d.id for d in device_database)
        device_combinations = product(all_ids, all_ids)
        device = partial(xinput.InputDevice, display)
        for left_id, right_id in device_combinations:
            if left_id == right_id:
                assert device(left_id) == device(right_id)
            else:
                assert device(left_id) != device(right_id)

    def test_repr(self, device, test_device):
        rep = '<InputDevice({0.id}, name={0.name!r})>'.format(test_device)
        assert repr(device) == rep

    def test_hash(self, device, test_device):
        assert hash(device) == hash(test_device.id)

    def test_iter(self, device, test_device):
        assert set(device) == set(test_device.properties)

    def test_len(self, device, test_device):
        assert len(device) == len(test_device.properties)

    def test_contains(self, device, device_property):
        assert device_property in device

    def test_contains_undefined_property(self, device):
        assert not 'a undefined property' in device

    def test_getitem(self, device, device_property, device_property_value):
        if not device_property_value:
            pytest.skip('no items for property {0}'.format(device_property))
        if isinstance(device_property_value[0], float):
            values = [round(v, 6) for v in device[device_property]]
        else:
            values = device[device_property]
        assert values == device_property_value

    def test_getitem_non_defined_property(self, device):
        with pytest.raises(xinput.UndefinedPropertyError) as excinfo:
            device['a undefined property']
        assert excinfo.value.name == 'a undefined property'

    def test_set_bool_alias(self):
        assert xinput.InputDevice.set_bool == xinput.InputDevice.set_byte

    def test_set_byte(self, test_keyboard):
        property = 'Device Enabled'
        assert test_keyboard[property] == [1]
        test_keyboard.set_byte(property, [0])
        assert test_keyboard[property] == [0]
        test_keyboard.set_byte(property, [1])
        assert test_keyboard[property] == [1]

    def test_set_int(self):
        pytest.xfail('not implemented')

    def test_set_float(self):
        pytest.xfail('Not implemented')
