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
Package to test the openlp.core.lib.ui package.
"""
from unittest import TestCase
from unittest.mock import MagicMock, patch

from PyQt5 import QtCore, QtGui, QtWidgets

from openlp.core.common.i18n import UiStrings, translate
from openlp.core.lib.ui import add_welcome_page, create_button_box, create_horizontal_adjusting_combo_box, \
    create_button, create_action, create_valign_selection_widgets, find_and_set_in_combo_box, create_widget_action, \
    set_case_insensitive_completer


class TestUi(TestCase):
    """
    Test the functions in the ui module
    """

    def test_add_welcome_page(self):
        """
        Test appending a welcome page to a wizard
        """
        # GIVEN: A wizard
        wizard = QtWidgets.QWizard()

        # WHEN: A welcome page has been added to the wizard
        add_welcome_page(wizard, ':/wizards/wizard_firsttime.bmp')

        # THEN: The wizard should have one page with a pixmap.
        self.assertEqual(1, len(wizard.pageIds()), 'The wizard should have one page.')
        self.assertIsInstance(wizard.page(0).pixmap(QtWidgets.QWizard.WatermarkPixmap), QtGui.QPixmap)

    def test_create_button_box(self):
        """
        Test creating a button box for a dialog
        """
        # GIVEN: A dialog
        dialog = QtWidgets.QDialog()

        # WHEN: We create the button box with five buttons
        btnbox = create_button_box(dialog, 'my_btns', ['ok', 'save', 'cancel', 'close', 'defaults'])

        # THEN: We should get a QDialogButtonBox with five buttons
        self.assertIsInstance(btnbox, QtWidgets.QDialogButtonBox)
        self.assertEqual(5, len(btnbox.buttons()))

        # WHEN: We create the button box with a custom button
        btnbox = create_button_box(dialog, 'my_btns', None, [QtWidgets.QPushButton('Custom')])
        # THEN: We should get a QDialogButtonBox with one button
        self.assertIsInstance(btnbox, QtWidgets.QDialogButtonBox)
        self.assertEqual(1, len(btnbox.buttons()))

        # WHEN: We create the button box with a custom button and a custom role
        btnbox = create_button_box(dialog, 'my_btns', None,
                                   [(QtWidgets.QPushButton('Help'), QtWidgets.QDialogButtonBox.HelpRole)])
        # THEN: We should get a QDialogButtonBox with one button with a certain role
        self.assertIsInstance(btnbox, QtWidgets.QDialogButtonBox)
        self.assertEqual(1, len(btnbox.buttons()))
        self.assertEqual(QtWidgets.QDialogButtonBox.HelpRole, btnbox.buttonRole(btnbox.buttons()[0]))

    def test_create_horizontal_adjusting_combo_box(self):
        """
        Test creating a horizontal adjusting combo box
        """
        # GIVEN: A dialog
        dialog = QtWidgets.QDialog()

        # WHEN: We create the combobox
        combo = create_horizontal_adjusting_combo_box(dialog, 'combo1')

        # THEN: We should get a ComboBox
        self.assertIsInstance(combo, QtWidgets.QComboBox)
        self.assertEqual('combo1', combo.objectName())
        self.assertEqual(QtWidgets.QComboBox.AdjustToMinimumContentsLength, combo.sizeAdjustPolicy())

    def test_create_button(self):
        """
        Test creating a button
        """
        # GIVEN: A dialog
        dialog = QtWidgets.QDialog()

        # WHEN: We create the button
        btn = create_button(dialog, 'my_btn')

        # THEN: We should get a button with a name
        self.assertIsInstance(btn, QtWidgets.QPushButton)
        self.assertEqual('my_btn', btn.objectName())
        self.assertTrue(btn.isEnabled())

        # WHEN: We create a button with some attributes
        btn = create_button(dialog, 'my_btn', text='Hello', tooltip='How are you?', enabled=False)

        # THEN: We should get a button with those attributes
        self.assertIsInstance(btn, QtWidgets.QPushButton)
        self.assertEqual('Hello', btn.text())
        self.assertEqual('How are you?', btn.toolTip())
        self.assertFalse(btn.isEnabled())

        # WHEN: We create a toolbutton
        btn = create_button(dialog, 'my_btn', btn_class='toolbutton')

        # THEN: We should get a toolbutton
        self.assertIsInstance(btn, QtWidgets.QToolButton)
        self.assertEqual('my_btn', btn.objectName())
        self.assertTrue(btn.isEnabled())

    def test_create_action(self):
        """
        Test creating an action
        """
        # GIVEN: A dialog
        dialog = QtWidgets.QDialog()

        # WHEN: We create an action
        action = create_action(dialog, 'my_action')

        # THEN: We should get a QAction
        self.assertIsInstance(action, QtWidgets.QAction)
        self.assertEqual('my_action', action.objectName())

        # WHEN: We create an action with some properties
        action = create_action(dialog, 'my_action', text='my text', icon=':/wizards/wizard_firsttime.bmp',
                               tooltip='my tooltip', statustip='my statustip')

        # THEN: These properties should be set
        self.assertIsInstance(action, QtWidgets.QAction)
        self.assertEqual('my text', action.text())
        self.assertIsInstance(action.icon(), QtGui.QIcon)
        self.assertEqual('my tooltip', action.toolTip())
        self.assertEqual('my statustip', action.statusTip())

    def test_create_action_on_mac_osx(self):
        """
        Test creating an action on OS X calls the correct method
        """
        # GIVEN: A dialog and a mocked out is_macosx() method to always return True
        with patch('openlp.core.lib.ui.is_macosx') as mocked_is_macosx, \
                patch('openlp.core.lib.ui.QtWidgets.QAction') as MockedQAction:
            mocked_is_macosx.return_value = True
            mocked_action = MagicMock()
            MockedQAction.return_value = mocked_action
            dialog = QtWidgets.QDialog()

            # WHEN: An action is created
            create_action(dialog, 'my_action')

            # THEN: setIconVisibleInMenu should be called
            mocked_action.setIconVisibleInMenu.assert_called_with(False)

    def test_create_action_not_on_mac_osx(self):
        """
        Test creating an action on something other than OS X doesn't call the method
        """
        # GIVEN: A dialog and a mocked out is_macosx() method to always return True
        with patch('openlp.core.lib.ui.is_macosx') as mocked_is_macosx, \
                patch('openlp.core.lib.ui.QtWidgets.QAction') as MockedQAction:
            mocked_is_macosx.return_value = False
            mocked_action = MagicMock()
            MockedQAction.return_value = mocked_action
            dialog = QtWidgets.QDialog()

            # WHEN: An action is created
            create_action(dialog, 'my_action')

            # THEN: setIconVisibleInMenu should not be called
            self.assertEqual(0, mocked_action.setIconVisibleInMenu.call_count,
                             'setIconVisibleInMenu should not have been called')

    def test_create_checked_disabled_invisible_action(self):
        """
        Test that an invisible, disabled, checked action is created correctly
        """
        # GIVEN: A dialog
        dialog = QtWidgets.QDialog()

        # WHEN: We create an action with some properties
        action = create_action(dialog, 'my_action', checked=True, enabled=False, visible=False)

        # THEN: These properties should be set
        self.assertTrue(action.isChecked(), 'The action should be checked')
        self.assertFalse(action.isEnabled(), 'The action should be disabled')
        self.assertFalse(action.isVisible(), 'The action should be invisble')

    def test_create_action_separator(self):
        """
        Test creating an action as separator
        """
        # GIVEN: A dialog
        dialog = QtWidgets.QDialog()

        # WHEN: We create an action as a separator
        action = create_action(dialog, 'my_action', separator=True)

        # THEN: The action should be a separator
        self.assertTrue(action.isSeparator(), 'The action should be a separator')

    def test_create_valign_selection_widgets(self):
        """
        Test creating a combo box for valign selection
        """
        # GIVEN: A dialog
        dialog = QtWidgets.QDialog()

        # WHEN: We create the widgets
        label, combo = create_valign_selection_widgets(dialog)

        # THEN: We should get a label and a combobox.
        self.assertEqual(translate('OpenLP.Ui', '&Vertical Align:'), label.text())
        self.assertIsInstance(combo, QtWidgets.QComboBox)
        self.assertEqual(combo, label.buddy())
        for text in [UiStrings().Top, UiStrings().Middle, UiStrings().Bottom]:
            self.assertTrue(combo.findText(text) >= 0)

    def test_find_and_set_in_combo_box(self):
        """
        Test finding a string in a combo box and setting it as the selected item if present
        """
        # GIVEN: A ComboBox
        combo = QtWidgets.QComboBox()
        combo.addItems(['One', 'Two', 'Three'])
        combo.setCurrentIndex(1)

        # WHEN: We call the method with a non-existing value and set_missing=False
        find_and_set_in_combo_box(combo, 'Four', set_missing=False)

        # THEN: The index should not have changed
        self.assertEqual(1, combo.currentIndex())

        # WHEN: We call the method with a non-existing value
        find_and_set_in_combo_box(combo, 'Four')

        # THEN: The index should have been reset
        self.assertEqual(0, combo.currentIndex())

        # WHEN: We call the method with the default behavior
        find_and_set_in_combo_box(combo, 'Three')

        # THEN: The index should have changed
        self.assertEqual(2, combo.currentIndex())

    def test_create_widget_action(self):
        """
        Test creating an action for a widget
        """
        # GIVEN: A button
        button = QtWidgets.QPushButton()

        # WHEN: We call the function
        action = create_widget_action(button, 'some action')

        # THEN: The action should be returned
        self.assertIsInstance(action, QtWidgets.QAction)
        self.assertEqual(action.objectName(), 'some action')

    def test_set_case_insensitive_completer(self):
        """
        Test setting a case insensitive completer on a widget
        """
        # GIVEN: A QComboBox and a list of completion items
        line_edit = QtWidgets.QLineEdit()
        suggestions = ['one', 'Two', 'THRee', 'FOUR']

        # WHEN: We call the function
        set_case_insensitive_completer(suggestions, line_edit)

        # THEN: The Combobox should have a completer which is case insensitive
        completer = line_edit.completer()
        self.assertIsInstance(completer, QtWidgets.QCompleter)
        self.assertEqual(completer.caseSensitivity(), QtCore.Qt.CaseInsensitive)
