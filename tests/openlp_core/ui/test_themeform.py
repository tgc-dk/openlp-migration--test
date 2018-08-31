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
Interface tests to test the ThemeWizard class and related methods.
"""
from unittest import TestCase

from openlp.core.common.registry import Registry
from openlp.core.ui.themeform import ThemeForm
from tests.helpers.testmixin import TestMixin


class TestThemeManager(TestCase, TestMixin):
    """
    Test the functions in the ThemeManager module
    """
    def setUp(self):
        """
        Create the UI
        """
        Registry.create()

    def test_create_theme_wizard(self):
        """
        Test creating a ThemeForm instance
        """
        # GIVEN: A ThemeForm class
        # WHEN: An object is created
        # THEN: There should be no problems
        ThemeForm(None)
