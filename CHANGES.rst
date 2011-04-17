0.6 (in development)
====================

- #1: Use XRecord for keyboard management, if available
- #6: Reinitialize mouse monitoring and mouse display if the system is resuming
  from suspend
- #4: Fixed touchpad search on 64-bit systems


0.5.3 (Mar 8, 2011)
===================

- Fixed segfault on failed connection to X11 display in ``synaptikscfg``
- #7: Show a clean error message instead of a traceback, when no touchpad is
  found by ``synaptikscfg``


0.5.2 (Feb 8, 2011)
===================

- Fixed corner coasting configuration to actually reflect the corner coasting
  setting from the touchpad driver
- #3: Fixed property data extraction on 64 bit architectures


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
