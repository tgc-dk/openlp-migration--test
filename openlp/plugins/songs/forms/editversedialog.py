# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2016 OpenLP Developers                                   #
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

from openlp.core.ui.lib import SpellTextEdit
from openlp.core.lib import build_icon, translate
from openlp.core.lib.ui import UiStrings, create_button_box
from openlp.plugins.songs.lib import VerseType


class Ui_EditVerseDialog(object):
    def setupUi(self, edit_verse_dialog):
        edit_verse_dialog.setObjectName('edit_verse_dialog')
        edit_verse_dialog.setWindowIcon(build_icon(':/icon/openlp-logo.svg'))
        edit_verse_dialog.resize(400, 400)
        edit_verse_dialog.setModal(True)
        self.dialog_layout = QtWidgets.QVBoxLayout(edit_verse_dialog)
        self.dialog_layout.setObjectName('dialog_layout')
        self.verse_text_edit = SpellTextEdit(edit_verse_dialog)
        self.verse_text_edit.setObjectName('verse_text_edit')
        self.dialog_layout.addWidget(self.verse_text_edit)
        self.verse_type_layout = QtWidgets.QHBoxLayout()
        self.verse_type_layout.setObjectName('verse_type_layout')
        self.split_button = QtWidgets.QPushButton(edit_verse_dialog)
        self.split_button.setIcon(build_icon(':/general/general_add.png'))
        self.split_button.setObjectName('split_button')
        self.verse_type_layout.addWidget(self.split_button)
        self.verse_type_label = QtWidgets.QLabel(edit_verse_dialog)
        self.verse_type_label.setObjectName('verse_type_label')
        self.verse_type_layout.addWidget(self.verse_type_label)
        self.verse_type_combo_box = QtWidgets.QComboBox(edit_verse_dialog)
        self.verse_type_combo_box.addItems(['', '', '', '', '', '', ''])
        self.verse_type_combo_box.setObjectName('verse_type_combo_box')
        self.verse_type_label.setBuddy(self.verse_type_combo_box)
        self.verse_type_layout.addWidget(self.verse_type_combo_box)
        self.verse_number_box = QtWidgets.QSpinBox(edit_verse_dialog)
        self.verse_number_box.setMinimum(1)
        self.verse_number_box.setObjectName('verse_number_box')
        self.verse_type_layout.addWidget(self.verse_number_box)
        self.insert_button = QtWidgets.QPushButton(edit_verse_dialog)
        self.insert_button.setIcon(build_icon(':/general/general_add.png'))
        self.insert_button.setObjectName('insert_button')
        self.verse_type_layout.addWidget(self.insert_button)
        self.verse_type_layout.addStretch()
        self.dialog_layout.addLayout(self.verse_type_layout)
        self.transpose_layout = QtWidgets.QHBoxLayout()
        self.transpose_layout.setObjectName('transpose_layout')
        self.transpose_label = QtWidgets.QLabel(edit_verse_dialog)
        self.transpose_label.setObjectName('transpose_label')
        self.transpose_layout.addWidget(self.transpose_label)
        self.transpose_up_button = QtWidgets.QPushButton(edit_verse_dialog)
        self.transpose_up_button.setIcon(build_icon(':/services/service_up.png'))
        self.transpose_up_button.setObjectName('transpose_up')
        self.transpose_layout.addWidget(self.transpose_up_button)
        self.transpose_down_button = QtWidgets.QPushButton(edit_verse_dialog)
        self.transpose_down_button.setIcon(build_icon(':/services/service_down.png'))
        self.transpose_down_button.setObjectName('transpose_down')
        self.transpose_layout.addWidget(self.transpose_down_button)
        self.dialog_layout.addLayout(self.transpose_layout)
        self.button_box = create_button_box(edit_verse_dialog, 'button_box', ['cancel', 'ok'])
        self.dialog_layout.addWidget(self.button_box)
        self.retranslateUi(edit_verse_dialog)

    def retranslateUi(self, edit_verse_dialog):
        edit_verse_dialog.setWindowTitle(translate('SongsPlugin.EditVerseForm', 'Edit Verse'))
        self.verse_type_label.setText(translate('SongsPlugin.EditVerseForm', '&Verse type:'))
        self.verse_type_combo_box.setItemText(VerseType.Verse, VerseType.translated_names[VerseType.Verse])
        self.verse_type_combo_box.setItemText(VerseType.Chorus, VerseType.translated_names[VerseType.Chorus])
        self.verse_type_combo_box.setItemText(VerseType.Bridge, VerseType.translated_names[VerseType.Bridge])
        self.verse_type_combo_box.setItemText(VerseType.PreChorus, VerseType.translated_names[VerseType.PreChorus])
        self.verse_type_combo_box.setItemText(VerseType.Intro, VerseType.translated_names[VerseType.Intro])
        self.verse_type_combo_box.setItemText(VerseType.Ending, VerseType.translated_names[VerseType.Ending])
        self.verse_type_combo_box.setItemText(VerseType.Other, VerseType.translated_names[VerseType.Other])
        self.split_button.setText(UiStrings().Split)
        self.split_button.setToolTip(UiStrings().SplitToolTip)
        self.insert_button.setText(translate('SongsPlugin.EditVerseForm', '&Insert'))
        self.insert_button.setToolTip(translate('SongsPlugin.EditVerseForm',
                                      'Split a slide into two by inserting a verse splitter.'))
        self.transpose_label.setText(translate('SongsPlugin.EditVerseForm', 'Transpose:'))
        self.transpose_up_button.setText(translate('SongsPlugin.EditVerseForm', 'Up'))
        self.transpose_down_button.setText(translate('SongsPlugin.EditVerseForm', 'Down'))
