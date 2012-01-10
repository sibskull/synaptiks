# -*- coding: utf-8 -*-
# Copyright (c) 2009, 2010, 2011, 2012, Sebastian Wiesner <lunaryorn@googlemail.com>
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


def locate_kde4_resource(type, relative_name):
    """
    Locate a KDE resource of the given ``type`` with the given relative name.

    Return the path, or ``None`` if the resource was not found.
    """
    cmd = ['kde4-config', '--path', type, '--locate', relative_name]
    kde4_config = Popen(cmd, stdout=PIPE)
    stdout = kde4_config.communicate()[0].strip()
    if kde4_config.returncode:
        raise CalledProcessError(kde4_config.returncode, cmd)
    return stdout or None


def meinproc4(document, stylesheet, target_directory):
    """
    Run :command:`meinproc4` on the given ``document`` using the given
    ``stylesheet``.

    The generated html files will be written to the ``target_directory``,
    which will be created, if it does not already exist.

    Raise :exc:`OSError`, if creation of ``target_directory`` or execution
    of :command:`meinproc4` failed or :exc:`subprocess.CalledProcessError`
    if :command:`meinproc4` failed to build html files.
    """
    ensuredir(target_directory)
    # turn arguments into absolute paths, as meinproc4 uses a different
    # working directory
    check_call(['meinproc4', '--param', 'kde.common="common/"',
                '--check', '--stylesheet', os.path.abspath(stylesheet),
                os.path.abspath(document)],
               cwd=target_directory)


def copy_commons(commons, target):
    """
    Copy all the given common files to ``target`` directory.

    ``target`` is created, if it does not already exist.  Raise :exc:`OSError`,
    if creation of ``target_directory`` failed.
    """
    ensuredir(target)
    for common in commons:
        filename = os.path.basename(common)
        sourcepath = locate_kde4_resource('html', posixpath.join('en', common))
        targetpath = os.path.join(target, filename)
        copy(sourcepath, targetpath)


def copy_images(source, target):
    """
    Copy all PNG images from ``source`` directory to ``target`` directory.

    ``target`` is created, if it does not already exist.  Raise :exc:`OSError`,
    if creation of ``target_directory`` failed.
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

    Return a set links to common files.
    """
    commons = set()
    for filename in os.listdir(target):
        if os.path.splitext(filename)[1] != '.html':
            continue
        filename = os.path.join(target, filename)
        tree = lxml.html.parse(filename)
        for element, attribute, link, pos in tree.getroot().iterlinks():
            if link.startswith('common/'):
                commons.add(link)
        # replace the KDE logo in the header with the synaptiks logo and make
        # the logo a backlink to the homepage
        header = tree.getroot().get_element_by_id('header_right')
        header_img = header.find('img')
        header_img.attrib['src'] = '../_static/synaptiks.png'
        header_link = lxml.html.Element('a', href='../index.html')
        header.replace(header_img, header_link)
        header_link.append(header_img)
        header_link.tail = header_img.tail
        header_img.tail = ''
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
    stylesheet = locate_kde4_resource(
        'data', 'ksgmltools2/customization/kde-chunk-online.xsl')
    copy_images(source, target)
    meinproc4(document, stylesheet, target)
    commons = post_process_files(target)
    copy_commons(commons, os.path.join(target, 'common'))
    app.builder.info('done')


def setup(app):
    app.add_config_value('handbook_source_directory', None, 'env')
    app.connect('build-finished', build_handbook)
