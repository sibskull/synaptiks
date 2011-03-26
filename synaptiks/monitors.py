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
    synaptiks.monitors
    ==================

    Monitor classes for various external event sources.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from itertools import ifilter
from collections import namedtuple
from itertools import izip
from array import array
from threading import Event

import pyudev
try:
    import dbus
    from  dbus.mainloop.glib import DBusGMainLoop
except ImportError:
    dbus = None
from pyudev.pyqt4 import QUDevMonitorObserver
from PyQt4.QtCore import QObject, QTimer, QThread, QTime, pyqtSignal
from PyQt4.QtGui import QApplication

from synaptiks.qx11 import QX11Display
from synaptiks._bindings import xlib
try:
    from synaptiks._bindings import xrecord
except ImportError:
    xrecord = None
from synaptiks._bindings.util import scoped_pointer


def _is_mouse(device):
    return (device.sys_name.startswith('mouse') and
            device.get('ID_INPUT_MOUSE') == '1' and
            not device.get('ID_INPUT_TOUCHPAD') == '1')


class MouseDevice(namedtuple('_MouseDevice', ['serial', 'name'])):
    """
    A :func:`~collections.namedtuple()` representing a mouse device.

    A mouse device currently has two attributes, the order corresponds to the
    tuple index:

    - :attr:`serial`
    - :attr:`name`
    """

    @classmethod
    def from_udev(cls, device):
        """
        Create a :class:`MouseDevice` tuple from a :class:`pyudev.Device`.
        """
        # The name is available from the parent device of the actual event
        # device.  The parent represents the actual physical device.  The name
        # may be decorated with quotation marks, which are removed for the sake
        # of a clean represenation
        return cls(device['ID_SERIAL'], device.parent['NAME'].strip('"'))


class MouseDevicesMonitor(QObject):
    """
    Watch for plugged or unplugged mouse devices.
    """

    #: Qt signal, which is emitted, when a mouse is plugged.  The slot gets a
    #: single argument of :class:`MouseDevice`, which represents the plugged
    #: mouse device
    mousePlugged = pyqtSignal(MouseDevice)
    #: Qt signal, which is emitted, when a mouse is unplugged.  The slot gets a
    #: single argument of type :class:`MouseDevice`, which represents the
    #: unplugged mouse device
    mouseUnplugged = pyqtSignal(MouseDevice)

    def __init__(self, parent=None):
        """
        Create a new monitor.

        ``parent`` is the parent :class:`~PyQt4.QtCore.QObject`.
        """
        QObject.__init__(self, parent)
        self._udev = pyudev.Context()
        self._notifier = QUDevMonitorObserver(
            pyudev.Monitor.from_netlink(self._udev), self)
        self._notifier.deviceEvent.connect(self._handle_udev_event)
        self._notifier.monitor.filter_by('input')
        self._notifier.monitor.start()
        self._event_signal_map = dict(
            add=self.mousePlugged, remove=self.mouseUnplugged)

    @property
    def plugged_devices(self):
        """
        An iterator over all plugged mouse devices as :class:`MouseDevice`
        objects.
        """
        devices = self._udev.list_devices().match_subsystem(
            'input').match_property('ID_INPUT_MOUSE', True)
        for device in ifilter(_is_mouse, devices):
            yield MouseDevice.from_udev(device)

    def _handle_udev_event(self, evt, device):
        signal = self._event_signal_map.get(unicode(evt))
        if signal and _is_mouse(device):
            signal.emit(MouseDevice.from_udev(device))


