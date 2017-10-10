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
Package to test the openlp.core.ui.media.webkitplayer package.
"""
from unittest import TestCase
from unittest.mock import MagicMock, patch

from openlp.core.ui.media.webkitplayer import WebkitPlayer


class TestWebkitPlayer(TestCase):
    """
    Test the functions in the :mod:`webkitplayer` module.
    """

    def test_check_available_video_disabled(self):
        """
        Test of webkit video unavailability
        """
        # GIVEN: A WebkitPlayer instance and a mocked QWebPage
        mocked_qwebpage = MagicMock()
        mocked_qwebpage.mainFrame().evaluateJavaScript.return_value = '[object HTMLUnknownElement]'
        with patch('openlp.core.ui.media.webkitplayer.QtWebKitWidgets.QWebPage', **{'return_value': mocked_qwebpage}):
            webkit_player = WebkitPlayer(None)

            # WHEN: An checking if the player is available
            available = webkit_player.check_available()

            # THEN: The player should not be available when '[object HTMLUnknownElement]' is returned
            self.assertEqual(False, available,
                             'The WebkitPlayer should not be available when video feature detection fails')

    def test_check_available_video_enabled(self):
        """
        Test of webkit video availability
        """
        # GIVEN: A WebkitPlayer instance and a mocked QWebPage
        mocked_qwebpage = MagicMock()
        mocked_qwebpage.mainFrame().evaluateJavaScript.return_value = '[object HTMLVideoElement]'
        with patch('openlp.core.ui.media.webkitplayer.QtWebKitWidgets.QWebPage', **{'return_value': mocked_qwebpage}):
            webkit_player = WebkitPlayer(None)

            # WHEN: An checking if the player is available
            available = webkit_player.check_available()

            # THEN: The player should be available when '[object HTMLVideoElement]' is returned
            self.assertEqual(True, available,
                             'The WebkitPlayer should be available when video feature detection passes')
