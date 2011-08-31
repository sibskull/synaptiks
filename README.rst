#########
synaptiks
#########

http://synaptiks.lunaryorn.de

synaptiks is a touchpad configuration and management tool for KDE_, available
under the terms of the `simplified BSD licence`_ (see ``COPYING``).

It provides a System Settings module to configure basic and advanced features
of the touchpad.  Additionally it comes with a little system tray application,
which can switch the touchpad automatically off, while an external mouse is
plugged or while you are typing.

Please refer to the website_ for more information about synaptiks including
some screenshots, a detailled handbook and also some API documentation for
interested developers.


Requirements
============

synaptiks is implemented in Python_ atop of PyQt4_ and PyKDE4_ and requires the
following native libraries and tools:

- Python_ (at least 2.6, Python 3 is *not* supported)
- PyQt4_ (at least 4.7)
- PyKDE4_ (at least 4.5)
- libXi (at least 1.4, earlier releases are untested)
- gettext_ (only required during installation to compile the translations, can
  be removed after successful installation)
- `Docbook XSL stylesheets`_ (only required during installation to compile the
  handbook, can be removed after successful installation)

Moreover some Python modules are required:

- pyudev_ (at least 0.8)
- argparse_ (at least 1.1, not required, if Python 2.7 is installed)

All these libraries must be available before installing **synaptiks**.  It is
recommended, that you install them through the package manager of your
distribution.  However, the Python modules listed above are also automatically
installed by the installation script of **synaptiks**.

Additionally **synaptiks** has some optional dependencies, which are not
strictly required, but enable some additional features or improved components
in **synaptiks**:

- libXtst (client side of the XRecord extension, for improved keyboard
  monitoring)
- dbus-python_ and UPower_ (to handle mouse devices correctly across suspend
  and resume)

Finally xf86-input-synaptics 1.3 or newer must be installed and configured
as touchpad driver.  synaptiks will not work, if the touchpad is managed by a
generic mouse device driver like xf86-input-evdev.

Please make sure, that any previous release of synaptiks is completely removed
before this release of synaptiks is installed.


Installation
============

If all dependencies are installed, you can simply install synaptiks using
pip_::

   sudo pip install synaptiks

This will automatically download and install synaptiks and all missing Python
modules (but not the native libraries).

If pip is not available on your system, please download synaptiks manually,
extract the archive, and run the following command from the source directory::

   sudo python2 setup.py install --single-version-externally-managed

Make sure, that you pass the option ``--single-version-externally-managed``,
otherwise synaptiks will not be installed correctly.  Therefore it is
absolutely recommended, that you use pip.


Issues and feedback
===================

If you like or dislike synaptiks or if you have any problems with synaptiks,
feel free to send an email with compliments or blame or with some questions.

If you have found a bug in synaptiks, if miss a certain feature or have any
proposals concerning synaptiks, please report them to the `issue tracker`_.
To help us with solving this issue, please include any information that you can
get into your report, including especially any error messages or tracebacks.
If unsure, better post more information than required.


Contribution and development
============================

All development of synaptiks happens on GitHub_.  The complete source code is
available in a git_ repository::

   git clone --recursive git://github.com/lunaryorn/synaptiks

If you want to create or update translations, or fix some issue in synaptiks,
or even add some new features, please fork this repository on GitHub_ and send
a pull requests with your work.  Of course, should you dislike GitHub, you can
also send patches through the issue tracker or through email.


.. _KDE: http://www.kde.org
.. _simplified BSD licence: http://www.opensource.org/licenses/bsd-license.php
.. _website: http://synaptiks.lunaryorn.de
.. _python: http://www.python.org
.. _PyQt4: http://riverbankcomputing.co.uk/software/pyqt/intro
.. _PyKDE4: http://techbase.kde.org/Development/Languages/Python
.. _pyudev: http://packages.python.org/pyudev
.. _argparse: http://code.google.com/p/argparse/
.. _gettext: http://www.gnu.org/software/gettext/
.. _pip: http://www.pip-installer.org/
.. _docbook xsl stylesheets: http://docbook.sourceforge.net/
.. _dbus-python: http://www.freedesktop.org/wiki/Software/DBusBindings#Python
.. _UPower: http://upower.freedesktop.org
.. _issue tracker: https://github.com/lunaryorn/synaptiks/issues
.. _GitHub: https://github.com/lunaryorn/synaptiks
.. _git: http://git-scm.com/
