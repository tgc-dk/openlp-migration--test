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
Package to test the openlp.core.ui.renderer package.
"""
from unittest import TestCase
from unittest.mock import MagicMock, patch

from PyQt5 import QtCore

from openlp.core.common import Registry
from openlp.core.lib import Renderer, ScreenList, ServiceItem, FormattingTags
from openlp.core.lib.renderer import words_split, get_start_tags
from openlp.core.lib.theme import ThemeXML


SCREEN = {
    'primary': False,
    'number': 1,
    'size': QtCore.QRect(0, 0, 1024, 768)
}


# WARNING: Leave formatting alone - this is how it's returned in renderer.py
CSS_TEST_ONE = """<!DOCTYPE html><html><head><script>
            function show_text(newtext) {
                var main = document.getElementById('main');
                main.innerHTML = newtext;
                // We need to be sure that the page is loaded, that is why we
                // return the element's height (even though we do not use the
                // returned value).
                return main.offsetHeight;
            }
            </script>
            <style>
                *{margin: 0; padding: 0; border: 0;}
                #main {position: absolute; top: 0px;  FORMAT CSS;   OUTLINE CSS; }
            </style></head>
            <body><div id="main"></div></body></html>'"""


class TestRenderer(TestCase):

    def setUp(self):
        """
        Set up the components need for all tests
        """
        # Mocked out desktop object
        self.desktop = MagicMock()
        self.desktop.primaryScreen.return_value = SCREEN['primary']
        self.desktop.screenCount.return_value = SCREEN['number']
        self.desktop.screenGeometry.return_value = SCREEN['size']
        self.screens = ScreenList.create(self.desktop)
        Registry.create()

    def tearDown(self):
        """
        Delete QApplication.
        """
        del self.screens

    def test_default_screen_layout(self):
        """
        Test the default layout calculations
        """
        # GIVEN: A new renderer instance.
        renderer = Renderer()
        # WHEN: given the default screen size has been created.
        # THEN: The renderer have created a default screen.
        self.assertEqual(renderer.width, 1024, 'The base renderer should be a live controller')
        self.assertEqual(renderer.height, 768, 'The base renderer should be a live controller')
        self.assertEqual(renderer.screen_ratio, 0.75, 'The base renderer should be a live controller')
        self.assertEqual(renderer.footer_start, 691, 'The base renderer should be a live controller')

    @patch('openlp.core.lib.renderer.FormattingTags.get_html_tags')
    def test_get_start_tags(self, mocked_get_html_tags):
        """
        Test the get_start_tags() method
        """
        # GIVEN: A new renderer instance. Broken raw_text (missing closing tags).
        given_raw_text = '{st}{r}Text text text'
        expected_tuple = ('{st}{r}Text text text{/r}{/st}', '{st}{r}',
                          '<strong><span style="-webkit-text-fill-color:red">')
        mocked_get_html_tags.return_value = [{'temporary': False, 'end tag': '{/r}', 'desc': 'Red',
                                              'start html': '<span style="-webkit-text-fill-color:red">',
                                              'end html': '</span>', 'start tag': '{r}', 'protected': True},
                                             {'temporary': False, 'end tag': '{/st}', 'desc': 'Bold',
                                              'start html': '<strong>', 'end html': '</strong>', 'start tag': '{st}',
                                              'protected': True}]

        # WHEN: The renderer converts the start tags
        result = get_start_tags(given_raw_text)

        # THEN: Check if the correct tuple is returned.
        self.assertEqual(result, expected_tuple), 'A tuple should be returned containing the text with correct ' \
            'tags, the opening tags, and the opening html tags.'

    def test_word_split(self):
        """
        Test the word_split() method
        """
        # GIVEN: A line of text
        given_line = 'beginning asdf \n end asdf'
        expected_words = ['beginning', 'asdf', 'end', 'asdf']

        # WHEN: Split the line based on word split rules
        result_words = words_split(given_line)

        # THEN: The word lists should be the same.
        self.assertListEqual(result_words, expected_words)

    def test_format_slide_logical_split(self):
        """
        Test that a line with text and a logic break does not break the renderer just returns the input
        """
        # GIVEN: A line of with a space text and the logical split
        renderer = Renderer()
        renderer.empty_height = 480
        given_line = 'a\n[---]\nb'
        expected_words = ['a<br>[---]<br>b']
        service_item = ServiceItem(None)

        # WHEN: Split the line based on word split rules
        result_words = renderer.format_slide(given_line, service_item)

        # THEN: The word lists should be the same.
        self.assertListEqual(result_words, expected_words)

    def test_format_slide_blank_before_split(self):
        """
        Test that a line with blanks before the logical split at handled
        """
        # GIVEN: A line of with a space before the logical split
        renderer = Renderer()
        renderer.empty_height = 480
        given_line = '\n       [---]\n'
        expected_words = ['<br>       [---]']
        service_item = ServiceItem(None)

        # WHEN: Split the line based on word split rules
        result_words = renderer.format_slide(given_line, service_item)

        # THEN: The blanks have been removed.
        self.assertListEqual(result_words, expected_words)

    def test_format_slide_blank_after_split(self):
        """
        Test that a line with blanks before the logical split at handled
        """
        # GIVEN: A line of with a space after the logical split
        renderer = Renderer()
        renderer.empty_height = 480
        given_line = '\n[---]  \n'
        expected_words = ['<br>[---]  ']
        service_item = ServiceItem(None)

        # WHEN: Split the line based on word split rules
        result_words = renderer.format_slide(given_line, service_item)

        # THEN: The blanks have been removed.
        self.assertListEqual(result_words, expected_words)

    @patch('openlp.core.lib.renderer.QtWebKitWidgets.QWebView')
    @patch('openlp.core.lib.renderer.build_lyrics_format_css')
    @patch('openlp.core.lib.renderer.build_lyrics_outline_css')
    def test_set_text_rectangle(self, mock_outline_css, mock_lyrics_css, mock_webview):
        """
        Test set_text_rectangle returns a proper html string
        """
        # GIVEN: test object and data
        mock_lyrics_css.return_value = ' FORMAT CSS; '
        mock_outline_css.return_value = ' OUTLINE CSS; '
        theme_data = ThemeXML()
        theme_data.font_main_name = 'Arial'
        theme_data.font_main_size = 20
        theme_data.font_main_color = '#FFFFFF'
        theme_data.font_main_outline_color = '#FFFFFF'
        main = QtCore.QRect(10, 10, 1280, 900)
        foot = QtCore.QRect(10, 1000, 1260, 24)
        renderer = Renderer()

        # WHEN: Calling method
        renderer._set_text_rectangle(theme_data=theme_data, rect_main=main, rect_footer=foot)

        # THEN: QtWebKitWidgets should be called with the proper string
        mock_webview.setHtml.called_with(CSS_TEST_ONE, 'Should be the same')
