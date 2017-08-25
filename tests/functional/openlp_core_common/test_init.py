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
Functional tests to test the AppLocation class and related methods.
"""
import os
from io import BytesIO
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, PropertyMock, call, patch

from openlp.core.common import add_actions, clean_filename, delete_file, get_file_encoding, get_filesystem_encoding,  \
    get_uno_command, get_uno_instance, split_filename

from tests.helpers.testmixin import TestMixin


class TestInit(TestCase, TestMixin):
    """
    A test suite to test out various methods around the common __init__ class.
    """

    def setUp(self):
        """
        Create an instance and a few example actions.
        """
        self.build_settings()

    def tearDown(self):
        """
        Clean up
        """
        self.destroy_settings()

    def test_add_actions_empty_list(self):
        """
        Test that no actions are added when the list is empty
        """
        # GIVEN: a mocked action list, and an empty list
        mocked_target = MagicMock()
        empty_list = []

        # WHEN: The empty list is added to the mocked target
        add_actions(mocked_target, empty_list)

        # THEN: The add method on the mocked target is never called
        self.assertEqual(0, mocked_target.addSeparator.call_count, 'addSeparator method should not have been called')
        self.assertEqual(0, mocked_target.addAction.call_count, 'addAction method should not have been called')

    def test_add_actions_none_action(self):
        """
        Test that a separator is added when a None action is in the list
        """
        # GIVEN: a mocked action list, and a list with None in it
        mocked_target = MagicMock()
        separator_list = [None]

        # WHEN: The list is added to the mocked target
        add_actions(mocked_target, separator_list)

        # THEN: The addSeparator method is called, but the addAction method is never called
        mocked_target.addSeparator.assert_called_with()
        self.assertEqual(0, mocked_target.addAction.call_count, 'addAction method should not have been called')

    def test_add_actions_add_action(self):
        """
        Test that an action is added when a valid action is in the list
        """
        # GIVEN: a mocked action list, and a list with an action in it
        mocked_target = MagicMock()
        action_list = ['action']

        # WHEN: The list is added to the mocked target
        add_actions(mocked_target, action_list)

        # THEN: The addSeparator method is not called, and the addAction method is called
        self.assertEqual(0, mocked_target.addSeparator.call_count, 'addSeparator method should not have been called')
        mocked_target.addAction.assert_called_with('action')

    def test_add_actions_action_and_none(self):
        """
        Test that an action and a separator are added when a valid action and None are in the list
        """
        # GIVEN: a mocked action list, and a list with an action and None in it
        mocked_target = MagicMock()
        action_list = ['action', None]

        # WHEN: The list is added to the mocked target
        add_actions(mocked_target, action_list)

        # THEN: The addSeparator method is called, and the addAction method is called
        mocked_target.addSeparator.assert_called_with()
        mocked_target.addAction.assert_called_with('action')

    def test_get_uno_instance_pipe(self):
        """
        Test that when the UNO connection type is "pipe" the resolver is given the "pipe" URI
        """
        # GIVEN: A mock resolver object and UNO_CONNECTION_TYPE is "pipe"
        mock_resolver = MagicMock()

        # WHEN: get_uno_instance() is called
        get_uno_instance(mock_resolver)

        # THEN: the resolve method is called with the correct argument
        mock_resolver.resolve.assert_called_with('uno:pipe,name=openlp_pipe;urp;StarOffice.ComponentContext')

    def test_get_uno_instance_socket(self):
        """
        Test that when the UNO connection type is other than "pipe" the resolver is given the "socket" URI
        """
        # GIVEN: A mock resolver object and UNO_CONNECTION_TYPE is "socket"
        mock_resolver = MagicMock()

        # WHEN: get_uno_instance() is called
        get_uno_instance(mock_resolver, 'socket')

        # THEN: the resolve method is called with the correct argument
        mock_resolver.resolve.assert_called_with('uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext')

    def test_get_uno_command_libreoffice_command_exists(self):
        """
        Test the ``get_uno_command`` function uses the libreoffice command when available.
        :return:
        """

        # GIVEN: A patched 'which' method which returns a path when called with 'libreoffice'
        with patch('openlp.core.common.which',
                   **{'side_effect': lambda command: {'libreoffice': '/usr/bin/libreoffice'}[command]}):
            # WHEN: Calling get_uno_command
            result = get_uno_command()

            # THEN: The command 'libreoffice' should be called with the appropriate parameters
            self.assertEquals(result,
                              'libreoffice --nologo --norestore --minimized --nodefault --nofirststartwizard'
                              ' "--accept=pipe,name=openlp_pipe;urp;"')

    def test_get_uno_command_only_soffice_command_exists(self):
        """
        Test the ``get_uno_command`` function uses the soffice command when the libreoffice command is not available.
        :return:
        """

        # GIVEN: A patched 'which' method which returns None when called with 'libreoffice' and a path when called with
        #        'soffice'
        with patch('openlp.core.common.which',
                   **{'side_effect': lambda command: {'libreoffice': None, 'soffice': '/usr/bin/soffice'}[
                       command]}):
            # WHEN: Calling get_uno_command
            result = get_uno_command()

            # THEN: The command 'soffice' should be called with the appropriate parameters
            self.assertEquals(result, 'soffice --nologo --norestore --minimized --nodefault --nofirststartwizard'
                                      ' "--accept=pipe,name=openlp_pipe;urp;"')

    def test_get_uno_command_when_no_command_exists(self):
        """
        Test the ``get_uno_command`` function raises an FileNotFoundError when neither the libreoffice or soffice
        commands are available.
        :return:
        """

        # GIVEN: A patched 'which' method which returns None
        with patch('openlp.core.common.which', **{'return_value': None}):
            # WHEN: Calling get_uno_command

            # THEN: a FileNotFoundError exception should be raised
            self.assertRaises(FileNotFoundError, get_uno_command)

    def test_get_uno_command_connection_type(self):
        """
        Test the ``get_uno_command`` function when the connection type is anything other than pipe.
        :return:
        """

        # GIVEN: A patched 'which' method which returns 'libreoffice'
        with patch('openlp.core.common.which', **{'return_value': 'libreoffice'}):
            # WHEN: Calling get_uno_command with a connection type other than pipe
            result = get_uno_command('socket')

            # THEN: The connection parameters should be set for socket
            self.assertEqual(result, 'libreoffice --nologo --norestore --minimized --nodefault --nofirststartwizard'
                                     ' "--accept=socket,host=localhost,port=2002;urp;"')

    def test_get_filesystem_encoding_sys_function_not_called(self):
        """
        Test the get_filesystem_encoding() function does not call the sys.getdefaultencoding() function
        """
        # GIVEN: sys.getfilesystemencoding returns "cp1252"
        with patch('openlp.core.common.sys.getfilesystemencoding') as mocked_getfilesystemencoding, \
                patch('openlp.core.common.sys.getdefaultencoding') as mocked_getdefaultencoding:
            mocked_getfilesystemencoding.return_value = 'cp1252'

            # WHEN: get_filesystem_encoding() is called
            result = get_filesystem_encoding()

            # THEN: getdefaultencoding should have been called
            mocked_getfilesystemencoding.assert_called_with()
            self.assertEqual(0, mocked_getdefaultencoding.called, 'getdefaultencoding should not have been called')
            self.assertEqual('cp1252', result, 'The result should be "cp1252"')

    def test_get_filesystem_encoding_sys_function_is_called(self):
        """
        Test the get_filesystem_encoding() function calls the sys.getdefaultencoding() function
        """
        # GIVEN: sys.getfilesystemencoding returns None and sys.getdefaultencoding returns "utf-8"
        with patch('openlp.core.common.sys.getfilesystemencoding') as mocked_getfilesystemencoding, \
                patch('openlp.core.common.sys.getdefaultencoding') as mocked_getdefaultencoding:
            mocked_getfilesystemencoding.return_value = None
            mocked_getdefaultencoding.return_value = 'utf-8'

            # WHEN: get_filesystem_encoding() is called
            result = get_filesystem_encoding()

            # THEN: getdefaultencoding should have been called
            mocked_getfilesystemencoding.assert_called_with()
            mocked_getdefaultencoding.assert_called_with()
            self.assertEqual('utf-8', result, 'The result should be "utf-8"')

    def test_split_filename_with_file_path(self):
        """
        Test the split_filename() function with a path to a file
        """
        # GIVEN: A path to a file.
        if os.name == 'nt':
            file_path = 'C:\\home\\user\\myfile.txt'
            wanted_result = ('C:\\home\\user', 'myfile.txt')
        else:
            file_path = '/home/user/myfile.txt'
            wanted_result = ('/home/user', 'myfile.txt')
        with patch('openlp.core.common.os.path.isfile') as mocked_is_file:
            mocked_is_file.return_value = True

            # WHEN: Split the file name.
            result = split_filename(file_path)

            # THEN: A tuple should be returned.
            self.assertEqual(wanted_result, result, 'A tuple with the dir and file name should have been returned')

    def test_split_filename_with_dir_path(self):
        """
        Test the split_filename() function with a path to a directory
        """
        # GIVEN: A path to a dir.
        if os.name == 'nt':
            file_path = 'C:\\home\\user\\mydir'
            wanted_result = ('C:\\home\\user\\mydir', '')
        else:
            file_path = '/home/user/mydir'
            wanted_result = ('/home/user/mydir', '')
        with patch('openlp.core.common.os.path.isfile') as mocked_is_file:
            mocked_is_file.return_value = False

            # WHEN: Split the file name.
            result = split_filename(file_path)

            # THEN: A tuple should be returned.
            self.assertEqual(wanted_result, result,
                             'A two-entry tuple with the directory and file name (empty) should have been returned.')

    def test_clean_filename(self):
        """
        Test the clean_filename() function
        """
        # GIVEN: A invalid file name and the valid file name.
        invalid_name = 'A_file_with_invalid_characters_[\\/:\*\?"<>\|\+\[\]%].py'
        wanted_name = 'A_file_with_invalid_characters______________________.py'

        # WHEN: Clean the name.
        result = clean_filename(invalid_name)

        # THEN: The file name should be cleaned.
        self.assertEqual(wanted_name, result, 'The file name should not contain any special characters.')

    def test_delete_file_no_path(self):
        """
        Test the delete_file function when called with out a valid path
        """
        # GIVEN: A blank path
        # WEHN: Calling delete_file
        result = delete_file(None)

        # THEN: delete_file should return False
        self.assertFalse(result, "delete_file should return False when called with None")

    def test_delete_file_path_success(self):
        """
        Test the delete_file function when it successfully deletes a file
        """
        # GIVEN: A mocked os which returns True when os.path.exists is called
        with patch('openlp.core.common.os', **{'path.exists.return_value': False}):

            # WHEN: Calling delete_file with a file path
            result = delete_file(Path('path', 'file.ext'))

            # THEN: delete_file should return True
            self.assertTrue(result, 'delete_file should return True when it successfully deletes a file')

    def test_delete_file_path_no_file_exists(self):
        """
        Test the `delete_file` function when the file to remove does not exist
        """
        # GIVEN: A patched `exists` methods on the Path object, which returns False
        with patch.object(Path, 'exists', return_value=False), \
                patch.object(Path, 'unlink') as mocked_unlink:

            # WHEN: Calling `delete_file with` a file path
            result = delete_file(Path('path', 'file.ext'))

            # THEN: The function should not attempt to delete the file and it should return True
            self.assertFalse(mocked_unlink.called)
            self.assertTrue(result, 'delete_file should return True when the file doesnt exist')

    def test_delete_file_path_exception(self):
        """
        Test the delete_file function when an exception is raised
        """
        # GIVEN: A test `Path` object with a patched exists method which raises an OSError
        #       called.
        with patch.object(Path, 'exists') as mocked_exists, \
                patch('openlp.core.common.log') as mocked_log:
            mocked_exists.side_effect = OSError

            # WHEN: Calling delete_file with a the test Path object
            result = delete_file(Path('path', 'file.ext'))

            # THEN: The exception should be logged and `delete_file` should return False
            self.assertTrue(mocked_log.exception.called)
            self.assertFalse(result, 'delete_file should return False when an OSError is raised')

    def test_get_file_encoding_done_test(self):
        """
        Test get_file_encoding when the detector sets done to True
        """
        # GIVEN: A mocked UniversalDetector instance with done attribute set to True after first iteration
        with patch('openlp.core.common.UniversalDetector') as mocked_universal_detector, \
                patch.object(Path, 'open', return_value=BytesIO(b"data" * 260)) as mocked_open:
            encoding_result = {'encoding': 'UTF-8', 'confidence': 0.99}
            mocked_universal_detector_inst = MagicMock(result=encoding_result)
            type(mocked_universal_detector_inst).done = PropertyMock(side_effect=[False, True])
            mocked_universal_detector.return_value = mocked_universal_detector_inst

            # WHEN: Calling get_file_encoding
            result = get_file_encoding(Path('file name'))

            # THEN: The feed method of UniversalDetector should only br called once before returning a result
            mocked_open.assert_called_once_with('rb')
            self.assertEqual(mocked_universal_detector_inst.feed.mock_calls, [call(b"data" * 256)])
            mocked_universal_detector_inst.close.assert_called_once_with()
            self.assertEqual(result, encoding_result)

    def test_get_file_encoding_eof_test(self):
        """
        Test get_file_encoding when the end of the file is reached
        """
        # GIVEN: A mocked UniversalDetector instance which isn't set to done and a mocked open, with 1040 bytes of test
        #       data (enough to run the iterator twice)
        with patch('openlp.core.common.UniversalDetector') as mocked_universal_detector, \
                patch.object(Path, 'open', return_value=BytesIO(b"data" * 260)) as mocked_open:
            encoding_result = {'encoding': 'UTF-8', 'confidence': 0.99}
            mocked_universal_detector_inst = MagicMock(mock=mocked_universal_detector,
                                                       **{'done': False, 'result': encoding_result})
            mocked_universal_detector.return_value = mocked_universal_detector_inst

            # WHEN: Calling get_file_encoding
            result = get_file_encoding(Path('file name'))

            # THEN: The feed method of UniversalDetector should have been called twice before returning a result
            mocked_open.assert_called_once_with('rb')
            self.assertEqual(mocked_universal_detector_inst.feed.mock_calls, [call(b"data" * 256), call(b"data" * 4)])
            mocked_universal_detector_inst.close.assert_called_once_with()
            self.assertEqual(result, encoding_result)

    def test_get_file_encoding_oserror_test(self):
        """
        Test get_file_encoding when the end of the file is reached
        """
        # GIVEN: A mocked UniversalDetector instance which isn't set to done and a mocked open, with 1040 bytes of test
        #       data (enough to run the iterator twice)
        with patch('openlp.core.common.UniversalDetector'), \
                patch('builtins.open', side_effect=OSError), \
                patch('openlp.core.common.log') as mocked_log:

            # WHEN: Calling get_file_encoding
            result = get_file_encoding(Path('file name'))

            # THEN: log.exception should be called and get_file_encoding should return None
            mocked_log.exception.assert_called_once_with('Error detecting file encoding')
            self.assertIsNone(result)
