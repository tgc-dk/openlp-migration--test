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
The :mod:`~openlp.core.widgets.docks` module contains a customised base dock widget and dock widgets
"""
import logging

from PyQt5 import QtWidgets

from openlp.core.display.screens import ScreenList
from openlp.core.lib import StringContent, build_icon

log = logging.getLogger(__name__)


class OpenLPDockWidget(QtWidgets.QDockWidget):
    """
    Custom DockWidget class to handle events
    """
    def __init__(self, parent=None, name=None, icon=None):
        """
        Initialise the DockWidget
        """
        log.debug('Initialise the %s widget' % name)
        super(OpenLPDockWidget, self).__init__(parent)
        if name:
            self.setObjectName(name)
        if icon:
            self.setWindowIcon(build_icon(icon))
        # Sort out the minimum width.
        screens = ScreenList()
        main_window_docbars = screens.current['size'].width() // 5
        if main_window_docbars > 300:
            self.setMinimumWidth(300)
        else:
            self.setMinimumWidth(main_window_docbars)


class MediaDockManager(object):
    """
    Provide a repository for MediaManagerItems
    """
    def __init__(self, media_dock):
        """
        Initialise the media dock
        """
        self.media_dock = media_dock

    def add_item_to_dock(self, media_item):
        """
        Add a MediaManagerItem to the dock
        If the item has been added before, it's silently skipped

        :param media_item: The item to add to the dock
        """
        visible_title = media_item.plugin.get_string(StringContent.VisibleName)
        log.debug('Inserting %s dock' % visible_title['title'])
        match = False
        for dock_index in range(self.media_dock.count()):
            if self.media_dock.widget(dock_index).settings_section == media_item.plugin.name:
                match = True
                break
        if not match:
            self.media_dock.addItem(media_item, media_item.plugin.icon, visible_title['title'])

    def remove_dock(self, media_item):
        """
        Removes a MediaManagerItem from the dock

        :param media_item: The item to add to the dock
        """
        visible_title = media_item.plugin.get_string(StringContent.VisibleName)
        log.debug('remove %s dock' % visible_title['title'])
        for dock_index in range(self.media_dock.count()):
            if self.media_dock.widget(dock_index):
                if self.media_dock.widget(dock_index).settings_section == media_item.plugin.name:
                    self.media_dock.widget(dock_index).setVisible(False)
                    self.media_dock.removeItem(dock_index)
