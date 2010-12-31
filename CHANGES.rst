Changelog
#########

0.5 (in development)
====================

- Complete rewrite in Python instead of C++
- The KDED module is gone, touchpad management is now done by a little system
  tray application
- The System Settings module contains only touchpad configuration, but not the
  touchpad management settings anymore.

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
