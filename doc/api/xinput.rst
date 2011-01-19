:mod:`synaptiks.xinput` – XInput device management
==================================================

.. automodule:: synaptiks.xinput
   :synopsis: Input device access
   :platform: Xorg


The :class:`InputDevice` class
------------------------------

.. autoclass:: InputDevice()

   .. automethod:: all_devices

   .. automethod:: find_devices_by_name

   .. automethod:: find_devices_with_property

   .. attribute:: id

      The device id as integer

   .. autoattribute:: name

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

.. autofunction:: is_property_defined

.. autofunction:: assert_xinput_version

.. autoexception:: XInputVersionError
   :members:
