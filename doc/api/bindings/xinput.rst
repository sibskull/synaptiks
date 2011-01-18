:mod:`~synaptiks._bindings.xinput` – Binding to libXi
=====================================================

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

   .. attribute:: attachment

   .. attribute:: enabled

.. class:: XIDeviceInfo_p

   Pointer to :class:`XIDeviceInfo`


Constants
---------

.. autodata:: ALL_DEVICES


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

