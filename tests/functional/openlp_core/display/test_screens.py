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
Package to test the openlp.core.lib.screenlist package.
"""
from unittest import TestCase
from unittest.mock import MagicMock

from PyQt5 import QtCore, QtWidgets

from openlp.core.common.registry import Registry
from openlp.core.display.screens import ScreenList

SCREEN = {
    'primary': False,
    'number': 1,
    'size': QtCore.QRect(0, 0, 1024, 768)
}


class TestScreenList(TestCase):

    def setUp(self):
        """
        Set up the components need for all tests.
        """
        # Mocked out desktop object
        self.desktop = MagicMock()
        self.desktop.primaryScreen.return_value = SCREEN['primary']
        self.desktop.screenCount.return_value = SCREEN['number']
        self.desktop.screenGeometry.return_value = SCREEN['size']

        self.application = QtWidgets.QApplication.instance()
        Registry.create()
        self.application.setOrganizationName('OpenLP-tests')
        self.application.setOrganizationDomain('openlp.org')
        self.screens = ScreenList.create(self.desktop)

    def tearDown(self):
        """
        Delete QApplication.
        """
        del self.screens
        del self.application

    def test_add_desktop(self):
        """
        Test the ScreenList.screen_count_changed method to check if new monitors are detected by OpenLP.
        """
        # GIVEN: The screen list at its current size
        old_screen_count = len(self.screens.screen_list)

        # WHEN: We add a new screen
        self.desktop.screenCount.return_value = SCREEN['number'] + 1
        self.screens.screen_count_changed(old_screen_count)

        # THEN: The screen should have been added and the screens should be identical
        new_screen_count = len(self.screens.screen_list)
        assert old_screen_count + 1 == new_screen_count, 'The new_screens list should be bigger'
        assert SCREEN == self.screens.screen_list.pop(), \
            'The 2nd screen should be identical to the first screen'
