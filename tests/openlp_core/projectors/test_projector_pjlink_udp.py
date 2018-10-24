
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
Package to test the PJLink UDP functions
"""

from unittest import TestCase
from unittest.mock import call, patch

import openlp.core.projectors.pjlink
from openlp.core.common.registry import Registry
from openlp.core.projectors.constants import PJLINK_PORT
from openlp.core.projectors.tab import ProjectorTab
from openlp.core.projectors.pjlink import PJLinkUDP

from tests.helpers.testmixin import TestMixin
from tests.resources.projector.data import TEST1_DATA


class TestPJLinkBase(TestCase, TestMixin):
    """
    Tests for the PJLinkUDP class
    """
    def setUp(self):
        """
        Create the UI and setup necessary options
        """
        self.setup_application()
        self.build_settings()
        Registry.create()
        """
        with patch('openlp.core.projectors.db.init_url') as mocked_init_url:
            if os.path.exists(TEST_DB):
                os.unlink(TEST_DB)
            mocked_init_url.return_value = 'sqlite:///%s' % TEST_DB
            self.projectordb = ProjectorDB()
            if not hasattr(self, 'projector_manager'):
                self.projector_manager = ProjectorManager(projectordb=self.projectordb)
        """

    def tearDown(self):
        """
        Remove test database.
        Delete all the C++ objects at the end so that we don't have a segfault.
        """
        # self.projectordb.session.close()
        self.destroy_settings()
        # del self.projector_manager

    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_get_datagram_data_negative_zero_length(self, mock_log):
        """
        Test get_datagram when pendingDatagramSize = 0
        """
        # GIVEN: Test setup
        pjlink_udp = PJLinkUDP()
        log_warning_calls = [call('(UDP:4352) No data (-1)')]
        log_debug_calls = [call('(UDP:4352) PJLinkUDP() Initialized'),
                           call('(UDP:4352) get_datagram() - Receiving data')]
        with patch.object(pjlink_udp, 'pendingDatagramSize') as mock_datagram, \
                patch.object(pjlink_udp, 'readDatagram') as mock_read:
            mock_datagram.return_value = -1
            mock_read.return_value = ('', TEST1_DATA['ip'], PJLINK_PORT)

            # WHEN: get_datagram called with 0 bytes ready
            pjlink_udp.get_datagram()

            # THEN: Log entries should be made and method returns
            mock_log.warning.assert_has_calls(log_warning_calls)
            mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_get_datagram_data_no_data(self, mock_log):
        """
        Test get_datagram when data length = 0
        """
        # GIVEN: Test setup
        pjlink_udp = PJLinkUDP()
        log_warning_calls = [call('(UDP:4352) get_datagram() called when pending data size is 0')]
        log_debug_calls = [call('(UDP:4352) PJLinkUDP() Initialized'),
                           call('(UDP:4352) get_datagram() - Receiving data')]
        with patch.object(pjlink_udp, 'pendingDatagramSize') as mock_datagram, \
                patch.object(pjlink_udp, 'readDatagram') as mock_read:
            mock_datagram.return_value = 0
            mock_read.return_value = ('', TEST1_DATA['ip'], PJLINK_PORT)

            # WHEN: get_datagram called with 0 bytes ready
            pjlink_udp.get_datagram()

            # THEN: Log entries should be made and method returns
            mock_log.warning.assert_has_calls(log_warning_calls)
            mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_get_datagram_pending_zero_length(self, mock_log):
        """
        Test get_datagram when pendingDatagramSize = 0
        """
        # GIVEN: Test setup
        pjlink_udp = PJLinkUDP()
        log_warning_calls = [call('(UDP:4352) get_datagram() called when pending data size is 0')]
        log_debug_calls = [call('(UDP:4352) PJLinkUDP() Initialized'),
                           call('(UDP:4352) get_datagram() - Receiving data')]
        with patch.object(pjlink_udp, 'pendingDatagramSize') as mock_datagram:
            mock_datagram.return_value = 0

            # WHEN: get_datagram called with 0 bytes ready
            pjlink_udp.get_datagram()

            # THEN: Log entries should be made and method returns
            mock_log.warning.assert_has_calls(log_warning_calls)
            mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.tab, 'log')
    def test_pjlinksettings_add_udp_listener(self, mock_log):
        """
        Test adding UDP listners to PJLink Settings tab
        """
        # GIVEN: Initial setup
        log_debug_calls = [call('PJLink settings tab initialized'),
                           call('PJLinkSettings: new callback list: dict_keys([4352])')]
        log_warning_calls = []

        pjlink_udp = PJLinkUDP()
        settings_tab = ProjectorTab(parent=None)

        # WHEN: add_udp_listener is called with single port
        settings_tab.add_udp_listener(port=pjlink_udp.port, callback=pjlink_udp.check_settings)

        # THEN: settings tab should have one entry
        assert len(settings_tab.udp_listeners) == 1
        assert pjlink_udp.port in settings_tab.udp_listeners
        mock_log.debug.assert_has_calls(log_debug_calls)
        mock_log.warning.assert_has_calls(log_warning_calls)

    @patch.object(openlp.core.projectors.tab, 'log')
    def test_pjlinksettings_add_udp_listener_multiple_same(self, mock_log):
        """
        Test adding second UDP listner with same port to PJLink Settings tab
        """
        # GIVEN: Initial setup
        log_debug_calls = [call('PJLink settings tab initialized'),
                           call('PJLinkSettings: new callback list: dict_keys([4352])')]
        log_warning_calls = [call('Port 4352 already in list - not adding')]
        pjlink_udp = PJLinkUDP()
        settings_tab = ProjectorTab(parent=None)
        settings_tab.add_udp_listener(port=pjlink_udp.port, callback=pjlink_udp.check_settings)

        # WHEN: add_udp_listener is called with second instance same port
        settings_tab.add_udp_listener(port=pjlink_udp.port, callback=pjlink_udp.check_settings)

        # THEN: settings tab should have one entry
        assert len(settings_tab.udp_listeners) == 1
        assert pjlink_udp.port in settings_tab.udp_listeners
        mock_log.debug.assert_has_calls(log_debug_calls)
        mock_log.warning.assert_has_calls(log_warning_calls)

    @patch.object(openlp.core.projectors.tab, 'log')
    def test_pjlinksettings_add_udp_listener_multiple_different(self, mock_log):
        """
        Test adding second UDP listner with different port to PJLink Settings tab
        """
        # GIVEN: Initial setup
        log_debug_calls = [call('PJLink settings tab initialized'),
                           call('PJLinkSettings: new callback list: dict_keys([4352])')]
        log_warning_calls = []

        settings_tab = ProjectorTab(parent=None)
        pjlink_udp1 = PJLinkUDP(port=4352)
        settings_tab.add_udp_listener(port=pjlink_udp1.port, callback=pjlink_udp1.check_settings)

        # WHEN: add_udp_listener is called with second instance different port
        pjlink_udp2 = PJLinkUDP(port=4353)
        settings_tab.add_udp_listener(port=pjlink_udp2.port, callback=pjlink_udp2.check_settings)

        # THEN: settings tab should have two entry
        assert len(settings_tab.udp_listeners) == 2
        assert pjlink_udp1.port in settings_tab.udp_listeners
        assert pjlink_udp2.port in settings_tab.udp_listeners
        mock_log.debug.assert_has_calls(log_debug_calls)
        mock_log.warning.assert_has_calls(log_warning_calls)

    @patch.object(openlp.core.projectors.tab, 'log')
    def test_pjlinksettings_remove_udp_listener(self, mock_log):
        """
        Test removing UDP listners to PJLink Settings tab
        """
        # GIVEN: Initial setup
        log_debug_calls = [call('PJLink settings tab initialized'),
                           call('PJLinkSettings: new callback list: dict_keys([4352])'),
                           call('PJLinkSettings: new callback list: dict_keys([])')]
        log_warning_calls = []

        pjlink_udp = PJLinkUDP()
        settings_tab = ProjectorTab(parent=None)
        settings_tab.add_udp_listener(port=pjlink_udp.port, callback=pjlink_udp.check_settings)

        # WHEN: remove_udp_listener is called with single port
        settings_tab.remove_udp_listener(port=pjlink_udp.port)

        # THEN: settings tab should have one entry
        assert len(settings_tab.udp_listeners) == 0
        mock_log.debug.assert_has_calls(log_debug_calls)
        mock_log.warning.assert_has_calls(log_warning_calls)

    @patch.object(openlp.core.projectors.tab, 'log')
    def test_pjlinksettings_remove_udp_listener_multiple_different(self, mock_log):
        """
        Test adding second UDP listner with different port to PJLink Settings tab
        """
        # GIVEN: Initial setup
        log_debug_calls = [call('PJLink settings tab initialized'),
                           call('PJLinkSettings: new callback list: dict_keys([4352])')]
        log_warning_calls = []

        settings_tab = ProjectorTab(parent=None)
        pjlink_udp1 = PJLinkUDP(port=4352)
        settings_tab.add_udp_listener(port=pjlink_udp1.port, callback=pjlink_udp1.check_settings)
        pjlink_udp2 = PJLinkUDP(port=4353)
        settings_tab.add_udp_listener(port=pjlink_udp2.port, callback=pjlink_udp2.check_settings)

        # WHEN: remove_udp_listener called for one port
        settings_tab.remove_udp_listener(port=4353)

        # THEN: settings tab should have one entry
        assert len(settings_tab.udp_listeners) == 1
        assert pjlink_udp1.port in settings_tab.udp_listeners
        assert pjlink_udp2.port not in settings_tab.udp_listeners
        mock_log.debug.assert_has_calls(log_debug_calls)
        mock_log.warning.assert_has_calls(log_warning_calls)

    @patch.object(PJLinkUDP, 'check_settings')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    @patch.object(openlp.core.projectors.tab, 'log')
    def test_pjlinksettings_call_udp_listener(self, mock_tab_log, mock_pjlink_log, mock_check_settings):
        """
        Test calling UDP listners in PJLink Settings tab
        """
        # GIVEN: Initial setup
        tab_debug_calls = [call('PJLink settings tab initialized'),
                           call('PJLinkSettings: new callback list: dict_keys([4352])'),
                           call('PJLinkSettings: Calling UDP listeners')]
        pjlink_debug_calls = [call.debug('(UDP:4352) PJLinkUDP() Initialized')]

        pjlink_udp = PJLinkUDP()
        settings_tab = ProjectorTab(parent=None)
        settings_tab.add_udp_listener(port=pjlink_udp.port, callback=pjlink_udp.check_settings)

        # WHEN: calling UDP listener via registry
        settings_tab.call_udp_listener()

        # THEN: settings tab should have one entry
        assert len(settings_tab.udp_listeners) == 1
        mock_check_settings.assert_called()
        mock_tab_log.debug.assert_has_calls(tab_debug_calls)
        mock_pjlink_log.assert_has_calls(pjlink_debug_calls)
