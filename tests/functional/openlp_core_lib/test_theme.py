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
Package to test the openlp.core.lib.theme package.
"""
import json
from unittest import TestCase
import os

from openlp.core.common import json_default
from openlp.core.lib.theme import Theme


class TestTheme(TestCase):
    """
    Test the Theme class
    """
    def test_new_theme(self):
        """
        Test the Theme constructor
        """
        # GIVEN: The Theme class
        # WHEN: A theme object is created
        default_theme = Theme()

        # THEN: The default values should be correct
        self.check_theme(default_theme)

    def test_expand_json(self):
        """
        Test the expand_json method
        """
        # GIVEN: A Theme object and some JSON to "expand"
        theme = Theme()
        theme_json = {
            'background': {
                'border_color': '#000000',
                'type': 'solid'
            },
            'display': {
                'vertical_align': 0
            },
            'font': {
                'footer': {
                    'bold': False
                },
                'main': {
                    'name': 'Arial'
                }
            }
        }

        # WHEN: Theme.expand_json() is run
        theme.expand_json(theme_json)

        # THEN: The attributes should be set on the object
        self.check_theme(theme)

    def test_extend_image_filename(self):
        """
        Test the extend_image_filename method
        """
        # GIVEN: A theme object
        theme = Theme()
        theme.theme_name = 'MyBeautifulTheme   '
        theme.background_filename = '    video.mp4'
        theme.background_type = 'video'
        path = os.path.expanduser('~')

        # WHEN: Theme.extend_image_filename is run
        theme.extend_image_filename(path)

        # THEN: The filename of the background should be correct
        expected_filename = os.path.join(path, 'MyBeautifulTheme', 'video.mp4')
        self.assertEqual(expected_filename, theme.background_filename)
        self.assertEqual('MyBeautifulTheme', theme.theme_name)

    def test_save_retrieve(self):
        """
        Load a dummy theme, save it and reload it
        """
        # GIVEN: The default Theme class
        # WHEN: A theme object is created
        default_theme = Theme()
        # THEN: The default values should be correct
        save_theme_json = json.dumps(default_theme, default=json_default)
        lt = Theme()
        lt.load_theme(save_theme_json)
        self.check_theme(lt)

    def check_theme(self, theme):
        self.assertEqual('#000000', theme.background_border_color, 'background_border_color should be "#000000"')
        self.assertEqual('solid', theme.background_type, 'background_type should be "solid"')
        self.assertEqual(0, theme.display_vertical_align, 'display_vertical_align should be 0')
        self.assertFalse(theme.font_footer_bold, 'font_footer_bold should be False')
        self.assertEqual('Arial', theme.font_main_name, 'font_main_name should be "Arial"')
        self.assertEqual(47, len(theme.__dict__), 'The theme should have 47 attributes')
