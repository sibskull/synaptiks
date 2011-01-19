:mod:`synaptiks.touchpad` – Touchpad access
===========================================

.. automodule:: synaptiks.touchpad
   :synopsis: Touchpad access
   :platform: Xorg

The touchpad class
------------------

.. autoexception:: NoTouchpadError

.. autoclass:: Touchpad
   :show-inheritance:

   .. automethod:: find_all

   .. automethod:: find_first

   .. autoattribute:: off

   .. rubric:: cursor motion properties

   .. autoattribute:: minimum_speed

   .. autoattribute:: maximum_speed

   .. autoattribute:: acceleration_factor

   .. autoattribute:: edge_motion_always

   .. rubric:: scrolling properties

   .. autoattribute:: vertical_edge_scrolling

   .. autoattribute:: horizontal_edge_scrolling

   .. autoattribute:: vertical_scrolling_distance

   .. autoattribute:: horizontal_scrolling_distance

   .. autoattribute:: coasting_speed

   .. autoattribute:: corner_coasting

   .. autoattribute:: vertical_two_finger_scrolling

   .. autoattribute:: horizontal_two_finger_scrolling

   .. autoattribute:: circular_scrolling

   .. autoattribute:: circular_scrolling_trigger

   .. autoattribute:: circular_scrolling_distance

   .. rubric:: tapping properties

   .. autoattribute:: fast_taps

   .. autoattribute:: rt_tap_action

   .. autoattribute:: rb_tap_action

   .. autoattribute:: lt_tap_action

   .. autoattribute:: lb_tap_action

   .. autoattribute:: f1_tap_action

   .. autoattribute:: f2_tap_action

   .. autoattribute:: f3_tap_action

   .. autoattribute:: tap_and_drag_gesture

   .. autoattribute:: locked_drags

   .. autoattribute:: locked_drags_timeout

   .. rubric:: touchpad capabilities

   .. autoattribute:: coasting

   .. autoattribute:: capabilities

   .. autoattribute:: finger_detection

   .. autoattribute:: buttons

   .. autoattribute:: has_pressure_detection

   .. autoattribute:: has_finger_width_detection

   .. autoattribute:: has_two_finger_emulation
