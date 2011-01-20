:mod:`synaptiks.config` – Configuration handling
================================================

.. automodule:: synaptiks.config
   :synopsis: Configuration handling


Standard configuration directories and files
--------------------------------------------

.. autofunction:: get_configuration_directory

.. autofunction:: get_touchpad_config_file_path

.. autofunction:: get_touchpad_defaults_file_path

.. autofunction:: get_management_config_file_path


Touchpad configuration
----------------------

.. autofunction:: get_touchpad_defaults

.. autoclass:: TouchpadConfiguration

   .. automethod:: load

   .. automethod:: __init__

   .. automethod:: save


Manager Configuration
---------------------

.. autoclass:: ManagerConfiguration

   .. autoattribute:: DEFAULTS

   .. automethod:: load

   .. automethod:: __init__

   .. automethod:: save

