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
"""
This module contains tests for the SWORD Bible importer.
"""
from unittest import TestCase, skipUnless
from unittest.mock import MagicMock, patch

try:
    from openlp.plugins.bibles.lib.importers.sword import SwordBible
    HAS_PYSWORD = True
except ImportError:
    HAS_PYSWORD = False

from openlp.plugins.bibles.lib.db import BibleDB

from tests.utils import load_external_result_data
from tests.utils.constants import RESOURCE_PATH

TEST_PATH = RESOURCE_PATH / 'bibles'


@skipUnless(HAS_PYSWORD, 'pysword not installed')
class TestSwordImport(TestCase):
    """
    Test the functions in the :mod:`swordimport` module.
    """

    def setUp(self):
        self.registry_patcher = patch('openlp.plugins.bibles.lib.bibleimport.Registry')
        self.registry_patcher.start()
        self.manager_patcher = patch('openlp.plugins.bibles.lib.db.Manager')
        self.manager_patcher.start()

    def tearDown(self):
        self.registry_patcher.stop()
        self.manager_patcher.stop()

    def test_create_importer(self):
        """
        Test creating an instance of the Sword file importer
        """
        # GIVEN: A mocked out "manager"
        mocked_manager = MagicMock()

        # WHEN: An importer object is created
        importer = SwordBible(mocked_manager, path='.', name='.', file_path=None, sword_key='', sword_path='')

        # THEN: The importer should be an instance of BibleDB
        assert isinstance(importer, BibleDB)

    @patch('openlp.plugins.bibles.lib.importers.sword.SwordBible.application')
    @patch('openlp.plugins.bibles.lib.importers.sword.modules')
    def test_simple_import(self, mocked_pysword_modules, mocked_application):
        """
        Test that a simple SWORD import works
        """
        # GIVEN: Test files with a mocked out "manager", "import_wizard", and mocked functions
        #       get_book_ref_id_by_name, create_verse, create_book, session and get_language.
        #       Also mocked pysword structures
        mocked_manager = MagicMock()
        mocked_import_wizard = MagicMock()
        importer = SwordBible(mocked_manager, path='.', name='.', file_path=None, sword_key='', sword_path='')
        test_data = load_external_result_data(TEST_PATH / 'dk1933.json')
        importer.wizard = mocked_import_wizard
        importer.get_book_ref_id_by_name = MagicMock()
        importer.create_verse = MagicMock()
        importer.create_book = MagicMock()
        importer.session = MagicMock()
        importer.get_language = MagicMock(return_value='Danish')
        mocked_bible = MagicMock()
        mocked_genesis = MagicMock()
        mocked_genesis.name = 'Genesis'
        mocked_genesis.num_chapters = 1
        books = {'ot': [mocked_genesis]}
        mocked_structure = MagicMock()
        mocked_structure.get_books.return_value = books
        mocked_bible.get_structure.return_value = mocked_structure
        mocked_bible.get_iter.return_value = [verse[1] for verse in test_data['verses']]
        mocked_module = MagicMock()
        mocked_module.get_bible_from_module.return_value = mocked_bible
        mocked_pysword_modules.SwordModules.return_value = mocked_module

        # WHEN: Importing bible file
        importer.do_import()

        # THEN: The create_verse() method should have been called with each verse in the file.
        assert importer.create_verse.called is True
        for verse_tag, verse_text in test_data['verses']:
            importer.create_verse.assert_any_call(importer.create_book().id, 1, int(verse_tag), verse_text)
