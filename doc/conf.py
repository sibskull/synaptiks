# -*- coding: utf-8 -*-
# Copyright (c) 2010, 2011, 2012, Sebastian Wiesner <lunaryorn@googlemail.com>
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import sys, os

# add project directory to module path in order to import synaptiks correctly
doc_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(
    os.path.join(doc_directory, os.pardir)))


class Mock(object):
    """
    Mock modules.

    Taken from
    http://read-the-docs.readthedocs.org/en/latest/faq.html#i-get-import-errors-on-libraries-that-depend-on-c-modules
    with some slight changes.
    """

    # fake some module constants
    MASTER_POINTER = MASTER_KEYBOARD =  SLAVE_POINTER = SLAVE_KEYBOARD = FLOATING_SLAVE = 'foo'

    @classmethod
    def mock_modules(cls, *modules):
        for module in modules:
            sys.modules[module] = cls()

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self.__class__()

    def __getattr__(self, attribute):
        if attribute in ('__file__', '__path__'):
            return os.devnull
        else:
            # return the *class* object here.  Mocked attributes may be used as
            # base class in synaptiks code, thus the returned mock object must
            # behave as class, or else Sphinx autodoc will fail to recognize
            # the mocked base class as such, and "autoclass" will become
            # meaningless
            return self.__class__


# mock out native modules used throughout synaptiks to enable Sphinx autodoc even
# if these modules are unavailable, as on readthedocs.org
Mock.mock_modules('PyQt4', 'PyQt4.QtCore', 'PyQt4.QtGui',
                  'synaptiks._bindings', 'synaptiks._bindings.util', 'synaptiks._bindings.xlib',
                  'synaptiks._bindings.xinput', 'synaptiks._bindings.xrecord')


import synaptiks

needs_sphinx = '1.0'

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx', 'sphinx.ext.graphviz', 'sphinxcontrib.issuetracker']

master_doc = 'index'
exclude_patterns = ['_build/*', 'substitutions.rst']
source_suffix = '.rst'

project = u'synaptiks'
copyright = u'2010, 2011 Sebastian Wiesner'
version = '.'.join(synaptiks.__version__.split('.')[:2])
release = synaptiks.__version__

templates_path = ['_templates']
html_theme = 'synaptiks'
html_theme_path = ['_themes']
html_static_path = ['_static']
html_title = 'synaptiks {0}'.format(version)
html_favicon = 'favicon.ico'
html_logo = '_static/synaptiks.png'
html_sidebars = {
    '**': ['sidebartop.html', 'localtoc.html', 'relations.html',
           'searchbox.html'],
    'index': ['sidebartop.html', 'issues.html', 'searchbox.html'],
}

intersphinx_mapping = {'http://docs.python.org/': None}
handbook_source_directory = 'handbook'

issuetracker = 'github'
issuetracker_project = 'lunaryorn/synaptiks'


def setup(app):
    from sphinx.ext.autodoc import cut_lines
    app.connect('autodoc-process-docstring', cut_lines(2, what=['module']))
