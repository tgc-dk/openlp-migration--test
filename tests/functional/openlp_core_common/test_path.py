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
Package to test the openlp.core.common.path package.
"""
import os
from pathlib import Path
from unittest import TestCase

from openlp.core.common.path import path_to_str, str_to_path


class TestPath(TestCase):
    """
    Tests for the :mod:`openlp.core.common.path` module
    """

    def test_path_to_str_type_error(self):
        """
        Test that `path_to_str` raises a type error when called with an invalid type
        """
        # GIVEN: The `path_to_str` function
        # WHEN: Calling `path_to_str` with an invalid Type
        # THEN: A TypeError should have been raised
        with self.assertRaises(TypeError):
            path_to_str(str())

    def test_path_to_str_none(self):
        """
        Test that `path_to_str` correctly converts the path parameter when passed with None
        """
        # GIVEN: The `path_to_str` function
        # WHEN: Calling the `path_to_str` function with None
        result = path_to_str(None)

        # THEN: `path_to_str` should return an empty string
        self.assertEqual(result, '')

    def test_path_to_str_path_object(self):
        """
        Test that `path_to_str` correctly converts the path parameter when passed a Path object
        """
        # GIVEN: The `path_to_str` function
        # WHEN: Calling the `path_to_str` function with a Path object
        result = path_to_str(Path('test/path'))

        # THEN: `path_to_str` should return a string representation of the Path object
        self.assertEqual(result, os.path.join('test', 'path'))

    def test_str_to_path_type_error(self):
        """
        Test that `str_to_path` raises a type error when called with an invalid type
        """
        # GIVEN: The `str_to_path` function
        # WHEN: Calling `str_to_path` with an invalid Type
        # THEN: A TypeError should have been raised
        with self.assertRaises(TypeError):
            str_to_path(Path())

    def test_str_to_path_empty_str(self):
        """
        Test that `str_to_path` correctly converts the string parameter when passed with and empty string
        """
        # GIVEN: The `str_to_path` function
        # WHEN: Calling the `str_to_path` function with None
        result = str_to_path('')

        # THEN: `path_to_str` should return None
        self.assertEqual(result, None)