def create_keyboard_monitor(parent=None):
    """
    Create a new keyboard monitor:

    >>> monitor = create_keyboard_monitor(parent)
    >>> monitor.idle_time = 0.5
    >>> monitor.keys_to_ignore = monitor.IGNORE_MODIFIER_COMBOS
    >>> monitor.typingStarted.connect(lambda: print('typing started'))
    >>> monitor.typingStopped.connect(lambda: print('typing stopped'))
    >>> monitor.start()

    This function automatically chooses the "best" available implementation.
    Currently this means, that a :class:`RecordingKeyboardMonitor` is created,
    if the XRecord extension is available.  Otherwise this functions falls back
    to :class:`PollingKeyboardMonitor`.

    ``parent`` is the parent :class:`~PyQt4.QtCore.QObject`.

    Return an implementation of :class:`AbstractKeyboardMonitor`.
    """
    if xrecord:
        success, _ = xrecord.query_version(QX11Display())
        if success:
            return RecordingKeyboardMonitor(parent)
    return PollingKeyboardMonitor(parent)


class AbstractKeyboardMonitor(QObject):
    """
    Abstract base class for keyboard monitors.

    This class defines the interface for keyboard monitoring classes.
    Currently there are two base classes:

    - :class:`RecordingKeyboardMonitor`
    - :class:`PollingKeyboardMonitor`

    Use :func:`create_keyboard_monitor` to create an instance of the "best"
    monitoring class.

    Keyboard monitoring means to emit signals, whenever the user starts or
    stops typing.  Whenever a keyboard event occurs, the keyboard is considered
    active and :attr:`typingStarted` is emitted.  After the last keyboard
    event, this class waits a configurable timespan (see :attr:`idle_time`)
    before considering the keyboard inactive and emitting
    :attr:`typingStopped`.  This is done to make sure, that the user really
    stopped typing and didn't just type a bit slower.

    Modifier keys can be ignored (see :attr:`keys_to_ignore`) as this kind of
    keys is mostly involved in hotkeys and shortcuts and doesn't really
    indicate keyboard activity.
    """

    #: default time span before considering the keyboard inactive again
    DEFAULT_IDLETIME = 2000

    #: Ignore no keys
    IGNORE_NO_KEYS = 0
    #: Ignore modifier keys alone
    IGNORE_MODIFIER_KEYS = 1
    #: Ignore combinations of modifiers and standard keys
    IGNORE_MODIFIER_COMBOS = 2

    #: Qt signal, emitted once this monitor is started.  Has no arguments.
    started = pyqtSignal()
    #: Qt signal, emitted once this monitor is stopped.  Has no arguments.
    stopped = pyqtSignal()
    #: Qt signal, emitted if typing is started.  Has no arguments.
    typingStarted = pyqtSignal()
    #: Qt signal, emitted if typing is stopped.  Has no arguments.
    typingStopped = pyqtSignal()

    def start():
        """
        Start monitoring the keyboard.
        """
        raise NotImplementedError()

    def stop(self):
        """
        Stop monitoring the keyboard.
        """
        # since we are not monitoring the keyboard anymore, we assume, that
        # there is no keyboard activity anymore.
        self.typingStopped.emit()

    @property
    def is_running(self):
        """
        ``True``, if the keyboard monitor is currently running, ``False``
        otherwise.
        """
        raise NotImplementedError()

    @property
    def idle_time(self):
        """
        The time to wait before assuming, that the typing has stopped, in
        seconds as float.
        """
        raise NotImplementedError()

    @idle_time.setter
    def idle_time(self, value):
        raise NotImplementedError()

    @property
    def keys_to_ignore(self):
        """
        The keys to ignore while observing the keyboard.

        If such a key is pressed, the keyboard will not be considered active,
        the signal :attr:`typingStarted` will consequently not be emitted.

        Raise :exc:`~exceptions.ValueError` upon assignment, if the given value
        is not one of :attr:`IGNORE_NO_KEYS`, :attr:`IGNORE_MODIFIER_KEYS` or
        :attr:`IGNORE_MODIFIER_COMBOS`.
        """
        raise NotImplementedError()

    @keys_to_ignore.setter
    def keys_to_ignore(self, value):
        raise NotImplementedError()

    @property
    def keyboard_active(self):
        """
        Is the keyboard currently active (with respect to
        :attr:`keys_to_ignore`)?

        ``True``, if the keyboard is currently active, ``False`` otherwise.
        """
        raise NotImplementedError()


