# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2014 Raoul Snyman                                        #
# Portions copyright (c) 2008-2014 Tim Bentley, Gerald Britton, Jonathan      #
# Corwin, Samuel Findlay, Michael Gorven, Scott Guerrieri, Matthias Hub,      #
# Meinert Jordan, Armin Köhler, Erik Lundin, Edwin Lunando, Brian T. Meyer.   #
# Joshua Miller, Stevan Pettit, Andreas Preikschat, Mattias Põldaru,          #
# Christian Richter, Philip Ridout, Simon Scudder, Jeffrey Smith,             #
# Maikel Stuivenberg, Martin Thompson, Jon Tibble, Dave Warnock,              #
# Frode Woldsund, Martin Zibricky, Patrick Zimmermann                         #
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
Package to test the openlp.core.__init__ package.
"""
import os

from unittest import TestCase
from unittest.mock import MagicMock, patch
from PyQt4 import QtCore, QtGui

from openlp.core import OpenLP
from openlp.core.common import Settings
from tests.helpers.testmixin import TestMixin


TEST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources'))


class TestInit(TestCase, TestMixin):
    def setUp(self):
        self.build_settings()
        with patch('openlp.core.common.OpenLPMixin.__init__') as constructor:
            constructor.return_value = None
            self.openlp = OpenLP(list())

    def tearDown(self):
        self.destroy_settings()
        del self.openlp

    def event_test(self):
        """
        Test the reimplemented event method
        """
        # GIVEN: A file path and a QEvent.
        file_path = os.path.join(TEST_PATH, 'church.jpg')
        mocked_file_method = MagicMock(return_value=file_path)
        event = QtCore.QEvent(QtCore.QEvent.FileOpen)
        event.file = mocked_file_method

        # WHEN: Call the vent method.
        result = self.openlp.event(event)

        # THEN: The path should be inserted.
        self.assertTrue(result, "The method should have returned True.")
        mocked_file_method.assert_called_once_with()
        self.assertEqual(self.openlp.args[0], file_path, "The path should be in args.")

    def backup_on_upgrade_first_install_test(self):
        """
        Test that we don't try to backup on a new install
        """
        # GIVEN: Mocked data version and OpenLP version which are the same
        old_install = False
        MOCKED_VERSION = {
            'full': '2.2.0-bzr000',
            'version': '2.2.0',
            'build': 'bzr000'
        }
        Settings().setValue('core/application version', '2.2.0')
        with patch('openlp.core.get_application_version') as mocked_get_application_version,\
                patch('openlp.core.QtGui.QMessageBox.question') as mocked_question:
            mocked_get_application_version.return_value = MOCKED_VERSION
            mocked_question.return_value = QtGui.QMessageBox.No

            # WHEN: We check if a backup should be created
            self.openlp.backup_on_upgrade(old_install)

            # THEN: It should not ask if we want to create a backup
            self.assertEqual(Settings().value('core/application version'), '2.2.0', 'Version should be the same!')
            self.assertEqual(mocked_question.call_count, 0, 'No question should have been asked!')

    def backup_on_upgrade_test(self):
        """
        Test that we try to backup on a new install
        """
        # GIVEN: Mocked data version and OpenLP version which are different
        old_install = True
        MOCKED_VERSION = {
            'full': '2.2.0-bzr000',
            'version': '2.2.0',
            'build': 'bzr000'
        }
        Settings().setValue('core/application version', '2.0.5')
        with patch('openlp.core.get_application_version') as mocked_get_application_version,\
                patch('openlp.core.QtGui.QMessageBox.question') as mocked_question:
            mocked_get_application_version.return_value = MOCKED_VERSION
            mocked_question.return_value = QtGui.QMessageBox.No

            # WHEN: We check if a backup should be created
            self.openlp.backup_on_upgrade(old_install)

            # THEN: It should ask if we want to create a backup
            self.assertEqual(Settings().value('core/application version'), '2.2.0', 'Version should be upgraded!')
            self.assertEqual(mocked_question.call_count, 1, 'A question should have been asked!')