:mod:`synaptiks._bindings.xrecord` – Binding to the XRecord
===========================================================

.. automodule:: synaptiks._bindings.xrecord
   :synopsis: Binding to the XRecord extension interface provided by libXtst
   :platform: X11

Data types
----------

.. class:: XRecordContext

   A context to record data from X11 server.

.. class:: XRecordInterceptData

   .. attribute:: server_time

      The time of recording as :class:`~synaptiks._bindings.xlib.Time` object

   .. attribute:: category

      The category of the recorded data.  See :ref:`category-constants` for a
      list of possible values.

   .. attribute:: event

      A ``(event_type, detail)`` pair.  The ``event_type`` is the integral ID
      of the recorded event (e.g. :data:`~synaptiks._bindings.xlib.KEY_PRESS`),
      ``detail`` contains the event details as integer (e.g. the
      :class:`~synaptiks._bindings.xlib.KeyCode` in case of key events).

.. class:: XRecordInterceptData_p

   Pointer to :class:`XRecordInterceptData`


Constants
---------

.. rubric:: Client constants for :func:`context`

.. autodata:: CURRENT_CLIENTS

.. autodata:: FUTURE_CLIENTS

.. autodata:: ALL_CLIENTS

.. _category-constants:

Event categories
^^^^^^^^^^^^^^^^

The following constants describe the category of recorded protocol data (see
:attr:`XRecordInterceptData.category`):

.. autodata:: FROM_SERVER

.. autodata:: FROM_CLIENT

.. autodata:: CLIENT_STARTED

.. autodata:: CLIENT_DIED

.. autodata:: START_OF_DATA

.. autodata:: END_OF_DATA


Functions
---------

.. autofunction:: query_version

.. autofunction:: context

.. autofunction:: enable_context

.. function:: disable_context(display, context)

   Disable the given ``context``.

   ``display`` is an X11 display connection
   (e.g. :class:`~synaptiks._bindings.xlib.Display_p` or
   :class:`~synaptiks.qx11.QX11Display`).  ``context`` is a
   :class:`XRecordContext` object.

.. function:: free_data(data)

   Free the given protocol ``data`` (a :class:`XRecordInterceptData_p` object).
