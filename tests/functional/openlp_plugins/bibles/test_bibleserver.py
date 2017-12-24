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
This module contains tests for the http module of the Bibles plugin.
"""
from unittest import TestCase
from unittest.mock import patch, MagicMock

from bs4 import BeautifulSoup

from openlp.plugins.bibles.lib.importers.http import BSExtract


class TestBSExtract(TestCase):
    """
    Test the BSExtractClass
    """
    def setUp(self):
        self.get_soup_for_bible_ref_patcher = patch('openlp.plugins.bibles.lib.importers.http.get_soup_for_bible_ref')
        self.log_patcher = patch('openlp.plugins.bibles.lib.importers.http.log')
        self.send_error_message_patcher = patch('openlp.plugins.bibles.lib.importers.http.send_error_message')
        self.socket_patcher = patch('openlp.plugins.bibles.lib.importers.http.socket')
        self.urllib_patcher = patch('openlp.plugins.bibles.lib.importers.http.urllib')

        self.mock_get_soup_for_bible_ref = self.get_soup_for_bible_ref_patcher.start()
        self.mock_log = self.log_patcher.start()
        self.mock_send_error_message = self.send_error_message_patcher.start()
        self.mock_socket = self.socket_patcher.start()
        self.mock_soup = MagicMock()
        self.mock_urllib = self.urllib_patcher.start()

    def tearDown(self):
        self.get_soup_for_bible_ref_patcher.stop()
        self.log_patcher.stop()
        self.send_error_message_patcher.stop()
        self.socket_patcher.stop()
        self.urllib_patcher.stop()

    def test_get_books_from_http_no_soup(self):
        """
        Test the get_books_from_http method when get_soup_for_bible_ref returns a falsey value
        """
        # GIVEN: An instance of BSExtract, and reset log, urllib & get_soup_for_bible_ref mocks
        instance = BSExtract()
        self.mock_log.debug.reset_mock()
        self.mock_urllib.reset_mock()
        self.mock_get_soup_for_bible_ref.reset_mock()

        # WHEN: get_books_from_http is called with 'NIV' and get_soup_for_bible_ref returns a None value
        self.mock_urllib.parse.quote.return_value = 'NIV'
        self.mock_get_soup_for_bible_ref.return_value = None
        result = instance.get_books_from_http('NIV')

        # THEN: The rest mocks should be called with known values and get_books_from_http should return None
        self.mock_log.debug.assert_called_once_with('BSExtract.get_books_from_http("{book}")'.format(book='NIV'))
        self.mock_urllib.parse.quote.assert_called_once_with(b'NIV')
        self.mock_get_soup_for_bible_ref.assert_called_once_with(
            'http://m.bibleserver.com/overlay/selectBook?translation=NIV')
        assert result is None, \
            'BSExtract.get_books_from_http should return None when get_soup_for_bible_ref returns a false value'

    def test_get_books_from_http_no_content(self):
        """
        Test the get_books_from_http method when the specified element cannot be found in the tag object returned from
        get_soup_for_bible_ref
        """
        # GIVEN: An instance of BSExtract, and reset log, urllib, get_soup_for_bible_ref & soup mocks
        instance = BSExtract()
        self.mock_log.reset_mock()
        self.mock_urllib.reset_mock()
        self.mock_get_soup_for_bible_ref.reset_mock()
        self.mock_soup.reset_mock()

        # WHEN: get_books_from_http is called with 'NIV', get_soup_for_bible_ref returns a mocked_soup object and
        #       mocked_soup.find returns None
        self.mock_urllib.parse.quote.return_value = 'NIV'
        self.mock_soup.find.return_value = None
        self.mock_get_soup_for_bible_ref.return_value = self.mock_soup
        result = instance.get_books_from_http('NIV')

        # THEN: The rest mocks should be called with known values and get_books_from_http should return None
        self.mock_log.debug.assert_called_once_with('BSExtract.get_books_from_http("{book}")'.format(book='NIV'))
        self.mock_urllib.parse.quote.assert_called_once_with(b'NIV')
        self.mock_get_soup_for_bible_ref.assert_called_once_with(
            'http://m.bibleserver.com/overlay/selectBook?translation=NIV')
        self.mock_soup.find.assert_called_once_with('ul')
        self.mock_log.error.assert_called_once_with('No books found in the Bibleserver response.')
        self.mock_send_error_message.assert_called_once_with('parse')
        assert result is None, \
            'BSExtract.get_books_from_http should return None when get_soup_for_bible_ref returns a false value'

    def test_get_books_from_http_content(self):
        """
        Test the get_books_from_http method with sample HTML
        Also a regression test for bug #1184869. (The anchor tag in the second list item is empty)
        """
        # GIVEN: An instance of BSExtract, and reset log, urllib & get_soup_for_bible_ref mocks and sample HTML data
        self.test_html = '<ul><li><a href="/overlay/selectChapter?tocBook=1">Genesis</a></li>' \
            '<li><a href="/overlay/selectChapter?tocBook=2"></a></li>' \
            '<li><a href="/overlay/selectChapter?tocBook=3">Leviticus</a></li></ul>'
        self.test_soup = BeautifulSoup(self.test_html, 'lxml')
        instance = BSExtract()
        self.mock_log.reset_mock()
        self.mock_urllib.reset_mock()
        self.mock_get_soup_for_bible_ref.reset_mock()
        self.mock_send_error_message.reset_mock()

        # WHEN: get_books_from_http is called with 'NIV' and get_soup_for_bible_ref returns tag object based on the
        #       supplied test data.
        self.mock_urllib.parse.quote.return_value = 'NIV'
        self.mock_get_soup_for_bible_ref.return_value = self.test_soup
        result = instance.get_books_from_http('NIV')

        # THEN: The rest mocks should be called with known values and get_books_from_http should return the two books
        #       in the test data
        self.mock_log.debug.assert_called_once_with('BSExtract.get_books_from_http("{book}")'.format(book='NIV'))
        self.mock_urllib.parse.quote.assert_called_once_with(b'NIV')
        self.mock_get_soup_for_bible_ref.assert_called_once_with(
            'http://m.bibleserver.com/overlay/selectBook?translation=NIV')
        assert self.mock_log.error.called is False, 'log.error should not have been called'
        assert self.mock_send_error_message.called is False, 'send_error_message should not have been called'
        assert result == ['Genesis', 'Leviticus']
