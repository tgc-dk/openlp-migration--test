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
import logging
import os

from PyQt5 import QtCore, QtWidgets
from sqlalchemy.sql import and_, or_

from openlp.core.common.applocation import AppLocation
from openlp.core.common.i18n import UiStrings, UiIcons, translate, get_natural_key
from openlp.core.common.path import copyfile, create_paths
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.lib import MediaManagerItem, ItemCapabilities, PluginStatus, ServiceItemContext, \
    check_item_selected, create_separated_list
from openlp.core.lib.ui import create_widget_action
from openlp.plugins.songs.forms.editsongform import EditSongForm
from openlp.plugins.songs.forms.songexportform import SongExportForm
from openlp.plugins.songs.forms.songimportform import SongImportForm
from openlp.plugins.songs.forms.songmaintenanceform import SongMaintenanceForm
from openlp.plugins.songs.lib import VerseType, clean_string, delete_song
from openlp.plugins.songs.lib.db import Author, AuthorType, Song, Book, MediaFile, SongBookEntry, Topic
from openlp.plugins.songs.lib.openlyricsxml import OpenLyrics, SongXML
from openlp.plugins.songs.lib.ui import SongStrings

log = logging.getLogger(__name__)


class SongSearch(object):
    """
    An enumeration for song search methods.
    """
    Entire = 1
    Titles = 2
    Lyrics = 3
    Authors = 4
    Topics = 5
    Books = 6
    Themes = 7
    Copyright = 8
    CCLInumber = 9


