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

import re
import logging

from PyQt5 import QtCore, QtGui, QtWidgets

from openlp.plugins.songs.lib import VerseType, transpose_lyrics
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.common import translate, Settings
from .editversedialog import Ui_EditVerseDialog

log = logging.getLogger(__name__)

VERSE_REGEX = re.compile(r'---\[(.+):\D*(\d*)\D*.*\]---')


class EditVerseForm(QtWidgets.QDialog, Ui_EditVerseDialog):
    """
    This is the form that is used to edit the verses of the song.
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(EditVerseForm, self).__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint |
                                            QtCore.Qt.WindowCloseButtonHint)
        self.setupUi(self)
        self.has_single_verse = False
        self.insert_button.clicked.connect(self.on_insert_button_clicked)
        self.split_button.clicked.connect(self.on_split_button_clicked)
        self.verse_text_edit.cursorPositionChanged.connect(self.on_cursor_position_changed)
        self.verse_type_combo_box.currentIndexChanged.connect(self.on_verse_type_combo_box_changed)
        self.divide_split_button.clicked.connect(self.on_divide_split_button_clicked)
        if Settings().value('songs/enable chords'):
            self.transpose_down_button.clicked.connect(self.on_transpose_down_button_clicked)
            self.transpose_up_button.clicked.connect(self.on_transpose_up_button_clicked)

    def insert_verse(self, verse_tag, verse_num=1):
        """
        Insert a verse

        :param verse_tag: The verse tag
        :param verse_num: The verse number
        """
        if self.verse_text_edit.textCursor().columnNumber() != 0:
            self.verse_text_edit.insertPlainText('\n')
        verse_tag = VerseType.translated_name(verse_tag)
        self.verse_text_edit.insertPlainText('---[{tag}:{number}]---\n'.format(tag=verse_tag, number=verse_num))
        self.verse_text_edit.setFocus()

    def on_split_button_clicked(self):
        """
        The optional split button has been pressed so we need add the split
        """
        self._add_splitter_to_text('[---]')

    def on_divide_split_button_clicked(self):
        """
        The force split button has been pressed so we need add the split
        """
        self._add_splitter_to_text('[--}{--]')

    def _add_splitter_to_text(self, insert_string):
        """
        Add a custom splitter to the song text

        :param insert_string: The string to insert
        :return:
        """
        text = self.verse_text_edit.toPlainText()
        position = self.verse_text_edit.textCursor().position()
        if position and text[position - 1] != '\n':
            insert_string = '\n' + insert_string
        if position == len(text) or text[position] != '\n':
            insert_string += '\n'
        self.verse_text_edit.insertPlainText(insert_string)
        self.verse_text_edit.setFocus()

    def on_insert_button_clicked(self):
        """
        The insert button has been pressed
        """
        verse_type_index = self.verse_type_combo_box.currentIndex()
        self.insert_verse(VerseType.tags[verse_type_index], self.verse_number_box.value())

    def on_verse_type_combo_box_changed(self):
        """
        The verse type combo has been changed
        """
        self.update_suggested_verse_number()

    def on_cursor_position_changed(self):
        """
        The cursor position has been changed
        """
        self.update_suggested_verse_number()

    def on_transpose_up_button_clicked(self):
        """
        The transpose up button clicked
        """
        try:
            transposed_lyrics = transpose_lyrics(self.verse_text_edit.toPlainText(), 1)
            self.verse_text_edit.setPlainText(transposed_lyrics)
        except ValueError as ve:
            # Transposing failed
            critical_error_message_box(title=translate('SongsPlugin.EditVerseForm', 'Transposing failed'),
                                       message=translate('SongsPlugin.EditVerseForm',
                                                         'Transposing failed because of invalid chord:\n{err_msg}'
                                                         .format(err_msg=ve)))
            return
        self.verse_text_edit.setFocus()
        self.verse_text_edit.moveCursor(QtGui.QTextCursor.End)

    def on_transpose_down_button_clicked(self):
        """
        The transpose down button clicked
        """
        try:
            transposed_lyrics = transpose_lyrics(self.verse_text_edit.toPlainText(), -1)
            self.verse_text_edit.setPlainText(transposed_lyrics)
        except ValueError as ve:
            # Transposing failed
            critical_error_message_box(title=translate('SongsPlugin.EditVerseForm', 'Transposing failed'),
                                       message=translate('SongsPlugin.EditVerseForm',
                                                         'Transposing failed because of invalid chord:\n{err_msg}'
                                                         .format(err_msg=ve)))
            return
        self.verse_text_edit.setPlainText(transposed_lyrics)
        self.verse_text_edit.setFocus()
        self.verse_text_edit.moveCursor(QtGui.QTextCursor.End)

    def update_suggested_verse_number(self):
        """
        Adjusts the verse number SpinBox in regard to the selected verse type and the cursor's position.
        """
        if self.has_single_verse:
            return
        position = self.verse_text_edit.textCursor().position()
        text = self.verse_text_edit.toPlainText()
        verse_name = VerseType.translated_names[
            self.verse_type_combo_box.currentIndex()]
        if not text:
            return
        position = text.rfind('---[{verse}'.format(verse=verse_name), 0, position)
        if position == -1:
            self.verse_number_box.setValue(1)
            return
        text = text[position:]
        position = text.find(']---')
        if position == -1:
            return
        text = text[:position + 4]
        match = VERSE_REGEX.match(text)
        if match:
            try:
                verse_num = int(match.group(2)) + 1
            except ValueError:
                verse_num = 1
            self.verse_number_box.setValue(verse_num)

    def set_verse(self, text, single=False, tag='{verse}1'.format(verse=VerseType.tags[VerseType.Verse])):
        """
        Save the verse

        :param text: The text
        :param single: is this a single verse
        :param tag: The tag
        """
        self.has_single_verse = single
        if single:
            verse_type_index = VerseType.from_tag(tag[0], None)
            verse_number = tag[1:]
            if verse_type_index is not None:
                self.verse_type_combo_box.setCurrentIndex(verse_type_index)
            self.verse_number_box.setValue(int(verse_number))
            self.insert_button.setVisible(False)
        else:
            if not text:
                text = '---[{tag}:1]---\n'.format(tag=VerseType.translated_names[VerseType.Verse])
            self.verse_type_combo_box.setCurrentIndex(0)
            self.verse_number_box.setValue(1)
            self.insert_button.setVisible(True)
        self.verse_text_edit.setPlainText(text)
        self.verse_text_edit.setFocus()
        self.verse_text_edit.moveCursor(QtGui.QTextCursor.End)

    def get_verse(self):
        """
        Extract the verse text

        :return: The text
        """
        return self.verse_text_edit.toPlainText(), VerseType.tags[self.verse_type_combo_box.currentIndex()], \
            str(self.verse_number_box.value())

    def get_all_verses(self):
        """
        Extract all the verses

        :return: The text
        """
        text = self.verse_text_edit.toPlainText()
        if not text.startswith('---['):
            text = '---[{tag}:1]---\n{text}'.format(tag=VerseType.translated_names[VerseType.Verse], text=text)
        return text

    def accept(self):
        """
        Test if any invalid chords has been entered before closing the verse editor
        """
        if Settings().value('songs/enable chords'):
            try:
                transposed_lyrics = transpose_lyrics(self.verse_text_edit.toPlainText(), 1)
                super(EditVerseForm, self).accept()
            except ValueError as ve:
                # Transposing failed
                critical_error_message_box(title=translate('SongsPlugin.EditVerseForm', 'Invalid Chord'),
                                           message=translate('SongsPlugin.EditVerseForm',
                                                             'An invalid chord was detected:\n{err_msg}'
                                                             .format(err_msg=ve)))
        else:
            super(EditVerseForm, self).accept()