class EventRecorder(QThread):
    """
    A thread to record keyboard events.

    Once started, this thread connects to the X11 display, and records all
    keyboard events.  On every keyboard event, the :attr:`keyboardEvent` signal
    is emitted.

    Use :meth:`stop()` to stop recording.
    """

    #: Qt signal emitted whenever a key was pressed.  Has a single argument,
    #: which is the key code of the pressed key
    keyPressed = pyqtSignal(int)
    #: Qt signal emitted whenever a key was released.  Has a single argument,
    #: which is the key code of the pressed key
    keyReleased = pyqtSignal(int)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        # to synchronize startup
        self._started = Event()
        # XXX: dirty hack: ctypes insists on a per-instance reference to the
        # event handling callback, otherwise "self" is garbage in the event
        # handler, and access to "self" causes a segfault.  Reason is unknown
        # to me.
        self._callback = self._handle_event
        # maps event types to signals
        self._event_signal_map = {xlib.KEY_PRESS: self.keyPressed,
                                  xlib.KEY_RELEASE: self.keyReleased}

    def run(self):
        # create a special display connection for recording
        with xlib.display() as recording_display:
            # record all key presses and releases, as these events indicate
            # keyboard activity
            key_events = (xlib.KEY_PRESS, xlib.KEY_RELEASE)
            with xrecord.context(recording_display, xrecord.ALL_CLIENTS,
                                 device_events=key_events) as context:
                self._context = context
                # create the recording context and enable it.  This function
                # does not return until disable_context is called, which
                # happens in stop.
                xrecord.enable_context(recording_display, context,
                                       self._callback, None)

    def stop(self):
        """
        Stop this recorder.
        """
        if not self.isRunning():
            return
        self._started.wait()
        xrecord.disable_context(QX11Display(), self._context)
        # immediately process the end of data event.  This allows us to wait
        # for this thread to terminate in the next line, thus making this
        # method synchronous.
        QApplication.instance().processEvents()
        self.wait()
        self._started.clear()

    def _handle_event(self, _, data):
        with scoped_pointer(data, xrecord.free_data):
            if data.contents.category == xrecord.START_OF_DATA:
                # the recorder has started
                self._started.set()
            elif data.contents.category == xrecord.FROM_SERVER:
                event_type, keycode = data.contents.event
                signal = self._event_signal_map[event_type]
                signal.emit(keycode)
            # all other client side events are ignored (e.g. END_OF_DATA)