class SongMediaItem(MediaManagerItem):
    """
    This is the custom media manager item for Songs.
    """
    songs_go_live = QtCore.pyqtSignal(list)
    songs_add_to_service = QtCore.pyqtSignal(list)
    log.info('Song Media Item loaded')

    def __init__(self, parent, plugin):
        self.icon_path = 'songs/song'
        super(SongMediaItem, self).__init__(parent, plugin)

    def setup_item(self):
        """
        Do some additional setup.
        """
        self.songs_go_live.connect(self.go_live_remote)
        self.songs_add_to_service.connect(self.add_to_service_remote)
        self.single_service_item = False
        # Holds information about whether the edit is remotely triggered and which Song is required.
        self.remote_song = -1
        self.edit_item = None
        self.quick_preview_allowed = True
        self.has_search = True

    def _update_background_audio(self, song, item):
        song.media_files = []
        for i, bga in enumerate(item.background_audio):
            dest_path =\
                AppLocation.get_section_data_path(self.plugin.name) / 'audio' / str(song.id) / os.path.split(bga)[1]
            create_paths(dest_path.parent)
            copyfile(AppLocation.get_section_data_path('servicemanager') / bga, dest_path)
            song.media_files.append(MediaFile.populate(weight=i, file_path=dest_path))
        self.plugin.manager.save_object(song, True)

    def add_end_header_bar(self):
        self.toolbar.addSeparator()
        # Song Maintenance Button
        self.maintenance_action = self.toolbar.add_toolbar_action('maintenance_action',
                                                                  icon=UiIcons().database,
                                                                  triggers=self.on_song_maintenance_click)
        self.add_search_to_toolbar()
        # Signals and slots
        Registry().register_function('songs_load_list', self.on_song_list_load)
        Registry().register_function('songs_preview', self.on_preview_click)
        self.search_text_edit.cleared.connect(self.on_clear_text_button_click)
        self.search_text_edit.searchTypeChanged.connect(self.on_search_text_button_clicked)

    def add_custom_context_actions(self):
        create_widget_action(self.list_view, separator=True)
        create_widget_action(
            self.list_view, text=translate('OpenLP.MediaManagerItem', '&Clone'), icon=':/general/general_clone.png',
            triggers=self.on_clone_click)

    def on_focus(self):
        self.search_text_edit.setFocus()
        self.search_text_edit.selectAll()

    def config_update(self):
        """
        Is triggered when the songs config is updated
        """
        log.debug('config_updated')
        self.is_search_as_you_type_enabled = Settings().value('advanced/search as type')
        self.update_service_on_edit = Settings().value(self.settings_section + '/update service on edit')
        self.add_song_from_service = Settings().value(self.settings_section + '/add song from service')
        self.display_songbook = Settings().value(self.settings_section + '/display songbook')
        self.display_written_by_text = Settings().value(self.settings_section + '/display written by')
        self.display_copyright_symbol = Settings().value(self.settings_section + '/display copyright symbol')

    def retranslateUi(self):
        self.search_text_label.setText('{text}:'.format(text=UiStrings().Search))
        self.search_text_button.setText(UiStrings().Search)
        self.maintenance_action.setText(SongStrings.SongMaintenance)
        self.maintenance_action.setToolTip(translate('SongsPlugin.MediaItem',
                                                     'Maintain the lists of authors, topics and books.'))

    def initialise(self):
        """
        Initialise variables when they cannot be initialised in the constructor.
        """
        self.song_maintenance_form = SongMaintenanceForm(self.plugin.manager, self)
        self.edit_song_form = EditSongForm(self, self.main_window, self.plugin.manager)
        self.open_lyrics = OpenLyrics(self.plugin.manager)
        self.search_text_edit.set_search_types([
            (SongSearch.Entire, UiIcons().music,
                translate('SongsPlugin.MediaItem', 'Entire Song'),
                translate('SongsPlugin.MediaItem', 'Search Entire Song...')),
            (SongSearch.Titles, ':/songs/song_search_title.png',
                translate('SongsPlugin.MediaItem', 'Titles'),
                translate('SongsPlugin.MediaItem', 'Search Titles...')),
            (SongSearch.Lyrics, ':/songs/song_search_lyrics.png',
                translate('SongsPlugin.MediaItem', 'Lyrics'),
                translate('SongsPlugin.MediaItem', 'Search Lyrics...')),
            (SongSearch.Authors, ':/songs/song_search_author.png', SongStrings.Authors,
                translate('SongsPlugin.MediaItem', 'Search Authors...')),
            (SongSearch.Topics, ':/songs/song_search_topic.png', SongStrings.Topics,
                translate('SongsPlugin.MediaItem', 'Search Topics...')),
            (SongSearch.Books, UiIcons().address, SongStrings.SongBooks,
                translate('SongsPlugin.MediaItem', 'Search Songbooks...')),
            (SongSearch.Themes, ':/slides/slide_theme.png', UiStrings().Themes, UiStrings().SearchThemes),
            (SongSearch.Copyright, UiIcons().copyright,
                translate('SongsPlugin.MediaItem', 'Copyright'),
                translate('SongsPlugin.MediaItem', 'Search Copyright...')),
            (SongSearch.CCLInumber, ':/songs/song_search_ccli.png',
                translate('SongsPlugin.MediaItem', 'CCLI number'),
                translate('SongsPlugin.MediaItem', 'Search CCLI number...'))
        ])
        self.config_update()

    def on_search_text_button_clicked(self):
        # Reload the list considering the new search type.
        search_keywords = str(self.search_text_edit.displayText())
        search_type = self.search_text_edit.current_search_type()
        if search_type == SongSearch.Entire:
            log.debug('Entire Song Search')
            search_results = self.search_entire(search_keywords)
            self.display_results_song(search_results)
        elif search_type == SongSearch.Titles:
            log.debug('Titles Search')
            search_string = '%{text}%'.format(text=clean_string(search_keywords))
            search_results = self.plugin.manager.get_all_objects(Song, Song.search_title.like(search_string))
            self.display_results_song(search_results)
        elif search_type == SongSearch.Lyrics:
            log.debug('Lyrics Search')
            search_string = '%{text}%'.format(text=clean_string(search_keywords))
            search_results = self.plugin.manager.get_all_objects(Song, Song.search_lyrics.like(search_string))
            self.display_results_song(search_results)
        elif search_type == SongSearch.Authors:
            log.debug('Authors Search')
            search_string = '%{text}%'.format(text=search_keywords)
            search_results = self.plugin.manager.get_all_objects(
                Author, Author.display_name.like(search_string))
            self.display_results_author(search_results)
        elif search_type == SongSearch.Topics:
            log.debug('Topics Search')
            search_string = '%{text}%'.format(text=search_keywords)
            search_results = self.plugin.manager.get_all_objects(
                Topic, Topic.name.like(search_string))
            self.display_results_topic(search_results)
        elif search_type == SongSearch.Books:
            log.debug('Songbook Search')
            search_keywords = search_keywords.rpartition(' ')
            search_book = '{text}%'.format(text=search_keywords[0])
            search_entry = '{text}%'.format(text=search_keywords[2])
            search_results = (self.plugin.manager.session.query(SongBookEntry.entry, Book.name, Song.title, Song.id)
                              .join(Song)
                              .join(Book)
                              .filter(Book.name.like(search_book), SongBookEntry.entry.like(search_entry),
                                      Song.temporary.is_(False)).all())
            self.display_results_book(search_results)
        elif search_type == SongSearch.Themes:
            log.debug('Theme Search')
            search_string = '%{text}%'.format(text=search_keywords)
            search_results = self.plugin.manager.get_all_objects(
                Song, Song.theme_name.like(search_string))
            self.display_results_themes(search_results)
        elif search_type == SongSearch.Copyright:
            log.debug('Copyright Search')
            search_string = '%{text}%'.format(text=search_keywords)
            search_results = self.plugin.manager.get_all_objects(
                Song, and_(Song.copyright.like(search_string), Song.copyright != ''))
            self.display_results_song(search_results)
        elif search_type == SongSearch.CCLInumber:
            log.debug('CCLI number Search')
            search_string = '%{text}%'.format(text=search_keywords)
            search_results = self.plugin.manager.get_all_objects(
                Song, and_(Song.ccli_number.like(search_string), Song.ccli_number != ''))
            self.display_results_cclinumber(search_results)

    def search_entire(self, search_keywords):
        search_string = '%{text}%'.format(text=clean_string(search_keywords))
        return self.plugin.manager.session.query(Song) \
            .join(SongBookEntry, isouter=True) \
            .join(Book, isouter=True) \
            .filter(or_(Book.name.like(search_string), SongBookEntry.entry.like(search_string),
                        # hint: search_title contains alternate title
                        Song.search_title.like(search_string), Song.search_lyrics.like(search_string),
                        Song.comments.like(search_string))) \
            .all()

    def on_song_list_load(self):
        """
        Handle the exit from the edit dialog and trigger remote updates of songs
        """
        log.debug('on_song_list_load - start')
        # Called to redisplay the song list screen edit from a search or from the exit of the Song edit dialog. If
        # remote editing is active Trigger it and clean up so it will not update again. Push edits to the service
        # manager to update items
        if self.edit_item and self.update_service_on_edit and not self.remote_triggered:
            item = self.build_service_item(self.edit_item)
            self.service_manager.replace_service_item(item)
        self.on_search_text_button_clicked()
        log.debug('on_song_list_load - finished')

    def display_results_song(self, search_results):
        """
        Display the song search results in the media manager list

        :param search_results: A list of db Song objects
        :return: None
        """
        def get_song_key(song):
            """Get the key to sort by"""
            return song.sort_key

        log.debug('display results Song')
        self.save_auto_select_id()
        self.list_view.clear()
        search_results.sort(key=get_song_key)
        for song in search_results:
            # Do not display temporary songs
            if song.temporary:
                continue
            author_list = [author.display_name for author in song.authors]
            text = create_separated_list(author_list) if author_list else song.title
            song_detail = '{title} ({author})'.format(title=song.title, author=text)
            song_name = QtWidgets.QListWidgetItem(song_detail)
            song_name.setData(QtCore.Qt.UserRole, song.id)
            self.list_view.addItem(song_name)
            # Auto-select the item if name has been set
            if song.id == self.auto_select_id:
                self.list_view.setCurrentItem(song_name)
        self.auto_select_id = -1

    def display_results_author(self, search_results):
        """
        Display the song search results in the media manager list, grouped by author

        :param search_results: A list of db Author objects
        :return: None
        """
        def get_author_key(author):
            """Get the key to sort by"""
            return get_natural_key(author.display_name)

        def get_song_key(song):
            """Get the key to sort by"""
            return song.sort_key

        log.debug('display results Author')
        self.list_view.clear()
        search_results.sort(key=get_author_key)
        for author in search_results:
            author.songs.sort(key=get_song_key)
            for song in author.songs:
                # Do not display temporary songs
                if song.temporary:
                    continue
                song_detail = '{author} ({title})'.format(author=author.display_name, title=song.title)
                song_name = QtWidgets.QListWidgetItem(song_detail)
                song_name.setData(QtCore.Qt.UserRole, song.id)
                self.list_view.addItem(song_name)

    def display_results_book(self, search_results):
        """
        Display the song search results in the media manager list, grouped by book and entry

        :param search_results: A tuple containing (songbook entry, book name, song title, song id)
        :return: None
        """
        def get_songbook_key(text_array):
            """
            Get the key to sort by
            :param text_array: the result text to be processed.
            """
            return get_natural_key(text_array[1]), get_natural_key(text_array[0]), get_natural_key(text_array[2])

        log.debug('display results Book')
        self.list_view.clear()
        search_results.sort(key=get_songbook_key)
        for result in search_results:
            song_detail = '{result1} #{result0}: {result2}'.format(result1=result[1], result0=result[0],
                                                                   result2=result[2])
            song_name = QtWidgets.QListWidgetItem(song_detail)
            song_name.setData(QtCore.Qt.UserRole, result[3])
            self.list_view.addItem(song_name)

    def display_results_topic(self, search_results):
        """
        Display the song search results in the media manager list, grouped by topic

        :param search_results: A list of db Topic objects
        :return: None
        """
        def get_topic_key(topic):
            """Get the key to sort by"""
            return get_natural_key(topic.name)

        def get_song_key(song):
            """Get the key to sort by"""
            return song.sort_key

        log.debug('display results Topic')
        self.list_view.clear()
        search_results.sort(key=get_topic_key)
        for topic in search_results:
            topic.songs.sort(key=get_song_key)
            for song in topic.songs:
                # Do not display temporary songs
                if song.temporary:
                    continue
                song_detail = '{topic} ({title})'.format(topic=topic.name, title=song.title)
                song_name = QtWidgets.QListWidgetItem(song_detail)
                song_name.setData(QtCore.Qt.UserRole, song.id)
                self.list_view.addItem(song_name)

    def display_results_themes(self, search_results):
        """
        Display the song search results in the media manager list, sorted by theme

        :param search_results: A list of db Song objects
        :return: None
        """
        def get_theme_key(song):
            """Get the key to sort by"""
            return get_natural_key(song.theme_name), song.sort_key

        log.debug('display results Themes')
        self.list_view.clear()
        search_results.sort(key=get_theme_key)
        for song in search_results:
            # Do not display temporary songs
            if song.temporary:
                continue
            song_detail = '{theme} ({song})'.format(theme=song.theme_name, song=song.title)
            song_name = QtWidgets.QListWidgetItem(song_detail)
            song_name.setData(QtCore.Qt.UserRole, song.id)
            self.list_view.addItem(song_name)

    def display_results_cclinumber(self, search_results):
        """
        Display the song search results in the media manager list, sorted by CCLI number

        :param search_results: A list of db Song objects
        :return: None
        """
        def get_cclinumber_key(song):
            """Get the key to sort by"""
            return get_natural_key(song.ccli_number), song.sort_key

        log.debug('display results CCLI number')
        self.list_view.clear()
        search_results.sort(key=get_cclinumber_key)
        for song in search_results:
            # Do not display temporary songs
            if song.temporary:
                continue
            song_detail = '{ccli} ({song})'.format(ccli=song.ccli_number, song=song.title)
            song_name = QtWidgets.QListWidgetItem(song_detail)
            song_name.setData(QtCore.Qt.UserRole, song.id)
            self.list_view.addItem(song_name)

    def on_clear_text_button_click(self):
        """
        Clear the search text.
        """
        self.search_text_edit.clear()
        self.on_search_text_button_clicked()

    def on_search_text_edit_changed(self, text):
        """
        If search as type enabled invoke the search on each key press. If the Lyrics are being searched do not start
        till 7 characters have been entered.
        """
        if self.is_search_as_you_type_enabled:
            search_length = 1
            if self.search_text_edit.current_search_type() == SongSearch.Entire:
                search_length = 4
            elif self.search_text_edit.current_search_type() == SongSearch.Lyrics:
                search_length = 3
            if len(text) > search_length:
                self.on_search_text_button_clicked()
            elif not text:
                self.on_clear_text_button_click()

    def on_import_click(self):
        if not hasattr(self, 'import_wizard'):
            self.import_wizard = SongImportForm(self, self.plugin)
        self.import_wizard.exec()
        # Run song load as list may have been cancelled but some songs loaded
        Registry().execute('songs_load_list')

    def on_export_click(self):
        if not hasattr(self, 'export_wizard'):
            self.export_wizard = SongExportForm(self, self.plugin)
        self.export_wizard.exec()

    def on_new_click(self):
        log.debug('on_new_click')
        self.edit_song_form.new_song()
        self.edit_song_form.exec()
        self.on_clear_text_button_click()
        self.on_selection_change()
        self.auto_select_id = -1

    def on_song_maintenance_click(self):
        self.song_maintenance_form.exec()

    def on_remote_edit(self, song_id, preview=False):
        """
        Called by ServiceManager or SlideController by event passing the Song Id in the payload along with an indicator
        to say which type of display is required.
        :param song_id: the id of the song
        :param preview: show we preview after the update
        """
        log.debug('on_remote_edit for song {song}'.format(song=song_id))
        song_id = int(song_id)
        valid = self.plugin.manager.get_object(Song, song_id)
        if valid:
            self.edit_song_form.load_song(song_id, preview)
            if self.edit_song_form.exec() == QtWidgets.QDialog.Accepted:
                self.auto_select_id = -1
                self.on_song_list_load()
                self.remote_song = song_id
                self.remote_triggered = True
                item = self.build_service_item(remote=True)
                self.remote_song = -1
                self.remote_triggered = None
                if item:
                    if preview:
                        # A song can only be edited if it comes from plugin, so we set it again for the new item.
                        item.from_plugin = True
                    return item
        return None

    def on_edit_click(self):
        """
        Edit a song
        """
        log.debug('on_edit_click')
        if check_item_selected(self.list_view, UiStrings().SelectEdit):
            self.edit_item = self.list_view.currentItem()
            item_id = self.edit_item.data(QtCore.Qt.UserRole)
            self.edit_song_form.load_song(item_id, False)
            self.edit_song_form.exec()
            self.auto_select_id = -1
            self.on_song_list_load()
        self.edit_item = None

    def on_delete_click(self):
        """
        Remove a song from the list and database
        """
        if check_item_selected(self.list_view, UiStrings().SelectDelete):
            items = self.list_view.selectedIndexes()
            if QtWidgets.QMessageBox.question(
                    self, UiStrings().ConfirmDelete,
                    translate('SongsPlugin.MediaItem',
                              'Are you sure you want to delete the "{items:d}" '
                              'selected song(s)?').format(items=len(items)),
                    defaultButton=QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.No:
                return
            self.application.set_busy_cursor()
            self.main_window.display_progress_bar(len(items))
            for item in items:
                item_id = item.data(QtCore.Qt.UserRole)
                delete_song(item_id, self.plugin)
                self.main_window.increment_progress_bar()
            self.main_window.finished_progress_bar()
            self.application.set_normal_cursor()
            self.on_search_text_button_clicked()

    def on_clone_click(self):
        """
        Clone a Song
        """
        log.debug('on_clone_click')
        if check_item_selected(self.list_view, UiStrings().SelectEdit):
            self.edit_item = self.list_view.currentItem()
            item_id = self.edit_item.data(QtCore.Qt.UserRole)
            old_song = self.plugin.manager.get_object(Song, item_id)
            song_xml = self.open_lyrics.song_to_xml(old_song)
            new_song = self.open_lyrics.xml_to_song(song_xml)
            new_song.title = '{title} <{text}>'.format(title=new_song.title,
                                                       text=translate('SongsPlugin.MediaItem',
                                                                      'copy', 'For song cloning'))
            # Copy audio files from the old to the new song
            if len(old_song.media_files) > 0:
                save_path = AppLocation.get_section_data_path(self.plugin.name) / 'audio' / str(new_song.id)
                create_paths(save_path)
                for media_file in old_song.media_files:
                    new_media_file_path = save_path / media_file.file_path.name
                    copyfile(media_file.file_path, new_media_file_path)
                    new_media_file = MediaFile()
                    new_media_file.file_path = new_media_file_path
                    new_media_file.type = media_file.type
                    new_media_file.weight = media_file.weight
                    new_song.media_files.append(new_media_file)
            self.plugin.manager.save_object(new_song)
        self.on_song_list_load()

    def generate_slide_data(self, service_item, item=None, xml_version=False, remote=False,
                            context=ServiceItemContext.Service):
        """
        Generate the slide data. Needs to be implemented by the plugin.

        :param service_item: The service item to be built on
        :param item: The Song item to be used
        :param xml_version: The xml version (not used)
        :param remote: Triggered from remote
        :param context: Why is it being generated
        """
        log.debug('generate_slide_data: {service}, {item}, {remote}'.format(service=service_item, item=item,
                                                                            remote=self.remote_song))
        item_id = self._get_id_of_item_to_generate(item, self.remote_song)
        service_item.add_capability(ItemCapabilities.CanEdit)
        service_item.add_capability(ItemCapabilities.CanPreview)
        service_item.add_capability(ItemCapabilities.CanLoop)
        service_item.add_capability(ItemCapabilities.OnLoadUpdate)
        service_item.add_capability(ItemCapabilities.AddIfNewItem)
        service_item.add_capability(ItemCapabilities.CanSoftBreak)
        service_item.add_capability(ItemCapabilities.HasMetaData)
        song = self.plugin.manager.get_object(Song, item_id)
        service_item.theme = song.theme_name
        service_item.edit_id = item_id
        verse_list = SongXML().get_verses(song.lyrics)
        if Settings().value('songs/add songbook slide') and song.songbook_entries:
            first_slide = '\n'
            for songbook_entry in song.songbook_entries:
                first_slide = first_slide + '{book}/{num}/{pub}\n\n'.format(book=songbook_entry.songbook.name,
                                                                            num=songbook_entry.entry,
                                                                            pub=songbook_entry.songbook.publisher)

            service_item.add_from_text(first_slide, 'O1')
        # no verse list or only 1 space (in error)
        verse_tags_translated = False
        if VerseType.from_translated_string(str(verse_list[0][0]['type'])) is not None:
            verse_tags_translated = True
        if not song.verse_order.strip():
            for verse in verse_list:
                # We cannot use from_loose_input() here, because database is supposed to contain English lowercase
                # single char tags.
                verse_tag = verse[0]['type']
                verse_index = None
                if len(verse_tag) > 1:
                    verse_index = VerseType.from_translated_string(verse_tag)
                    if verse_index is None:
                        verse_index = VerseType.from_string(verse_tag, None)
                if verse_index is None:
                    verse_index = VerseType.from_tag(verse_tag)
                verse_tag = VerseType.translated_tags[verse_index].upper()
                verse_def = '{tag}{label}'.format(tag=verse_tag, label=verse[0]['label'])
                force_verse = verse[1].split('[--}{--]\n')
                for split_verse in force_verse:
                    service_item.add_from_text(split_verse, verse_def)
        else:
            # Loop through the verse list and expand the song accordingly.
            for order in song.verse_order.lower().split():
                if not order:
                    break
                for verse in verse_list:
                    if verse[0]['type'][0].lower() == \
                            order[0] and (verse[0]['label'].lower() == order[1:] or not order[1:]):
                        if verse_tags_translated:
                            verse_index = VerseType.from_translated_tag(verse[0]['type'])
                        else:
                            verse_index = VerseType.from_tag(verse[0]['type'])
                        verse_tag = VerseType.translated_tags[verse_index]
                        verse_def = '{tag}{label}'.format(tag=verse_tag, label=verse[0]['label'])
                        force_verse = verse[1].split('[--}{--]\n')
                        for split_verse in force_verse:
                            service_item.add_from_text(split_verse, verse_def)
        service_item.title = song.title
        author_list = self.generate_footer(service_item, song)
        service_item.data_string = {'title': song.search_title, 'authors': ', '.join(author_list)}
        service_item.xml_version = self.open_lyrics.song_to_xml(song)
        # Add the audio file to the service item.
        if song.media_files:
            service_item.add_capability(ItemCapabilities.HasBackgroundAudio)
            service_item.background_audio = [m.file_path for m in song.media_files]
            item.metadata.append('<em>{label}:</em> {media}'.
                                 format(label=translate('SongsPlugin.MediaItem', 'Media'),
                                        media=service_item.background_audio))
        return True

    def generate_footer(self, item, song):
        """
        Generates the song footer based on a song and adds details to a service item.

        :param item: The service item to be amended
        :param song: The song to be used to generate the footer
        :return: List of all authors (only required for initial song generation)
        """
        authors_words = []
        authors_music = []
        authors_words_music = []
        authors_translation = []
        authors_none = []
        for author_song in song.authors_songs:
            if author_song.author_type == AuthorType.Words:
                authors_words.append(author_song.author.display_name)
            elif author_song.author_type == AuthorType.Music:
                authors_music.append(author_song.author.display_name)
            elif author_song.author_type == AuthorType.WordsAndMusic:
                authors_words_music.append(author_song.author.display_name)
            elif author_song.author_type == AuthorType.Translation:
                authors_translation.append(author_song.author.display_name)
            else:
                authors_none.append(author_song.author.display_name)
        authors_all = authors_words_music + authors_words + authors_music + authors_translation + authors_none
        item.audit = [
            song.title, authors_all, song.copyright, str(song.ccli_number)
        ]
        item.raw_footer = []
        item.raw_footer.append(song.title)
        if authors_none:
            # If the setting for showing "Written by:" is enabled, show it before unspecified authors.
            if Settings().value('songs/display written by'):
                item.raw_footer.append("{text}: {authors}".format(text=translate('OpenLP.Ui', 'Written by'),
                                                                  authors=create_separated_list(authors_none)))
            else:
                item.raw_footer.append("{authors}".format(authors=create_separated_list(authors_none)))
        if authors_words_music:
            item.raw_footer.append("{text}: {authors}".format(text=AuthorType.Types[AuthorType.WordsAndMusic],
                                                              authors=create_separated_list(authors_words_music)))
        if authors_words:
            item.raw_footer.append("{text}: {authors}".format(text=AuthorType.Types[AuthorType.Words],
                                                              authors=create_separated_list(authors_words)))
        if authors_music:
            item.raw_footer.append("{text}: {authors}".format(text=AuthorType.Types[AuthorType.Music],
                                                              authors=create_separated_list(authors_music)))
        if authors_translation:
            item.raw_footer.append("{text}: {authors}".format(text=AuthorType.Types[AuthorType.Translation],
                                                              authors=create_separated_list(authors_translation)))
        if song.copyright:
            if self.display_copyright_symbol:
                item.raw_footer.append("{symbol} {song}".format(symbol=SongStrings.CopyrightSymbol,
                                                                song=song.copyright))
            else:
                item.raw_footer.append(song.copyright)
        if self.display_songbook and song.songbook_entries:
            songbooks = [str(songbook_entry) for songbook_entry in song.songbook_entries]
            item.raw_footer.append(", ".join(songbooks))
        if Settings().value('core/ccli number'):
            item.raw_footer.append(translate('SongsPlugin.MediaItem',
                                             'CCLI License: ') + Settings().value('core/ccli number'))
        item.metadata.append('<em>{label}:</em> {title}'.format(label=translate('SongsPlugin.MediaItem', 'Title'),
                                                                title=song.title))
        if song.alternate_title:
            item.metadata.append('<em>{label}:</em> {title}'.
                                 format(label=translate('SongsPlugin.MediaItem', 'Alt Title'),
                                        title=song.alternate_title))
        if song.songbook_entries:
            for songbook_entry in song.songbook_entries:
                item.metadata.append('<em>{label}:</em> {book}/{num}/{pub}'.
                                     format(label=translate('SongsPlugin.MediaItem', 'Songbook'),
                                            book=songbook_entry.songbook.name,
                                            num=songbook_entry.entry,
                                            pub=songbook_entry.songbook.publisher))
        if song.topics:
            for topics in song.topics:
                item.metadata.append('<em>{label}:</em> {topic}'.
                                     format(label=translate('SongsPlugin.MediaItem', 'Topic'), topic=topics.name))
        return authors_all

    def service_load(self, item):
        """
        Triggered by a song being loaded by the service manager.
        """
        log.debug('service_load')
        if self.plugin.status != PluginStatus.Active or not item.data_string:
            return
        search_results = self.plugin.manager.get_all_objects(
            Song, Song.search_title == item.data_string['title'], Song.search_title.asc())
        edit_id = 0
        add_song = True
        if search_results:
            for song in search_results:
                if self._authors_match(song, item.data_string['authors']):
                    add_song = False
                    edit_id = song.id
                    break
                # If there's any backing tracks, copy them over.
                if item.background_audio:
                    self._update_background_audio(song, item)
        if add_song and self.add_song_from_service:
            song = self.open_lyrics.xml_to_song(item.xml_version)
            # If there's any backing tracks, copy them over.
            if item.background_audio:
                self._update_background_audio(song, item)
            edit_id = song.id
            self.on_search_text_button_clicked()
        elif add_song and not self.add_song_from_service:
            # Make sure we temporary import formatting tags.
            song = self.open_lyrics.xml_to_song(item.xml_version, True)
            # If there's any backing tracks, copy them over.
            if item.background_audio:
                self._update_background_audio(song, item)
            edit_id = song.id
        # Update service with correct song id and return it to caller.
        item.edit_id = edit_id
        self.generate_footer(item, song)
        return item

    @staticmethod
    def _authors_match(song, authors):
        """
        Checks whether authors from a song in the database match the authors of the song to be imported.

        :param song: A list of authors from the song in the database
        :param authors: A string with authors from the song to be imported
        :return: True when Authors do match, else False.
        """
        author_list = authors.split(', ')
        for author in song.authors:
            if author.display_name in author_list:
                author_list.remove(author.display_name)
            else:
                return False
        # List must be empty at the end
        return not author_list

    def search(self, string, show_error=True):
        """
        Search for some songs
        :param string: The string to show
        :param show_error: Is this an error?
        :return: the results of the search
        """
        search_results = self.search_entire(string)
        return [[song.id, song.title, song.alternate_title] for song in search_results]
