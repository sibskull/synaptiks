Installation instructions
=========================

.. warning::

   Please remove any previously installed version of **synaptiks** 0.4 or
   earlier first.


.. _requirements:

Requirements
------------

**synaptiks** is implemented in Python_ atop of PyQt4_ and PyKDE4_ and requires
the following native libraries and tools:

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

Finally xf86-input-synaptics 1.3 or newer must be installed and configured as
touchpad driver.  **synaptiks** will not work, if the touchpad is managed by a
generic mouse device driver like xf86-input-evdev.


Installation
------------

Just install **synaptiks** with pip_::

   sudo pip install synaptiks

This will automatically download and install **synaptiks** and any missing
python modules required by **synaptiks**.  It will however *not* install native
libraries and bindings, so make sure, that you have installed all those
libraries, which are mentioned in the :ref:`requirements` section.

.. note::

   If `pip`_ is not present on your system, download **synaptiks** manually
   from the `Python Package Index`_, extract the archive and run the following
   command in the extracted directory::

      sudo python setup.py install --single-version-externally-managed

   Do *not* omit ``--single-version-externally-managed``, and do *not* use
   ``easy_install``!


Distribution-specific instructions
==================================

This sections contains installation instructions for some distributions.  These
installations may be slightly outdated, because the developers do not use all
of these distributions at a regular basis.


Arch linux
----------

A `PKGBUILD`_ for **synaptiks** is provided in the `Arch User Repository`_.  It
is maintained and supported by the **synaptiks** developers.


Ubuntu
------

**synaptiks** is contained in the Ubuntu repositories by the name
  ``kde-config-touchpad``.


Gentoo
------

An ebuild for **synaptiks** is contained in the main portage tree as
``kde-misc/synaptiks``.


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
.. _Python Package Index: http://pypi.python.org/pypi/synaptiks
.. _PKGBUILD: http://aur.archlinux.org/packages.php?ID=32204
.. _Arch User Repository: http://aur.archlinux.org/
