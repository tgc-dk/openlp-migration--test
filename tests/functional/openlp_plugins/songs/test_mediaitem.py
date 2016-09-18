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
This module contains tests for the lib submodule of the Songs plugin.
"""
from unittest import TestCase
from unittest.mock import call

from PyQt5 import QtCore

from openlp.core.common import Registry, Settings
from openlp.core.lib import ServiceItem
from openlp.plugins.songs.lib.mediaitem import SongMediaItem
from openlp.plugins.songs.lib.db import AuthorType, Song
from tests.functional import patch, MagicMock
from tests.helpers.testmixin import TestMixin


class TestMediaItem(TestCase, TestMixin):
    """
    Test the functions in the :mod:`lib` module.
    """
    def setUp(self):
        """
        Set up the components need for all tests.
        """
        Registry.create()
        Registry().register('service_list', MagicMock())
        Registry().register('main_window', MagicMock())
        with patch('openlp.core.lib.mediamanageritem.MediaManagerItem._setup'), \
                patch('openlp.plugins.songs.forms.editsongform.EditSongForm.__init__'):
            self.media_item = SongMediaItem(None, MagicMock())
            self.media_item.save_auto_select_id = MagicMock()
            self.media_item.list_view = MagicMock()
            self.media_item.list_view.save_auto_select_id = MagicMock()
            self.media_item.list_view.clear = MagicMock()
            self.media_item.list_view.addItem = MagicMock()
            self.media_item.list_view.setCurrentItem = MagicMock()
            self.media_item.auto_select_id = -1
            self.media_item.display_songbook = False
            self.media_item.display_copyright_symbol = False
        self.setup_application()
        self.build_settings()
        QtCore.QLocale.setDefault(QtCore.QLocale('en_GB'))

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        self.destroy_settings()

    def test_display_results_song(self):
        """
        Test displaying song search results with basic song
        """
        # GIVEN: Search results, plus a mocked QtListWidgetItem
        with patch('openlp.core.lib.QtWidgets.QListWidgetItem') as MockedQListWidgetItem, \
                patch('openlp.core.lib.QtCore.Qt.UserRole') as MockedUserRole:
            mock_search_results = []
            mock_song = MagicMock()
            mock_song.id = 1
            mock_song.title = 'My Song'
            mock_song.sort_key = 'My Song'
            mock_song.authors = []
            mock_song_temp = MagicMock()
            mock_song_temp.id = 2
            mock_song_temp.title = 'My Temporary'
            mock_song_temp.sort_key = 'My Temporary'
            mock_song_temp.authors = []
            mock_author = MagicMock()
            mock_author.display_name = 'My Author'
            mock_song.authors.append(mock_author)
            mock_song_temp.authors.append(mock_author)
            mock_song.temporary = False
            mock_song_temp.temporary = True
            mock_search_results.append(mock_song)
            mock_search_results.append(mock_song_temp)
            mock_qlist_widget = MagicMock()
            MockedQListWidgetItem.return_value = mock_qlist_widget
            self.media_item.auto_select_id = 1

            # WHEN: I display song search results
            self.media_item.display_results_song(mock_search_results)

            # THEN: The current list view is cleared, the widget is created, and the relevant attributes set
            self.media_item.list_view.clear.assert_called_with()
            self.media_item.save_auto_select_id.assert_called_with()
            MockedQListWidgetItem.assert_called_once_with('My Song (My Author)')
            mock_qlist_widget.setData.assert_called_once_with(MockedUserRole, mock_song.id)
            self.media_item.list_view.addItem.assert_called_once_with(mock_qlist_widget)
            self.media_item.list_view.setCurrentItem.assert_called_with(mock_qlist_widget)

    def test_display_results_author(self):
        """
        Test displaying song search results grouped by author with basic song
        """
        # GIVEN: Search results grouped by author, plus a mocked QtListWidgetItem
        with patch('openlp.core.lib.QtWidgets.QListWidgetItem') as MockedQListWidgetItem, \
                patch('openlp.core.lib.QtCore.Qt.UserRole') as MockedUserRole:
            mock_search_results = []
            mock_author = MagicMock()
            mock_song = MagicMock()
            mock_song_temp = MagicMock()
            mock_author.display_name = 'My Author'
            mock_author.songs = []
            mock_song.id = 1
            mock_song.title = 'My Song'
            mock_song.sort_key = 'My Song'
            mock_song.temporary = False
            mock_song_temp.id = 2
            mock_song_temp.title = 'My Temporary'
            mock_song_temp.sort_key = 'My Temporary'
            mock_song_temp.temporary = True
            mock_author.songs.append(mock_song)
            mock_author.songs.append(mock_song_temp)
            mock_search_results.append(mock_author)
            mock_qlist_widget = MagicMock()
            MockedQListWidgetItem.return_value = mock_qlist_widget

            # WHEN: I display song search results grouped by author
            self.media_item.display_results_author(mock_search_results)

            # THEN: The current list view is cleared, the widget is created, and the relevant attributes set
            self.media_item.list_view.clear.assert_called_with()
            MockedQListWidgetItem.assert_called_once_with('My Author (My Song)')
            mock_qlist_widget.setData.assert_called_once_with(MockedUserRole, mock_song.id)
            self.media_item.list_view.addItem.assert_called_once_with(mock_qlist_widget)

    def test_display_results_book(self):
        """
        Test displaying song search results grouped by book and entry with basic song
        """
        # GIVEN: Search results grouped by book and entry, plus a mocked QtListWidgetItem
        with patch('openlp.core.lib.QtWidgets.QListWidgetItem') as MockedQListWidgetItem, \
                patch('openlp.core.lib.QtCore.Qt.UserRole') as MockedUserRole:
            mock_search_results = [('1', 'My Book', 'My Song', 1)]
            mock_qlist_widget = MagicMock()
            MockedQListWidgetItem.return_value = mock_qlist_widget

            # WHEN: I display song search results grouped by book
            self.media_item.display_results_book(mock_search_results)

            # THEN: The current list view is cleared, the widget is created, and the relevant attributes set
            self.media_item.list_view.clear.assert_called_with()
            MockedQListWidgetItem.assert_called_once_with('My Book #1: My Song')
            mock_qlist_widget.setData.assert_called_once_with(MockedUserRole, 1)
            self.media_item.list_view.addItem.assert_called_once_with(mock_qlist_widget)

    def test_songbook_natural_sorting(self):
        """
        Test that songbooks are sorted naturally
        """
        # GIVEN: Search results grouped by book and entry, plus a mocked QtListWidgetItem
        with patch('openlp.core.lib.QtWidgets.QListWidgetItem') as MockedQListWidgetItem:
            mock_search_results = [('2', 'Thy Book', 'Thy Song', 50),
                                   ('2', 'My Book', 'Your Song', 7),
                                   ('10', 'My Book', 'Our Song', 12),
                                   ('1', 'My Book', 'My Song', 1),
                                   ('2', 'Thy Book', 'A Song', 8)]
            mock_qlist_widget = MagicMock()
            MockedQListWidgetItem.return_value = mock_qlist_widget

            # WHEN: I display song search results grouped by book
            self.media_item.display_results_book(mock_search_results)

            # THEN: The songbooks are inserted in the right (natural) order,
            #       grouped first by book, then by number, then by song title
            calls = [call('My Book #1: My Song'), call().setData(QtCore.Qt.UserRole, 1),
                     call('My Book #2: Your Song'), call().setData(QtCore.Qt.UserRole, 7),
                     call('My Book #10: Our Song'), call().setData(QtCore.Qt.UserRole, 12),
                     call('Thy Book #2: A Song'), call().setData(QtCore.Qt.UserRole, 8),
                     call('Thy Book #2: Thy Song'), call().setData(QtCore.Qt.UserRole, 50)]
            MockedQListWidgetItem.assert_has_calls(calls)

    def test_display_results_topic(self):
        """
        Test displaying song search results grouped by topic with basic song
        """
        # GIVEN: Search results grouped by topic, plus a mocked QtListWidgetItem
        with patch('openlp.core.lib.QtWidgets.QListWidgetItem') as MockedQListWidgetItem, \
                patch('openlp.core.lib.QtCore.Qt.UserRole') as MockedUserRole:
            mock_search_results = []
            mock_topic = MagicMock()
            mock_song = MagicMock()
            mock_song_temp = MagicMock()
            mock_topic.name = 'My Topic'
            mock_topic.songs = []
            mock_song.id = 1
            mock_song.title = 'My Song'
            mock_song.sort_key = 'My Song'
            mock_song.temporary = False
            mock_song_temp.id = 2
            mock_song_temp.title = 'My Temporary'
            mock_song_temp.sort_key = 'My Temporary'
            mock_song_temp.temporary = True
            mock_topic.songs.append(mock_song)
            mock_topic.songs.append(mock_song_temp)
            mock_search_results.append(mock_topic)
            mock_qlist_widget = MagicMock()
            MockedQListWidgetItem.return_value = mock_qlist_widget

            # WHEN: I display song search results grouped by topic
            self.media_item.display_results_topic(mock_search_results)

            # THEN: The current list view is cleared, the widget is created, and the relevant attributes set
            self.media_item.list_view.clear.assert_called_with()
            MockedQListWidgetItem.assert_called_once_with('My Topic (My Song)')
            mock_qlist_widget.setData.assert_called_once_with(MockedUserRole, mock_song.id)
            self.media_item.list_view.addItem.assert_called_once_with(mock_qlist_widget)

    def test_display_results_themes(self):
        """
        Test displaying song search results sorted by theme with basic song
        """
        # GIVEN: Search results sorted by theme, plus a mocked QtListWidgetItem
        with patch('openlp.core.lib.QtWidgets.QListWidgetItem') as MockedQListWidgetItem, \
                patch('openlp.core.lib.QtCore.Qt.UserRole') as MockedUserRole:
            mock_search_results = []
            mock_song = MagicMock()
            mock_song_temp = MagicMock()
            mock_song.id = 1
            mock_song.title = 'My Song'
            mock_song.sort_key = 'My Song'
            mock_song.theme_name = 'My Theme'
            mock_song.temporary = False
            mock_song_temp.id = 2
            mock_song_temp.title = 'My Temporary'
            mock_song_temp.sort_key = 'My Temporary'
            mock_song_temp.theme_name = 'My Theme'
            mock_song_temp.temporary = True
            mock_search_results.append(mock_song)
            mock_search_results.append(mock_song_temp)
            mock_qlist_widget = MagicMock()
            MockedQListWidgetItem.return_value = mock_qlist_widget

            # WHEN: I display song search results sorted by theme
            self.media_item.display_results_themes(mock_search_results)

            # THEN: The current list view is cleared, the widget is created, and the relevant attributes set
            self.media_item.list_view.clear.assert_called_with()
            MockedQListWidgetItem.assert_called_once_with('My Theme (My Song)')
            mock_qlist_widget.setData.assert_called_once_with(MockedUserRole, mock_song.id)
            self.media_item.list_view.addItem.assert_called_once_with(mock_qlist_widget)

    def test_display_results_cclinumber(self):
        """
        Test displaying song search results sorted by CCLI number with basic song
        """
        # GIVEN: Search results sorted by CCLI number, plus a mocked QtListWidgetItem
        with patch('openlp.core.lib.QtWidgets.QListWidgetItem') as MockedQListWidgetItem, \
                patch('openlp.core.lib.QtCore.Qt.UserRole') as MockedUserRole:
            mock_search_results = []
            mock_song = MagicMock()
            mock_song_temp = MagicMock()
            mock_song.id = 1
            mock_song.title = 'My Song'
            mock_song.sort_key = 'My Song'
            mock_song.ccli_number = '12345'
            mock_song.temporary = False
            mock_song_temp.id = 2
            mock_song_temp.title = 'My Temporary'
            mock_song_temp.sort_key = 'My Temporary'
            mock_song_temp.ccli_number = '12346'
            mock_song_temp.temporary = True
            mock_search_results.append(mock_song)
            mock_search_results.append(mock_song_temp)
            mock_qlist_widget = MagicMock()
            MockedQListWidgetItem.return_value = mock_qlist_widget

            # WHEN: I display song search results sorted by CCLI number
            self.media_item.display_results_cclinumber(mock_search_results)

            # THEN: The current list view is cleared, the widget is created, and the relevant attributes set
            self.media_item.list_view.clear.assert_called_with()
            MockedQListWidgetItem.assert_called_once_with('12345 (My Song)')
            mock_qlist_widget.setData.assert_called_once_with(MockedUserRole, mock_song.id)
            self.media_item.list_view.addItem.assert_called_once_with(mock_qlist_widget)

    @patch(u'openlp.plugins.songs.lib.mediaitem.Settings')
    def test_build_song_footer_one_author_show_written_by(self, MockedSettings):
        """
        Test build songs footer with basic song and one author
        """
        # GIVEN: A Song and a Service Item, mocked settings: True for 'songs/display written by'
        # and False for 'core/ccli number' (ccli will cause traceback if true)

        mocked_settings = MagicMock()
        mocked_settings.value.side_effect = [True, False]
        MockedSettings.return_value = mocked_settings

        mock_song = MagicMock()
        mock_song.title = 'My Song'
        mock_song.authors_songs = []
        mock_author = MagicMock()
        mock_author.display_name = 'my author'
        mock_author_song = MagicMock()
        mock_author_song.author = mock_author
        mock_song.authors_songs.append(mock_author_song)
        mock_song.copyright = 'My copyright'
        service_item = ServiceItem(None)

        # WHEN: I generate the Footer with default settings
        author_list = self.media_item.generate_footer(service_item, mock_song)

        # THEN: I get the following Array returned
        self.assertEqual(service_item.raw_footer, ['My Song', 'Written by: my author', 'My copyright'],
                         'The array should be returned correctly with a song, one author and copyright')
        self.assertEqual(author_list, ['my author'],
                         'The author list should be returned correctly with one author')

    def test_build_song_footer_two_authors(self):
        """
        Test build songs footer with basic song and two authors
        """
        # GIVEN: A Song and a Service Item
        mock_song = MagicMock()
        mock_song.title = 'My Song'
        mock_song.authors_songs = []
        mock_author = MagicMock()
        mock_author.display_name = 'my author'
        mock_author_song = MagicMock()
        mock_author_song.author = mock_author
        mock_author_song.author_type = AuthorType.Music
        mock_song.authors_songs.append(mock_author_song)
        mock_author = MagicMock()
        mock_author.display_name = 'another author'
        mock_author_song = MagicMock()
        mock_author_song.author = mock_author
        mock_author_song.author_type = AuthorType.Words
        mock_song.authors_songs.append(mock_author_song)
        mock_author = MagicMock()
        mock_author.display_name = 'translator'
        mock_author_song = MagicMock()
        mock_author_song.author = mock_author
        mock_author_song.author_type = AuthorType.Translation
        mock_song.authors_songs.append(mock_author_song)
        mock_song.copyright = 'My copyright'
        service_item = ServiceItem(None)

        # WHEN: I generate the Footer with default settings
        author_list = self.media_item.generate_footer(service_item, mock_song)

        # THEN: I get the following Array returned
        self.assertEqual(service_item.raw_footer, ['My Song', 'Words: another author', 'Music: my author',
                                                   'Translation: translator', 'My copyright'],
                         'The array should be returned correctly with a song, two authors and copyright')
        self.assertEqual(author_list, ['another author', 'my author', 'translator'],
                         'The author list should be returned correctly with two authors')

    def test_build_song_footer_base_ccli(self):
        """
        Test build songs footer with basic song and a CCLI number
        """
        # GIVEN: A Song and a Service Item and a configured CCLI license
        mock_song = MagicMock()
        mock_song.title = 'My Song'
        mock_song.copyright = 'My copyright'
        service_item = ServiceItem(None)
        Settings().setValue('core/ccli number', '1234')

        # WHEN: I generate the Footer with default settings
        self.media_item.generate_footer(service_item, mock_song)

        # THEN: I get the following Array returned
        self.assertEqual(service_item.raw_footer, ['My Song', 'My copyright', 'CCLI License: 1234'],
                         'The array should be returned correctly with a song, an author, copyright and ccli')

        # WHEN: I amend the CCLI value
        Settings().setValue('core/ccli number', '4321')
        self.media_item.generate_footer(service_item, mock_song)

        # THEN: I would get an amended footer string
        self.assertEqual(service_item.raw_footer, ['My Song', 'My copyright', 'CCLI License: 4321'],
                         'The array should be returned correctly with a song, an author, copyright and amended ccli')

    def test_build_song_footer_base_songbook(self):
        """
        Test build songs footer with basic song and multiple songbooks
        """
        # GIVEN: A Song and a Service Item
        song = Song()
        song.title = 'My Song'
        song.copyright = 'My copyright'
        song.authors_songs = []
        song.songbook_entries = []
        song.ccli_number = ''
        book1 = MagicMock()
        book1.name = "My songbook"
        book2 = MagicMock()
        book2.name = "Thy songbook"
        song.songbookentries = []
        song.add_songbook_entry(book1, '12')
        song.add_songbook_entry(book2, '502A')
        service_item = ServiceItem(None)

        # WHEN: I generate the Footer with default settings
        self.media_item.generate_footer(service_item, song)

        # THEN: The songbook should not be in the footer
        self.assertEqual(service_item.raw_footer, ['My Song', 'My copyright'])

        # WHEN: I activate the "display songbook" option
        self.media_item.display_songbook = True
        self.media_item.generate_footer(service_item, song)

        # THEN: The songbook should be in the footer
        self.assertEqual(service_item.raw_footer, ['My Song', 'My copyright', 'My songbook #12, Thy songbook #502A'])

    def test_build_song_footer_copyright_enabled(self):
        """
        Test building song footer with displaying the copyright symbol
        """
        # GIVEN: A Song and a Service Item; displaying the copyright symbol is enabled
        self.media_item.display_copyright_symbol = True
        mock_song = MagicMock()
        mock_song.title = 'My Song'
        mock_song.copyright = 'My copyright'
        service_item = ServiceItem(None)

        # WHEN: I generate the Footer with default settings
        self.media_item.generate_footer(service_item, mock_song)

        # THEN: The copyright symbol should be in the footer
        self.assertEqual(service_item.raw_footer, ['My Song', '© My copyright'])

    def test_build_song_footer_copyright_disabled(self):
        """
        Test building song footer without displaying the copyright symbol
        """
        # GIVEN: A Song and a Service Item; displaying the copyright symbol should be disabled by default
        mock_song = MagicMock()
        mock_song.title = 'My Song'
        mock_song.copyright = 'My copyright'
        service_item = ServiceItem(None)

        # WHEN: I generate the Footer with default settings
        self.media_item.generate_footer(service_item, mock_song)

        # THEN: The copyright symbol should not be in the footer
        self.assertEqual(service_item.raw_footer, ['My Song', 'My copyright'])

    def test_authors_match(self):
        """
        Test the author matching when importing a song from a service
        """
        # GIVEN: A song and a string with authors
        song = MagicMock()
        song.authors = []
        author = MagicMock()
        author.display_name = "Hans Wurst"
        song.authors.append(author)
        author2 = MagicMock()
        author2.display_name = "Max Mustermann"
        song.authors.append(author2)
        # There are occasions where an author appears twice in a song (with different types).
        # We need to make sure that this case works (lp#1313538)
        author3 = MagicMock()
        author3.display_name = "Max Mustermann"
        song.authors.append(author3)
        authors_str = "Hans Wurst, Max Mustermann, Max Mustermann"

        # WHEN: Checking for matching
        result = self.media_item._authors_match(song, authors_str)

        # THEN: They should match
        self.assertTrue(result, "Authors should match")

    def test_authors_dont_match(self):
        # GIVEN: A song and a string with authors
        song = MagicMock()
        song.authors = []
        author = MagicMock()
        author.display_name = "Hans Wurst"
        song.authors.append(author)
        author2 = MagicMock()
        author2.display_name = "Max Mustermann"
        song.authors.append(author2)
        # There are occasions where an author appears twice in a song (with different types).
        # We need to make sure that this case works (lp#1313538)
        author3 = MagicMock()
        author3.display_name = "Max Mustermann"
        song.authors.append(author3)

        # WHEN: An author is missing in the string
        authors_str = "Hans Wurst, Max Mustermann"
        result = self.media_item._authors_match(song, authors_str)

        # THEN: They should not match
        self.assertFalse(result, "Authors should not match")

    def test_build_remote_search(self):
        """
        Test results for the remote search api
        """
        # GIVEN: A Song and a search a JSON array should be returned.
        mock_song = MagicMock()
        mock_song.id = 123
        mock_song.title = 'My Song'
        mock_song.search_title = 'My Song'
        mock_song.alternate_title = 'My alternative'
        self.media_item.search_entire = MagicMock()
        self.media_item.search_entire.return_value = [mock_song]

        # WHEN: I process a search
        search_results = self.media_item.search('My Song', False)

        # THEN: The correct formatted results are returned
        self.assertEqual(search_results, [[123, 'My Song', 'My alternative']])
