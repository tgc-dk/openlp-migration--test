#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2018 OpenLP Developers                                   #
# --------------------------------------------------------------------------- #
# This program is free software; you can redistribute it and/or modify it     #
# under the terms of the GNU General Public License as published by the Free  #
# Software Foundation; version 2 of the License.                              #
#                                                                             #
# This program is distributed in the hope that it will be useful, but WITHOUT #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for    #
# more details.                                                               #
#                                                                             #
# You should have received a copy of the GNU General Public License along     #
# with this program; if not, write to the Free Software Foundation, Inc., 59  #
# Temple Place, Suite 330, Boston, MA 02111-1307 USA                          #
###############################################################################

import re
import sys
from setuptools import setup, find_packages
from subprocess import Popen, PIPE


VERSION_FILE = 'openlp/.version'
SPLIT_ALPHA_DIGITS = re.compile(r'(\d+|\D+)')


def try_int(s):
    """
    Convert string s to an integer if possible. Fail silently and return
    the string as-is if it isn't an integer.

    :param s: The string to try to convert.
    """
    try:
        return int(s)
    except (TypeError, ValueError):
        return s


def natural_sort_key(s):
    """
    Return a tuple by which s is sorted.

    :param s: A string value from the list we want to sort.
    """
    return list(map(try_int, SPLIT_ALPHA_DIGITS.findall(s)))


def natural_sort(seq):
    """
    Returns a copy of seq, sorted by natural string sort.

    :param seq: The sequence to sort.
    :param compare: The comparison method to use
    :return: The sorted sequence
    """
    import copy
    temp = copy.copy(seq)
    temp.sort(key=natural_sort_key)
    return temp


# NOTE: The following code is a duplicate of the code in openlp/core/common/checkversion.py.
# Any fix applied here should also be applied there.
ver_file = None
try:
    # Get the revision of this tree.
    bzr = Popen(('bzr', 'revno'), stdout=PIPE)
    tree_revision, error = bzr.communicate()
    code = bzr.wait()
    if code != 0:
        raise Exception('Error running bzr log')

    # Get all tags.
    bzr = Popen(('bzr', 'tags'), stdout=PIPE)
    output, error = bzr.communicate()
    code = bzr.wait()
    if code != 0:
        raise Exception('Error running bzr tags')
    tags = output.splitlines()
    if not tags:
        tag_version = '0.0.0'
        tag_revision = '0'
    else:
        # Remove any tag that has "?" as revision number. A "?" as revision number indicates, that this tag is from
        # another series.
        tags = [tag for tag in tags if tag.split()[-1].strip() != '?']
        # Get the last tag and split it in a revision and tag name.
        tag_version, tag_revision = tags[-1].split()
    # If they are equal, then this tree is tarball with the source for the release. We do not want the revision number
    # in the version string.
    tree_revision = tree_revision.strip()
    tag_revision = tag_revision.strip()
    if tree_revision == tag_revision:
        version_string = tag_version.decode('utf-8')
    else:
        version_string = '{version}.dev{revision}'.format(version=tag_version.decode('utf-8'),
                                                          revision=tree_revision.decode('utf-8'))
    ver_file = open(VERSION_FILE, 'w')
    ver_file.write(version_string)
except Exception:
    ver_file = open(VERSION_FILE, 'r')
    version_string = ver_file.read().strip()
finally:
    ver_file.close()

requires = [
    'alembic',
    'beautifulsoup4',
    'chardet',
    'lxml',
    'Mako',
    'PyQt5',
    'QtAwesome',
    'requests',
    'SQLAlchemy >= 0.5',
    'waitress',
    'WebOb',
    'websockets'
]
if sys.platform.startswith('win'):
    requires.extend([
        'PyICU',
        'pywin32'
    ])
elif sys.platform.startswith('darwin'):
    requires.extend([
        'pyobjc',
        'pyobjc-framework-Cocoa'
    ])
elif sys.platform.startswith('linux'):
    requires.append('dbus-python')

setup(
    name='OpenLP',
    version=version_string,
    description="Open source Church presentation and lyrics projection application.",
    long_description="""\
OpenLP (previously openlp.org) is free church presentation software, or lyrics projection software, used to display
slides of songs, Bible verses, videos, images, and even presentations (if PowerPoint is installed) for church worship
using a computer and a data projector.""",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Religion',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: Afrikaans',
        'Natural Language :: Dutch',
        'Natural Language :: English',
        'Natural Language :: French',
        'Natural Language :: German',
        'Natural Language :: Hungarian',
        'Natural Language :: Indonesian',
        'Natural Language :: Japanese',
        'Natural Language :: Norwegian',
        'Natural Language :: Portuguese (Brazilian)',
        'Natural Language :: Russian',
        'Natural Language :: Swedish',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: BSD :: FreeBSD',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Desktop Environment :: Gnome',
        'Topic :: Desktop Environment :: K Desktop Environment (KDE)',
        'Topic :: Multimedia',
        'Topic :: Multimedia :: Graphics :: Presentation',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Video',
        'Topic :: Religion'
    ],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='open source church presentation lyrics projection song bible display project',
    author='Raoul Snyman',
    author_email='raoulsnyman@openlp.org',
    url='https://openlp.org/',
    license='GNU General Public License',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.6',
    install_requires=requires,
    extras_require={
        'jenkins': ['python-jenkins'],
        'mysql': ['mysql-connector-python'],
        'odbc': ['pyodbc'],
        'postgresql': ['psycopg2'],
        'spellcheck': ['pyenchant >= 1.6'],
        'sword-bibles': ['pysword'],
        'xdg': ['pyxdg']
    },
    tests_require=['nose2', 'PyICU', 'pylint'],
    entry_points={'gui_scripts': ['openlp = openlp.__main__:start']}
)
