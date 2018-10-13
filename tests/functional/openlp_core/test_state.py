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
from unittest import TestCase
from unittest.mock import MagicMock, patch

from openlp.core.state import State
from openlp.core.common.registry import Registry
from openlp.core.lib.plugin import PluginStatus

from tests.helpers.testmixin import TestMixin

"""
Test the Status class.
"""


class TestState(TestCase, TestMixin):
    """
    Test the Server Class used to check if OpenLP is running.
    """
    def setUp(self):
        Registry.create()
        self.state = State()

    def tearDown(self):
        pass

    def test_add_service(self):
        # GIVEN a new state
        State().load_settings()

        # WHEN I add a new service
        State().add_service("test", 1, PluginStatus.Active)

        # THEN I have a saved service
        assert len(State().modules) == 1

    def test_add_service_multiple(self):
        # GIVEN a new state
        State().load_settings()

        # WHEN I add a new service twice
        State().add_service("test", 1, PluginStatus.Active)
        State().add_service("test", 1, PluginStatus.Active)

        # THEN I have a single saved service
        assert len(State().modules) == 1

    def test_add_service_multiple_depend(self):
        # GIVEN a new state
        State().load_settings()

        # WHEN I add a new service twice
        State().add_service("test", 1, PluginStatus.Active)
        State().add_service("test1", 1, PluginStatus.Active, "test")

        # THEN I have a single saved service
        assert len(State().modules) == 2

    def test_active_service(self):
        # GIVEN a new state
        State().load_settings()

        # WHEN I add a new service which is Active
        State().add_service("test", 1, PluginStatus.Active)

        # THEN I have a single saved service
        assert State().is_service_active('test') is True

    def test_inactive_service(self):
        # GIVEN a new state
        State().load_settings()

        # WHEN I add a new service which is Inactive
        State().add_service("test", 1, PluginStatus.Inactive)

        # THEN I have a single saved service
        assert State().is_service_active('test') is False
