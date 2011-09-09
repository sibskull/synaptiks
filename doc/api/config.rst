:mod:`synaptiks.config` – Configuration handling
================================================

.. automodule:: synaptiks.config
   :synopsis: Configuration handling


Standard configuration directory
--------------------------------

.. autofunction:: get_configuration_directory


Configuration classes
---------------------

.. autoclass:: TouchpadConfiguration

   .. automethod:: defaults

   .. automethod:: load

   .. automethod:: load_from_touchpad

   .. automethod:: save

   .. automethod:: apply_to

   .. automethod:: update_from_touchpad


.. autoclass:: ManagerConfiguration
   :show-inheritance:

   .. automethod:: defaults

   .. automethod:: load

   .. automethod:: save

   .. automethod:: apply_to
