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
Functional tests to test calls for network interfaces.
"""
from unittest import TestCase
from unittest.mock import call, patch
from PyQt5.QtCore import QObject
from PyQt5.QtNetwork import QHostAddress, QNetworkAddressEntry, QNetworkInterface

import openlp.core.common
from openlp.core.common import get_local_ip4

from tests.helpers.testmixin import TestMixin


class FakeIP4InterfaceEntry(QObject):
    """
    Class to face an interface for testing purposes
    """
    def __init__(self, name='lo'):
        self.my_name = name
        if name in ['localhost', 'lo']:
            self.my_ip = QNetworkAddressEntry()
            self.my_ip.setBroadcast(QHostAddress('255.0.0.0'))
            self.my_ip.setIp(QHostAddress('127.0.0.2'))
            self.my_ip.setPrefixLength(8)
            self.fake_data = {'lo': {'ip': '127.0.0.2',
                                     'broadcast': '255.0.0.0',
                                     'netmask': '255.0.0.0',
                                     'prefix': 8,
                                     'localnet': '127.0.0.0'}}
        else:
            # Define a fake real address
            self.my_ip = QNetworkAddressEntry()
            self.my_ip.setBroadcast(QHostAddress('255.255.255.0'))
            self.my_ip.setIp(QHostAddress('127.254.0.2'))
            self.my_ip.setPrefixLength(24)
            self.fake_data = {self.my_name: {'ip': '127.254.0.2',
                                             'broadcast': '255.255.255.0',
                                             'netmask': '255.255.255.0',
                                             'prefix': 24,
                                             'localnet': '127.254.0.0'}}

    def addressEntries(self):
        """
        Return fake IP address
        """
        return [self.my_ip]

    def flags(self):
        """
        Return a QFlags enum with IsUp and IsRunning
        """
        return (QNetworkInterface.IsUp | QNetworkInterface.IsRunning)

    def name(self):
        return self.my_name

    def isValid(self):
        return True


class TestInterfaces(TestCase, TestMixin):
    """
    A test suite to test out functions/methods that use network interface(s).
    """
    def setUp(self):
        """
        Create an instance and a few example actions.
        """
        self.build_settings()
        if not hasattr(self, 'fake_lo'):
            # Since these shouldn't change, only need to instantiate them the first time
            self.fake_lo = FakeIP4InterfaceEntry()
            self.fake_localhost = FakeIP4InterfaceEntry(name='localhost')
            self.fake_address = FakeIP4InterfaceEntry(name='eth25')

    def tearDown(self):
        """
        Clean up
        """
        self.destroy_settings()

    @patch.object(openlp.core.common, 'log')
    def test_ip4_no_interfaces(self, mock_log):
        """
        Test no interfaces available
        """
        # GIVEN: Test environment
        call_debug = [call('Getting local IPv4 interface(es) information')]
        call_warning = [call('No active IPv4 network interfaces detected')]

        # WHEN: get_local_ip4 is called
        with patch('openlp.core.common.QNetworkInterface') as mock_network_interface:
            mock_network_interface.allInterfaces.return_value = []
            ifaces = get_local_ip4()

        # THEN: There should not be any interfaces detected
        mock_log.debug.assert_has_calls(call_debug)
        mock_log.warning.assert_has_calls(call_warning)
        assert not ifaces, 'There should have been no active interfaces listed'

    @patch.object(openlp.core.common, 'log')
    def test_ip4_lo(self, mock_log):
        """
        Test get_local_ip4 returns proper dictionary with 'lo'
        """
        # GIVEN: Test environment
        call_debug = [call('Getting local IPv4 interface(es) information'),
                      call('Checking for isValid and flags == IsUP | IsRunning'),
                      call('Checking address(es) protocol'),
                      call('Checking for protocol == IPv4Protocol'),
                      call('Getting interface information'),
                      call('Adding lo to active list')]
        call_warning = [call('No active IPv4 interfaces found except localhost')]

        # WHEN: get_local_ip4 is called
        with patch('openlp.core.common.QNetworkInterface') as mock_network_interface:
            mock_network_interface.allInterfaces.return_value = [self.fake_lo]
            ifaces = get_local_ip4()

        # THEN: There should be a fake 'lo' interface
        mock_log.debug.assert_has_calls(call_debug)
        mock_log.warning.assert_has_calls(call_warning)
        assert ifaces == self.fake_lo.fake_data, "There should have been an 'lo' interface listed"

    @patch.object(openlp.core.common, 'log')
    def test_ip4_localhost(self, mock_log):
        """
        Test get_local_ip4 returns proper dictionary with 'lo' if interface is 'localhost'
        """
        # GIVEN: Test environment
        call_debug = [call('Getting local IPv4 interface(es) information'),
                      call('Checking for isValid and flags == IsUP | IsRunning'),
                      call('Checking address(es) protocol'),
                      call('Checking for protocol == IPv4Protocol'),
                      call('Getting interface information'),
                      call('Adding localhost to active list'),
                      call('Renaming windows localhost to lo')]
        call_warning = [call('No active IPv4 interfaces found except localhost')]

        # WHEN: get_local_ip4 is called
        with patch('openlp.core.common.QNetworkInterface') as mock_network_interface:
            mock_network_interface.allInterfaces.return_value = [self.fake_localhost]
            ifaces = get_local_ip4()

        # THEN: There should be a fake 'lo' interface
        mock_log.debug.assert_has_calls(call_debug)
        mock_log.warning.assert_has_calls(call_warning)
        assert ifaces == self.fake_lo.fake_data, "There should have been an 'lo' interface listed"

    @patch.object(openlp.core.common, 'log')
    def test_ip4_eth25(self, mock_log):
        """
        Test get_local_ip4 returns proper dictionary with 'eth25'
        """
        # GIVEN: Test environment
        call_debug = [call('Getting local IPv4 interface(es) information'),
                      call('Checking for isValid and flags == IsUP | IsRunning'),
                      call('Checking address(es) protocol'),
                      call('Checking for protocol == IPv4Protocol'),
                      call('Getting interface information'),
                      call('Adding eth25 to active list')]
        call_warning = []

        # WHEN: get_local_ip4 is called
        with patch('openlp.core.common.QNetworkInterface') as mock_network_interface:
            mock_network_interface.allInterfaces.return_value = [self.fake_address]
            ifaces = get_local_ip4()

        # THEN: There should be a fake 'eth25' interface
        mock_log.debug.assert_has_calls(call_debug)
        mock_log.warning.assert_has_calls(call_warning)
        assert ifaces == self.fake_address.fake_data

    @patch.object(openlp.core.common, 'log')
    def test_ip4_lo_eth25(self, mock_log):
        """
        Test get_local_ip4 returns proper dictionary with 'eth25'
        """
        # GIVEN: Test environment
        call_debug = [call('Getting local IPv4 interface(es) information'),
                      call('Checking for isValid and flags == IsUP | IsRunning'),
                      call('Checking address(es) protocol'),
                      call('Checking for protocol == IPv4Protocol'),
                      call('Getting interface information'),
                      call('Adding lo to active list'),
                      call('Checking for isValid and flags == IsUP | IsRunning'),
                      call('Checking address(es) protocol'),
                      call('Checking for protocol == IPv4Protocol'),
                      call('Getting interface information'),
                      call('Adding eth25 to active list'),
                      call('Found at least one IPv4 interface, removing localhost')]
        call_warning = []

        # WHEN: get_local_ip4 is called
        with patch('openlp.core.common.QNetworkInterface') as mock_network_interface:
            mock_network_interface.allInterfaces.return_value = [self.fake_lo, self.fake_address]
            ifaces = get_local_ip4()

        # THEN: There should be a fake 'eth25' interface
        mock_log.debug.assert_has_calls(call_debug)
        mock_log.warning.assert_has_calls(call_warning)
        assert ifaces == self.fake_address.fake_data, "There should have been only 'eth25' interface listed"