class RecordingKeyboardMonitor(AbstractKeyboardMonitor):
    """
    Monitor the keyboard by recording X11 protocol data.
    """

    def __init__(self, parent=None):
        AbstractKeyboardMonitor.__init__(self, parent)
        # this timer is started on every keyboard event, its timeout signals,
        # that the keyboard is to be considered inactive again
        self._idle_timer = QTimer(self)
        self._idle_timer.setInterval(self.DEFAULT_IDLETIME)
        self._idle_timer.timeout.connect(self.typingStopped)
        self._idle_timer.setSingleShot(True)
        # this object records events
        self._recorder = EventRecorder(self)
        self._recorder.keyPressed.connect(self._key_pressed)
        self._recorder.keyReleased.connect(self._key_released)
        self._recorder.started.connect(self.started)
        self._recorder.finished.connect(self.stopped)
        # a set of all known modifier keycodes
        modifier_mapping = xlib.get_modifier_mapping(QX11Display())
        self._modifiers = frozenset(keycode for modifiers in modifier_mapping
                                    for keycode in modifiers if keycode != 0)
        # a set holding all pressed, but not yet released modifier keys
        self._pressed_modifiers = set()
        # the value of keys to ignore
        self._keys_to_ignore = self.IGNORE_NO_KEYS

    def _is_ignored_modifier(self, keycode):
        """
        Return ``True``, if ``keycode`` as a modifier key, which has to be
        ignored, ``False`` otherwise.
        """
        return (self._keys_to_ignore >= self.IGNORE_MODIFIER_KEYS and
                keycode in self._modifiers)

    def _is_ignored_modifier_combo(self):
        """
        Return ``True``, if the current key event occurred in combination
        with a modifier, which has to be ignored, ``False`` otherwise.
        """
        return (self._keys_to_ignore == self.IGNORE_MODIFIER_COMBOS and
                self._pressed_modifiers)

    def _is_ignored(self, keycode):
        """
        Return ``True``, if the given ``keycode`` has to be ignored,
        ``False`` otherwise.
        """
        return (self._is_ignored_modifier(keycode) or
                self._is_ignored_modifier_combo())

    def _key_pressed(self, keycode):
        if keycode in self._modifiers:
            self._pressed_modifiers.add(keycode)
        if not self._is_ignored(keycode):
            if not self.keyboard_active:
                self.typingStarted.emit()
            # reset the idle timeout
            self._idle_timer.start()

    def _key_released(self, keycode):
        self._pressed_modifiers.discard(keycode)
        if not self._is_ignored(keycode):
            if not self.keyboard_active:
                self.typingStarted.emit()
            # reset the idle timeout
            self._idle_timer.start()

    @property
    def is_running(self):
        return self._recorder.isRunning()

    def start(self):
        self._recorder.start()

    def stop(self):
        AbstractKeyboardMonitor.stop(self)
        self._idle_timer.stop()
        self._recorder.stop()

    @property
    def keys_to_ignore(self):
        return self._keys_to_ignore

    @keys_to_ignore.setter
    def keys_to_ignore(self, value):
        if not (self.IGNORE_NO_KEYS <= value <= self.IGNORE_MODIFIER_COMBOS):
            raise ValueError('unknown constant for keys_to_ignore')
        self._keys_to_ignore = value

    @property
    def idle_time(self):
        return self._idle_timer.interval() / 1000

    @idle_time.setter
    def idle_time(self, value):
        self._idle_timer.setInterval(int(value * 1000))

    @property
    def keyboard_active(self):
        return self._idle_timer.isActive()


