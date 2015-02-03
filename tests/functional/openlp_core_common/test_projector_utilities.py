# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2015 OpenLP Developers                                   #
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
Package to test the openlp.core.ui.projector.networkutils package.
"""

import os

from unittest import TestCase

from openlp.core.common import verify_ip_address, md5_hash, qmd5_hash, md5_filecheck, sha1_filecheck

TEST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                         '..', '..', 'resources', 'projector'))
TEST_FILENAME = 'Wheat.otz'
TEST_FILE_HASH = '2d7daae6f8ce6dc0963ea8c0fa4d67aa'
TEST_FILE_SHA1 = '20a2ca97a479d166ac9f59147054b58304b4d264'

salt = '498e4a67'
pin = 'JBMIAProjectorLink'
test_hash = '5d8409bc1c3fa39749434aa3a5c38682'

ip4_loopback = '127.0.0.1'
ip4_local = '192.168.1.1'
ip4_broadcast = '255.255.255.255'
ip4_bad = '192.168.1.256'

ip6_loopback = '::1'
ip6_link_local = 'fe80::223:14ff:fe99:d315'
ip6_bad = 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff'


class testProjectorUtilities(TestCase):
    """
    Validate functions in the projector utilities module
    """
    def test_ip4_loopback_valid(self):
        """
        Test IPv4 loopbackvalid
        """
        # WHEN: Test with a local loopback test
        valid = verify_ip_address(addr=ip4_loopback)

        # THEN: Verify we received True
        self.assertTrue(valid, 'IPv4 loopback address should have been valid')

    def test_ip4_local_valid(self):
        """
        Test IPv4 local valid
        """
        # WHEN: Test with a local loopback test
        valid = verify_ip_address(addr=ip4_local)

        # THEN: Verify we received True
        self.assertTrue(valid, 'IPv4 local address should have been valid')

    def test_ip4_broadcast_valid(self):
        """
        Test IPv4 broadcast valid
        """
        # WHEN: Test with a local loopback test
        valid = verify_ip_address(addr=ip4_broadcast)

        # THEN: Verify we received True
        self.assertTrue(valid, 'IPv4 broadcast address should have been valid')

    def test_ip4_address_invalid(self):
        """
        Test IPv4 address invalid
        """
        # WHEN: Test with a local loopback test
        valid = verify_ip_address(addr=ip4_bad)

        # THEN: Verify we received True
        self.assertFalse(valid, 'Bad IPv4 address should not have been valid')

    def test_ip6_loopback_valid(self):
        """
        Test IPv6 loopback valid
        """
        # WHEN: Test IPv6 loopback address
        valid = verify_ip_address(addr=ip6_loopback)

        # THEN: Validate return
        self.assertTrue(valid, 'IPv6 loopback address should have been valid')

    def test_ip6_local_valid(self):
        """
        Test IPv6 link-local valid
        """
        # WHEN: Test IPv6 link-local address
        valid = verify_ip_address(addr=ip6_link_local)

        # THEN: Validate return
        self.assertTrue(valid, 'IPv6 link-local address should have been valid')

    def test_ip6_address_invalid(self):
        """
        Test NetworkUtils IPv6 address invalid
        """
        # WHEN: Given an invalid IPv6 address
        valid = verify_ip_address(addr=ip6_bad)

        # THEN: Validate bad return
        self.assertFalse(valid, 'IPv6 bad address should have been invalid')

    def test_md5_hash(self):
        """
        Test MD5 hash from salt+data pass (python)
        """
        # WHEN: Given a known salt+data
        hash_ = md5_hash(salt=salt.encode('ascii'), data=pin.encode('ascii'))

        # THEN: Validate return has is same
        self.assertEquals(hash_, test_hash, 'MD5 should have returned a good hash')

    def test_md5_hash_bad(self):
        """
        Test MD5 hash from salt+data fail (python)
        """
        # WHEN: Given a different salt+hash
        hash_ = md5_hash(salt=pin.encode('ascii'), data=salt.encode('ascii'))

        # THEN: return data is different
        self.assertNotEquals(hash_, test_hash, 'MD5 should have returned a bad hash')

    def test_qmd5_hash(self):
        """
        Test MD5 hash from salt+data pass (Qt)
        """
        # WHEN: Given a known salt+data
        hash_ = qmd5_hash(salt=salt, data=pin)

        # THEN: Validate return has is same
        self.assertEquals(hash_.decode('ascii'), test_hash, 'Qt-MD5 should have returned a good hash')

    def test_qmd5_hash_bad(self):
        """
        Test MD5 hash from salt+hash fail (Qt)
        """
        # WHEN: Given a different salt+hash
        hash_ = qmd5_hash(salt=pin, data=salt)

        # THEN: return data is different
        self.assertNotEquals(hash_.decode('ascii'), test_hash, 'Qt-MD5 should have returned a bad hash')

    def md5sum_filecheck_test(self):
        """
        Test file MD5SUM check
        """
        # GIVEN: Test file to verify
        test_file = os.path.join(TEST_PATH, TEST_FILENAME)

        # WHEN: md5_filecheck is called
        valid = md5_filecheck(test_file, TEST_FILE_HASH)

        # THEN: Check should pass
        self.assertEqual(valid, True, 'Test file MD5 should match test MD5')

    def sa1sum_filecheck_test(self):
        """
        Test file SHA1SUM check
        """
        # GIVEN: Test file to verify
        test_file = os.path.join(TEST_PATH, TEST_FILENAME)

        # WHEN: md5_filecheck is called
        valid = sha1_filecheck(test_file, TEST_FILE_SHA1)

        # THEN: Check should pass
        self.assertEqual(valid, True, 'Test file SHA1 should match test SHA1')
