:mod:`synaptiks.x11.input` – X11 input device management
========================================================

.. automodule:: synaptiks.x11.input
   :synopsis: Input device access
   :platform: Xorg


The :class:`InputDevice` class
------------------------------

.. autoclass:: InputDevice()

   .. automethod:: all_devices

   .. automethod:: find_devices_by_type

   .. automethod:: find_devices_by_name

   .. automethod:: find_devices_with_property

   .. attribute:: display

      The :class:`~synaptiks.x11.Display` on which this device is defined

   .. attribute:: id

      The device id as integer

   .. autoattribute:: name

   .. autoattribute:: is_master

   .. autoattribute:: type

   .. autoattribute:: attachment_device

   .. automethod:: __len__

   .. automethod:: __iter__

   .. automethod:: __contains__

   .. automethod:: __getitem__

   .. automethod:: set_int

   .. automethod:: set_byte

   .. method:: set_bool(property, values)

      Alias for :meth:`set_byte`

   .. automethod:: set_float

.. autoexception:: InputDeviceNotFoundError
   :members:

.. autoexception:: PropertyTypeError
   :show-inheritance:
   :members:

.. autoexception:: UndefinedPropertyError
   :show-inheritance:
   :members:


Miscellaneous stuff
-------------------

.. autofunction:: assert_xinput_version

.. autoexception:: XInputVersionError
   :members:

.. autoexception:: XInputVersion

   .. attribute:: major

      The ``major`` version number as integer

   .. attribute:: minor

      The ``minor`` version number as integer
