:mod:`synaptiks.monitors` – Event monitoring
============================================

.. automodule:: synaptiks.monitors
   :synopsis: event monitoring
   :platform: Linux


Mouse device monitoring
-----------------------

.. autoclass:: MouseDevice

   .. attribute:: serial

      The serial number of the device as string.  First item of the tuple

   .. attribute:: name

      The product name of the device as string

.. autoclass:: MouseDevicesMonitor

   .. autoattribute:: plugged_devices

   .. rubric:: Signals

   .. autoattribute:: mousePlugged

   .. autoattribute:: mouseUnplugged

.. autoclass::  MouseDevicesManager

   .. rubric:: Signals

   .. autoattribute:: firstMousePlugged

   .. autoattribute:: lastMouseUnplugged

   .. rubric:: Other members

   .. automethod:: start

   .. automethod:: stop

   .. attribute:: is_running

      ``True``, if the manager is currently running, ``False`` otherwise.

      .. seealso:: :meth:`start()` and :meth:`stop()`

   .. autoattribute:: ignored_mouses



Keyboard monitoring
-------------------

.. autofunction:: create_keyboard_monitor

.. autoclass:: AbstractKeyboardMonitor

   .. rubric:: Class-level constants

   .. autoattribute:: DEFAULT_IDLETIME

   .. rubric:: Class-level constants for :attr:`keys_to_ignore`

   .. autoattribute:: IGNORE_NO_KEYS

   .. autoattribute:: IGNORE_MODIFIER_KEYS

   .. autoattribute:: IGNORE_MODIFIER_COMBOS

   .. rubric:: Signals

   .. autoattribute:: started

   .. autoattribute:: stopped

   .. autoattribute:: typingStarted

   .. autoattribute:: typingStopped

   .. rubric:: Other members

   .. autoattribute:: is_running

   .. automethod:: start

   .. automethod:: stop

   .. autoattribute:: idle_time

   .. autoattribute:: keys_to_ignore

   .. autoattribute:: keyboard_active

.. rubric:: Available implementations

.. autoclass:: PollingKeyboardMonitor()

.. autoclass:: RecordingKeyboardMonitor()


Resume monitoring
-----------------

.. autofunction:: create_resume_monitor

.. autoclass:: AbstractResumeMonitor

   .. autoattribute:: resuming

.. rubric:: Available implementations

.. autoclass:: UPowerResumeMonitor