class PollingKeyboardMonitor(AbstractKeyboardMonitor):
    """
    Monitor the keyboard for state changes by constantly polling the keyboard.
    """

    #: default polling interval
    DEFAULT_POLLDELAY = 200
    #: size of the X11 keymap array
    _KEYMAP_SIZE = 32

    def __init__(self, parent=None):
        AbstractKeyboardMonitor.__init__(self, parent)
        self._keyboard_was_active = False
        self._old_keymap = array(b'B', b'\0' * 32)
        self._keyboard_timer = QTimer(self)
        self._keyboard_timer.timeout.connect(self._check_keyboard_activity)
        self._keyboard_timer.setInterval(self.DEFAULT_POLLDELAY)
        self._activity = QTime()
        self._keys_to_ignore = self.IGNORE_NO_KEYS
        self._keymap_mask = self._setup_mask()
        self._idle_time = self.DEFAULT_IDLETIME

    @property
    def is_running(self):
        return self._keyboard_timer.isActive()

    def start(self):
        self._keyboard_timer.start()
        self.started.emit()

    def stop(self):
        AbstractKeyboardMonitor.stop(self)
        self._keyboard_timer.stop()
        self.stopped.emit()

    @property
    def keys_to_ignore(self):
        return self._keys_to_ignore

    @keys_to_ignore.setter
    def keys_to_ignore(self, value):
        if not (self.IGNORE_NO_KEYS <= value <= self.IGNORE_MODIFIER_COMBOS):
            raise ValueError('unknown constant for keys_to_ignore')
        self._keys_to_ignore = value
        self._keymap_mask = self._setup_mask()

    @property
    def idle_time(self):
        return self._idle_time / 1000

    @idle_time.setter
    def idle_time(self, value):
        self._idle_time = int(value * 1000)

    def _setup_mask(self):
        mask = array(b'B', b'\xff' * 32)
        if self._keys_to_ignore >= self.IGNORE_MODIFIER_KEYS:
            modifier_mappings = xlib.get_modifier_mapping(QX11Display())
            for modifier_keys in modifier_mappings:
                for keycode in modifier_keys:
                    mask[keycode // 8] &= ~(1 << (keycode % 8))
        return mask

    @property
    def keyboard_active(self):
        is_active = False

        _, raw_keymap = xlib.query_keymap(QX11Display())
        keymap = array(b'B', raw_keymap)

        is_active = keymap != self._old_keymap
        for new_state, old_state, mask in izip(keymap, self._old_keymap,
                                               self._keymap_mask):
            is_active = new_state & ~old_state & mask
            if is_active:
                break

        if self._keys_to_ignore == self.IGNORE_MODIFIER_COMBOS:
            for state, mask in izip(keymap, self._keymap_mask):
                if state & ~mask:
                    is_active = False
                    break

        self._old_keymap = keymap
        return is_active

    def _check_keyboard_activity(self):
        if self.keyboard_active:
            self._activity.start()
            if not self._keyboard_was_active:
                self._keyboard_was_active = True
                self.typingStarted.emit()
        elif self._activity.elapsed() > self._idle_time and \
                 self._keyboard_was_active:
            self._keyboard_was_active = False
            self.typingStopped.emit()


def create_resume_monitor(parent=None):
    """
    Create a new resume monitor:

    >>> monitor = create_resume_monitor(parent)
    >>> monitor.resuming.connect(lambda: print('system is resuming'))

    This function automatically chooses the "best" available implementation.
    Currently this means, that a :class:`UPowerResumeMonitor` is created, if
    UPower is installed and working.  Otherwise ``None`` is returned.

    .. note::

       This should actually be the task of KDEs hardware abstraction library
       Solid.  It indeed provides this functionality through the
       ``Solid::PowerManagement::Notifier::resumingFromSuspend`` signal, but
       unfortunately the ``Notifier`` class is not wrapped by PyKDE.

    Return an implementation of :class:`AbstractResumeMonitor`, or ``None``, if
    this system does not support monitoring of power state.
    """
    if dbus:
        bus = dbus.SystemBus(mainloop=DBusGMainLoop())
        activatable_names = bus.list_activatable_names()
        if 'org.freedesktop.UPower' in activatable_names:
            # UPower is available on the system bus
            return UPowerResumeMonitor(parent)
    # no power state monitoring available
    return None


class AbstractResumeMonitor(QObject):
    """
    Abstract base class for suspend monitors.

    This class defines the interface for classes, which monitor the systems
    power state and emit :attr:`resuming`, whenever the system resumes from a
    sleep state.

    Use :func:`create_resume_monitor()` to create an instance of the "best"
    implementation of this class.
    """

    #: Qt signal, emitted whenever the system resumes from a sleep state.  Has
    #: no arguments.
    resuming = pyqtSignal()


class UPowerResumeMonitor(AbstractResumeMonitor):
    """
    Implementation of :class:`AbstractResumeMonitor`, which uses UPower_ to
    monitor the system's power state.

    .. _UPower: http://upower.freedesktop.org
    """

    UPOWER_SERVICE_NAME = 'org.freedesktop.UPower'
    UPOWER_INTERFACE = 'org.freedesktop.UPower'
    UPOWER_OBJECT_PATH = '/org/freedesktop/UPower'

    def __init__(self, parent=None):
        AbstractResumeMonitor.__init__(self, parent)
        self._bus = dbus.SystemBus(mainloop=DBusGMainLoop())
        self._bus.add_signal_receiver(
            self.resuming.emit, 'Resuming', self.UPOWER_SERVICE_NAME,
            self.UPOWER_INTERFACE, self.UPOWER_OBJECT_PATH)
