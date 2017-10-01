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
The :mod:`~openlp.plugins.songs.forms.editsongform` module contains the form
used to edit songs.
"""
import logging
import os
import re

from PyQt5 import QtCore, QtWidgets

from openlp.core.common import Registry, RegistryProperties, AppLocation, UiStrings, check_directory_exists, translate
from openlp.core.common.languagemanager import get_natural_key
from openlp.core.common.path import copyfile
from openlp.core.lib import PluginStatus, MediaType, create_separated_list
from openlp.core.lib.ui import set_case_insensitive_completer, critical_error_message_box, find_and_set_in_combo_box
from openlp.core.ui.lib.filedialog import FileDialog
from openlp.plugins.songs.forms.editsongdialog import Ui_EditSongDialog
from openlp.plugins.songs.forms.editverseform import EditVerseForm
from openlp.plugins.songs.forms.mediafilesform import MediaFilesForm
from openlp.plugins.songs.lib import VerseType, clean_song
from openlp.plugins.songs.lib.db import Book, Song, Author, AuthorType, Topic, MediaFile, SongBookEntry
from openlp.plugins.songs.lib.openlyricsxml import SongXML
from openlp.plugins.songs.lib.ui import SongStrings

log = logging.getLogger(__name__)


class EditSongForm(QtWidgets.QDialog, Ui_EditSongDialog, RegistryProperties):
    """
    Class to manage the editing of a song
    """
    log.info('{name} EditSongForm loaded'.format(name=__name__))

    def __init__(self, media_item, parent, manager):
        """
        Constructor
        """
        super(EditSongForm, self).__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint |
                                           QtCore.Qt.WindowCloseButtonHint)
        self.media_item = media_item
        self.song = None
        # can this be automated?
        self.width = 400
        self.setupUi(self)
        # Connecting signals and slots
        self.author_add_button.clicked.connect(self.on_author_add_button_clicked)
        self.author_edit_button.clicked.connect(self.on_author_edit_button_clicked)
        self.author_remove_button.clicked.connect(self.on_author_remove_button_clicked)
        self.authors_list_view.itemClicked.connect(self.on_authors_list_view_clicked)
        self.topic_add_button.clicked.connect(self.on_topic_add_button_clicked)
        self.topic_remove_button.clicked.connect(self.on_topic_remove_button_clicked)
        self.topics_list_view.itemClicked.connect(self.on_topic_list_view_clicked)
        self.songbook_add_button.clicked.connect(self.on_songbook_add_button_clicked)
        self.songbook_remove_button.clicked.connect(self.on_songbook_remove_button_clicked)
        self.songbooks_list_view.itemClicked.connect(self.on_songbook_list_view_clicked)
        self.copyright_insert_button.clicked.connect(self.on_copyright_insert_button_triggered)
        self.verse_add_button.clicked.connect(self.on_verse_add_button_clicked)
        self.verse_list_widget.doubleClicked.connect(self.on_verse_edit_button_clicked)
        self.verse_edit_button.clicked.connect(self.on_verse_edit_button_clicked)
        self.verse_edit_all_button.clicked.connect(self.on_verse_edit_all_button_clicked)
        self.verse_delete_button.clicked.connect(self.on_verse_delete_button_clicked)
        self.verse_list_widget.itemClicked.connect(self.on_verse_list_view_clicked)
        self.verse_order_edit.textEdited.connect(self.on_verse_order_text_changed)
        self.theme_add_button.clicked.connect(self.theme_manager.on_add_theme)
        self.maintenance_button.clicked.connect(self.on_maintenance_button_clicked)
        self.from_file_button.clicked.connect(self.on_audio_add_from_file_button_clicked)
        self.from_media_button.clicked.connect(self.on_audio_add_from_media_button_clicked)
        self.audio_remove_button.clicked.connect(self.on_audio_remove_button_clicked)
        self.audio_remove_all_button.clicked.connect(self.on_audio_remove_all_button_clicked)
        Registry().register_function('theme_update_list', self.load_themes)
        self.preview_button = QtWidgets.QPushButton()
        self.preview_button.setObjectName('preview_button')
        self.preview_button.setText(UiStrings().SaveAndPreview)
        self.button_box.addButton(self.preview_button, QtWidgets.QDialogButtonBox.ActionRole)
        self.button_box.clicked.connect(self.on_preview)
        # Create other objects and forms
        self.manager = manager
        self.verse_form = EditVerseForm(self)
        self.media_form = MediaFilesForm(self)
        self.initialise()
        self.authors_list_view.setSortingEnabled(False)
        self.authors_list_view.setAlternatingRowColors(True)
        self.topics_list_view.setSortingEnabled(False)
        self.topics_list_view.setAlternatingRowColors(True)
        self.audio_list_widget.setAlternatingRowColors(True)
        self.find_verse_split = re.compile('---\[\]---\n', re.UNICODE)
        self.whitespace = re.compile(r'\W+', re.UNICODE)
        self.find_tags = re.compile(u'\{/?\w+\}', re.UNICODE)

    def _load_objects(self, cls, combo, cache):
        """
        Generically load a set of objects into a cache and a combobox.
        """
        def get_key(obj):
            """Get the key to sort by"""
            return get_natural_key(obj.name)

        objects = self.manager.get_all_objects(cls)
        objects.sort(key=get_key)
        combo.clear()
        for obj in objects:
            row = combo.count()
            combo.addItem(obj.name)
            cache.append(obj.name)
            combo.setItemData(row, obj.id)
        set_case_insensitive_completer(cache, combo)
        combo.setCurrentIndex(-1)
        combo.setCurrentText('')

    def _add_author_to_list(self, author, author_type):
        """
        Add an author to the author list.
        """
        author_item = QtWidgets.QListWidgetItem(author.get_display_name(author_type))
        author_item.setData(QtCore.Qt.UserRole, (author.id, author_type))
        self.authors_list_view.addItem(author_item)

    def add_songbook_entry_to_list(self, songbook_id, songbook_name, entry):
        songbook_entry_item = QtWidgets.QListWidgetItem(SongBookEntry.get_display_name(songbook_name, entry))
        songbook_entry_item.setData(QtCore.Qt.UserRole, (songbook_id, entry))
        self.songbooks_list_view.addItem(songbook_entry_item)

    def _extract_verse_order(self, verse_order):
        """
        Split out the verse order

        :param verse_order: The starting verse order
        :return: revised order
        """
        order = []
        order_names = str(verse_order).split()
        for item in order_names:
            if len(item) == 1:
                verse_index = VerseType.from_translated_tag(item, None)
                if verse_index is not None:
                    order.append(VerseType.tags[verse_index] + '1')
                else:
                    # it matches no verses anyway
                    order.append('')
            else:
                verse_index = VerseType.from_translated_tag(item[0], None)
                if verse_index is None:
                    # it matches no verses anyway
                    order.append('')
                else:
                    verse_tag = VerseType.tags[verse_index]
                    verse_num = item[1:].lower()
                    order.append(verse_tag + verse_num)
        return order

    def _validate_verse_list(self, verse_order, verse_count):
        """
        Check the verse order list has valid verses

        :param verse_order: Verse order
        :param verse_count: number of verses
        :return: Count of invalid verses
        """
        verses = []
        invalid_verses = []
        verse_names = []
        order_names = str(verse_order).split()
        order = self._extract_verse_order(verse_order)
        for index in range(verse_count):
            verse = self.verse_list_widget.item(index, 0)
            verse = verse.data(QtCore.Qt.UserRole)
            if verse not in verse_names:
                verses.append(verse)
                verse_names.append('{verse1}{verse2}'.format(verse1=VerseType.translated_tag(verse[0]),
                                                             verse2=verse[1:]))
        for count, item in enumerate(order):
            if item not in verses:
                invalid_verses.append(order_names[count])
        if invalid_verses:
            valid = create_separated_list(verse_names)
            if len(invalid_verses) > 1:
                msg = translate('SongsPlugin.EditSongForm',
                                'There are no verses corresponding to "{invalid}". Valid entries are {valid}.\n'
                                'Please enter the verses separated by spaces.'
                                ).format(invalid=', '.join(invalid_verses), valid=valid)
            else:
                msg = translate('SongsPlugin.EditSongForm',
                                'There is no verse corresponding to "{invalid}". Valid entries are {valid}.\n'
                                'Please enter the verses separated by spaces.').format(invalid=invalid_verses[0],
                                                                                       valid=valid)
            critical_error_message_box(title=translate('SongsPlugin.EditSongForm', 'Invalid Verse Order'), message=msg)
        return len(invalid_verses) == 0

    def _validate_song(self):
        """
        Check the validity of the song.
        """
        # This checks data in the form *not* self.song. self.song is still
        # None at this point.
        log.debug('Validate Song')
        # Lets be nice and assume the data is correct.
        if not self.title_edit.text():
            self.song_tab_widget.setCurrentIndex(0)
            self.title_edit.setFocus()
            critical_error_message_box(
                message=translate('SongsPlugin.EditSongForm', 'You need to type in a song title.'))
            return False
        if self.verse_list_widget.rowCount() == 0:
            self.song_tab_widget.setCurrentIndex(0)
            self.verse_list_widget.setFocus()
            critical_error_message_box(
                message=translate('SongsPlugin.EditSongForm', 'You need to type in at least one verse.'))
            return False
        if self.authors_list_view.count() == 0:
            self.song_tab_widget.setCurrentIndex(1)
            self.authors_list_view.setFocus()
            critical_error_message_box(message=translate('SongsPlugin.EditSongForm',
                                                         'You need to have an author for this song.'))
            return False
        if self.verse_order_edit.text():
            result = self._validate_verse_list(self.verse_order_edit.text(), self.verse_list_widget.rowCount())
            if not result:
                return False
        # Validate tags (lp#1199639)
        misplaced_tags = []
        verse_tags = []
        for i in range(self.verse_list_widget.rowCount()):
            item = self.verse_list_widget.item(i, 0)
            tags = self.find_tags.findall(item.text())
            field = item.data(QtCore.Qt.UserRole)
            verse_tags.append(field)
            if not self._validate_tags(tags):
                misplaced_tags.append('{field1} {field2}'.format(field1=VerseType.translated_name(field[0]),
                                                                 field2=field[1:]))
        if misplaced_tags:
            critical_error_message_box(
                message=translate('SongsPlugin.EditSongForm',
                                  'There are misplaced formatting tags in the following verses:\n\n{tag}\n\n'
                                  'Please correct these tags before continuing.').format(tag=', '.join(misplaced_tags)))
            return False
        for tag in verse_tags:
            if verse_tags.count(tag) > 26:
                # lp#1310523: OpenLyrics allows only a-z variants of one verse:
                # http://openlyrics.info/dataformat.html#verse-name
                critical_error_message_box(message=translate(
                    'SongsPlugin.EditSongForm',
                    'You have {count} verses named {name} {number}. You can have at most '
                    '26 verses with the same name').format(count=verse_tags.count(tag),
                                                           name=VerseType.translated_name(tag[0]),
                                                           number=tag[1:]))
                return False
        return True

    def _validate_tags(self, tags, first_time=True):
        """
        Validates a list of tags
        Deletes the first affiliated tag pair which is located side by side in the list
        and call itself recursively with the shortened tag list.
        If there is any misplaced tag in the list, either the length of the tag list is not even,
        or the function won't find any tag pairs side by side.
        If there is no misplaced tag, the length of the list will be zero on any recursive run.

        :param tags: A list of tags
        :return: True if the function can't find any mismatched tags. Else False.
        """
        if first_time:
            fixed_tags = []
            for i in range(len(tags)):
                if tags[i] != '{br}':
                    fixed_tags.append(tags[i])
            tags = fixed_tags
        if len(tags) == 0:
            return True
        if len(tags) % 2 != 0:
            return False
        for i in range(len(tags) - 1):
            if tags[i + 1] == "{/" + tags[i][1:]:
                del tags[i:i + 2]
                return self._validate_tags(tags, False)
        return False

    def _process_lyrics(self):
        """
        Process the lyric data entered by the user into the OpenLP XML format.
        """
        # This method must only be run after the self.song = Song() assignment.
        log.debug('_processLyrics')
        sxml = None
        try:
            sxml = SongXML()
            multiple = []
            for i in range(self.verse_list_widget.rowCount()):
                item = self.verse_list_widget.item(i, 0)
                verse_id = item.data(QtCore.Qt.UserRole)
                verse_tag = verse_id[0]
                verse_num = verse_id[1:]
                sxml.add_verse_to_lyrics(verse_tag, verse_num, item.text())
                if verse_num > '1' and verse_tag not in multiple:
                    multiple.append(verse_tag)
            self.song.lyrics = str(sxml.extract_xml(), 'utf-8')
            for verse in multiple:
                self.song.verse_order = re.sub('([' + verse.upper() + verse.lower() + '])(\W|$)',
                                               r'\g<1>1\2', self.song.verse_order)
        except:
            log.exception('Problem processing song Lyrics \n{xml}'.format(xml=sxml.dump_xml()))
            raise

    def keyPressEvent(self, event):
        """
        Re-implement the keyPressEvent to react on Return/Enter keys. When some combo boxes have focus we do not want
        dialog's default action be triggered but instead our own.

        :param event: A QtWidgets.QKeyEvent event.
        """
        if event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
            if self.authors_combo_box.hasFocus() and self.authors_combo_box.currentText():
                self.on_author_add_button_clicked()
                return
            if self.topics_combo_box.hasFocus() and self.topics_combo_box.currentText():
                self.on_topic_add_button_clicked()
                return
            if self.songbooks_combo_box.hasFocus() or self.songbook_entry_edit.hasFocus():
                self.on_songbook_add_button_clicked()
                return
        QtWidgets.QDialog.keyPressEvent(self, event)

    def initialise(self):
        """
        Set up the form for when it is displayed.
        """
        self.verse_edit_button.setEnabled(False)
        self.verse_delete_button.setEnabled(False)
        self.author_edit_button.setEnabled(False)
        self.author_remove_button.setEnabled(False)
        self.topic_remove_button.setEnabled(False)

    def load_authors(self):
        """
        Load the authors from the database into the combobox.
        """
        def get_author_key(author):
            """Get the key to sort by"""
            return get_natural_key(author.display_name)

        authors = self.manager.get_all_objects(Author)
        authors.sort(key=get_author_key)
        self.authors_combo_box.clear()
        self.authors = []
        for author in authors:
            row = self.authors_combo_box.count()
            self.authors_combo_box.addItem(author.display_name)
            self.authors_combo_box.setItemData(row, author.id)
            self.authors.append(author.display_name)
        set_case_insensitive_completer(self.authors, self.authors_combo_box)
        self.authors_combo_box.setCurrentIndex(-1)
        self.authors_combo_box.setCurrentText('')

        # Types
        self.author_types_combo_box.clear()
        # Don't iterate over the dictionary to give them this specific order
        for author_type in AuthorType.SortedTypes:
            self.author_types_combo_box.addItem(AuthorType.Types[author_type], author_type)

    def load_topics(self):
        """
        Load the topics into the combobox.
        """
        self.topics = []
        self._load_objects(Topic, self.topics_combo_box, self.topics)

    def load_songbooks(self):
        """
        Load the Songbooks into the combobox
        """
        self.songbooks = []
        self._load_objects(Book, self.songbooks_combo_box, self.songbooks)

    def load_themes(self, theme_list):
        """
        Load the themes into a combobox.
        """
        def get_theme_key(theme):
            """Get the key to sort by"""
            return get_natural_key(theme)

        self.theme_combo_box.clear()
        self.themes = theme_list
        self.themes.sort(key=get_theme_key)
        self.theme_combo_box.addItems(theme_list)
        set_case_insensitive_completer(self.themes, self.theme_combo_box)
        self.theme_combo_box.setCurrentIndex(-1)
        self.theme_combo_box.setCurrentText('')

    def load_media_files(self):
        """
        Load the media files into a combobox.
        """
        self.from_media_button.setVisible(False)
        for plugin in self.plugin_manager.plugins:
            if plugin.name == 'media' and plugin.status == PluginStatus.Active:
                self.from_media_button.setVisible(True)
                self.media_form.populate_files(plugin.media_item.get_list(MediaType.Audio))
                break

    def new_song(self):
        """
        Blank the edit form out in preparation for a new song.
        """
        log.debug('New Song')
        self.song = None
        self.initialise()
        self.song_tab_widget.setCurrentIndex(0)
        self.title_edit.clear()
        self.alternative_edit.clear()
        self.copyright_edit.clear()
        self.verse_order_edit.clear()
        self.comments_edit.clear()
        self.ccli_number_edit.clear()
        self.verse_list_widget.clear()
        self.verse_list_widget.setRowCount(0)
        self.authors_list_view.clear()
        self.topics_list_view.clear()
        self.songbooks_list_view.clear()
        self.songbook_entry_edit.clear()
        self.audio_list_widget.clear()
        self.title_edit.setFocus()
        self.load_authors()
        self.load_topics()
        self.load_songbooks()
        self.load_media_files()
        self.theme_combo_box.setCurrentIndex(-1)
        self.theme_combo_box.setCurrentText('')
        # it's a new song to preview is not possible
        self.preview_button.setVisible(False)

    def load_song(self, song_id, preview=False):
        """
        Loads a song.

        :param song_id: The song id (int).
        :param preview: Should be ``True`` if the song is also previewed (boolean).
        """
        log.debug('Load Song')
        self.initialise()
        self.song_tab_widget.setCurrentIndex(0)
        self.load_authors()
        self.load_topics()
        self.load_songbooks()
        self.load_media_files()
        self.song = self.manager.get_object(Song, song_id)
        self.title_edit.setText(self.song.title)
        self.alternative_edit.setText(self.song.alternate_title if self.song.alternate_title else '')
        if self.song.theme_name:
            find_and_set_in_combo_box(self.theme_combo_box, str(self.song.theme_name))
        else:
            # Clear the theme combo box in case it was previously set (bug #1212801)
            self.theme_combo_box.setCurrentIndex(-1)
            self.theme_combo_box.setCurrentText('')
        self.copyright_edit.setText(self.song.copyright if self.song.copyright else '')
        self.comments_edit.setPlainText(self.song.comments if self.song.comments else '')
        self.ccli_number_edit.setText(self.song.ccli_number if self.song.ccli_number else '')
        # lazy xml migration for now
        self.verse_list_widget.clear()
        self.verse_list_widget.setRowCount(0)
        verse_tags_translated = False
        if self.song.lyrics.startswith('<?xml version='):
            song_xml = SongXML()
            verse_list = song_xml.get_verses(self.song.lyrics)
            for count, verse in enumerate(verse_list):
                self.verse_list_widget.setRowCount(self.verse_list_widget.rowCount() + 1)
                # This silently migrates from localized verse type markup.
                # If we trusted the database, this would be unnecessary.
                verse_tag = verse[0]['type']
                index = None
                if len(verse_tag) > 1:
                    index = VerseType.from_translated_string(verse_tag)
                    if index is None:
                        index = VerseType.from_string(verse_tag, None)
                    else:
                        verse_tags_translated = True
                if index is None:
                    index = VerseType.from_tag(verse_tag)
                verse[0]['type'] = VerseType.tags[index]
                if verse[0]['label'] == '':
                    verse[0]['label'] = '1'
                verse_def = '{verse}{label}'.format(verse=verse[0]['type'], label=verse[0]['label'])
                item = QtWidgets.QTableWidgetItem(verse[1])
                item.setData(QtCore.Qt.UserRole, verse_def)
                self.verse_list_widget.setItem(count, 0, item)
        else:
            verses = self.song.lyrics.split('\n\n')
            for count, verse in enumerate(verses):
                self.verse_list_widget.setRowCount(self.verse_list_widget.rowCount() + 1)
                item = QtWidgets.QTableWidgetItem(verse)
                verse_def = '{verse}{count:d}'.format(verse=VerseType.tags[VerseType.Verse], count=(count + 1))
                item.setData(QtCore.Qt.UserRole, verse_def)
                self.verse_list_widget.setItem(count, 0, item)
        if self.song.verse_order:
            # we translate verse order
            translated = []
            for verse_def in self.song.verse_order.split():
                verse_index = None
                if verse_tags_translated:
                    verse_index = VerseType.from_translated_tag(verse_def[0], None)
                if verse_index is None:
                    verse_index = VerseType.from_tag(verse_def[0])
                verse_tag = VerseType.translated_tags[verse_index].upper()
                translated.append('{tag}{verse}'.format(tag=verse_tag, verse=verse_def[1:]))
            self.verse_order_edit.setText(' '.join(translated))
        else:
            self.verse_order_edit.setText('')
        self.tag_rows()
        # clear the results
        self.authors_list_view.clear()
        for author_song in self.song.authors_songs:
            self._add_author_to_list(author_song.author, author_song.author_type)
        # clear the results
        self.topics_list_view.clear()
        for topic in self.song.topics:
            topic_name = QtWidgets.QListWidgetItem(str(topic.name))
            topic_name.setData(QtCore.Qt.UserRole, topic.id)
            self.topics_list_view.addItem(topic_name)
        self.songbooks_list_view.clear()
        self.songbook_entry_edit.clear()
        for songbook_entry in self.song.songbook_entries:
            self.add_songbook_entry_to_list(songbook_entry.songbook.id, songbook_entry.songbook.name,
                                            songbook_entry.entry)
        self.audio_list_widget.clear()
        for media in self.song.media_files:
            item = QtWidgets.QListWidgetItem(media.file_path.name)
            item.setData(QtCore.Qt.UserRole, media.file_path)
            self.audio_list_widget.addItem(item)
        self.title_edit.setFocus()
        # Hide or show the preview button.
        self.preview_button.setVisible(preview)
        # Check if all verse tags are used.
        self.on_verse_order_text_changed(self.verse_order_edit.text())

    def tag_rows(self):
        """
        Tag the Song List rows based on the verse list
        """
        row_label = []
        for row in range(self.verse_list_widget.rowCount()):
            item = self.verse_list_widget.item(row, 0)
            verse_def = item.data(QtCore.Qt.UserRole)
            verse_tag = VerseType.translated_tag(verse_def[0])
            row_def = '{tag}{verse}'.format(tag=verse_tag, verse=verse_def[1:])
            row_label.append(row_def)
        self.verse_list_widget.setVerticalHeaderLabels(row_label)
        self.verse_list_widget.resizeRowsToContents()
        self.verse_list_widget.repaint()

    def on_author_add_button_clicked(self):
        """
        Add the author to the list of authors associated with this song when the button is clicked.
        """
        item = int(self.authors_combo_box.currentIndex())
        text = self.authors_combo_box.currentText().strip(' \r\n\t')
        author_type = self.author_types_combo_box.itemData(self.author_types_combo_box.currentIndex())
        if item == -1 and text:
            if QtWidgets.QMessageBox.question(
                    self,
                    translate('SongsPlugin.EditSongForm', 'Add Author'),
                    translate('SongsPlugin.EditSongForm', 'This author does not exist, do you want to add them?'),
                    defaultButton=QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes:
                if text.find(' ') == -1:
                    author = Author.populate(first_name='', last_name='', display_name=text)
                else:
                    author = Author.populate(first_name=text.rsplit(' ', 1)[0], last_name=text.rsplit(' ', 1)[1],
                                             display_name=text)
                self.manager.save_object(author)
                self._add_author_to_list(author, author_type)
                self.load_authors()
                self.authors_combo_box.setCurrentIndex(-1)
                self.authors_combo_box.setCurrentText('')
            else:
                return
        elif item >= 0:
            item_id = (self.authors_combo_box.itemData(item))
            author = self.manager.get_object(Author, item_id)
            if self.authors_list_view.findItems(author.get_display_name(author_type), QtCore.Qt.MatchExactly):
                critical_error_message_box(
                    message=translate('SongsPlugin.EditSongForm', 'This author is already in the list.'))
            else:
                self._add_author_to_list(author, author_type)
            self.authors_combo_box.setCurrentIndex(-1)
            self.authors_combo_box.setCurrentText('')
        else:
            QtWidgets.QMessageBox.warning(
                self, UiStrings().NISs,
                translate('SongsPlugin.EditSongForm', 'You have not selected a valid author. Either select an author '
                          'from the list, or type in a new author and click the "Add Author to Song" button to add '
                          'the new author.'))

    def on_authors_list_view_clicked(self):
        """
        Run a set of actions when an author in the list is selected (mainly enable the delete button).
        """
        count = self.authors_list_view.count()
        if count > 0:
            self.author_edit_button.setEnabled(True)
        if count > 1:
            # There must be at least one author
            self.author_remove_button.setEnabled(True)

    def on_author_edit_button_clicked(self):
        """
        Show a dialog to change the type of an author when the edit button is clicked
        """
        self.author_edit_button.setEnabled(False)
        item = self.authors_list_view.currentItem()
        author_id, author_type = item.data(QtCore.Qt.UserRole)
        choice, ok = QtWidgets.QInputDialog.getItem(self, translate('SongsPlugin.EditSongForm', 'Edit Author Type'),
                                                    translate('SongsPlugin.EditSongForm',
                                                              'Choose type for this author'),
                                                    AuthorType.TranslatedTypes,
                                                    current=AuthorType.SortedTypes.index(author_type),
                                                    editable=False)
        if not ok:
            return
        author = self.manager.get_object(Author, author_id)
        author_type = AuthorType.from_translated_text(choice)
        item.setData(QtCore.Qt.UserRole, (author_id, author_type))
        item.setText(author.get_display_name(author_type))

    def on_author_remove_button_clicked(self):
        """
        Remove the author from the list when the delete button is clicked.
        """
        if self.authors_list_view.count() <= 2:
            self.author_remove_button.setEnabled(False)
        item = self.authors_list_view.currentItem()
        row = self.authors_list_view.row(item)
        self.authors_list_view.takeItem(row)

    def on_topic_add_button_clicked(self):
        item = int(self.topics_combo_box.currentIndex())
        text = self.topics_combo_box.currentText()
        if item == -1 and text:
            if QtWidgets.QMessageBox.question(
                    self, translate('SongsPlugin.EditSongForm', 'Add Topic'),
                    translate('SongsPlugin.EditSongForm', 'This topic does not exist, do you want to add it?'),
                    defaultButton=QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes:
                topic = Topic.populate(name=text)
                self.manager.save_object(topic)
                topic_item = QtWidgets.QListWidgetItem(str(topic.name))
                topic_item.setData(QtCore.Qt.UserRole, topic.id)
                self.topics_list_view.addItem(topic_item)
                self.load_topics()
                self.topics_combo_box.setCurrentIndex(-1)
                self.topics_combo_box.setCurrentText('')
            else:
                return
        elif item >= 0:
            item_id = (self.topics_combo_box.itemData(item))
            topic = self.manager.get_object(Topic, item_id)
            if self.topics_list_view.findItems(str(topic.name), QtCore.Qt.MatchExactly):
                critical_error_message_box(
                    message=translate('SongsPlugin.EditSongForm', 'This topic is already in the list.'))
            else:
                topic_item = QtWidgets.QListWidgetItem(str(topic.name))
                topic_item.setData(QtCore.Qt.UserRole, topic.id)
                self.topics_list_view.addItem(topic_item)
            self.topics_combo_box.setCurrentIndex(-1)
            self.topics_combo_box.setCurrentText('')
        else:
            QtWidgets.QMessageBox.warning(
                self, UiStrings().NISs,
                translate('SongsPlugin.EditSongForm', 'You have not selected a valid topic. Either select a topic '
                          'from the list, or type in a new topic and click the "Add Topic to Song" button to add the '
                          'new topic.'))

    def on_topic_list_view_clicked(self):
        self.topic_remove_button.setEnabled(True)

    def on_topic_remove_button_clicked(self):
        self.topic_remove_button.setEnabled(False)
        item = self.topics_list_view.currentItem()
        row = self.topics_list_view.row(item)
        self.topics_list_view.takeItem(row)

    def on_songbook_add_button_clicked(self):
        item = int(self.songbooks_combo_box.currentIndex())
        text = self.songbooks_combo_box.currentText()
        if item == -1 and text:
            if QtWidgets.QMessageBox.question(
                    self, translate('SongsPlugin.EditSongForm', 'Add Songbook'),
                    translate('SongsPlugin.EditSongForm', 'This Songbook does not exist, do you want to add it?'),
                    defaultButton=QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes:
                songbook = Book.populate(name=text)
                self.manager.save_object(songbook)
                self.add_songbook_entry_to_list(songbook.id, songbook.name, self.songbook_entry_edit.text())
                self.load_songbooks()
                self.songbooks_combo_box.setCurrentIndex(-1)
                self.songbooks_combo_box.setCurrentText('')
                self.songbook_entry_edit.clear()
            else:
                return
        elif item >= 0:
            item_id = (self.songbooks_combo_box.itemData(item))
            songbook = self.manager.get_object(Book, item_id)
            if self.songbooks_list_view.findItems(str(songbook.name), QtCore.Qt.MatchExactly):
                critical_error_message_box(
                    message=translate('SongsPlugin.EditSongForm', 'This Songbook is already in the list.'))
            else:
                self.add_songbook_entry_to_list(songbook.id, songbook.name, self.songbook_entry_edit.text())
            self.songbooks_combo_box.setCurrentIndex(-1)
            self.songbooks_combo_box.setCurrentText('')
            self.songbook_entry_edit.clear()
        else:
            QtWidgets.QMessageBox.warning(
                self, UiStrings().NISs,
                translate('SongsPlugin.EditSongForm', 'You have not selected a valid Songbook. Either select a '
                          'Songbook from the list, or type in a new Songbook and click the "Add to Song" '
                          'button to add the new Songbook.'))

    def on_songbook_list_view_clicked(self):
        self.songbook_remove_button.setEnabled(True)

    def on_songbook_remove_button_clicked(self):
        self.songbook_remove_button.setEnabled(False)
        row = self.songbooks_list_view.row(self.songbooks_list_view.currentItem())
        self.songbooks_list_view.takeItem(row)

    def on_verse_list_view_clicked(self):
        self.verse_edit_button.setEnabled(True)
        self.verse_delete_button.setEnabled(True)

    def on_verse_add_button_clicked(self):
        self.verse_form.set_verse('', True)
        if self.verse_form.exec():
            after_text, verse_tag, verse_num = self.verse_form.get_verse()
            verse_def = '{tag}{number}'.format(tag=verse_tag, number=verse_num)
            item = QtWidgets.QTableWidgetItem(after_text)
            item.setData(QtCore.Qt.UserRole, verse_def)
            item.setText(after_text)
            self.verse_list_widget.setRowCount(self.verse_list_widget.rowCount() + 1)
            self.verse_list_widget.setItem(self.verse_list_widget.rowCount() - 1, 0, item)
        self.tag_rows()
        # Check if all verse tags are used.
        self.on_verse_order_text_changed(self.verse_order_edit.text())

    def on_verse_edit_button_clicked(self):
        item = self.verse_list_widget.currentItem()
        if item:
            temp_text = item.text()
            verse_id = item.data(QtCore.Qt.UserRole)
            self.verse_form.set_verse(temp_text, True, verse_id)
            if self.verse_form.exec():
                after_text, verse_tag, verse_num = self.verse_form.get_verse()
                verse_def = '{tag}{number}'.format(tag=verse_tag, number=verse_num)
                item.setData(QtCore.Qt.UserRole, verse_def)
                item.setText(after_text)
                # number of lines has changed, repaint the list moving the data
                if len(temp_text.split('\n')) != len(after_text.split('\n')):
                    temp_list = []
                    temp_ids = []
                    for row in range(self.verse_list_widget.rowCount()):
                        item = self.verse_list_widget.item(row, 0)
                        temp_list.append(item.text())
                        temp_ids.append(item.data(QtCore.Qt.UserRole))
                    self.verse_list_widget.clear()
                    for row, entry in enumerate(temp_list):
                        item = QtWidgets.QTableWidgetItem(entry, 0)
                        item.setData(QtCore.Qt.UserRole, temp_ids[row])
                        self.verse_list_widget.setItem(row, 0, item)
        self.tag_rows()
        # Check if all verse tags are used.
        self.on_verse_order_text_changed(self.verse_order_edit.text())

    def on_verse_edit_all_button_clicked(self):
        """
        Verse edit all button (save) pressed

        :return:
        """
        verse_list = ''
        if self.verse_list_widget.rowCount() > 0:
            for row in range(self.verse_list_widget.rowCount()):
                item = self.verse_list_widget.item(row, 0)
                field = item.data(QtCore.Qt.UserRole)
                verse_tag = VerseType.translated_name(field[0])
                verse_num = field[1:]
                verse_list += '---[{tag}:{number}]---\n'.format(tag=verse_tag, number=verse_num)
                verse_list += item.text()
                verse_list += '\n'
            self.verse_form.set_verse(verse_list)
        else:
            self.verse_form.set_verse('')
        if not self.verse_form.exec():
            return
        verse_list = self.verse_form.get_all_verses()
        verse_list = str(verse_list.replace('\r\n', '\n'))
        self.verse_list_widget.clear()
        self.verse_list_widget.setRowCount(0)
        for row in self.find_verse_split.split(verse_list):
            for match in row.split('---['):
                for count, parts in enumerate(match.split(']---\n')):
                    if count == 0:
                        if len(parts) == 0:
                            continue
                        # handling carefully user inputted versetags
                        separator = parts.find(':')
                        if separator >= 0:
                            verse_name = parts[0:separator].strip()
                            verse_num = parts[separator + 1:].strip()
                        else:
                            verse_name = parts
                            verse_num = '1'
                        verse_index = VerseType.from_loose_input(verse_name)
                        verse_tag = VerseType.tags[verse_index]
                        # Later we need to handle v1a as well.
                        regex = re.compile(r'\D*(\d+)\D*')
                        match = regex.match(verse_num)
                        if match:
                            verse_num = match.group(1)
                        else:
                            verse_num = '1'
                        verse_def = '{tag}{number}'.format(tag=verse_tag, number=verse_num)
                    else:
                        if parts.endswith('\n'):
                            parts = parts.rstrip('\n')
                        item = QtWidgets.QTableWidgetItem(parts)
                        item.setData(QtCore.Qt.UserRole, verse_def)
                        self.verse_list_widget.setRowCount(self.verse_list_widget.rowCount() + 1)
                        self.verse_list_widget.setItem(self.verse_list_widget.rowCount() - 1, 0, item)
        self.tag_rows()
        self.verse_edit_button.setEnabled(False)
        self.verse_delete_button.setEnabled(False)
        # Check if all verse tags are used.
        self.on_verse_order_text_changed(self.verse_order_edit.text())

    def on_verse_delete_button_clicked(self):
        """
        Verse Delete button pressed

        """
        self.verse_list_widget.removeRow(self.verse_list_widget.currentRow())
        if not self.verse_list_widget.selectedItems():
            self.verse_edit_button.setEnabled(False)
            self.verse_delete_button.setEnabled(False)

    def on_verse_order_text_changed(self, text):
        """
        Checks if the verse order is complete or missing. Shows a error message according to the state of the verse
        order.

        :param text: The text of the verse order edit (ignored).
        """
        # First make sure that all letters entered in the verse order field are uppercase
        pos = self.verse_order_edit.cursorPosition()
        self.verse_order_edit.setText(text.upper())
        self.verse_order_edit.setCursorPosition(pos)
        # Extract all verses which were used in the order.
        verses_in_order = self._extract_verse_order(self.verse_order_edit.text())
        # Find the verses which were not used in the order.
        verses_not_used = []
        for index in range(self.verse_list_widget.rowCount()):
            verse = self.verse_list_widget.item(index, 0)
            verse = verse.data(QtCore.Qt.UserRole)
            if verse not in verses_in_order:
                verses_not_used.append(verse)
        # Set the label text.
        label_text = ''
        # No verse order was entered.
        if not verses_in_order:
            label_text = self.no_verse_order_entered_warning
        # The verse order does not contain all verses.
        elif verses_not_used:
            label_text = self.not_all_verses_used_warning
        self.warning_label.setText(label_text)

    def on_copyright_insert_button_triggered(self):
        """
        Copyright insert button pressed
        """
        text = self.copyright_edit.text()
        pos = self.copyright_edit.cursorPosition()
        sign = SongStrings.CopyrightSymbol
        text = text[:pos] + sign + text[pos:]
        self.copyright_edit.setText(text)
        self.copyright_edit.setFocus()
        self.copyright_edit.setCursorPosition(pos + len(sign))

    def on_maintenance_button_clicked(self):
        """
        Maintenance button pressed
        """
        self.media_item.song_maintenance_form.exec(True)
        self.load_authors()
        self.load_songbooks()
        self.load_topics()

    def on_preview(self, button):
        """
        Save and Preview button clicked.
        The Song is valid so as the plugin to add it to preview to see.

        :param button: A button (QPushButton).
        """
        log.debug('onPreview')
        if button.objectName() == 'preview_button':
            self.save_song(True)
            Registry().execute('songs_preview')

    def on_audio_add_from_file_button_clicked(self):
        """
        Loads file(s) from the filesystem.
        """
        filters = '{text} (*)'.format(text=UiStrings().AllFiles)
        file_paths, filter_used = FileDialog.getOpenFileNames(
            parent=self, caption=translate('SongsPlugin.EditSongForm', 'Open File(s)'), filter=filters)
        for file_path in file_paths:
            item = QtWidgets.QListWidgetItem(file_path.name)
            item.setData(QtCore.Qt.UserRole, file_path)
            self.audio_list_widget.addItem(item)

    def on_audio_add_from_media_button_clicked(self):
        """
        Loads file(s) from the media plugin.
        """
        if self.media_form.exec():
            for file_path in self.media_form.get_selected_files():
                item = QtWidgets.QListWidgetItem(file_path.name)
                item.setData(QtCore.Qt.UserRole, file_path)
                self.audio_list_widget.addItem(item)

    def on_audio_remove_button_clicked(self):
        """
        Removes a file from the list.
        """
        row = self.audio_list_widget.currentRow()
        if row == -1:
            return
        self.audio_list_widget.takeItem(row)

    def on_audio_remove_all_button_clicked(self):
        """
        Removes all files from the list.
        """
        self.audio_list_widget.clear()

    def on_up_button_clicked(self):
        """
        Moves a file up when the user clicks the up button on the audio tab.
        """
        row = self.audio_list_widget.currentRow()
        if row <= 0:
            return
        item = self.audio_list_widget.takeItem(row)
        self.audio_list_widget.insertItem(row - 1, item)
        self.audio_list_widget.setCurrentRow(row - 1)

    def on_down_button_clicked(self):
        """
        Moves a file down when the user clicks the up button on the audio tab.
        """
        row = self.audio_list_widget.currentRow()
        if row == -1 or row > self.audio_list_widget.count() - 1:
            return
        item = self.audio_list_widget.takeItem(row)
        self.audio_list_widget.insertItem(row + 1, item)
        self.audio_list_widget.setCurrentRow(row + 1)

    def clear_caches(self):
        """
        Free up auto-completion memory on dialog exit
        """
        log.debug('SongEditForm.clearCaches')
        self.authors = []
        self.themes = []
        self.songbooks = []
        self.topics = []

    def reject(self):
        """
        Exit Dialog and do not save
        """
        log.debug('SongEditForm.reject')
        self.clear_caches()
        QtWidgets.QDialog.reject(self)

    def accept(self):
        """
        Exit Dialog and save song if valid
        """
        log.debug('SongEditForm.accept')
        self.clear_caches()
        if self._validate_song():
            self.save_song()
            self.song = None
            QtWidgets.QDialog.accept(self)

    def save_song(self, preview=False):
        """
        Get all the data from the widgets on the form, and then save it to the database. The form has been validated
        and all reference items (Authors, Books and Topics) have been saved before this function is called.

        :param preview: Should be ``True`` if the song is also previewed (boolean).
        """
        # The Song() assignment. No database calls should be made while a
        # Song() is in a partially complete state.
        if not self.song:
            self.song = Song()
        self.song.title = self.title_edit.text()
        self.song.alternate_title = self.alternative_edit.text()
        self.song.copyright = self.copyright_edit.text()
        # Values will be set when cleaning the song.
        self.song.search_title = ''
        self.song.search_lyrics = ''
        self.song.verse_order = ''
        self.song.comments = self.comments_edit.toPlainText()
        order_text = self.verse_order_edit.text()
        order = []
        for item in order_text.split():
            verse_tag = VerseType.tags[VerseType.from_translated_tag(item[0])]
            verse_num = item[1:].lower()
            order.append('{tag}{number}'.format(tag=verse_tag, number=verse_num))
        self.song.verse_order = ' '.join(order)
        self.song.ccli_number = self.ccli_number_edit.text()
        theme_name = self.theme_combo_box.currentText()
        if theme_name:
            self.song.theme_name = theme_name
        else:
            self.song.theme_name = None
        self._process_lyrics()
        self.song.authors_songs = []
        for row in range(self.authors_list_view.count()):
            item = self.authors_list_view.item(row)
            self.song.add_author(self.manager.get_object(Author, item.data(QtCore.Qt.UserRole)[0]),
                                 item.data(QtCore.Qt.UserRole)[1])
        self.song.topics = []
        for row in range(self.topics_list_view.count()):
            item = self.topics_list_view.item(row)
            topic_id = (item.data(QtCore.Qt.UserRole))
            topic = self.manager.get_object(Topic, topic_id)
            if topic is not None:
                self.song.topics.append(topic)
        self.song.songbook_entries = []
        for row in range(self.songbooks_list_view.count()):
            item = self.songbooks_list_view.item(row)
            songbook_id = item.data(QtCore.Qt.UserRole)[0]
            songbook = self.manager.get_object(Book, songbook_id)
            entry = item.data(QtCore.Qt.UserRole)[1]
            self.song.add_songbook_entry(songbook, entry)
        # Save the song here because we need a valid id for the audio files.
        clean_song(self.manager, self.song)
        self.manager.save_object(self.song)
        audio_paths = [a.file_path for a in self.song.media_files]
        log.debug(audio_paths)
        save_path = AppLocation.get_section_data_path(self.media_item.plugin.name) / 'audio' / str(self.song.id)
        check_directory_exists(save_path)
        self.song.media_files = []
        file_paths = []
        for row in range(self.audio_list_widget.count()):
            item = self.audio_list_widget.item(row)
            file_path = item.data(QtCore.Qt.UserRole)
            if save_path not in file_path.parents:
                old_file_path, file_path = file_path, save_path / file_path.name
                copyfile(old_file_path, file_path)
            file_paths.append(file_path)
            media_file = MediaFile()
            media_file.file_path = file_path
            media_file.type = 'audio'
            media_file.weight = row
            self.song.media_files.append(media_file)
        for audio_path in audio_paths:
            if audio_path not in file_paths:
                try:
                    audio_path.unlink()
                except:
                    log.exception('Could not remove file: {audio}'.format(audio=audio_path))
        if not file_paths:
            try:
                save_path.rmdir()
            except OSError:
                log.exception('Could not remove directory: {path}'.format(path=save_path))
        clean_song(self.manager, self.song)
        self.manager.save_object(self.song)
        self.media_item.auto_select_id = self.song.id
