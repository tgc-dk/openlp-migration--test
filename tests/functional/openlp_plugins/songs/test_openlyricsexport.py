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
This module contains tests for the OpenLyrics song importer.
"""
import shutil
from tempfile import mkdtemp
from unittest import TestCase
from unittest.mock import MagicMock, patch

from openlp.core.common.registry import Registry
from openlp.core.common.path import Path, rmtree
from openlp.plugins.songs.lib.openlyricsexport import OpenLyricsExport

from tests.helpers.testmixin import TestMixin


class TestOpenLyricsExport(TestCase, TestMixin):
    """
    Test the functions in the :mod:`openlyricsexport` module.
    """
    def setUp(self):
        """
        Create the registry
        """
        Registry.create()
        self.temp_folder = Path(mkdtemp())

    def tearDown(self):
        """
        Cleanup
        """
        rmtree(self.temp_folder)

    def test_export_same_filename(self):
        """
        Test that files is not overwritten if songs has same title and author
        """
        # GIVEN: A mocked song_to_xml, 2 mocked songs, a mocked application and an OpenLyricsExport instance
        with patch('openlp.plugins.songs.lib.openlyricsexport.OpenLyrics.song_to_xml') as mocked_song_to_xml:
            mocked_song_to_xml.return_value = '<?xml version="1.0" encoding="UTF-8"?>\n<empty/>'
            author = MagicMock()
            author.display_name = 'Test Author'
            song = MagicMock()
            song.authors = [author]
            song.title = 'Test Title'
            parent = MagicMock()
            parent.stop_export_flag = False
            mocked_application_object = MagicMock()
            Registry().register('application', mocked_application_object)
            ol_export = OpenLyricsExport(parent, [song, song], self.temp_folder)

            # WHEN: Doing the export
            ol_export.do_export()

            # THEN: The exporter should have created 2 files
            self.assertTrue((self.temp_folder /
                             '{title} ({display_name}).xml'.format(
                                 title=song.title, display_name=author.display_name)).exists())
            self.assertTrue((self.temp_folder /
                             '{title} ({display_name})-1.xml'.format(
                                 title=song.title, display_name=author.display_name)).exists())
