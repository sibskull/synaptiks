Translation Guide
=================

**synaptiks** provides complete support for localization based on the KDE
libraries and gettext.  This makes it very easy to add new translations or
update existing ones.  Before you start, make sure that you have all required
programs installed.  You will need:

- gettext_
- and an editor for translation files, like lokalize_ or poedit_.

To actually work with the translations, you need a copy of the latest sources
of **synaptiks**.  If you are familar with git, just clone the whole
repository::

   git clone git://github.com/lunaryorn/synaptiks.git

Alternatively, you can download and extract an archive containing the latest
sources from `archives page
<https://github.com/lunaryorn/synaptiks/archives/master>`_.


Introduction into **synaptiks** translations
--------------------------------------------

The source directory of **synaptiks** contains a subdirectory called ``po/``,
which contains all translation data:

- The :term:`template catalog` :file:`synaptiks.pot`
- All :term:`message catalogs <message catalog>`

The :term:`template catalog` is automatically updated from the **synaptiks**
sources by the **synaptiks** developers.  As a translator, just care for the
:term:`message catalogs <message catalog>`.


Adding a new translation
------------------------

To create a new translation, execute the ``init_catalog`` command from the
source directory.  This command will ask for your email address and create a
new :term:`message catalog` using the language of your current locale
settings::

   $ python setup.py init_catalog
   running init_catalog
   /usr/bin/msginit --locale en --input po/synaptiks.pot --output po/en.po
   The new message catalog should contain your email address, so that users can
   give you feedback about the translations, and so that maintainers can contact
   you in case of unexpected technical problems.

   Is the following your email address?
     lunar@localhost.localdomain
   Please confirm by pressing Return, or enter your email address.
   your_email_address@example.com
   Retrieving http://translationproject.org/team/index.html... done.
   A translation team for your language (en) does not exist yet.
   If you want to create a new translation team for en, please visit
     http://www.iro.umontreal.ca/contrib/po/HTML/teams.html
     http://www.iro.umontreal.ca/contrib/po/HTML/leaders.html
     http://www.iro.umontreal.ca/contrib/po/HTML/index.html

   Created po/en.po.

Now open the created :file:`po/en.po` with the translation editor and start
translating **synaptiks**.

To create a :term:`message catalog` for another language than the one of your
current locale, use the ``--locale`` option.  This option takes a single
argument, the :term:`language code` for the new translation::

   $ python setup.py init_catalog --locale de


Updating an existing translation
--------------------------------

To update an existing translation, first merge all new messages from the
:term:`template catalog` into the :term:`message catalog` with the following
command::

   $ python setup.py update_catalog --locale en

Of course, you have to replace ``en`` with the :term:`language code` of the
translation, you want to work on.  If you leave the ``--locale`` option, all
catalogs will be updated.

Then edit the translation using your favourite translation editor and translate
all messages, which are not translated, or marked as "fuzzy".


Contributing your translation
-----------------------------

In order to have your translation included into **synaptiks** you have to send
it to the developers.  You can either send it by email, or upload the
translation somewhere (e.g. in a pastebin like http://paste.pocoo.org) and
create a new issue in the `issue tracker`_ with a link to the uploaded
translation.

If you want to maintain a translation for a longer time, it will be easier for
you, if you fork_ the **synaptiks** repository on Github_ and send `pull
requests`_, whenever you updated the translation.


Terms
-----

.. glossary::

   language code
      A two-letter language code as defined in `ISO 639-1`_.

   message
      Anything, that needs translation, like labels in the user interface or
      the text contents of dialogs and notifications.  The original, english
      messages are contained in the **synaptiks** sources.

   template catalog
      Template for new :term:`message catalogs <message catalog>`.  It contains
      all :term:`messages <message>` and is automatically updated from the
      **synaptiks** sources.

   message catalog
      A file containing translations for a specific language.  The filename
      consists of the :term:`language code` of this translation and the
      extension ``.po``.


.. _gettext: http://www.gnu.org/software/gettext/
.. _lokalize: http://kde.org/applications/development/lokalize/
.. _poedit: http://www.poedit.net/
.. _ISO 639-1: http://en.wikipedia.org/wiki/ISO_639
.. _issue tracker: https://github.com/lunaryorn/synaptiks/issues
.. _GitHub: https://github.com/lunaryorn/synaptiks
.. _fork: http://help.github.com/forking/
.. _pull requests: http://help.github.com/pull-requests/
