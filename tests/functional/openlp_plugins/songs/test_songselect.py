# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4
# pylint: disable=protected-access

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
This module contains tests for the CCLI SongSelect importer.
"""
from unittest import TestCase
from unittest.mock import MagicMock, patch, call
from urllib.error import URLError

from PyQt5 import QtWidgets

from openlp.core.common.registry import Registry
from openlp.plugins.songs.forms.songselectform import SongSelectForm, SearchWorker
from openlp.plugins.songs.lib import Song
from openlp.plugins.songs.lib.songselect import SongSelectImport, LOGOUT_URL, BASE_URL
from tests.helpers.songfileimport import SongImportTestHelper
from tests.helpers.testmixin import TestMixin
from tests.utils.constants import RESOURCE_PATH

TEST_PATH = RESOURCE_PATH / 'songs' / 'songselect'


class TestSongSelectImport(TestCase, TestMixin):
    """
    Test the :class:`~openlp.plugins.songs.lib.songselect.SongSelectImport` class
    """
    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    def test_constructor(self, mocked_build_opener):
        """
        Test that constructing a basic SongSelectImport object works correctly
        """
        # GIVEN: The SongSelectImporter class and a mocked out build_opener
        # WHEN: An object is instantiated
        importer = SongSelectImport(None)

        # THEN: The object should have the correct properties
        assert importer.db_manager is None, 'The db_manager should be None'
        assert importer.html_parser is not None, 'There should be a valid html_parser object'
        assert importer.opener is not None, 'There should be a valid opener object'
        assert 1 == mocked_build_opener.call_count, 'The build_opener method should have been called once'

    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    @patch('openlp.plugins.songs.lib.songselect.BeautifulSoup')
    def test_login_fails(self, MockedBeautifulSoup, mocked_build_opener):
        """
        Test that when logging in to SongSelect fails, the login method returns False
        """
        # GIVEN: A bunch of mocked out stuff and an importer object
        mocked_opener = MagicMock()
        mocked_build_opener.return_value = mocked_opener
        mocked_login_page = MagicMock()
        mocked_login_page.find.side_effect = [{'value': 'blah'}, None]
        mocked_posted_page = MagicMock()
        mocked_posted_page.find.return_value = None
        MockedBeautifulSoup.side_effect = [mocked_login_page, mocked_posted_page]
        mock_callback = MagicMock()
        importer = SongSelectImport(None)

        # WHEN: The login method is called after being rigged to fail
        result = importer.login('username', 'password', mock_callback)

        # THEN: callback was called 3 times, open was called twice, find was called twice, and False was returned
        assert 3 == mock_callback.call_count, 'callback should have been called 3 times'
        assert 2 == mocked_login_page.find.call_count, 'find should have been called twice'
        assert 1 == mocked_posted_page.find.call_count, 'find should have been called once'
        assert 2 == mocked_opener.open.call_count, 'opener should have been called twice'
        assert result is False, 'The login method should have returned False'

    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    def test_login_except(self, mocked_build_opener):
        """
        Test that when logging in to SongSelect fails, the login method raises URLError
        """
        # GIVEN: A bunch of mocked out stuff and an importer object
        mocked_build_opener.open.side_effect = URLError('Fake URLError')
        mock_callback = MagicMock()
        importer = SongSelectImport(None)

        # WHEN: The login method is called after being rigged to fail
        result = importer.login('username', 'password', mock_callback)

        # THEN: callback was called 1 time and False was returned
        assert 1 == mock_callback.call_count, 'callback should have been called 1 times'
        assert result is False, 'The login method should have returned False'

    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    @patch('openlp.plugins.songs.lib.songselect.BeautifulSoup')
    def test_login_succeeds(self, MockedBeautifulSoup, mocked_build_opener):
        """
        Test that when logging in to SongSelect succeeds, the login method returns True
        """
        # GIVEN: A bunch of mocked out stuff and an importer object
        mocked_opener = MagicMock()
        mocked_build_opener.return_value = mocked_opener
        mocked_login_page = MagicMock()
        mocked_login_page.find.side_effect = [{'value': 'blah'}, None]
        mocked_posted_page = MagicMock()
        mocked_posted_page.find.return_value = MagicMock()
        MockedBeautifulSoup.side_effect = [mocked_login_page, mocked_posted_page]
        mock_callback = MagicMock()
        importer = SongSelectImport(None)

        # WHEN: The login method is called after being rigged to fail
        result = importer.login('username', 'password', mock_callback)

        # THEN: callback was called 3 times, open was called twice, find was called twice, and True was returned
        assert 3 == mock_callback.call_count, 'callback should have been called 3 times'
        assert 2 == mocked_login_page.find.call_count, 'find should have been called twice on the login page'
        assert 1 == mocked_posted_page.find.call_count, 'find should have been called once on the posted page'
        assert 2 == mocked_opener.open.call_count, 'opener should have been called twice'
        assert result is True, 'The login method should have returned True'

    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    @patch('openlp.plugins.songs.lib.songselect.BeautifulSoup')
    def test_login_url_from_form(self, MockedBeautifulSoup, mocked_build_opener):
        """
        Test that the login URL is from the form
        """
        # GIVEN: A bunch of mocked out stuff and an importer object
        mocked_opener = MagicMock()
        mocked_build_opener.return_value = mocked_opener
        mocked_form = MagicMock()
        mocked_form.attrs = {'action': 'do/login'}
        mocked_login_page = MagicMock()
        mocked_login_page.find.side_effect = [{'value': 'blah'}, mocked_form]
        mocked_posted_page = MagicMock()
        mocked_posted_page.find.return_value = MagicMock()
        MockedBeautifulSoup.side_effect = [mocked_login_page, mocked_posted_page]
        mock_callback = MagicMock()
        importer = SongSelectImport(None)

        # WHEN: The login method is called after being rigged to fail
        result = importer.login('username', 'password', mock_callback)

        # THEN: callback was called 3 times, open was called twice, find was called twice, and True was returned
        assert 3 == mock_callback.call_count, 'callback should have been called 3 times'
        assert 2 == mocked_login_page.find.call_count, 'find should have been called twice on the login page'
        assert 1 == mocked_posted_page.find.call_count, 'find should have been called once on the posted page'
        assert 'https://profile.ccli.com/do/login', mocked_opener.open.call_args_list[1][0][0]
        assert result is True, 'The login method should have returned True'

    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    def test_logout(self, mocked_build_opener):
        """
        Test that when the logout method is called, it logs the user out of SongSelect
        """
        # GIVEN: A bunch of mocked out stuff and an importer object
        mocked_opener = MagicMock()
        mocked_build_opener.return_value = mocked_opener
        importer = SongSelectImport(None)

        # WHEN: The login method is called after being rigged to fail
        importer.logout()

        # THEN: The opener is called once with the logout url
        assert 1 == mocked_opener.open.call_count, 'opener should have been called once'
        mocked_opener.open.assert_called_with(LOGOUT_URL)

    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    @patch('openlp.plugins.songs.lib.songselect.BeautifulSoup')
    def test_search_returns_no_results(self, MockedBeautifulSoup, mocked_build_opener):
        """
        Test that when the search finds no results, it simply returns an empty list
        """
        # GIVEN: A bunch of mocked out stuff and an importer object
        mocked_opener = MagicMock()
        mocked_build_opener.return_value = mocked_opener
        mocked_results_page = MagicMock()
        mocked_results_page.find_all.return_value = []
        MockedBeautifulSoup.return_value = mocked_results_page
        mock_callback = MagicMock()
        importer = SongSelectImport(None)

        # WHEN: The login method is called after being rigged to fail
        results = importer.search('text', 1000, mock_callback)

        # THEN: callback was never called, open was called once, find_all was called once, an empty list returned
        assert 0 == mock_callback.call_count, 'callback should not have been called'
        assert 1 == mocked_opener.open.call_count, 'open should have been called once'
        assert 1 == mocked_results_page.find_all.call_count, 'find_all should have been called once'
        mocked_results_page.find_all.assert_called_with('div', 'song-result')
        assert [] == results, 'The search method should have returned an empty list'

    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    @patch('openlp.plugins.songs.lib.songselect.BeautifulSoup')
    def test_search_returns_two_results(self, MockedBeautifulSoup, mocked_build_opener):
        """
        Test that when the search finds 2 results, it simply returns a list with 2 results
        """
        # GIVEN: A bunch of mocked out stuff and an importer object
        # first search result
        mocked_result1 = MagicMock()
        mocked_result1.find.side_effect = [
            MagicMock(find=MagicMock(return_value=MagicMock(string='Title 1'))),
            MagicMock(string='James, John'),
            MagicMock(find=MagicMock(return_value={'href': '/url1'}))
        ]
        # second search result
        mocked_result2 = MagicMock()
        mocked_result2.find.side_effect = [
            MagicMock(find=MagicMock(return_value=MagicMock(string='Title 2'))),
            MagicMock(string='Philip'),
            MagicMock(find=MagicMock(return_value={'href': '/url2'}))
        ]
        # rest of the stuff
        mocked_opener = MagicMock()
        mocked_build_opener.return_value = mocked_opener
        mocked_results_page = MagicMock()
        mocked_results_page.find_all.side_effect = [[mocked_result1, mocked_result2], []]
        MockedBeautifulSoup.return_value = mocked_results_page
        mock_callback = MagicMock()
        importer = SongSelectImport(None)

        # WHEN: The search method is called
        results = importer.search('text', 1000, mock_callback)

        # THEN: callback was never called, open was called once, find_all was called once, an empty list returned
        assert 2 == mock_callback.call_count, 'callback should have been called twice'
        assert 2 == mocked_opener.open.call_count, 'open should have been called twice'
        assert 2 == mocked_results_page.find_all.call_count, 'find_all should have been called twice'
        mocked_results_page.find_all.assert_called_with('div', 'song-result')
        expected_list = [
            {'title': 'Title 1', 'authors': ['James', 'John'], 'link': BASE_URL + '/url1'},
            {'title': 'Title 2', 'authors': ['Philip'], 'link': BASE_URL + '/url2'}
        ]
        assert expected_list == results, 'The search method should have returned two songs'

    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    @patch('openlp.plugins.songs.lib.songselect.BeautifulSoup')
    def test_search_reaches_max_results(self, MockedBeautifulSoup, mocked_build_opener):
        """
        Test that when the search finds MAX (2) results, it simply returns a list with those (2)
        """
        # GIVEN: A bunch of mocked out stuff and an importer object
        # first search result
        mocked_result1 = MagicMock()
        mocked_result1.find.side_effect = [
            MagicMock(find=MagicMock(return_value=MagicMock(string='Title 1'))),
            MagicMock(string='James, John'),
            MagicMock(find=MagicMock(return_value={'href': '/url1'}))
        ]
        # second search result
        mocked_result2 = MagicMock()
        mocked_result2.find.side_effect = [
            MagicMock(find=MagicMock(return_value=MagicMock(string='Title 2'))),
            MagicMock(string='Philip'),
            MagicMock(find=MagicMock(return_value={'href': '/url2'}))
        ]
        # third search result
        mocked_result3 = MagicMock()
        mocked_result3.find.side_effect = [
            MagicMock(find=MagicMock(return_value=MagicMock(string='Title 3'))),
            MagicMock(string='Luke, Matthew'),
            MagicMock(find=MagicMock(return_value={'href': '/url3'}))
        ]
        # rest of the stuff
        mocked_opener = MagicMock()
        mocked_build_opener.return_value = mocked_opener
        mocked_results_page = MagicMock()
        mocked_results_page.find_all.side_effect = [[mocked_result1, mocked_result2, mocked_result3], []]
        MockedBeautifulSoup.return_value = mocked_results_page
        mock_callback = MagicMock()
        importer = SongSelectImport(None)

        # WHEN: The search method is called
        results = importer.search('text', 2, mock_callback)

        # THEN: callback was called twice, open was called twice, find_all was called twice, max results returned
        assert 2 == mock_callback.call_count, 'callback should have been called twice'
        assert 2 == mocked_opener.open.call_count, 'open should have been called twice'
        assert 2 == mocked_results_page.find_all.call_count, 'find_all should have been called twice'
        mocked_results_page.find_all.assert_called_with('div', 'song-result')
        expected_list = [{'title': 'Title 1', 'authors': ['James', 'John'], 'link': BASE_URL + '/url1'},
                         {'title': 'Title 2', 'authors': ['Philip'], 'link': BASE_URL + '/url2'}]
        assert expected_list == results, 'The search method should have returned two songs'

    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    @patch('openlp.plugins.songs.lib.songselect.BeautifulSoup')
    def test_stop_called(self, MockedBeautifulSoup, mocked_build_opener):
        """
        Test that the search is stopped with stop() is called
        """
        # GIVEN: An importer object that is currently "searching"
        importer = SongSelectImport(None)
        importer.run_search = True

        # WHEN: The stop method is called
        importer.stop()

        # THEN: Searching should have stopped
        assert importer.run_search is False, 'Searching should have been stopped'

    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    def test_get_song_page_raises_exception(self, mocked_build_opener):
        """
        Test that when BeautifulSoup gets a bad song page the get_song() method returns None
        """
        # GIVEN: A bunch of mocked out stuff and an importer object
        mocked_opener = MagicMock()
        mocked_build_opener.return_value = mocked_opener
        mocked_opener.open.read.side_effect = URLError('[Errno -2] Name or service not known')
        mocked_callback = MagicMock()
        importer = SongSelectImport(None)

        # WHEN: get_song is called
        result = importer.get_song({'link': 'link'}, callback=mocked_callback)

        # THEN: The callback should have been called once and None should be returned
        mocked_callback.assert_called_with()
        assert result is None, 'The get_song() method should have returned None'

    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    @patch('openlp.plugins.songs.lib.songselect.BeautifulSoup')
    def test_get_song_lyrics_raise_exception(self, MockedBeautifulSoup, mocked_build_opener):
        """
        Test that when BeautifulSoup gets a bad lyrics page the get_song() method returns None
        """
        # GIVEN: A bunch of mocked out stuff and an importer object
        MockedBeautifulSoup.side_effect = [None, TypeError('Test Error')]
        mocked_callback = MagicMock()
        importer = SongSelectImport(None)

        # WHEN: get_song is called
        result = importer.get_song({'link': 'link'}, callback=mocked_callback)

        # THEN: The callback should have been called twice and None should be returned
        assert 2 == mocked_callback.call_count, 'The callback should have been called twice'
        assert result is None, 'The get_song() method should have returned None'

    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    @patch('openlp.plugins.songs.lib.songselect.BeautifulSoup')
    def test_get_song(self, MockedBeautifulSoup, mocked_build_opener):
        """
        Test that the get_song() method returns the correct song details
        """
        # GIVEN: A bunch of mocked out stuff and an importer object
        mocked_song_page = MagicMock()
        mocked_copyright = MagicMock()
        mocked_copyright.find_all.return_value = [MagicMock(string='Copyright 1'), MagicMock(string='Copyright 2')]
        mocked_song_page.find.side_effect = [
            mocked_copyright,
            MagicMock(find=MagicMock(string='CCLI: 123456'))
        ]
        mocked_lyrics_page = MagicMock()
        mocked_find_all = MagicMock()
        mocked_find_all.side_effect = [
            [
                MagicMock(contents='The Lord told Noah: there\'s gonna be a floody, floody'),
                MagicMock(contents='So, rise and shine, and give God the glory, glory'),
                MagicMock(contents='The Lord told Noah to build him an arky, arky')
            ],
            [MagicMock(string='Verse 1'), MagicMock(string='Chorus'), MagicMock(string='Verse 2')]
        ]
        mocked_lyrics_page.find.return_value = MagicMock(find_all=mocked_find_all)
        MockedBeautifulSoup.side_effect = [mocked_song_page, mocked_lyrics_page]
        mocked_callback = MagicMock()
        importer = SongSelectImport(None)
        fake_song = {'title': 'Title', 'authors': ['Author 1', 'Author 2'], 'link': 'url'}

        # WHEN: get_song is called
        result = importer.get_song(fake_song, callback=mocked_callback)

        # THEN: The callback should have been called three times and the song should be returned
        assert 3 == mocked_callback.call_count, 'The callback should have been called twice'
        assert result is not None, 'The get_song() method should have returned a song dictionary'
        assert 2 == mocked_lyrics_page.find.call_count, 'The find() method should have been called twice'
        assert 2 == mocked_find_all.call_count, 'The find_all() method should have been called twice'
        assert [call('div', 'song-viewer lyrics'), call('div', 'song-viewer lyrics')] == \
            mocked_lyrics_page.find.call_args_list, 'The find() method should have been called with the right arguments'
        assert [call('p'), call('h3')] == mocked_find_all.call_args_list, \
            'The find_all() method should have been called with the right arguments'
        assert 'copyright' in result, 'The returned song should have a copyright'
        assert 'ccli_number' in result, 'The returned song should have a CCLI number'
        assert 'verses' in result, 'The returned song should have verses'
        assert 3 == len(result['verses']), 'Three verses should have been returned'

    @patch('openlp.plugins.songs.lib.songselect.clean_song')
    @patch('openlp.plugins.songs.lib.songselect.Topic')
    @patch('openlp.plugins.songs.lib.songselect.Author')
    def test_save_song_new_author(self, MockedAuthor, MockedTopic, mocked_clean_song):
        """
        Test that saving a song with a new author performs the correct actions
        """
        # GIVEN: A song to save, and some mocked out objects
        song_dict = {
            'title': 'Arky Arky',
            'authors': ['Public Domain'],
            'verses': [
                {'label': 'Verse 1', 'lyrics': 'The Lord told Noah: there\'s gonna be a floody, floody'},
                {'label': 'Chorus 1', 'lyrics': 'So, rise and shine, and give God the glory, glory'},
                {'label': 'Verse 2', 'lyrics': 'The Lord told Noah to build him an arky, arky'}
            ],
            'copyright': 'Public Domain',
            'ccli_number': '123456'
        }
        MockedAuthor.display_name.__eq__.return_value = False
        MockedTopic.name.__eq__.return_value = False
        mocked_db_manager = MagicMock()
        mocked_db_manager.get_object_filtered.return_value = None
        importer = SongSelectImport(mocked_db_manager)

        # WHEN: The song is saved to the database
        result = importer.save_song(song_dict)

        # THEN: The return value should be a Song class and the mocked_db_manager should have been called
        assert isinstance(result, Song), 'The returned value should be a Song object'
        mocked_clean_song.assert_called_with(mocked_db_manager, result)
        assert 2 == mocked_db_manager.save_object.call_count, \
            'The save_object() method should have been called twice'
        mocked_db_manager.get_object_filtered.assert_called_with(MockedAuthor, False)
        MockedAuthor.populate.assert_called_with(first_name='Public', last_name='Domain', display_name='Public Domain')
        assert 1 == len(result.authors_songs), 'There should only be one author'

    @patch('openlp.plugins.songs.lib.songselect.clean_song')
    @patch('openlp.plugins.songs.lib.songselect.Author')
    def test_save_song_existing_author(self, MockedAuthor, mocked_clean_song):
        """
        Test that saving a song with an existing author performs the correct actions
        """
        # GIVEN: A song to save, and some mocked out objects
        song_dict = {
            'title': 'Arky Arky',
            'authors': ['Public Domain'],
            'verses': [
                {'label': 'Verse 1', 'lyrics': 'The Lord told Noah: there\'s gonna be a floody, floody'},
                {'label': 'Chorus 1', 'lyrics': 'So, rise and shine, and give God the glory, glory'},
                {'label': 'Verse 2', 'lyrics': 'The Lord told Noah to build him an arky, arky'}
            ],
            'copyright': 'Public Domain',
            'ccli_number': '123456'
        }
        MockedAuthor.display_name.__eq__.return_value = False
        mocked_db_manager = MagicMock()
        mocked_db_manager.get_object_filtered.return_value = MagicMock()
        importer = SongSelectImport(mocked_db_manager)

        # WHEN: The song is saved to the database
        result = importer.save_song(song_dict)

        # THEN: The return value should be a Song class and the mocked_db_manager should have been called
        assert isinstance(result, Song), 'The returned value should be a Song object'
        mocked_clean_song.assert_called_with(mocked_db_manager, result)
        assert 2 == mocked_db_manager.save_object.call_count, \
            'The save_object() method should have been called twice'
        mocked_db_manager.get_object_filtered.assert_called_with(MockedAuthor, False)
        assert 0 == MockedAuthor.populate.call_count, 'A new author should not have been instantiated'
        assert 1 == len(result.authors_songs), 'There should only be one author'

    @patch('openlp.plugins.songs.lib.songselect.clean_song')
    @patch('openlp.plugins.songs.lib.songselect.Author')
    def test_save_song_unknown_author(self, MockedAuthor, mocked_clean_song):
        """
        Test that saving a song with an author name of only one word performs the correct actions
        """
        # GIVEN: A song to save, and some mocked out objects
        song_dict = {
            'title': 'Arky Arky',
            'authors': ['Unknown'],
            'verses': [
                {'label': 'Verse 1', 'lyrics': 'The Lord told Noah: there\'s gonna be a floody, floody'},
                {'label': 'Chorus 1', 'lyrics': 'So, rise and shine, and give God the glory, glory'},
                {'label': 'Verse 2', 'lyrics': 'The Lord told Noah to build him an arky, arky'}
            ],
            'copyright': 'Public Domain',
            'ccli_number': '123456'
        }
        MockedAuthor.display_name.__eq__.return_value = False
        mocked_db_manager = MagicMock()
        mocked_db_manager.get_object_filtered.return_value = None
        importer = SongSelectImport(mocked_db_manager)

        # WHEN: The song is saved to the database
        result = importer.save_song(song_dict)

        # THEN: The return value should be a Song class and the mocked_db_manager should have been called
        assert isinstance(result, Song), 'The returned value should be a Song object'
        mocked_clean_song.assert_called_with(mocked_db_manager, result)
        assert 2 == mocked_db_manager.save_object.call_count, \
            'The save_object() method should have been called twice'
        mocked_db_manager.get_object_filtered.assert_called_with(MockedAuthor, False)
        MockedAuthor.populate.assert_called_with(first_name='Unknown', last_name='', display_name='Unknown')
        assert 1 == len(result.authors_songs), 'There should only be one author'


class TestSongSelectForm(TestCase, TestMixin):
    """
    Test the :class:`~openlp.plugins.songs.forms.songselectform.SongSelectForm` class
    """
    def setUp(self):
        """
        Some set up for this test suite
        """
        self.setup_application()
        self.app.setApplicationVersion('0.0')
        self.app.process_events = lambda: None
        Registry.create()
        Registry().register('application', self.app)

    def test_create_form(self):
        """
        Test that we can create the SongSelect form
        """
        # GIVEN: The SongSelectForm class and a mocked db manager
        mocked_plugin = MagicMock()
        mocked_db_manager = MagicMock()

        # WHEN: We create an instance
        ssform = SongSelectForm(None, mocked_plugin, mocked_db_manager)

        # THEN: The correct properties should have been assigned
        assert mocked_plugin == ssform.plugin, 'The correct plugin should have been assigned'
        assert mocked_db_manager == ssform.db_manager, 'The correct db_manager should have been assigned'

    @patch('openlp.plugins.songs.forms.songselectform.SongSelectImport')
    @patch('openlp.plugins.songs.forms.songselectform.QtWidgets.QMessageBox.critical')
    @patch('openlp.plugins.songs.forms.songselectform.translate')
    def test_login_fails(self, mocked_translate, mocked_critical, MockedSongSelectImport):
        """
        Test that when the login fails, the form returns to the correct state
        """
        # GIVEN: A valid SongSelectForm with a mocked out SongSelectImport, and a bunch of mocked out controls
        mocked_song_select_import = MagicMock()
        mocked_song_select_import.login.return_value = False
        MockedSongSelectImport.return_value = mocked_song_select_import
        mocked_translate.side_effect = lambda *args: args[1]
        ssform = SongSelectForm(None, MagicMock(), MagicMock())
        ssform.initialise()
        with patch.object(ssform, 'username_edit') as mocked_username_edit, \
                patch.object(ssform, 'password_edit') as mocked_password_edit, \
                patch.object(ssform, 'save_password_checkbox') as mocked_save_password_checkbox, \
                patch.object(ssform, 'login_button') as mocked_login_button, \
                patch.object(ssform, 'login_spacer') as mocked_login_spacer, \
                patch.object(ssform, 'login_progress_bar') as mocked_login_progress_bar, \
                patch.object(ssform.application, 'process_events') as mocked_process_events:

            # WHEN: The login button is clicked, and the login is rigged to fail
            ssform.on_login_button_clicked()

            # THEN: The right things should have happened in the right order
            expected_username_calls = [call(False), call(True)]
            expected_password_calls = [call(False), call(True)]
            expected_save_password_calls = [call(False), call(True)]
            expected_login_btn_calls = [call(False), call(True)]
            expected_login_spacer_calls = [call(False), call(True)]
            expected_login_progress_visible_calls = [call(True), call(False)]
            expected_login_progress_value_calls = [call(0), call(0)]
            assert expected_username_calls == mocked_username_edit.setEnabled.call_args_list, \
                'The username edit should be disabled then enabled'
            assert expected_password_calls == mocked_password_edit.setEnabled.call_args_list, \
                'The password edit should be disabled then enabled'
            assert expected_save_password_calls == mocked_save_password_checkbox.setEnabled.call_args_list, \
                'The save password checkbox should be disabled then enabled'
            assert expected_login_btn_calls == mocked_login_button.setEnabled.call_args_list, \
                'The login button should be disabled then enabled'
            assert expected_login_spacer_calls == mocked_login_spacer.setVisible.call_args_list, \
                'Thee login spacer should be make invisible, then visible'
            assert expected_login_progress_visible_calls == mocked_login_progress_bar.setVisible.call_args_list, \
                'Thee login progress bar should be make visible, then invisible'
            assert expected_login_progress_value_calls == mocked_login_progress_bar.setValue.call_args_list, \
                'Thee login progress bar should have the right values set'
            assert 2 == mocked_process_events.call_count, 'The process_events() method should be called twice'
            mocked_critical.assert_called_with(ssform, 'Error Logging In', 'There was a problem logging in, '
                                                                           'perhaps your username or password is '
                                                                           'incorrect?')

    @patch('openlp.plugins.songs.forms.songselectform.QtWidgets.QMessageBox.question')
    @patch('openlp.plugins.songs.forms.songselectform.translate')
    def test_on_import_yes_clicked(self, mocked_translate, mocked_question):
        """
        Test that when a song is imported and the user clicks the "yes" button, the UI goes back to the previous page
        """
        # GIVEN: A valid SongSelectForm with a mocked out QMessageBox.question() method
        mocked_translate.side_effect = lambda *args: args[1]
        mocked_question.return_value = QtWidgets.QMessageBox.Yes
        ssform = SongSelectForm(None, MagicMock(), MagicMock())
        mocked_song_select_importer = MagicMock()
        ssform.song_select_importer = mocked_song_select_importer
        ssform.song = None

        # WHEN: The import button is clicked, and the user clicks Yes
        with patch.object(ssform, 'on_back_button_clicked') as mocked_on_back_button_clicked:
            ssform.on_import_button_clicked()

        # THEN: The on_back_button_clicked() method should have been called
        mocked_song_select_importer.save_song.assert_called_with(None)
        mocked_question.assert_called_with(ssform, 'Song Imported',
                                           'Your song has been imported, would you like to import more songs?',
                                           defaultButton=QtWidgets.QMessageBox.Yes)
        mocked_on_back_button_clicked.assert_called_with()
        assert ssform.song is None

    @patch('openlp.plugins.songs.forms.songselectform.QtWidgets.QMessageBox.question')
    @patch('openlp.plugins.songs.forms.songselectform.translate')
    def test_on_import_no_clicked(self, mocked_translate, mocked_question):
        """
        Test that when a song is imported and the user clicks the "no" button, the UI exits
        """
        # GIVEN: A valid SongSelectForm with a mocked out QMessageBox.question() method
        mocked_translate.side_effect = lambda *args: args[1]
        mocked_question.return_value = QtWidgets.QMessageBox.No
        ssform = SongSelectForm(None, MagicMock(), MagicMock())
        mocked_song_select_importer = MagicMock()
        ssform.song_select_importer = mocked_song_select_importer
        ssform.song = None

        # WHEN: The import button is clicked, and the user clicks Yes
        with patch.object(ssform, 'done') as mocked_done:
            ssform.on_import_button_clicked()

        # THEN: The on_back_button_clicked() method should have been called
        mocked_song_select_importer.save_song.assert_called_with(None)
        mocked_question.assert_called_with(ssform, 'Song Imported',
                                           'Your song has been imported, would you like to import more songs?',
                                           defaultButton=QtWidgets.QMessageBox.Yes)
        mocked_done.assert_called_with(QtWidgets.QDialog.Accepted)
        assert ssform.song is None

    def test_on_back_button_clicked(self):
        """
        Test that when the back button is clicked, the stacked widget is set back one page
        """
        # GIVEN: A SongSelect form
        ssform = SongSelectForm(None, MagicMock(), MagicMock())

        # WHEN: The back button is clicked
        with patch.object(ssform, 'stacked_widget') as mocked_stacked_widget, \
                patch.object(ssform, 'search_combobox') as mocked_search_combobox:
            ssform.on_back_button_clicked()

        # THEN: The stacked widget should be set back one page
        mocked_stacked_widget.setCurrentIndex.assert_called_with(1)
        mocked_search_combobox.setFocus.assert_called_with()

    @patch('openlp.plugins.songs.forms.songselectform.QtWidgets.QMessageBox.information')
    def test_on_search_show_info(self, mocked_information):
        """
        Test that when the search_show_info signal is emitted, the on_search_show_info() method shows a dialog
        """
        # GIVEN: A SongSelect form
        ssform = SongSelectForm(None, MagicMock(), MagicMock())
        expected_title = 'Test Title'
        expected_text = 'This is a test'

        # WHEN: on_search_show_info is called
        ssform.on_search_show_info(expected_title, expected_text)

        # THEN: An information dialog should be shown
        mocked_information.assert_called_with(ssform, expected_title, expected_text)

    def test_update_login_progress(self):
        """
        Test the _update_login_progress() method
        """
        # GIVEN: A SongSelect form
        ssform = SongSelectForm(None, MagicMock(), MagicMock())

        # WHEN: _update_login_progress() is called
        with patch.object(ssform, 'login_progress_bar') as mocked_login_progress_bar:
            mocked_login_progress_bar.value.return_value = 3
            ssform._update_login_progress()

        # THEN: The login progress bar should be updated
        mocked_login_progress_bar.setValue.assert_called_with(4)

    def test_update_song_progress(self):
        """
        Test the _update_song_progress() method
        """
        # GIVEN: A SongSelect form
        ssform = SongSelectForm(None, MagicMock(), MagicMock())

        # WHEN: _update_song_progress() is called
        with patch.object(ssform, 'song_progress_bar') as mocked_song_progress_bar:
            mocked_song_progress_bar.value.return_value = 2
            ssform._update_song_progress()

        # THEN: The song progress bar should be updated
        mocked_song_progress_bar.setValue.assert_called_with(3)

    def test_on_search_results_widget_double_clicked(self):
        """
        Test that a song is retrieved when a song in the results list is double-clicked
        """
        # GIVEN: A SongSelect form
        ssform = SongSelectForm(None, MagicMock(), MagicMock())
        expected_song = {'title': 'Amazing Grace'}

        # WHEN: A song result is double-clicked
        with patch.object(ssform, '_view_song') as mocked_view_song:
            ssform.on_search_results_widget_double_clicked(expected_song)

        # THEN: The song is fetched and shown to the user
        mocked_view_song.assert_called_with(expected_song)

    def test_on_view_button_clicked(self):
        """
        Test that a song is retrieved when the view button is clicked
        """
        # GIVEN: A SongSelect form
        ssform = SongSelectForm(None, MagicMock(), MagicMock())
        expected_song = {'title': 'Amazing Grace'}

        # WHEN: A song result is double-clicked
        with patch.object(ssform, '_view_song') as mocked_view_song, \
                patch.object(ssform, 'search_results_widget') as mocked_search_results_widget:
            mocked_search_results_widget.currentItem.return_value = expected_song
            ssform.on_view_button_clicked()

        # THEN: The song is fetched and shown to the user
        mocked_view_song.assert_called_with(expected_song)

    def test_on_search_results_widget_selection_changed(self):
        """
        Test that the view button is updated when the search results list is changed
        """
        # GIVEN: A SongSelect form
        ssform = SongSelectForm(None, MagicMock(), MagicMock())

        # WHEN: There is at least 1 item selected
        with patch.object(ssform, 'search_results_widget') as mocked_search_results_widget, \
                patch.object(ssform, 'view_button') as mocked_view_button:
            mocked_search_results_widget.selectedItems.return_value = [1]
            ssform.on_search_results_widget_selection_changed()

        # THEN: The view button should be enabled
        mocked_view_button.setEnabled.assert_called_with(True)

    @patch('openlp.plugins.songs.forms.songselectform.SongSelectImport')
    def test_on_stop_button_clicked(self, MockedSongSelectImport):
        """
        Test that the search is stopped when the stop button is clicked
        """
        # GIVEN: A mocked SongSelectImporter and a SongSelect form
        mocked_song_select_importer = MagicMock()
        MockedSongSelectImport.return_value = mocked_song_select_importer
        ssform = SongSelectForm(None, MagicMock(), MagicMock())
        ssform.initialise()

        # WHEN: The stop button is clicked
        ssform.on_stop_button_clicked()

        # THEN: The view button, search box and search button should be enabled
        mocked_song_select_importer.stop.assert_called_with()
        assert ssform.search_button.isEnabled() is True
        assert ssform.search_combobox.isEnabled() is True

    @patch('openlp.plugins.songs.forms.songselectform.Settings')
    @patch('openlp.plugins.songs.forms.songselectform.run_thread')
    @patch('openlp.plugins.songs.forms.songselectform.SearchWorker')
    def test_on_search_button_clicked(self, MockedSearchWorker, mocked_run_thread, MockedSettings):
        """
        Test that search fields are disabled when search button is clicked.
        """
        # GIVEN: A mocked SongSelect form
        ssform = SongSelectForm(None, MagicMock(), MagicMock())
        ssform.initialise()

        # WHEN: The search button is clicked
        ssform.on_search_button_clicked()

        # THEN: The search box and search button should be disabled
        assert ssform.search_button.isEnabled() is False
        assert ssform.search_combobox.isEnabled() is False

    def test_on_search_finished(self):
        """
        Test that search fields are enabled when search is finished.
        """
        # GIVEN: A mocked SongSelect form
        ssform = SongSelectForm(None, MagicMock(), MagicMock())
        ssform.initialise()

        # WHEN: The search is finished
        ssform.on_search_finished()

        # THEN: The search box and search button should be enabled
        assert ssform.search_button.isEnabled() is True
        assert ssform.search_combobox.isEnabled() is True


class TestSongSelectFileImport(SongImportTestHelper):

    def __init__(self, *args, **kwargs):
        self.importer_class_name = 'CCLIFileImport'
        self.importer_module_name = 'cclifile'
        super().__init__(*args, **kwargs)

    def test_song_import(self):
        """
        Test that loading an OpenSong file works correctly on various files
        """
        self.file_import([TEST_PATH / 'TestSong.bin'], self.load_external_result_data(TEST_PATH / 'TestSong-bin.json'))
        self.file_import([TEST_PATH / 'TestSong.txt'], self.load_external_result_data(TEST_PATH / 'TestSong-txt.json'))


class TestSearchWorker(TestCase, TestMixin):
    """
    Test the SearchWorker class
    """
    def test_constructor(self):
        """
        Test the SearchWorker constructor
        """
        # GIVEN: An importer mock object and some search text
        importer = MagicMock()
        search_text = 'Jesus'

        # WHEN: The search worker is created
        worker = SearchWorker(importer, search_text)

        # THEN: The correct values should be set
        assert importer is worker.importer, 'The importer should be the right object'
        assert search_text == worker.search_text, 'The search text should be correct'

    def test_start(self):
        """
        Test the start() method of the SearchWorker class
        """
        # GIVEN: An importer mock object, some search text and an initialised SearchWorker
        importer = MagicMock()
        importer.search.return_value = ['song1', 'song2']
        search_text = 'Jesus'
        worker = SearchWorker(importer, search_text)

        # WHEN: The start() method is called
        with patch.object(worker, 'finished') as mocked_finished, patch.object(worker, 'quit') as mocked_quit:
            worker.start()

        # THEN: The "finished" and "quit" signals should be emitted
        importer.search.assert_called_with(search_text, 1000, worker._found_song_callback)
        mocked_finished.emit.assert_called_with()
        mocked_quit.emit.assert_called_with()

    @patch('openlp.plugins.songs.forms.songselectform.translate')
    def test_start_over_1000_songs(self, mocked_translate):
        """
        Test the start() method of the SearchWorker class when it finds over 1000 songs
        """
        # GIVEN: An importer mock object, some search text and an initialised SearchWorker
        mocked_translate.side_effect = lambda x, y: y
        importer = MagicMock()
        importer.search.return_value = ['song%s' % num for num in range(1050)]
        search_text = 'Jesus'
        worker = SearchWorker(importer, search_text)

        # WHEN: The start() method is called
        with patch.object(worker, 'finished') as mocked_finished, patch.object(worker, 'quit') as mocked_quit, \
                patch.object(worker, 'show_info') as mocked_show_info:
            worker.start()

        # THEN: The "finished" and "quit" signals should be emitted
        importer.search.assert_called_with(search_text, 1000, worker._found_song_callback)
        mocked_show_info.emit.assert_called_with('More than 1000 results', 'Your search has returned more than 1000 '
                                                                           'results, it has been stopped. Please '
                                                                           'refine your search to fetch better '
                                                                           'results.')
        mocked_finished.emit.assert_called_with()
        mocked_quit.emit.assert_called_with()

    def test_found_song_callback(self):
        """
        Test that when the _found_song_callback() function is called, the "found_song" signal is emitted
        """
        # GIVEN: An importer mock object, some search text and an initialised SearchWorker
        importer = MagicMock()
        search_text = 'Jesus'
        song = {'title': 'Amazing Grace'}
        worker = SearchWorker(importer, search_text)

        # WHEN: The start() method is called
        with patch.object(worker, 'found_song') as mocked_found_song:
            worker._found_song_callback(song)                                   # pylint: disable=protected-access

        # THEN: The "found_song" signal should have been emitted
        mocked_found_song.emit.assert_called_with(song)
