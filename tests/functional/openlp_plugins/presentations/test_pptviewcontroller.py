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
This module contains tests for the pptviewcontroller module of the Presentations plugin.
"""
import shutil
from tempfile import mkdtemp
from unittest import TestCase, skipIf
from unittest.mock import MagicMock, patch

from openlp.core.common import is_win
from openlp.core.common.path import Path
from openlp.plugins.presentations.lib.pptviewcontroller import PptviewDocument, PptviewController
from tests.helpers.testmixin import TestMixin
from tests.utils.constants import TEST_RESOURCES_PATH


class TestPptviewController(TestCase, TestMixin):
    """
    Test the PptviewController Class
    """
    def setUp(self):
        """
        Set up the patches and mocks need for all tests.
        """
        self.setup_application()
        self.build_settings()
        self.mock_plugin = MagicMock()
        self.temp_folder = mkdtemp()
        self.mock_plugin.settings_section = self.temp_folder

    def tearDown(self):
        """
        Stop the patches
        """
        self.destroy_settings()
        shutil.rmtree(self.temp_folder)

    def test_constructor(self):
        """
        Test the Constructor from the PptViewController
        """
        # GIVEN: No presentation controller
        controller = None

        # WHEN: The presentation controller object is created
        controller = PptviewController(plugin=self.mock_plugin)

        # THEN: The name of the presentation controller should be correct
        assert 'Powerpoint Viewer' == controller.name, 'The name of the presentation controller should be correct'

    def test_check_available(self):
        """
        Test check_available / check_installed
        """
        # GIVEN: A mocked dll loader and a controller
        with patch('ctypes.cdll.LoadLibrary') as mocked_load_library:
            mocked_process = MagicMock()
            mocked_process.CheckInstalled.return_value = True
            mocked_load_library.return_value = mocked_process
            controller = PptviewController(plugin=self.mock_plugin)

            # WHEN: check_available is called
            available = controller.check_available()

            # THEN: On windows it should return True, on other platforms False
            if is_win():
                assert available is True, 'check_available should return True on windows.'
            else:
                assert available is False, 'check_available should return False when not on windows.'


class TestPptviewDocument(TestCase):
    """
    Test the PptviewDocument Class
    """
    def setUp(self):
        """
        Set up the patches and mocks need for all tests.
        """
        self.pptview_document_create_thumbnails_patcher = patch(
            'openlp.plugins.presentations.lib.pptviewcontroller.PptviewDocument.create_thumbnails')
        self.pptview_document_stop_presentation_patcher = patch(
            'openlp.plugins.presentations.lib.pptviewcontroller.PptviewDocument.stop_presentation')
        self.presentation_document_get_temp_folder_patcher = patch(
            'openlp.plugins.presentations.lib.pptviewcontroller.PresentationDocument.get_temp_folder')
        self.presentation_document_setup_patcher = patch(
            'openlp.plugins.presentations.lib.pptviewcontroller.PresentationDocument._setup')
        self.screen_list_patcher = patch('openlp.plugins.presentations.lib.pptviewcontroller.ScreenList')
        self.rect_patcher = MagicMock()
        self.mock_pptview_document_create_thumbnails = self.pptview_document_create_thumbnails_patcher.start()
        self.mock_pptview_document_stop_presentation = self.pptview_document_stop_presentation_patcher.start()
        self.mock_presentation_document_get_temp_folder = self.presentation_document_get_temp_folder_patcher.start()
        self.mock_presentation_document_setup = self.presentation_document_setup_patcher.start()
        self.mock_rect = self.rect_patcher.start()
        self.mock_screen_list = self.screen_list_patcher.start()
        self.mock_controller = MagicMock()
        self.mock_presentation = MagicMock()
        self.temp_folder = mkdtemp()
        self.mock_presentation_document_get_temp_folder.return_value = self.temp_folder

    def tearDown(self):
        """
        Stop the patches
        """
        self.pptview_document_create_thumbnails_patcher.stop()
        self.pptview_document_stop_presentation_patcher.stop()
        self.presentation_document_get_temp_folder_patcher.stop()
        self.presentation_document_setup_patcher.stop()
        self.rect_patcher.stop()
        self.screen_list_patcher.stop()
        shutil.rmtree(self.temp_folder)

    @skipIf(not is_win(), 'Not Windows')
    def test_load_presentation_succesful(self):
        """
        Test the PptviewDocument.load_presentation() method when the PPT is successfully opened
        """
        # GIVEN: A reset mocked_os
        self.mock_controller.process.OpenPPT.return_value = 0
        instance = PptviewDocument(self.mock_controller, self.mock_presentation)
        instance.file_path = 'test\path.ppt'

        # WHEN: The temporary directory exists and OpenPPT returns successfully (not -1)
        result = instance.load_presentation()

        # THEN: PptviewDocument.load_presentation should return True
        assert result is True

    @skipIf(not is_win(), 'Not Windows')
    def test_load_presentation_un_succesful(self):
        """
        Test the PptviewDocument.load_presentation() method when the temporary directory does not exist and the PPT is
        not successfully opened
        """
        # GIVEN: A reset mock_os_isdir
        self.mock_controller.process.OpenPPT.return_value = -1
        instance = PptviewDocument(self.mock_controller, self.mock_presentation)
        instance.file_path = 'test\path.ppt'

        # WHEN: The temporary directory does not exist and OpenPPT returns unsuccessfully (-1)
        with patch.object(instance, 'get_temp_folder') as mocked_get_folder:
            mocked_get_folder.return_value = MagicMock(spec=Path)
            result = instance.load_presentation()

        # THEN: The temp folder should be created and PptviewDocument.load_presentation should return False
        assert result is False

    def test_create_titles_and_notes(self):
        """
        Test PowerpointController.create_titles_and_notes
        """
        # GIVEN: mocked PresentationController.save_titles_and_notes and a pptx file
        doc = PptviewDocument(self.mock_controller, self.mock_presentation)
        doc.file_path = Path(TEST_RESOURCES_PATH, 'presentations', 'test.pptx')
        doc.save_titles_and_notes = MagicMock()

        # WHEN reading the titles and notes
        doc.create_titles_and_notes()

        # THEN save_titles_and_notes should have been called once with empty arrays
        doc.save_titles_and_notes.assert_called_once_with(['Test 1\n', '\n', 'Test 2\n', 'Test 4\n', 'Test 3\n'],
                                                          ['Notes for slide 1', 'Inserted', 'Notes for slide 2',
                                                           'Notes \nfor slide 4', 'Notes for slide 3'])

    def test_create_titles_and_notes_nonexistent_file(self):
        """
        Test PowerpointController.create_titles_and_notes with nonexistent file
        """
        # GIVEN: mocked PresentationController.save_titles_and_notes and an nonexistent file
        with patch('builtins.open') as mocked_open, \
                patch.object(Path, 'exists') as mocked_path_exists, \
                patch('openlp.plugins.presentations.lib.presentationcontroller.create_paths') as \
                mocked_dir_exists:
            mocked_path_exists.return_value = False
            mocked_dir_exists.return_value = False
            doc = PptviewDocument(self.mock_controller, self.mock_presentation)
            doc.file_path = Path('Idontexist.pptx')
            doc.save_titles_and_notes = MagicMock()

            # WHEN: Reading the titles and notes
            doc.create_titles_and_notes()

            # THEN: File existens should have been checked, and not have been opened.
            doc.save_titles_and_notes.assert_called_once_with(None, None)
            mocked_path_exists.assert_called_with()
            assert mocked_open.call_count == 0, 'There should be no calls to open a file.'

    def test_create_titles_and_notes_invalid_file(self):
        """
        Test PowerpointController.create_titles_and_notes with invalid file
        """
        # GIVEN: mocked PresentationController.save_titles_and_notes and an invalid file
        with patch('builtins.open') as mocked_open, \
                patch('openlp.plugins.presentations.lib.pptviewcontroller.zipfile.is_zipfile') as mocked_is_zf:
            mocked_is_zf.return_value = False
            mocked_open.filesize = 10
            doc = PptviewDocument(self.mock_controller, self.mock_presentation)
            doc.file_path = Path(TEST_RESOURCES_PATH, 'presentations', 'test.ppt')
            doc.save_titles_and_notes = MagicMock()

            # WHEN: reading the titles and notes
            doc.create_titles_and_notes()

            # THEN:
            doc.save_titles_and_notes.assert_called_once_with(None, None)
            assert mocked_is_zf.call_count == 1, 'is_zipfile should have been called once'
