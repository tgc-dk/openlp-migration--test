# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2009 Raoul Snyman                                        #
# Portions copyright (c) 2008-2009 Martin Thompson, Tim Bentley, Carsten      #
# Tinggaard, Jon Tibble, Jonathan Corwin, Maikel Stuivenberg, Scott Guerrieri #
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

from PyQt4 import QtCore, QtGui

from openlp.core.lib import MediaManagerItem, translate, SongXMLParser, \
    BaseListWithDnD, Receiver
from openlp.plugins.songs.forms import EditSongForm, SongMaintenanceForm

class SongListView(BaseListWithDnD):
    def __init__(self, parent=None):
        self.PluginName = u'Songs'
        BaseListWithDnD.__init__(self, parent)

class SongMediaItem(MediaManagerItem):
    """
    This is the custom media manager item for Songs.
    """
    global log
    log = logging.getLogger(u'SongMediaItem')
    log.info(u'Song Media Item loaded')

    def __init__(self, parent, icon, title):
        self.TranslationContext = u'SongPlugin'
        self.PluginTextShort = u'Song'
        self.ConfigSection = u'songs'
        self.IconPath = u'songs/song'
        self.ListViewWithDnD_class = SongListView
        self.ServiceItemIconName = u':/media/song_image.png'
        self.servicePath = None
        MediaManagerItem.__init__(self, parent, icon, title)
        self.edit_song_form = EditSongForm(self.parent.songmanager, self)
        self.song_maintenance_form = SongMaintenanceForm(
            self.parent.songmanager, self)

    def requiredIcons(self):
        MediaManagerItem.requiredIcons(self)
        self.hasFileIcon = False

    def addEndHeaderBar(self):
        self.addToolbarSeparator()
        ## Song Maintenance Button ##
        self.addToolbarButton(translate(u'SongMediaItem', u'Song Maintenance'),
            translate(u'SongMediaItem',
            u'Maintain the lists of authors, topics and books'),
            ':/songs/song_maintenance.png', self.onSongMaintenanceClick,
            'SongMaintenanceItem')
        ## Add the SongListView widget ##
        # Create the tab widget
        self.SongWidget = QtGui.QWidget(self)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.SongWidget.sizePolicy().hasHeightForWidth())
        self.SongWidget.setSizePolicy(sizePolicy)
        self.SongWidget.setObjectName(u'SongWidget')
        self.SearchLayout = QtGui.QGridLayout(self.SongWidget)
        self.SearchLayout.setMargin(5)
        self.SearchLayout.setSpacing(4)
        self.SearchLayout.setObjectName(u'SearchLayout')
        self.SearchTypeComboBox = QtGui.QComboBox(self.SongWidget)
        self.SearchTypeComboBox.setObjectName(u'SearchTypeComboBox')
        self.SearchLayout.addWidget(self.SearchTypeComboBox, 0, 1, 1, 2)
        self.SearchTypeLabel = QtGui.QLabel(self.SongWidget)
        self.SearchTypeLabel.setObjectName(u'SearchTypeLabel')
        self.SearchLayout.addWidget(self.SearchTypeLabel, 0, 0, 1, 1)
        self.SearchTextLabel = QtGui.QLabel(self.SongWidget)
        self.SearchTextLabel.setObjectName(u'SearchTextLabel')
        self.SearchLayout.addWidget(self.SearchTextLabel, 2, 0, 1, 1)
        self.SearchTextEdit = QtGui.QLineEdit(self.SongWidget)
        self.SearchTextEdit.setObjectName(u'SearchTextEdit')
        self.SearchLayout.addWidget(self.SearchTextEdit, 2, 1, 1, 2)
        self.ClearTextButton = QtGui.QPushButton(self.SongWidget)
        self.ClearTextButton.setObjectName(u'ClearTextButton')
        self.SearchLayout.addWidget(self.ClearTextButton, 3, 1, 1, 1)
        self.SearchTextButton = QtGui.QPushButton(self.SongWidget)
        self.SearchTextButton.setObjectName(u'SearchTextButton')
        self.SearchLayout.addWidget(self.SearchTextButton, 3, 2, 1, 1)
        # Add the song widget to the page layout
        self.PageLayout.addWidget(self.SongWidget)
        # Signals and slots
        QtCore.QObject.connect(self.SearchTextButton,
            QtCore.SIGNAL(u'pressed()'), self.onSearchTextButtonClick)
        QtCore.QObject.connect(self.ClearTextButton,
            QtCore.SIGNAL(u'pressed()'), self.onClearTextButtonClick)
        QtCore.QObject.connect(self.SearchTextEdit,
            QtCore.SIGNAL(u'textChanged(const QString&)'),
            self.onSearchTextEditChanged)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'load_song_list'), self.onSearchTextButtonClick)

    def retranslateUi(self):
        self.SearchTypeLabel.setText(
            translate(u'SongMediaItem', u'Search Type:'))
        self.SearchTextLabel.setText(
            translate(u'SongMediaItem', u'Search Text:'))
        self.ClearTextButton.setText(translate(u'SongMediaItem', u'Clear'))
        self.SearchTextButton.setText(translate(u'SongMediaItem', u'Search'))

    def initialise(self):
        self.SearchTypeComboBox.addItem(translate(u'SongMediaItem', u'Titles'))
        self.SearchTypeComboBox.addItem(translate(u'SongMediaItem', u'Lyrics'))
        self.SearchTypeComboBox.addItem(translate(u'SongMediaItem', u'Authors'))

    def onSearchTextButtonClick(self):
        search_keywords = unicode(self.SearchTextEdit.displayText())
        search_results = []
        search_type = self.SearchTypeComboBox.currentIndex()
        if search_type == 0:
            log.debug(u'Titles Search')
            search_results = self.parent.songmanager.search_song_title(
                search_keywords)
            self.displayResultsSong(search_results)
        elif search_type == 1:
            log.debug(u'Lyrics Search')
            search_results = self.parent.songmanager.search_song_lyrics(
                search_keywords)
            self.displayResultsSong(search_results)
        elif search_type == 2:
            log.debug(u'Authors Search')
            search_results = self.parent.songmanager.get_song_from_author(
                search_keywords)
            self.displayResultsAuthor(search_results)

    def displayResultsSong(self, searchresults):
        log.debug(u'display results Song')
        self.ListView.clear()
        #log.debug(u'Records returned from search %s", len(searchresults))
        for song in searchresults:
            author_list = u''
            for author in song.authors:
                if author_list != u'':
                    author_list = author_list + u', '
                author_list = author_list + author.display_name
            song_detail = unicode(u'%s (%s)' % \
                (unicode(song.title), unicode(author_list)))
            song_name = QtGui.QListWidgetItem(song_detail)
            song_name.setData(QtCore.Qt.UserRole, QtCore.QVariant(song.id))
            self.ListView.addItem(song_name)

    def displayResultsAuthor(self, searchresults):
        log.debug(u'display results Author')
        self.ListView.clear()
        for author in searchresults:
            for song in author.songs:
                song_detail = unicode(u'%s (%s)' % \
                    (unicode(author.display_name), unicode(song.title)))
                song_name = QtGui.QListWidgetItem(song_detail)
                song_name.setData(QtCore.Qt.UserRole, QtCore.QVariant(song.id))
                self.ListView.addItem(song_name)

    def onClearTextButtonClick(self):
        """
        Clear the search text.
        """
        self.SearchTextEdit.clear()

    def onSearchTextEditChanged(self, text):
        search_length = 1
        if self.SearchTypeComboBox.currentIndex() == 1:
            search_length = 7
        if len(text) > search_length:
            self.onSearchTextButtonClick()

    def onNewClick(self):
        self.edit_song_form.newSong()
        self.edit_song_form.exec_()

    def onEditAuthorClick(self):
        self.authors_form.load_form()
        self.authors_form.exec_()

    def onEditTopicClick(self):
        self.topics_form.load_form()
        self.topics_form.exec_()

    def onEditBookClick(self):
        self.song_book_form.load_form()
        self.song_book_form.exec_()

    def onSongMaintenanceClick(self):
        self.song_maintenance_form.exec_()

    def onEditClick(self):
        item = self.ListView.currentItem()
        if item is not None:
            item_id = (item.data(QtCore.Qt.UserRole)).toInt()[0]
            self.edit_song_form.loadSong(item_id)
            self.edit_song_form.exec_()

    def onDeleteClick(self):
        item = self.ListView.currentItem()
        if item is not None:
            item_id = (item.data(QtCore.Qt.UserRole)).toInt()[0]
            self.parent.songmanager.delete_song(item_id)
            row = self.ListView.row(item)
            self.ListView.takeItem(row)

    def generateSlideData(self, service_item):
        #raw_slides =[]
        raw_footer = []
        author_list = u''
        author_audit = []
        ccl = u''
        item = self.ListView.currentItem()
        if item is None:
            return False
        item_id = (item.data(QtCore.Qt.UserRole)).toInt()[0]
        song = self.parent.songmanager.get_song(item_id)
        service_item.theme = song.theme_name
        if song.lyrics.startswith(u'<?xml version='):
            songXML=SongXMLParser(song.lyrics)
            verseList = songXML.get_verses()
            for verse in verseList:
                if verse[1] is not None:
                    service_item.add_from_text(verse[1][:30], verse[1])
        else:
            verses = song.lyrics.split(u'\n\n')
            for slide in verses:
                service_item.add_from_text(slide[:30], unicode(slide))
        service_item.title = song.title
        for author in song.authors:
            if len(author_list) > 1:
                author_list = author_list + u', '
            author_list = author_list + unicode(author.display_name)
            author_audit.append(unicode(author.display_name))
        if song.ccli_number is None or len(song.ccli_number) == 0:
            ccl = self.parent.settings.GeneralTab.CCLNumber
        else:
            ccl = unicode(song.ccli_number)
        raw_footer.append(song.title)
        raw_footer.append(author_list)
        raw_footer.append(song.copyright )
        raw_footer.append(unicode(
            translate(u'SongMediaItem', u'CCL Licence: ') + ccl))
        service_item.raw_footer = raw_footer
        service_item.audit = [song.title, author_audit, song.copyright, song.ccli_number]
        return True
