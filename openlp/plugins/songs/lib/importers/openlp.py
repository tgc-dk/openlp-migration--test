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
The :mod:`openlp` module provides the functionality for importing OpenLP
song databases into the current installation database.
"""
import logging

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import class_mapper, mapper, relation, scoped_session, sessionmaker
from sqlalchemy.orm.exc import UnmappedClassError

from openlp.core.common import translate
from openlp.core.lib.db import BaseModel
from openlp.core.ui.lib.wizard import WizardStrings
from openlp.plugins.songs.lib import clean_song
from openlp.plugins.songs.lib.db import Author, Book, Song, Topic, MediaFile
from .songimport import SongImport

log = logging.getLogger(__name__)


class OpenLPSongImport(SongImport):
    """
    The :class:`OpenLPSongImport` class provides OpenLP with the ability to
    import song databases from other installations of OpenLP.
    """
    def __init__(self, manager, **kwargs):
        """
        Initialise the import.

        :param manager: The song manager for the running OpenLP installation.
        :param kwargs: The database providing the data to import.
        """
        super(OpenLPSongImport, self).__init__(manager, **kwargs)
        self.source_session = None

    def do_import(self, progress_dialog=None):
        """
        Run the import for an OpenLP version 2 song database.

        :param progress_dialog: The QProgressDialog used when importing songs from the FRW.
        """

        class OldAuthor(BaseModel):
            """
            Maps to the authors table
            """
            pass

        class OldBook(BaseModel):
            """
            Maps to the songbooks table
            """
            pass

        class OldMediaFile(BaseModel):
            """
            Maps to the media_files table
            """
            pass

        class OldSong(BaseModel):
            """
            Maps to the songs table
            """
            pass

        class OldTopic(BaseModel):
            """
            Maps to the topics table
            """
            pass

        class OldSongBookEntry(BaseModel):
            """
            Maps to the songs_songbooks table
            """
            pass

        # Check the file type
        if not isinstance(self.import_source, str) or not self.import_source.endswith('.sqlite'):
            self.log_error(self.import_source, translate('SongsPlugin.OpenLPSongImport',
                                                         'Not a valid OpenLP 2 song database.'))
            return
        self.import_source = 'sqlite:///{url}'.format(url=self.import_source)
        # Load the db file and reflect it
        engine = create_engine(self.import_source)
        source_meta = MetaData()
        source_meta.reflect(engine)
        self.source_session = scoped_session(sessionmaker(bind=engine))
        # Run some checks to see which version of the database we have
        if 'media_files' in list(source_meta.tables.keys()):
            has_media_files = True
        else:
            has_media_files = False
        if 'songs_songbooks' in list(source_meta.tables.keys()):
            has_songs_books = True
        else:
            has_songs_books = False
        # Load up the tabls and map them out
        source_authors_table = source_meta.tables['authors']
        source_song_books_table = source_meta.tables['song_books']
        source_songs_table = source_meta.tables['songs']
        source_topics_table = source_meta.tables['topics']
        source_authors_songs_table = source_meta.tables['authors_songs']
        source_songs_topics_table = source_meta.tables['songs_topics']
        source_media_files_songs_table = None
        # Set up media_files relations
        if has_media_files:
            source_media_files_table = source_meta.tables['media_files']
            source_media_files_songs_table = source_meta.tables.get('media_files_songs')
            try:
                class_mapper(OldMediaFile)
            except UnmappedClassError:
                mapper(OldMediaFile, source_media_files_table)
        if has_songs_books:
            source_songs_songbooks_table = source_meta.tables['songs_songbooks']
            try:
                class_mapper(OldSongBookEntry)
            except UnmappedClassError:
                mapper(OldSongBookEntry, source_songs_songbooks_table, properties={'songbook': relation(OldBook)})
        # Set up the songs relationships
        song_props = {
            'authors': relation(OldAuthor, backref='songs', secondary=source_authors_songs_table),
            'topics': relation(OldTopic, backref='songs', secondary=source_songs_topics_table)
        }
        if has_media_files:
            if isinstance(source_media_files_songs_table, Table):
                song_props['media_files'] = relation(OldMediaFile, backref='songs',
                                                     secondary=source_media_files_songs_table)
            else:
                song_props['media_files'] = \
                    relation(OldMediaFile, backref='songs',
                             foreign_keys=[source_media_files_table.c.song_id],
                             primaryjoin=source_songs_table.c.id == source_media_files_table.c.song_id)
        if has_songs_books:
            song_props['songbook_entries'] = relation(OldSongBookEntry, backref='song', cascade='all, delete-orphan')
        else:
            song_props['book'] = relation(OldBook, backref='songs')
        # Map the rest of the tables
        try:
            class_mapper(OldAuthor)
        except UnmappedClassError:
            mapper(OldAuthor, source_authors_table)
        try:
            class_mapper(OldBook)
        except UnmappedClassError:
            mapper(OldBook, source_song_books_table)
        try:
            class_mapper(OldSong)
        except UnmappedClassError:
            mapper(OldSong, source_songs_table, properties=song_props)
        try:
            class_mapper(OldTopic)
        except UnmappedClassError:
            mapper(OldTopic, source_topics_table)

        source_songs = self.source_session.query(OldSong).all()
        if self.import_wizard:
            self.import_wizard.progress_bar.setMaximum(len(source_songs))
        for song in source_songs:
            new_song = Song()
            new_song.title = song.title
            if has_media_files and hasattr(song, 'alternate_title'):
                new_song.alternate_title = song.alternate_title
            else:
                old_titles = song.search_title.split('@')
                if len(old_titles) > 1:
                    new_song.alternate_title = old_titles[1]
            # Transfer the values to the new song object
            new_song.search_title = ''
            new_song.search_lyrics = ''
            new_song.lyrics = song.lyrics
            new_song.verse_order = song.verse_order
            new_song.copyright = song.copyright
            new_song.comments = song.comments
            new_song.theme_name = song.theme_name
            new_song.ccli_number = song.ccli_number
            if hasattr(song, 'song_number') and song.song_number:
                new_song.song_number = song.song_number
            # Find or create all the authors and add them to the new song object
            for author in song.authors:
                existing_author = self.manager.get_object_filtered(Author, Author.display_name == author.display_name)
                if not existing_author:
                    existing_author = Author.populate(
                        first_name=author.first_name,
                        last_name=author.last_name,
                        display_name=author.display_name)
                new_song.add_author(existing_author)
            # Find or create all the topics and add them to the new song object
            if song.topics:
                for topic in song.topics:
                    existing_topic = self.manager.get_object_filtered(Topic, Topic.name == topic.name)
                    if not existing_topic:
                        existing_topic = Topic.populate(name=topic.name)
                    new_song.topics.append(existing_topic)
            # Find or create all the songbooks and add them to the new song object
            if has_songs_books and song.songbook_entries:
                for entry in song.songbook_entries:
                    existing_book = self.manager.get_object_filtered(Book, Book.name == entry.songbook.name)
                    if not existing_book:
                        existing_book = Book.populate(name=entry.songbook.name, publisher=entry.songbook.publisher)
                    new_song.add_songbook_entry(existing_book, entry.entry)
            elif hasattr(song, 'book') and song.book:
                existing_book = self.manager.get_object_filtered(Book, Book.name == song.book.name)
                if not existing_book:
                    existing_book = Book.populate(name=song.book.name, publisher=song.book.publisher)
                # Get the song_number from "songs" table "song_number" field. (This is db structure from 2.2.1)
                # If there's a number, add it to the song, otherwise it will be "".
                existing_number = song.song_number if hasattr(song, 'song_number') else ''
                if existing_number:
                    new_song.add_songbook_entry(existing_book, existing_number)
                else:
                    new_song.add_songbook_entry(existing_book, '')
            # Find or create all the media files and add them to the new song object
            if has_media_files and song.media_files:
                for media_file in song.media_files:
                    existing_media_file = self.manager.get_object_filtered(
                        MediaFile, MediaFile.file_name == media_file.file_name)
                    if existing_media_file:
                        new_song.media_files.append(existing_media_file)
                    else:
                        new_song.media_files.append(MediaFile.populate(file_name=media_file.file_name))
            clean_song(self.manager, new_song)
            self.manager.save_object(new_song)
            if progress_dialog:
                progress_dialog.setValue(progress_dialog.value() + 1)
                # TODO: Verify format() with template strings
                progress_dialog.setLabelText(WizardStrings.ImportingType % new_song.title)
            else:
                # TODO: Verify format() with template strings
                self.import_wizard.increment_progress_bar(WizardStrings.ImportingType % new_song.title)
            if self.stop_import_flag:
                break
        self.source_session.close()
        engine.dispose()
