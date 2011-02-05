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

import re
from itertools import product
from functools import partial

import pytest

from synaptiks import xinput


def pytest_generate_tests(metafunc):
    if any(n in metafunc.funcargnames for n in
           ('device_id', 'device_name', 'device_properties', 'device')):
        devices = metafunc.config.xinput_device_database
        for device in sorted(devices.itervalues()):
            if 'device_property' in metafunc.funcargnames:
                # single test for each property defined on a device
                for property in device.properties:
                    test_id = '{0},id={1},property={2}'.format(
                        device.name, device.id, property)
                    funcargs=dict(device_property=property)
                    metafunc.addcall(param=device.id, funcargs=funcargs,
                                     id=test_id)
            else:
                test_id = '{0},id={1}'.format(device.name, device.id)
                metafunc.addcall(param=device.id, id=test_id)


def pytest_funcarg__device_id(request):
    return request.param

def pytest_funcarg__device_name(request):
    device_id = request.getfuncargvalue('device_id')
    devices = request.getfuncargvalue('device_database')
    return devices[device_id].name

def pytest_funcarg__device_properties(request):
    device_id = request.getfuncargvalue('device_id')
    devices = request.getfuncargvalue('device_database')
    return devices[device_id].properties

def pytest_funcarg__device_property_value(request):
    device_id = request.getfuncargvalue('device_id')
    devices = request.getfuncargvalue('device_database')
    device_property = request.getfuncargvalue('device_property')
    return devices[device_id].properties[device_property]

def pytest_funcarg__device(request):
    display = request.getfuncargvalue('display')
    device_id = request.getfuncargvalue('device_id')
    return xinput.InputDevice(display, device_id)


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


def test_is_property_defined_existing_property(display):
    assert xinput.is_property_defined(display, 'Device Enabled')
    assert xinput.is_property_defined(display, u'Device Enabled')


class TestInputDevice(object):

    def test_all_devices(self, display, device_database):
        devices = list(xinput.InputDevice.all_devices(display))
        assert set(d.id for d in devices) == set(device_database)
        assert set(d.name for d in devices) == \
               set(d.name for d in device_database.itervalues())
        # assert type
        assert all(isinstance(d, xinput.InputDevice) for d in devices)

    def test_find_devices_by_name(self, display, device_name, device_id):
        devices = list(xinput.InputDevice.find_devices_by_name(
            display, device_name))
        assert devices
        assert any(d.name == device_name for d in devices)
        assert any(d.id == device_id for d in devices)

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

    def test_self_identity(self, device):
        assert device == device
        assert not (device != device)

    def test_eq_ne(self, display, device_database):
        device_combinations = product(device_database, device_database)
        device = partial(xinput.InputDevice, display)
        for left_id, right_id in device_combinations:
            if left_id == right_id:
                assert device(left_id) == device(right_id)
            else:
                assert device(left_id) != device(right_id)

    def test_iter(self, device, device_properties):
        assert set(device) == set(device_properties)

    def test_len(self, device, device_properties):
        assert len(device) == len(device_properties)

    def test_contains(self, device, device_properties):
        assert all(p in device for p in device_properties)

    def test_contains_undefined_property(self, device):
        assert not 'a undefined property' in device

    def test_getitem(self, device, device_property, device_property_value):
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
        raise NotImplementedError()

    def test_set_float(self):
        raise NotImplementedError()
