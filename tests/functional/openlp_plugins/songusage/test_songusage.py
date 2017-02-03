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
This module contains tests for the Songusage plugin.
"""
from unittest import TestCase
from unittest.mock import MagicMock, patch

from openlp.core import Registry
from openlp.plugins.songusage.lib import upgrade
from openlp.plugins.songusage.lib.db import init_schema
from openlp.plugins.songusage.songusageplugin import SongUsagePlugin, __default_settings__


class TestSongUsage(TestCase):

    def setUp(self):
        Registry.create()

    def about_text_test(self):
        """
        Test the about text of the song usage plugin
        """
        # GIVEN: The SongUsagePlugin
        # WHEN: Retrieving the about text
        # THEN: about() should return a string object
        self.assertIsInstance(SongUsagePlugin.about(), str)
        # THEN: about() should return a non-empty string
        self.assertNotEquals(len(SongUsagePlugin.about()), 0)
        self.assertNotEquals(len(SongUsagePlugin.about()), 0)

    @patch('openlp.plugins.songusage.songusageplugin.Manager')
    def song_usage_init_test(self, MockedManager):
        """
        Test the initialisation of the SongUsagePlugin class
        """
        # GIVEN: A mocked database manager
        mocked_manager = MagicMock()
        MockedManager.return_value = mocked_manager

        # WHEN: The SongUsagePlugin class is instantiated
        song_usage = SongUsagePlugin()

        # THEN: It should be initialised correctly
        MockedManager.assert_called_with('songusage', init_schema, upgrade_mod=upgrade)
        self.assertEqual(mocked_manager, song_usage.manager)
        self.assertFalse(song_usage.song_usage_active)

    @patch('openlp.plugins.songusage.songusageplugin.Manager')
    def check_pre_conditions_test(self, MockedManager):
        """
        Test that check_pre_condition returns true for valid manager session
        """
        # GIVEN: A mocked database manager
        mocked_manager = MagicMock()
        mocked_manager.session = MagicMock()
        MockedManager.return_value = mocked_manager
        song_usage = SongUsagePlugin()

        # WHEN: The calling check_pre_conditions
        ret = song_usage.check_pre_conditions()

        # THEN: It should return True
        self.assertTrue(ret)

    def test_default_settings(self):
        """
        Test that all the default settings are correct
        """
        # GIVEN: A list of default settings
        expected_defaults = sorted([
            'songusage/db type',
            'songusage/db username',
            'songusage/db password',
            'songusage/db hostname',
            'songusage/db database',
            'songusage/active',
            'songusage/to date',
            'songusage/from date',
            'songusage/last directory',
            'songusage/last directory export',
            'songusage/status'
        ])

        # WHEN: The plugin is initialised
        # THEN: The defaults should be correct
        print(__default_settings__)
        for e_key, a_key in zip(expected_defaults, sorted(__default_settings__.keys())):
            assert e_key == a_key, '{} != {}'.format(e_key, a_key)
