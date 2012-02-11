.. _usage:

Usage of |synaptiks|
====================

Touchpad configuration
----------------------

To configure the behaviour of your touchpad, please oeb the |synaptiks| module
in |systemsettings| at :menuselection:`Input Devices --> Touchpad`.


.. _hardware-configuration:

Hardware information and configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :guilabel:`Hardware` page provides information about the touchpad and configures some
general hardware properties.

.. figure:: hardware.png
   :align: center
   :scale: 50 %

   Screenshot of the :guilabel:`Hardware` page

The bold centered text shows the product name of the touchpad.  The line right
below tells you, how many fingers the touchpad can detect separately.  Many
modern or more expensive laptops will have touchpads, which detect two or more
fingers separately, which allows for two-finger scrolling and taps with
multiple fingers.  Some touchpads do not provide native support for two
fingers, however they can emulate this feature.  The :guilabel:`Two-finger
emulation` box informs about whether this is supported or not.  If the touchpad
does neither detect multiple fingers nor support two-finger emulation, you are
stuck with using a single finger.

The :guilabel:`Buttons` box tells how, what physical buttons the touchpad
provides.  Most touchpads have a physical left mouse button and a physical
right mouse button.  Sometimes a physical middle mouse button is detected,
though the touchpad does not actually have one.  In this case, the middle mouse
button is triggered by pressing the left mouse button and the right mouse
button at the same time.

Some systems have a circular touchpad.  Unfortunately the touchpad driver does
not detect circular touchpad automatically, so if you have a circular touchpad,
please enable :guilabel:`The touchpad is circular` to let the driver know, that
your touchpad is circular.


.. _motion-configuration:

Motion configuration
~~~~~~~~~~~~~~~~~~~~

To configure cursor motion, please activate the :guilabel:`Cursor motion` page.

.. figure:: motion.png
   :align: center
   :scale: 50 %

The :guilabel:`Minimum speed` and :guilabel:`Maximum speed` controls configure
the speed, at which the cursors moves, if you move your finger.  The higher the
speed is, the more the cursor moves, if you move your finger across the
touchpad.  When moving the finger very slowly, the :guilabel:`Minimum speed` is
used, when moving very fast, the :guilabel:`Maximum speed` is used by the
touchpad driver.  When moving at moderate speed, a value somewhere in between
is used.  The :guilabel:`Acceleration factor` defines, how fast the driver
increases the speed as you move your finger faster.

If you do not want cursor acceleration, set :guilabel:`Minimum speed` and
:guilabel:`Maximum speed` to the same value.  Acceleration is then disabled,
the cursor always moves at the same speed.

If you drag something and hit the edge of the touchpad with your finger, the
touchpad driver automatically continues the cursor movements.  After all, you
cannot release the touchpad without interrupting the drag action.  If you want
to enable this feature for all movements, not only drags, enable :guilabel:`For
all movements, not only dragging` in the :guilabel:`Continue cursor motion when
hitting the touchpad edge` group.


.. _scrolling-configuration:

Scrolling configuration
~~~~~~~~~~~~~~~~~~~~~~~

To configure scrolling, please activate the :guilabel:`Scrolling` page.

.. figure:: scrolling.png
   :align: center
   :scale: 50 %

   Screenshot of the :guilabel:`Scrolling` page

In the upper half of the dialog you can configure :guilabel:`Horizontal
scrolling` and :guilabel:`Vertical scrolling`.  Scrolling with two fingers is
only possible, if your touchpad can detect two fingers separately or at least
emulate this feature (see :ref:`hardware-configuration`).  In the screenshot
above, this is not the case, and therefore the corresponding items are
disabled.

The setting :guilabel:`Move distance to scroll a single line` defines, how much
the finger must move to scroll a single line.  The larger this value, the
slower scrolling gets.

If :guilabel:`Continue edge scrolling automatically` is checked, edge scrolling
will continue automatically:

* If :guilabel:`Continue edge scrolling, while the finger stays in an edge
  corner` is checked, edge scrolling will continue automatically as long as
  your finger stays in the touchpad corner.
* If it is unchecked, edge scrolling will automatically continue, if you lift
  your finger from the touchpad, while your scrolling speed is above the
  :guilabel:`Scrolling speed threshold to continue scrolling`.  Scrolling will
  stop, if you touch the touchpad again.

If :guilabel:`Scrolling speed threshold to continue scrolling` is set to zero,
:guilabel:`Continue edge scrolling automatically` is automatically disabled.


.. _circular-scrolling:

Horizontal circular scrolling
+++++++++++++++++++++++++++++

An alternative approach to scrolling is :guilabel:`Circular scrolling`, which
allows you to scroll up and down by moving your fingers in circles across the
touchpad.  Circular scrolling starts, if you move your finger into the
:guilabel:`Area, which triggers circular scrolling`.  This avoids interference
with normal moves on the touchpads.  If you move your finger in this "trigger"
area, the circular scrolling mode is activated.  Now you can move in clockwise
or counter-clockwise circles to scroll downwards or upwards, moving your finger
by a certain angle scrolls by a single line.  The speed is configured by
:guilabel:`Angle by which to move the finger to scroll a single line`.  The
higher this angle, the more you need to move your finger to scroll a single
line.  For instance, if you set it to ``90°``, you need to move your finger a
quarter of the touchpad perimeter to scroll a single line.  Obviously, circular
scrolling gets slower as you increase the angle.


.. _tapping-configuration:

