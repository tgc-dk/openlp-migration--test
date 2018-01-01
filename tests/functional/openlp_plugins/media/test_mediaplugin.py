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
Test the media plugin
"""
from unittest import TestCase
from unittest.mock import patch

from openlp.core.common.registry import Registry
from openlp.plugins.media.mediaplugin import MediaPlugin, process_check_binary
from tests.helpers.testmixin import TestMixin


class MediaPluginTest(TestCase, TestMixin):
    """
    Test the media plugin
    """
    def setUp(self):
        Registry.create()

    @patch('openlp.plugins.media.mediaplugin.Plugin.initialise')
    def test_initialise(self, mocked_initialise):
        """
        Test that the initialise() method overwrites the built-in one, but still calls it
        """
        # GIVEN: A media plugin instance
        media_plugin = MediaPlugin()

        # WHEN: initialise() is called
        media_plugin.initialise()

        # THEN: The the base initialise() method should be called
        mocked_initialise.assert_called_with()

    def test_about_text(self):
        # GIVEN: The MediaPlugin
        # WHEN: Retrieving the about text
        # THEN: about() should return a string object
        assert isinstance(MediaPlugin.about(), str)
        # THEN: about() should return a non-empty string
        assert len(MediaPlugin.about()) is not 0

    @patch('openlp.plugins.media.mediaplugin.check_binary_exists')
    def test_process_check_binary_pass(self, mocked_checked_binary_exists):
        """
        Test that the Process check returns true if found
        """
        # GIVEN: A media plugin instance
        # WHEN: function is called with the correct name
        mocked_checked_binary_exists.return_value = str.encode('MediaInfo Command line')
        result = process_check_binary('MediaInfo')

        # THEN: The the result should be True
        assert result is True, 'Mediainfo should have been found'

    @patch('openlp.plugins.media.mediaplugin.check_binary_exists')
    def test_process_check_binary_fail(self, mocked_checked_binary_exists):
        """
        Test that the Process check returns false if not found
        """
        # GIVEN: A media plugin instance
        # WHEN: function is called with the wrong name
        mocked_checked_binary_exists.return_value = str.encode('MediaInfo1 Command line')
        result = process_check_binary("MediaInfo1")

        # THEN: The the result should be True
        assert result is False, "Mediainfo should not have been found"
