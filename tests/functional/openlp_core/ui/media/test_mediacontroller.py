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
Package to test the openlp.core.ui.media package.
"""
from unittest import TestCase
from unittest.mock import MagicMock, patch

from openlp.core.common.registry import Registry
from openlp.core.ui.media.mediacontroller import MediaController
from openlp.core.ui.media.vlcplayer import VlcPlayer
from tests.helpers.testmixin import TestMixin

from tests.utils.constants import RESOURCE_PATH


TEST_PATH = RESOURCE_PATH / 'media'
TEST_MEDIA = [['avi_file.avi', 61495], ['mp3_file.mp3', 134426], ['mpg_file.mpg', 9404], ['mp4_file.mp4', 188336]]


class TestMediaController(TestCase, TestMixin):

    def setUp(self):
        Registry.create()
        Registry().register('service_manager', MagicMock())

    def test_generate_extensions_lists(self):
        """
        Test that the extensions are create correctly
        """
        # GIVEN: A MediaController and an active player with audio and video extensions
        media_controller = MediaController()
        media_controller.vlc_player = VlcPlayer(None)
        media_controller.vlc_player.is_active = True
        media_controller.vlc_player.audio_extensions_list = ['*.mp3', '*.wav', '*.wma', '*.ogg']
        media_controller.vlc_player.video_extensions_list = ['*.mp4', '*.mov', '*.avi', '*.ogm']

        # WHEN: calling _generate_extensions_lists
        media_controller._generate_extensions_lists()

        # THEN: extensions list should have been copied from the player to the mediacontroller
        assert media_controller.video_extensions_list == media_controller.video_extensions_list, \
            'Video extensions should be the same'
        assert media_controller.audio_extensions_list == media_controller.audio_extensions_list, \
            'Audio extensions should be the same'

    def test_resize(self):
        """
        Test that the resize method is called correctly
        """
        # GIVEN: A media controller, a player and a display
        media_controller = MediaController()
        mocked_player = MagicMock()
        mocked_display = MagicMock()

        # WHEN: resize() is called
        media_controller.resize(mocked_display, mocked_player)

        # THEN: The player's resize method should be called correctly
        mocked_player.resize.assert_called_with(mocked_display)

    def test_check_file_type(self):
        """
        Test that we don't try to play media when no players available
        """
        # GIVEN: A mocked UiStrings, get_used_players, controller, display and service_item
        media_controller = MediaController()
        mocked_controller = MagicMock()
        mocked_display = MagicMock()
        media_controller.media_players = MagicMock()

        # WHEN: calling _check_file_type when no players exists
        ret = media_controller._check_file_type(mocked_controller, mocked_display)

        # THEN: it should return False
        assert ret is False, '_check_file_type should return False when no mediaplayers are available.'

    def test_media_play_msg(self):
        """
        Test that the media controller responds to the request to play a loaded video
        """
        # GIVEN: A media controller and a message with two elements
        media_controller = MediaController()
        message = (1, 2)

        # WHEN: media_play_msg() is called
        with patch.object(media_controller, u'media_play') as mocked_media_play:
            media_controller.media_play_msg(message, False)

        # THEN: The underlying method is called
        mocked_media_play.assert_called_with(1, False)

    def test_media_pause_msg(self):
        """
        Test that the media controller responds to the request to pause a loaded video
        """
        # GIVEN: A media controller and a message with two elements
        media_controller = MediaController()
        message = (1, 2)

        # WHEN: media_play_msg() is called
        with patch.object(media_controller, u'media_pause') as mocked_media_pause:
            media_controller.media_pause_msg(message)

        # THEN: The underlying method is called
        mocked_media_pause.assert_called_with(1)

    def test_media_stop_msg(self):
        """
        Test that the media controller responds to the request to stop a loaded video
        """
        # GIVEN: A media controller and a message with two elements
        media_controller = MediaController()
        message = (1, 2)

        # WHEN: media_play_msg() is called
        with patch.object(media_controller, u'media_stop') as mocked_media_stop:
            media_controller.media_stop_msg(message)

        # THEN: The underlying method is called
        mocked_media_stop.assert_called_with(1)

    def test_media_volume_msg(self):
        """
        Test that the media controller responds to the request to change the volume
        """
        # GIVEN: A media controller and a message with two elements
        media_controller = MediaController()
        message = (1, [50])

        # WHEN: media_play_msg() is called
        with patch.object(media_controller, u'media_volume') as mocked_media_volume:
            media_controller.media_volume_msg(message)

        # THEN: The underlying method is called
        mocked_media_volume.assert_called_with(1, 50)

    def test_media_seek_msg(self):
        """
        Test that the media controller responds to the request to seek to a particular position
        """
        # GIVEN: A media controller and a message with two elements
        media_controller = MediaController()
        message = (1, [800])

        # WHEN: media_play_msg() is called
        with patch.object(media_controller, u'media_seek') as mocked_media_seek:
            media_controller.media_seek_msg(message)

        # THEN: The underlying method is called
        mocked_media_seek.assert_called_with(1, 800)

    def test_media_length(self):
        """
        Test the Media Info basic functionality
        """
        media_controller = MediaController()
        for test_data in TEST_MEDIA:
            # GIVEN: a media file
            full_path = str(TEST_PATH / test_data[0])

            # WHEN the media data is retrieved
            results = media_controller.media_length(full_path)

            # THEN you can determine the run time
            assert results == test_data[1], 'The correct duration is returned for ' + test_data[0]