Tapping configuration
~~~~~~~~~~~~~~~~~~~~~

To configure tapping, please activate the :guilabel:`Tapping` page.

.. figure:: tapping.png
   :align: center
   :scale: 50 %

   Screenshot of the :guilabel:`Tapping` configuration page

Tapping on the touchpad works just like pressing mouse buttons.  In this dialog
page you can configure, which mouse buttons are triggered by tapping the
touchpad in a specific manner.

You will notice slight delays between the tap on the touchpad and actual mouse
click.  The touchpad driver needs this delay to distinguish between single
clicks and double clicks.  If you are mainly using single clicks, you can check
:guilabel:`Make single taps faster and double taps slower (fast taps)`.  The
touchpad driver will then react faster to a single tap, at the cost of making
double clicks caused by double tapping slower.

To configure, which mouse clicks are actually triggered by tapping, refer to
the group :guilabel:`Mouse clicks triggered by tapping`.  In the center of this
group, multi-finger tapping is configured.  If your touchpad doesn't support
multi-finger taps or at least an emulation of two-finger taps (see
:ref:`hardware-configuration`), the corresponding items are greyed out.  In the
screenshot above, taps with two and three fingers are obviously not supported
by the touchpad, and tapping with one finger is equivalent to the left mouse
button.

The four boxes in the corner configure taps in the touchpad corners.  In the
screenshot above, special corner taps are all disabled.  In this case, tapping
the corners works just like tapping the rest of the touchpad.  If however the
:guilabel:`Top right corner` was set to :guilabel:`Right mouse button` for
instance, tapping the top right corner with one finger would be like pressing
the right mouse button.


.. _tap-and-drag-gesture:

Drag and drop with tapping
++++++++++++++++++++++++++

Tapping can also be used to perform drag and drop operations, just check
:guilabel:`Drag items by tapping the touchpad and then immediately touching it
again`.  To drag something, tap the touchpad, and then immediately touch the
touchpad again and move your finger on the touchpad.  The item will be dragged
along with your finger's movements.

A drag operation started this way can continue, if you release the finger.
This gives you more freedom to move the item around, but may interfere with
other actions.  Check :guilabel:`Continue dragging when releasing the finger
until the touchpad is touched again` to enable this feature.  If you now
release your finger, the drag operation simply continues until you tap the
touchpad again or the :guilabel:`Timeout to automatically stop dragging`
expires.


.. _touchpad-management:

Touchpad management
-------------------

To use the hotkey to switch the touchpad on or off, and to have your touchpad
managed automatically, please start the tray application, available in the
|kde| menu under :menuselection:`Applications --> Utilities --> Touchpad
management`.

.. figure:: traymenu.png
   :align: center
   :scale: 100 %

   Screenshot of the |synaptiks| tray application and its menu

This tray application provides a global shortcut :kbd:`Ctrl+Alt+T` to switch
the touchpad on or off.

The tray application does not start automatically at logon by default.  If you
want to continue using the tray application, please use :guilabel:`Configure
synaptiks...` to open the configuration dialog and enable
:guilabel:`Automatically start at logon`:

.. figure:: management.png
   :align: center
   :scale: 50 %

   Screenshot of the configuration dialog of the tray application


.. _automatic-management:

Automatic touchpad management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The tray application can also switch your touchpad automatically off while you
are typing or if you plug in an external mouse.  These features are disabled by
default to not confuse users, you need to explicitly enable them in the
configuration dialog shown above.


.. _mouses:

Mouses
++++++

To switch off the touchpad, if an external mouse is plugged, check
:guilabel:`Automatically switch off touchpad, if mouse is plugged`.  In case,
your laptop has "virtual" mouse devices (e.g. :guilabel:`Broadcom Corp` and
:guilabel:`PS/2 Mouse` in the Screenshot), you can use the list box
:guilabel:`Ignore the following mouse devices`.  This box lists all connected
mouses.  Any mouse, that is checked in this box, will be completed ignored.


.. _keyboard-activity:

Keyboard activity
+++++++++++++++++

To switch off the touchpad while you are typing, check :guilabel:`Automatically
switch off touchpad on keyboard activity`.  Depending on your personal
preferences, you might not want the touchpad to be switched off, if you press
modifier keys like :kbd:`Ctrl` or :kbd:`Alt`.  The :guilabel:`Ignore these
keys` box provides three choices to match your preferences:

:guilabel:`No keys`
   Use this setting, if any key press should switch off the touchpad.

:guilabel:`Modifier keys`
   Use this setting, if you want to ignore modifier keys *only*.  Common
   modifier keys are :kbd:`Ctrl`, :kbd:`Alt` or :kbd:`Shift`.  Combinations of
   modifier keys and standard keys (e.g. :kbd:`Ctrl+Q`) are *not* ignored.

:guilabel:`Modifier combinations`
   If you also want combinations of standard keys and modifier keys to be
   ignored, use this last setting.  Combinations of modifier keys and standard
   keys like :kbd:`Ctrl+Q` are ignored.  However, standard :kbd:`Shift`
   combinations for uppercase letters (e.g. :kbd:`Shift+S`) are also ignored,
   which may not be, what you want.

After you stopped typing, and before switching the touchpad on again,
|synaptiks| will wait a short moment (two seconds by default), just in case,
you did not stop typing, but just typed a bit slower.  If you type fast, the
standard delay will be way to long, so decrease the :guilabel:`Time to wait
before switching the touchpad on again`.


.. include:: /substitutions.rst
