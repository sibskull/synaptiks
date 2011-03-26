:mod:`synaptiks.management` – Touchpad management
=================================================

.. automodule:: synaptiks.management
   :synopsis: Touchpad management
   :platform: X11

.. autoclass:: TouchpadManager

   .. attribute:: states

       A read-only mapping containing the touchpad states of this manager.  It
       maps the names of these states to :class:`~PyQt4.QtCore.QState` objects,
       which represent the states.  The object name of each state is the same
       as the name of the state in this mapping.

       You may freely access these objects to connect to the signals of the
       states, but do not modify the state objects.

   .. attribute:: transitions

      A read-only mapping containing the transitions between the :attr:`states`
      of this manager.  It maps pairs of state names in the form ``(source,
      destination)`` to a list of :class:`~PyQt4.QtCore.QAbstractTransition`
      objects, each of which represents a single transition from the ``source``
      state to the ``destination`` state.

   .. autoattribute:: current_state

   .. autoattribute:: current_state_name

   .. autoattribute:: monitor_mouses

   .. autoattribute:: monitor_keyboard

   .. automethod:: add_touchpad_switch_action
