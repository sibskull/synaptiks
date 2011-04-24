Installation instructions
=========================

Previous versions of **synaptiks**
----------------------------------

Please remove any previously installed version of **synaptiks** 0.4 or earlier.
Files from earlier versions of **synaptiks** conflict with those from the
current version, and will cause confusion and errors.

If you installed **synaptiks** through the package manager of your
distribution, simply uninstall the corresponding package.  Please beware, that
some distributions use a different name for the package, for instance in Debian
and Ubuntu it is called ``kde-config-touchpad`` instead of ``synaptiks``.

If you compiled **synaptiks** from source, change to the build directory and
execute the following command with root privileges::

   rm -r $(< install_manifest.txt)

Alternatively you can remove all files listed in :file:`install_manifest`
manually.

To re-create this file, if you have already removed the build directory, simply
re-install the older **synaptiks** version with *excately* the same build
configuration.  Refer to the installation instructions the release you have
installed, if you do not remember the installation procedure.


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

If all dependencies are installed, you can proceed to the installation of
**synaptiks** itself.  There are two different ways of installing
**synaptiks**, depending on what python module installer is availabe on your
distribution.


The modern way
^^^^^^^^^^^^^^

If the modern python installer tool pip_ is available on your distribution,
just run::

   sudo pip install synaptiks

This will automatically download and install **synaptiks** and any missing
python modules required by **synaptiks**.  It will however *not* install native
libraries and bindings, so make sure, that you have installed all those
libraries, which are mentioned in the :ref:`requirements` section.

If you have already downloaded **synaptiks**, you can also just extract the
archive, change into the directory and run::

   sudo pip install .

This works just like the above command, except that it does of course not
download **synaptiks** again.


The legacy way
^^^^^^^^^^^^^^

If your distribution is still stuck with the old and legacy ``easy_install``
tool, installation is slightly more complicated.

Download **synaptiks** manually (see `Downloads`_), extract the archive, change
into the directory and run the following command::

   sudo python2 setup.py install --single-version-externally-managed

Make *absolutely* sure, that you pass the option
``--single-version-externally-managed``, otherwise synaptiks will not be
installed correctly.  Especially all KDE-specific files and all translations
will be missing, consequently you will neither see **synaptiks** in the
application menu, nor will the System Settings module be available.

For the same reason you can *not* use the automatic ``easy_install`` script.


Distribution-specific instructions
==================================

This sections contains installation instructions for some distributions.  These
installations may be slightly outdated, because the developers do not use all
of these distributions at a regular basis.


Arch linux
----------

Install the dependencies::

   sudo pacman -S pyqt kdebindings-python python-pip gettext docbook-xsl dbus-python

Install **synaptiks**::

   sudo pip install synaptiks

Optionally remove the installation-only requirements again::

   sudo pacman -R python-pip gettext docbook-xsl

Alternatively you can use the `synaptiks PKGBUILD`_ from the `Arch User
Repository`_, which is however not supported by the **synaptiks** developers.


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
.. _Downloads: http://pypi.python.org/pypi/synaptiks
.. _synaptiks PKGBUILD: http://aur.archlinux.org/packages.php?ID=32204
.. _Arch User Repository: http://aur.archlinux.org/
