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

   .. attribute:: plugged_devices

   .. rubric:: Signals

   .. autoattribute:: mousePlugged

   .. autoattribute:: mouseUnplugged


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
