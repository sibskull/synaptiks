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
    synaptiks.models
    ================

    Qt model classes used in synaptiks

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
from PyQt4.QtCore import Qt, QAbstractListModel, QModelIndex

from synaptiks.monitors import MouseDevicesMonitor


class MouseDevicesModel(QAbstractListModel):
    """
    A Qt model which lists all connected mouse devices.

    The mouse devices are display with their product name, and their serial
    number as tooltip.  Each device is checkable, the checked devices are
    available through :attr:`checked_devices`.
    """

    def __init__(self, parent=None):
        """
        Create a model.

        ``parent`` is the parent :class:`~PyQt4.QtCore.QObject`.
        """
        QAbstractListModel.__init__(self, parent)
        self._monitor = MouseDevicesMonitor(self)
        self._monitor.mousePlugged.connect(self._mouse_plugged)
        self._monitor.mouseUnplugged.connect(self._mouse_unplugged)
        self._device_index = list(self._monitor.plugged_devices)
        self._checked_devices = set()

    def _mouse_plugged(self, device):
        """
        Slot called to handle a newly plugged mouse device.
        """
        pos = len(self._device_index)
        self.beginInsertRows(QModelIndex(), pos, pos)
        self._device_index.append(device)
        self.endInsertRows()

    def _mouse_unplugged(self, device):
        """
        Slot called to handle an unplugged mouse device.
        """
        try:
            pos = self._device_index.index(device)
            self.beginRemoveRows(QModelIndex(), pos, pos)
            del self._device_index[pos]
            self.endRemoveRows()
        except ValueError:
            pass

    @property
    def checked_devices(self):
        """
        All checked mouse devices as :func:`frozenset()`.

        This property holds a :func:`frozenset()` with the serial numbers of
        all checked mouse devices.  Any iterable yielding serial numbers or
        :class:`synaptiks.monitors.MouseDevice` objects can be assigned to this
        property.
        """
        return frozenset(self._checked_devices)

    @checked_devices.setter
    def checked_devices(self, devices):
        devices = set(d if isinstance(d, basestring) else d.serial
                      for d in devices)
        for row, device in enumerate(self._device_index):
            if device.serial in devices:
                index = self.index(row, 0)
                self.dataChanged.emit(index, index)
        self._checked_devices = devices

    def flags(self, index):
        """
        Return the flags for the given model ``index``.

        All items are generally enabled and user checkable.
        """
        return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable

    def rowCount(self, index):
        """
        Return the row count for the given model ``index``.
        """
        return len(self._device_index)

    def data(self, index, role):
        """
        Get the data for the given ``index`` and ``role``.
        """
        if index.isValid() and index.column() == 0:
            device = self._device_index[index.row()]
            if role == Qt.DisplayRole:
                return device.name
            elif role == Qt.ToolTipRole:
                return device.serial
            elif role == Qt.CheckStateRole:
                return (Qt.Checked
                        if device.serial in self._checked_devices
                        else Qt.Unchecked)

    def setData(self, index, value, role):
        """
        Set model data.

        Only handles check state changes (``CheckStateRole``).
        """
        if index.isValid() and role == Qt.CheckStateRole:
            device = self._device_index[index.row()]
            if value in (Qt.Checked, Qt.Unchecked):
                update_our_cache = getattr(self._checked_devices,
                        'add' if value == Qt.Checked else 'remove')
                update_our_cache(device.serial)
                self.dataChanged.emit(index, index)
                return True
