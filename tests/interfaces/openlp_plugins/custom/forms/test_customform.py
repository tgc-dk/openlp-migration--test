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
Module to test the EditCustomForm.
"""
from unittest import TestCase
from unittest.mock import MagicMock, patch

from PyQt5 import QtTest, QtCore, QtWidgets

from openlp.core.common.registry import Registry
from openlp.plugins.custom.forms.editcustomform import EditCustomForm
from tests.helpers.testmixin import TestMixin


class TestEditCustomForm(TestCase, TestMixin):
    """
    Test the EditCustomForm.
    """
    def setUp(self):
        """
        Create the UI
        """
        Registry.create()
        self.setup_application()
        self.main_window = QtWidgets.QMainWindow()
        Registry().register('main_window', self.main_window)
        media_item = MagicMock()
        manager = MagicMock()
        self.form = EditCustomForm(media_item, self.main_window, manager)

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.form
        del self.main_window

    def test_load_themes(self):
        """
        Test the load_themes() method.
        """
        # GIVEN: A theme list.
        theme_list = ['First Theme', 'Second Theme']

        # WHEN: Show the dialog and add pass a theme list.
        self.form.load_themes(theme_list)

        # THEN: There should be three items in the combo box.
        assert self.form.theme_combo_box.count() == 3, 'There should be three items (themes) in the combo box.'

    def test_load_custom(self):
        """
        Test the load_custom() method.
        """
        # WHEN: Create a new custom item.
        self.form.load_custom(0)

        # THEN: The line edits should not contain any text.
        assert self.form.title_edit.text() == '', 'The title edit should be empty'
        assert self.form.credit_edit.text() == '', 'The credit edit should be empty'

    def test_on_add_button_clicked(self):
        """
        Test the on_add_button_clicked_test method / add_button button.
        """
        # GIVEN: A mocked QDialog.exec() method
        with patch('PyQt5.QtWidgets.QDialog.exec') as mocked_exec:
            # WHEN: Add a new slide.
            QtTest.QTest.mouseClick(self.form.add_button, QtCore.Qt.LeftButton)

            # THEN: One slide should be added.
            assert self.form.slide_list_view.count() == 1, 'There should be one slide added.'

    def test_validate_not_valid_part1(self):
        """
        Test the _validate() method.
        """
        # GIVEN: Mocked methods.
        with patch('openlp.plugins.custom.forms.editcustomform.critical_error_message_box') as \
                mocked_critical_error_message_box:
            self.form.title_edit.displayText = MagicMock(return_value='')
            mocked_setFocus = MagicMock()
            self.form.title_edit.setFocus = mocked_setFocus

            # WHEN: Call the method.
            result = self.form._validate()

            # THEN: The validate method should have returned False.
            assert not result, 'The _validate() method should have retured False'
            mocked_setFocus.assert_called_with()
            mocked_critical_error_message_box.assert_called_with(message='You need to type in a title.')

    def test_validate_not_valid_part2(self):
        """
        Test the _validate() method.
        """
        # GIVEN: Mocked methods.
        with patch('openlp.plugins.custom.forms.editcustomform.critical_error_message_box') as \
                mocked_critical_error_message_box:
            self.form.title_edit.displayText = MagicMock(return_value='something')
            self.form.slide_list_view.count = MagicMock(return_value=0)

            # WHEN: Call the method.
            result = self.form._validate()

            # THEN: The validate method should have returned False.
            assert not result, 'The _validate() method should have retured False'
            mocked_critical_error_message_box.assert_called_with(message='You need to add at least one slide.')

    def test_update_slide_list(self):
        """
        Test the update_slide_list() method
        """
        # GIVEN: Mocked slide_list_view with a slide with 3 lines
        self.form.slide_list_view = MagicMock()
        self.form.slide_list_view.count.return_value = 1
        self.form.slide_list_view.currentRow.return_value = 0
        self.form.slide_list_view.item.return_value = MagicMock(return_value='1st Slide\n2nd Slide\n3rd Slide')

        # WHEN: updating the slide by splitting the lines into slides
        self.form.update_slide_list(['1st Slide', '2nd Slide', '3rd Slide'])

        # THEN: The slides should be created in correct order
        self.form.slide_list_view.addItems.assert_called_with(['1st Slide', '2nd Slide', '3rd Slide'])
