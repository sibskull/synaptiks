:mod:`synaptiks._bindings.xlib` – Binding to libX11
===================================================

.. automodule:: synaptiks._bindings.xlib
   :synopsis: Binding to libX11
   :platform: X11

Data types
----------

.. class:: Atom

   The type of xlib *Atoms*.  An atom is a special handle to efficiently identify
   an internal resource of the X11 server.

.. class:: Atom_p

   Pointer to an :class:`Atom`.

.. class:: Bool

   Boolean type used by libX11.

.. class:: Status

   Return type of libX11 functions to indicate error codes or success.

.. class:: KeyCode

   Represents the internal code of a single key.

.. class:: KeyCode_p

   Pointer to :class:`KeyCode`

.. class:: Display

   A connection to the X11 display.

.. class:: Display_p

   A pointer to :class:`Display`.

.. class:: XModifierKeyMap

   The keymap for modifier keys.

   .. attribute:: max_keypermod

      The number of key codes per modifier as integer.

   .. attribute:: modifiermapping

      The modifier mapping as C-array.  The array contains eight sets of
      :attr:`max_keypermod:` :class:`KeyCode` objects, one for each modifier in
      the order:

      - ``Shift``
      - ``Lock``
      - ``Control``
      - ``Mod1``
      - ``Mod2``
      - ``Mod3``
      - ``Mod4``
      - ``Mod5``

      Only non-zero key codes in this set are meaningful, zero key codes are
      ignored.

.. class:: XModifierKeymap_p

   Pointer to :class:`XModifierKeymap`


Constants
---------

.. autodata:: SUCCESS

.. autodata:: NONE

.. autodata:: ATOM

.. autodata:: INTEGER


Functions
---------

.. autofunction:: display(name=None)

.. autofunction:: free

.. function:: intern_atom(display, atom_name, only_if_exists)

   Create a :class:`Atom` for the given ``atom_name``.

   ``display`` is a :class:`Display_p` representing the connection to the X11
   display.  ``atom_name`` is a byte string with the name of the atom.
   ``only_if_exists`` is either a Python boolean or :class:`Bool`.  If ``True``
   or ``1``, the atom is only created, if it exists, otherwise :data:`NONE` is
   returned.  Else the atom is automatically created.

   Return an :class:`Atom` or :data:`NONE`, if the atom doesn't exist and
   ``only_if_exists`` is ``True`` or ``1``.

.. function:: get_atom_name(display, atom)

   Get the atom name for the given ``atom``.

   ``display`` is a :class:`Display_p` representing the connection to the X11
   display.  ``atom`` is the :class:`Atom` to get the name for.

   Return the name as byte string.

.. autofunction:: query_keymap

.. autoclass:: ModifierMap
   :members:

.. autofunction:: get_modifier_mapping
