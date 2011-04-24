:mod:`synaptiks.xlib` – Basic X11 API
=====================================

.. module:: synaptiks.xlib
   :synopsis: Basic X11 API
   :platform: X11

.. autoclass:: Display

   .. automethod:: from_name

   .. automethod:: from_qt

   .. attribute:: types

      Standard type atoms defined on this display as :class:`StandardTypes`.

   .. autoattribute:: open

   .. automethod:: close

   .. automethod:: intern_atom

.. autoexception:: DisplayError

.. autoclass:: StandardTypes

   .. attribute:: integer

      An :class:`Atom` representing an integer type

   .. attribute:: float

      An :class:`Atom` representing an float type

   .. attribute:: atom

      An :class:`Atom` representing an atom type

.. autoclass:: Atom

   .. automethod:: __init__

   .. attribute:: display

      The :class:`Display` this atom is defined on

   .. autoattribute:: value

   .. autoattribute:: name
