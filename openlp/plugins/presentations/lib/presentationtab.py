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

from PyQt5 import QtWidgets

from openlp.core.common.i18n import UiStrings, translate
from openlp.core.common.settings import Settings
from openlp.core.lib import SettingsTab
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.widgets.edits import PathEdit
from openlp.plugins.presentations.lib.pdfcontroller import PdfController


class PresentationTab(SettingsTab):
    """
    PresentationsTab is the Presentations settings tab in the settings dialog.
    """
    def __init__(self, parent, title, visible_title, controllers, icon_path):
        """
        Constructor
        """
        self.controllers = controllers
        super(PresentationTab, self).__init__(parent, title, visible_title, icon_path)
        self.activated = False

    def setupUi(self):
        """
        Create the controls for the settings tab
        """
        self.setObjectName('PresentationTab')
        super(PresentationTab, self).setupUi()
        self.controllers_group_box = QtWidgets.QGroupBox(self.left_column)
        self.controllers_group_box.setObjectName('controllers_group_box')
        self.controllers_layout = QtWidgets.QVBoxLayout(self.controllers_group_box)
        self.controllers_layout.setObjectName('ccontrollers_layout')
        self.presenter_check_boxes = {}
        for key in self.controllers:
            controller = self.controllers[key]
            checkbox = QtWidgets.QCheckBox(self.controllers_group_box)
            checkbox.setObjectName(controller.name + 'CheckBox')
            self.presenter_check_boxes[controller.name] = checkbox
            self.controllers_layout.addWidget(checkbox)
        self.left_layout.addWidget(self.controllers_group_box)
        # Advanced
        self.advanced_group_box = QtWidgets.QGroupBox(self.left_column)
        self.advanced_group_box.setObjectName('advanced_group_box')
        self.advanced_layout = QtWidgets.QVBoxLayout(self.advanced_group_box)
        self.advanced_layout.setObjectName('advanced_layout')
        self.override_app_check_box = QtWidgets.QCheckBox(self.advanced_group_box)
        self.override_app_check_box.setObjectName('override_app_check_box')
        self.advanced_layout.addWidget(self.override_app_check_box)
        self.left_layout.addWidget(self.advanced_group_box)
        # PowerPoint
        self.powerpoint_group_box = QtWidgets.QGroupBox(self.left_column)
        self.powerpoint_group_box.setObjectName('powerpoint_group_box')
        self.powerpoint_layout = QtWidgets.QVBoxLayout(self.powerpoint_group_box)
        self.powerpoint_layout.setObjectName('powerpoint_layout')
        self.ppt_slide_click_check_box = QtWidgets.QCheckBox(self.powerpoint_group_box)
        self.ppt_slide_click_check_box.setObjectName('ppt_slide_click_check_box')
        self.powerpoint_layout.addWidget(self.ppt_slide_click_check_box)
        self.ppt_window_check_box = QtWidgets.QCheckBox(self.powerpoint_group_box)
        self.ppt_window_check_box.setObjectName('ppt_window_check_box')
        self.powerpoint_layout.addWidget(self.ppt_window_check_box)
        self.left_layout.addWidget(self.powerpoint_group_box)
        # Pdf options
        self.pdf_group_box = QtWidgets.QGroupBox(self.left_column)
        self.pdf_group_box.setObjectName('pdf_group_box')
        self.pdf_layout = QtWidgets.QFormLayout(self.pdf_group_box)
        self.pdf_layout.setObjectName('pdf_layout')
        self.pdf_program_check_box = QtWidgets.QCheckBox(self.pdf_group_box)
        self.pdf_program_check_box.setObjectName('pdf_program_check_box')
        self.pdf_layout.addRow(self.pdf_program_check_box)
        self.program_path_edit = PathEdit(self.pdf_group_box)
        self.pdf_layout.addRow(self.program_path_edit)
        self.left_layout.addWidget(self.pdf_group_box)
        self.left_layout.addStretch()
        self.right_column.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.right_layout.addStretch()
        # Signals and slots
        self.program_path_edit.pathChanged.connect(self.on_program_path_edit_path_changed)
        self.pdf_program_check_box.clicked.connect(self.program_path_edit.setEnabled)

    def retranslateUi(self):
        """
        Make any translation changes
        """
        self.controllers_group_box.setTitle(translate('PresentationPlugin.PresentationTab', 'Available Controllers'))
        for key in self.controllers:
            controller = self.controllers[key]
            checkbox = self.presenter_check_boxes[controller.name]
            self.set_controller_text(checkbox, controller)
        self.advanced_group_box.setTitle(UiStrings().Advanced)
        self.pdf_group_box.setTitle(translate('PresentationPlugin.PresentationTab', 'PDF options'))
        self.powerpoint_group_box.setTitle(translate('PresentationPlugin.PresentationTab', 'PowerPoint options'))
        self.override_app_check_box.setText(
            translate('PresentationPlugin.PresentationTab', 'Allow presentation application to be overridden'))
        self.ppt_slide_click_check_box.setText(
            translate('PresentationPlugin.PresentationTab',
                      'Clicking on the current slide advances to the next effect'))
        self.ppt_window_check_box.setText(
            translate('PresentationPlugin.PresentationTab',
                      'Let PowerPoint control the size and monitor of the presentations\n'
                      '(This may fix PowerPoint scaling issues in Windows 8 and 10)'))
        self.pdf_program_check_box.setText(
            translate('PresentationPlugin.PresentationTab', 'Use given full path for mudraw or ghostscript binary:'))
        self.program_path_edit.dialog_caption = translate('PresentationPlugin.PresentationTab',
                                                          'Select mudraw or ghostscript binary')

    def set_controller_text(self, checkbox, controller):
        if checkbox.isEnabled():
            checkbox.setText(controller.name)
        else:
            checkbox.setText(translate('PresentationPlugin.PresentationTab',
                                       '{name} (unavailable)').format(name=controller.name))

    def load(self):
        """
        Load the settings.
        """
        powerpoint_available = False
        for key in self.controllers:
            controller = self.controllers[key]
            checkbox = self.presenter_check_boxes[controller.name]
            checkbox.setChecked(Settings().value(self.settings_section + '/' + controller.name))
            if controller.name == 'Powerpoint' and controller.is_available():
                powerpoint_available = True
        self.override_app_check_box.setChecked(Settings().value(self.settings_section + '/override app'))
        # Load PowerPoint settings
        self.ppt_slide_click_check_box.setChecked(Settings().value(self.settings_section +
                                                                   '/powerpoint slide click advance'))
        self.ppt_slide_click_check_box.setEnabled(powerpoint_available)
        self.ppt_window_check_box.setChecked(Settings().value(self.settings_section + '/powerpoint control window'))
        self.ppt_window_check_box.setEnabled(powerpoint_available)
        # load pdf-program settings
        enable_pdf_program = Settings().value(self.settings_section + '/enable_pdf_program')
        self.pdf_program_check_box.setChecked(enable_pdf_program)
        self.program_path_edit.setEnabled(enable_pdf_program)
        self.program_path_edit.path = Settings().value(self.settings_section + '/pdf_program')

    def save(self):
        """
        Save the settings. If the tab hasn't been made visible to the user then there is nothing to do, so exit. This
        removes the need to start presentation applications unnecessarily.
        """
        if not self.activated:
            return
        changed = False
        for key in self.controllers:
            controller = self.controllers[key]
            if controller.is_available():
                checkbox = self.presenter_check_boxes[controller.name]
                setting_key = self.settings_section + '/' + controller.name
                if Settings().value(setting_key) != checkbox.checkState():
                    changed = True
                    Settings().setValue(setting_key, checkbox.checkState())
                    if checkbox.isChecked():
                        controller.start_process()
                    else:
                        controller.kill()
        setting_key = self.settings_section + '/override app'
        if Settings().value(setting_key) != self.override_app_check_box.checkState():
            Settings().setValue(setting_key, self.override_app_check_box.checkState())
            changed = True
        # Save powerpoint settings
        setting_key = self.settings_section + '/powerpoint slide click advance'
        if Settings().value(setting_key) != self.ppt_slide_click_check_box.checkState():
            Settings().setValue(setting_key, self.ppt_slide_click_check_box.checkState())
            changed = True
        setting_key = self.settings_section + '/powerpoint control window'
        if Settings().value(setting_key) != self.ppt_window_check_box.checkState():
            Settings().setValue(setting_key, self.ppt_window_check_box.checkState())
            changed = True
        # Save pdf-settings
        pdf_program_path = self.program_path_edit.path
        enable_pdf_program = self.pdf_program_check_box.checkState()
        # If the given program is blank disable using the program
        if pdf_program_path is None:
            enable_pdf_program = 0
        if pdf_program_path != Settings().value(self.settings_section + '/pdf_program'):
            Settings().setValue(self.settings_section + '/pdf_program', pdf_program_path)
            changed = True
        if enable_pdf_program != Settings().value(self.settings_section + '/enable_pdf_program'):
            Settings().setValue(self.settings_section + '/enable_pdf_program', enable_pdf_program)
            changed = True
        if changed:
            self.settings_form.register_post_process('mediaitem_suffix_reset')
            self.settings_form.register_post_process('mediaitem_presentation_rebuild')
            self.settings_form.register_post_process('mediaitem_suffixes')

    def tab_visible(self):
        """
        Tab has just been made visible to the user
        """
        self.activated = True
        for key in self.controllers:
            controller = self.controllers[key]
            checkbox = self.presenter_check_boxes[controller.name]
            checkbox.setEnabled(controller.is_available())
            self.set_controller_text(checkbox, controller)

    def on_program_path_edit_path_changed(self, new_path):
        """
        Handle the `pathEditChanged` signal from program_path_edit

        :param openlp.core.common.path.Path new_path: File path to the new program
        :rtype: None
        """
        if new_path:
            if not PdfController.process_check_binary(new_path):
                critical_error_message_box(UiStrings().Error,
                                           translate('PresentationPlugin.PresentationTab',
                                                     'The program is not ghostscript or mudraw which is required.'))
