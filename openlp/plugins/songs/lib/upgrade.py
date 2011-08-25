# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2011 Raoul Snyman                                        #
# Portions copyright (c) 2008-2011 Tim Bentley, Gerald Britton, Jonathan      #
# Corwin, Michael Gorven, Scott Guerrieri, Matthias Hub, Meinert Jordan,      #
# Armin Köhler, Joshua Miller, Stevan Pettit, Andreas Preikschat, Mattias     #
# Põldaru, Christian Richter, Philip Ridout, Simon Scudder, Jeffrey Smith,    #
# Maikel Stuivenberg, Martin Thompson, Jon Tibble, Frode Woldsund             #
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
"""
The :mod:`upgrade` module provides a way for the database and schema that is the backend for
the Songs plugin
"""

from sqlalchemy import Column, ForeignKey, Table, types
from migrate import changeset
from migrate.changeset.constraint import ForeignKeyConstraint

__version__ = 1

def upgrade_setup(metadata):
    """
    Set up the latest revision all tables, with reflection, needed for the
    upgrade process. If you want to drop a table, you need to remove it from
    here, and add it to your upgrade function.
    """
    tables = {
        u'authors': Table(u'authors', metadata, autoload=True),
        u'media_files': Table(u'media_files', metadata, autoload=True),
        u'song_books': Table(u'song_books', metadata, autoload=True),
        u'songs': Table(u'songs', metadata, autoload=True),
        u'topics': Table(u'topics', metadata, autoload=True),
        u'authors_songs': Table(u'authors_songs', metadata, autoload=True),
        u'songs_topics': Table(u'songs_topics', metadata, autoload=True)
    }
    return tables


def upgrade_1(session, metadata, tables):
    Table(u'media_files_songs', metadata, autoload=True).drop(checkfirst=True)
    Column(u'song_id', types.Integer(), default=None)\
        .create(table=tables[u'media_files'], populate_default=True)
    Column(u'weight', types.Integer(), default=0)\
        .create(table=tables[u'media_files'], populate_default=True)
    if metadata.bind.url.get_dialect().name != 'sqlite':
        ForeignKeyConstraint([u'song_id'], [u'songs.id'],
            table=tables[u'media_files']).create()

