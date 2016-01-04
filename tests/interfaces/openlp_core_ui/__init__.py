# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2016 OpenLP Developers                                   #
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
Module-level functions for the functional test suite
"""

import os

from openlp.core.common import is_win

from tests.interfaces import patch
from .test_projectormanager import tmpfile


def setUp():
    """
    Set up this module of tests
    """
    if not is_win():
        # Wine creates a sharing violation during tests. Ignore.
        try:
            os.remove(tmpfile)
        except:
            pass


def tearDown():
    """
    Ensure test suite has been cleaned up after tests
    """
    patch.stopall()
    if not is_win():
        try:
            # In case of changed schema, remove old test file
            os.remove(tmpfile)
        except FileNotFoundError:
            pass
