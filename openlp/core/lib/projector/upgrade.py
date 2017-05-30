# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2017 OpenLP Developers                                   #
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
The :mod:`upgrade` module provides a way for the database and schema that is the
backend for the projector setup.
"""
import logging

# Not all imports used at this time, but keep for future upgrades
from sqlalchemy import Column, types
from sqlalchemy.sql.expression import null

from openlp.core.common.db import drop_columns
from openlp.core.lib.db import get_upgrade_op

log = logging.getLogger(__name__)

# Initial projector DB was unversioned
__version__ = 2

log.debug('Projector DB upgrade module loading')


def upgrade_1(session, metadata):
    """
    Version 1 upgrade - old db might/might not be versioned.
    """
    pass


def upgrade_2(session, metadata):
    """
    Version 2 upgrade.

    Update Projector() table to include new data defined in PJLink version 2 changes

    serial_no:      Column(String(30))
    sw_version:     Column(String(30))
    model_filter:   Column(String(30))
    model_lamp:     Column(String(30))

    :param session: DB session instance
    :param metadata: Metadata of current DB
    """

    new_op = get_upgrade_op(session)
    if 'serial_no' not in [t.name for t in metadata.tables.values()]:
        log.debug("Upgrading projector DB to version '2'")
        new_op.add_column('projector', Column('serial_no', types.String(30), server_default=null()))
        new_op.add_column('projector', Column('sw_version', types.String(30), server_default=null()))
        new_op.add_column('projector', Column('model_filter', types.String(30), server_default=null()))
        new_op.add_column('projector', Column('model_lamp', types.String(30), server_default=null()))
    else:
        log.warn("Skipping upgrade_2 of projector DB")
