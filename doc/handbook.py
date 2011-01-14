# -*- coding: utf-8 -*-
# Copyright (c) 2009, 2010, 2011, Sebastian Wiesner <lunaryorn@googlemail.com>
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


"""
    handbook
    ========

    Build the **synaptiks** handbook as part of sphinx' build process.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


import os
import posixpath
from subprocess import Popen, PIPE, check_call, CalledProcessError
from shutil import copy

import lxml.html

from sphinx.util import ensuredir, mtimes_of_files
from sphinx.util.console import bold


def get_kde4_path(type):
    """
    Query the KDE paths for the given ``type``.

    The paths are extracted from the output of the :command:`kde4-config`
    tool.

    Returns all available paths for ``type`` as a list of strings.  Raises
    :exc:`subprocess.CalledProcessError`, if :command:`kde4-config` failed.
    """
    localprefix = Popen(['kde4-config', '--localprefix'],
                        stdout=PIPE).communicate()[0].strip()
    cmd = ['kde4-config', '--path', type]
    kde4_config = Popen(cmd, stdout=PIPE)
    stdout = kde4_config.communicate()[0]
    if kde4_config.returncode:
        raise CalledProcessError(kde4_config.returncode, cmd)
    return [p for p in stdout.strip().split(os.pathsep)
            if not p.startswith(localprefix)]


def meinproc4(document, stylesheet, target_directory):
    """
    Run :command:`meinproc4` on the given ``document`` using the given
    ``stylesheet``.

    The generated html files will be written to the ``target_directory``,
    which will be created, if it does not already exist.

    Raises :exc:`OSError`, if creation of ``target_directory`` or execution
    of :command:`meinproc4` failed or :exc:`subprocess.CalledProcessError`
    if :command:`meinproc4` failed to build html files.
    """
    ensuredir(target_directory)
    # turn arguments into absolute paths, as meinproc4 uses a different
    # working directory
    check_call(['meinproc4', '--param', 'kde.common="common/"',
                '--stylesheet', os.path.abspath(stylesheet),
                os.path.abspath(document)],
               cwd=target_directory)


def copy_commons(commons, source, target):
    """
    Copy all the given common files from ``source`` directory to ``target``
    directory.

    ``target`` is created, if it does not already exist.  Raises
    :exc:`OSError`, if creation of ``target_directory`` failed.
    """
    ensuredir(target)
    for common in commons:
        filename = os.path.basename(common)
        sourcepath = os.path.join(source, filename)
        targetpath = os.path.join(target, filename)
        copy(sourcepath, targetpath)


def copy_images(source, target):
    """
    Copy all PNG images from ``source`` directory to ``target`` directory.

    ``target`` is created, if it does not already exist.  Raises
    :exc:`OSError`, if creation of ``target_directory`` failed.
    """
    ensuredir(target)
    for filename in os.listdir(source):
        if os.path.splitext(filename)[1] != '.png':
            continue
        sourcepath = os.path.join(source, filename)
        targetpath = os.path.join(target, filename)
        copy(sourcepath, targetpath)


def post_process_files(target):
    """
    Post-process all generated HTML files in the ``target`` directory.

    This function

    - extracts all links to common files (stylesheets, logos, etc.),
    - removes the kde logo and the search page link from the header,
    - replaces the link to docs.kde.org with a link to the homepage
    - adds the accesskey ``h`` to the new homepage link,
    - recodes the generated files to utf-8,
    - and prettfies and fixes the generated html.

    Returns a set links to common files.
    """
    commons = set()
    for filename in os.listdir(target):
        if os.path.splitext(filename)[1] != '.html':
            continue
        filename = os.path.join(target, filename)
        tree = lxml.html.parse(filename)
        for element, attribute, link, pos in tree.getroot().iterlinks():
            if element.text == 'docs.kde.org':
                element.attrib.update({
                    'href': '../index.html',
                    'accesskey': 'h'})
                element.text = 'Home'
            elif link == '/search_form.html':
                element.drop_tree()
            elif posixpath.basename(link) == 'kde_logo.png':
                element.drop_tree()
            if link.startswith('common/'):
                commons.add(link)
        with open(filename, 'wb') as stream:
            stream.write(lxml.html.tostring(
                tree, pretty_print=True, encoding='utf-8',
                include_meta_content_type=True))
    return commons


def build_handbook(app, exception):
    """
    Build the handbook, if the applications builder is a HTML builder and no
    exception occured (``exception`` is ``None``).
    """
    source = app.config.handbook_source_directory
    if exception or app.builder.name != 'html' or not source:
        return

    app.builder.info(bold('Building handbook... '), nonl=True)

    source = os.path.normpath(os.path.join(app.srcdir, source))

    if not os.path.isdir(source):
        app.builder.info(bold('{0} does not exist'.format(source)))
        return

    target = os.path.join(app.outdir, 'handbook')

    # check mtimes to avoid needless rebuilds
    source_mtime = max(mtimes_of_files([source], '.docbook'))
    img_mtime = max(mtimes_of_files([source], '.png'))
    target_mtimes = list(mtimes_of_files([target], '.html'))
    if target_mtimes:
        target_mtime = max(target_mtimes)
        if source_mtime < target_mtime and img_mtime < target_mtime:
            app.builder.info('skipped')
            return

    document = os.path.join(source, 'index.docbook')
    customization = os.path.join(
        get_kde4_path('data')[0], 'ksgmltools2', 'customization')
    stylesheet = os.path.join(customization, 'kde-chunk-online.xsl')
    copy_images(source, target)
    meinproc4(document, stylesheet, target)
    commons = post_process_files(target)
    common_directory = os.path.join(get_kde4_path('html')[0],
                                    'en', 'common')
    copy_commons(commons, common_directory,
                 os.path.join(target, 'common'))
    app.builder.info('done')


def setup(app):
    app.add_config_value('handbook_source_directory', None, 'env')
    app.connect('build-finished', build_handbook)
