0.5.1 (Jan 31, 2011)
====================

- Fixed source distribution to include the handbook


0.5 (Jan 29, 2011)
==================

- Complete rewrite in Python instead of C++
- Removed daemon
- Removed touchpad management from System Settings module
- Added a separate system tray application for touchpad management, which is
  *not* started automatically

Miscellaneous changes
---------------------

- Detect two-finger emulation support and enable two-finger configuration, if
  emulation is supported
- The acceleration factor setting now supports four decimals after point for
  increased precision
- Use UDev instead of HAL for mouse device monitoring


0.4 (Apr 11, 2010) and older releases
=====================================

These releases were written in C++ and developed on other places, please refer
to the changelog_ of these legacy releases for information about changes.

.. _changelog: http://gitorious.org/synaptiks/synaptiks-website/blobs/master/changes.rst
