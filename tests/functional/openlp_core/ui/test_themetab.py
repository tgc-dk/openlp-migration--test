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
Package to test the openlp.core.ui.ThemeTab package.
"""
from unittest import TestCase
from unittest.mock import MagicMock

from openlp.core.common.registry import Registry
from openlp.core.ui.themestab import ThemesTab
from openlp.core.ui.settingsform import SettingsForm

from tests.helpers.testmixin import TestMixin


class TestThemeTab(TestCase, TestMixin):

    def setUp(self):
        """
        Set up a few things for the tests
        """
        Registry.create()

    def test_creation(self):
        """
        Test that  Themes Tab is created.
        """
        # GIVEN: A new Advanced Tab
        settings_form = SettingsForm(None)

        # WHEN: I create an advanced tab
        themes_tab = ThemesTab(settings_form)

        # THEN:
        assert "Themes" == themes_tab.tab_title, 'The tab title should be Theme'

    def test_save_triggers_processes_true(self):
        """
        Test that the global theme event is triggered when the tab is visited.
        """
        # GIVEN: A new Advanced Tab
        settings_form = SettingsForm(None)
        themes_tab = ThemesTab(settings_form)
        Registry().register('renderer', MagicMock())
        themes_tab.tab_visited = True
        # WHEN: I change search as type check box
        themes_tab.save()

        # THEN: we should have two post save processed to run
        assert 1 == len(settings_form.processes), 'One post save processes should be created'

    def test_save_triggers_processes_false(self):
        """
        Test that the global theme event is not triggered when the tab is not visited.
        """
        # GIVEN: A new Advanced Tab
        settings_form = SettingsForm(None)
        themes_tab = ThemesTab(settings_form)
        Registry().register('renderer', MagicMock())
        themes_tab.tab_visited = False
        # WHEN: I change search as type check box
        themes_tab.save()

        # THEN: we should have two post save processed to run
        assert 0 == len(settings_form.processes), 'No post save processes should be created'
