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
This module contains tests for the lib submodule of the Images plugin.
"""
from unittest import TestCase
from unittest.mock import MagicMock

from PyQt5 import QtWidgets

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.plugins.images.lib import ImageTab

from tests.helpers.testmixin import TestMixin

__default_settings__ = {
    'images/db type': 'sqlite',
    'images/background color': '#000000',
}


class TestImageMediaItem(TestCase, TestMixin):
    """
    This is a test case to test various methods in the ImageTab.
    """

    def setUp(self):
        """
        Create the UI
        """
        Registry.create()
        Registry().register('settings_form', MagicMock())
        self.setup_application()
        self.build_settings()
        Settings().extend_default_settings(__default_settings__)
        self.parent = QtWidgets.QMainWindow()
        self.form = ImageTab(self.parent, 'Images', None, None)
        self.form.settings_form.register_post_process = MagicMock()

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.parent
        del self.form
        self.destroy_settings()

    def test_save_tab_nochange(self):
        """
        Test no changes does not trigger post processing
        """
        # GIVEN: No changes on the form.
        self.initial_color = '#999999'
        # WHEN: the save is invoked
        self.form.save()
        # THEN: the post process should not be requested
        assert 0 == self.form.settings_form.register_post_process.call_count, \
            'Image Post processing should not have been requested'

    def test_save_tab_change(self):
        """
        Test a color change is applied and triggers post processing.
        """
        # GIVEN: Apply a change to the form.
        self.form.on_background_color_changed('#999999')
        # WHEN: the save is invoked
        self.form.save()
        # THEN: the post process should be requested
        assert 1 == self.form.settings_form.register_post_process.call_count, \
            'Image Post processing should have been requested'
        # THEN: The color should be set
        assert self.form.background_color == '#999999', 'The updated color should have been saved'
