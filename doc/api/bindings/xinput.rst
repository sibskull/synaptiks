:mod:`synaptiks._bindings.xinput` – Binding to libXi
====================================================

.. automodule:: synaptiks._bindings.xinput
   :synopsis: Binding to libXI
   :platform: X11

Data types
----------

.. class:: XIDeviceInfo

   .. attribute:: deviceid

      The device id as integer

   .. attribute:: name

      The device name as byte string

   .. attribute:: use

      The usage of this device inside the X server as :ref:`device type
      <xinput-device-types>`.

   .. attribute:: attachment

      The device ID of the attached device.

      If :attr:`use` is :data:`MASTER_POINTER` or :data:`MASTER_KEYBOARD`, this
      contains the device ID of the paired master keyboard or pointer
      respectively.  If :attr:`use` is :data:`SLAVE_POINTER` or
      :data:`SLAVE_KEYBOARD`, this contains the device ID of the master pointer
      or keyboard respectively, this device is attached to.

      If :attr:`use` is :data:`FLOATING_SLAVE`, the value of this attribute is
      undefined.

   .. attribute:: enabled

.. class:: XIDeviceInfo_p

   Pointer to :class:`XIDeviceInfo`


.. _xinput-device-types:

Device types
------------

Constants for :attr:`XIDeviceInfo.use`.

.. autodata:: MASTER_POINTER

.. autodata:: MASTER_KEYBOARD

.. autodata:: SLAVE_POINTER

.. autodata:: SLAVE_KEYBOARD

.. autodata:: FLOATING_SLAVE


.. _xinput-special-ids:

Special device IDs
------------------

Special device IDs for :func:`query_device`

.. autodata:: ALL_DEVICES

.. autodata:: ALL_MASTER_DEVICES


Functions
---------

.. autofunction:: query_version

.. autofunction:: query_device

.. function:: free_device_info(info)

   Free the given device info.

   ``info`` is a :class:`XIDeviceInfo_p`.

.. autofunction:: list_properties

.. autofunction:: get_property

.. autofunction:: change_property
