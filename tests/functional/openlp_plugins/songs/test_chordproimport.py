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
This module contains tests for the OpenSong song importer.
"""
import os

from openlp.core.common.path import Path

from tests.helpers.songfileimport import SongImportTestHelper
from unittest.mock import patch, MagicMock

TEST_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', 'resources', 'chordprosongs'))


class TestChordProFileImport(SongImportTestHelper):

    def __init__(self, *args, **kwargs):
        self.importer_class_name = 'ChordProImport'
        self.importer_module_name = 'chordpro'
        super(TestChordProFileImport, self).__init__(*args, **kwargs)

    @patch('openlp.plugins.songs.lib.importers.chordpro.Settings')
    def test_song_import(self, mocked_settings):
        """
        Test that loading an ChordPro file works correctly on various files
        """
        # Mock out the settings - always return False
        mocked_returned_settings = MagicMock()
        mocked_returned_settings.value.side_effect = lambda value: True if value == 'songs/enable chords' else False
        mocked_settings.return_value = mocked_returned_settings
        # Do the test import
        self.file_import([Path(TEST_PATH, 'swing-low.chordpro')],
                         self.load_external_result_data(os.path.join(TEST_PATH, 'swing-low.json')))
