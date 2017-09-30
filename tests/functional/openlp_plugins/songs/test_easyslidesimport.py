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
This module contains tests for the EasySlides song importer.
"""
import os

from openlp.core.common.path import Path

from tests.helpers.songfileimport import SongImportTestHelper

TEST_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', 'resources', 'easyslidessongs'))


class TestEasySlidesFileImport(SongImportTestHelper):

    def __init__(self, *args, **kwargs):
        self.importer_class_name = 'EasySlidesImport'
        self.importer_module_name = 'easyslides'
        super(TestEasySlidesFileImport, self).__init__(*args, **kwargs)

    def test_song_import(self):
        """
        Test that loading an EasySlides file works correctly on various files
        """
        self.file_import(Path(TEST_PATH, 'amazing-grace.xml'),
                         self.load_external_result_data(os.path.join(TEST_PATH, 'Amazing Grace.json')))
        self.file_import(Path(TEST_PATH, 'Export_2017-01-12_BB.xml'),
                         self.load_external_result_data(os.path.join(TEST_PATH, 'Export_2017-01-12_BB.json')))
