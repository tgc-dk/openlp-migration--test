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
The Media plugin
"""
import logging
import os
import re

from PyQt5 import QtCore

from openlp.core.api.http import register_endpoint
from openlp.core.common import check_binary_exists
from openlp.core.common.applocation import AppLocation
from openlp.core.common.i18n import translate
from openlp.core.common.path import Path
from openlp.core.lib import Plugin, StringContent, build_icon
from openlp.plugins.media.endpoint import api_media_endpoint, media_endpoint
from openlp.plugins.media.lib import MediaMediaItem, MediaTab


log = logging.getLogger(__name__)


# Some settings starting with "media" are in core, because they are needed for core functionality.
__default_settings__ = {
    'media/media auto start': QtCore.Qt.Unchecked,
    'media/media files': [],
    'media/last directory': None
}


class MediaPlugin(Plugin):
    """
    The media plugin adds the ability to playback audio and video content.
    """
    log.info('{name} MediaPlugin loaded'.format(name=__name__))

    def __init__(self):
        super(MediaPlugin, self).__init__('media', __default_settings__, MediaMediaItem)
        self.weight = -6
        self.icon_path = ':/plugins/plugin_media.png'
        self.icon = build_icon(self.icon_path)
        # passed with drag and drop messages
        self.dnd_id = 'Media'
        register_endpoint(media_endpoint)
        register_endpoint(api_media_endpoint)

    def initialise(self):
        """
        Override the inherited initialise() method in order to upgrade the media before trying to load it
        """
        super().initialise()

    def check_pre_conditions(self):
        """
        Check it we have a valid environment.
        :return: true or false
        """
        log.debug('check_installed Mediainfo')
        # Try to find mediainfo in the path
        exists = process_check_binary('mediainfo')
        # If mediainfo is not in the path, try to find it in the application folder
        if not exists:
            exists = process_check_binary(os.path.join(str(AppLocation.get_directory(AppLocation.AppDir)), 'mediainfo'))
        return exists

    def app_startup(self):
        """
        Override app_startup() in order to do nothing
        """
        pass

    def create_settings_tab(self, parent):
        """
        Create the settings Tab

        :param parent:
        """
        visible_name = self.get_string(StringContent.VisibleName)
        self.settings_tab = MediaTab(parent, self.name, visible_name['title'], self.icon_path)

    @staticmethod
    def about():
        """
        Return the about text for the plugin manager
        """
        about_text = translate('MediaPlugin', '<strong>Media Plugin</strong>'
                               '<br />The media plugin provides playback of audio and video.')
        return about_text

    def set_plugin_text_strings(self):
        """
        Called to define all translatable texts of the plugin
        """
        # Name PluginList
        self.text_strings[StringContent.Name] = {
            'singular': translate('MediaPlugin', 'Media', 'name singular'),
            'plural': translate('MediaPlugin', 'Media', 'name plural')
        }
        # Name for MediaDockManager, SettingsManager
        self.text_strings[StringContent.VisibleName] = {
            'title': translate('MediaPlugin', 'Media', 'container title')
        }
        # Middle Header Bar
        tooltips = {
            'load': translate('MediaPlugin', 'Load new media.'),
            'import': '',
            'new': translate('MediaPlugin', 'Add new media.'),
            'edit': translate('MediaPlugin', 'Edit the selected media.'),
            'delete': translate('MediaPlugin', 'Delete the selected media.'),
            'preview': translate('MediaPlugin', 'Preview the selected media.'),
            'live': translate('MediaPlugin', 'Send the selected media live.'),
            'service': translate('MediaPlugin', 'Add the selected media to the service.')
        }
        self.set_plugin_ui_text_strings(tooltips)

    def finalise(self):
        """
        Time to tidy up on exit.
        """
        log.info('Media Finalising')
        self.media_controller.finalise()
        Plugin.finalise(self)

    def get_display_css(self):
        """
        Add css style sheets to htmlbuilder.
        """
        return self.media_controller.get_media_display_css()

    def get_display_javascript(self):
        """
        Add javascript functions to htmlbuilder.
        """
        return self.media_controller.get_media_display_javascript()

    def get_display_html(self):
        """
        Add html code to htmlbuilder.
        """
        return self.media_controller.get_media_display_html()


def process_check_binary(program_path):
    """
    Function that checks whether a binary MediaInfo is present

    :param program_path:The full path to the binary to check.
    :return: If exists or not
    """
    runlog = check_binary_exists(Path(program_path))
    # Analyse the output to see it the program is mediainfo
    for line in runlog.splitlines():
        decoded_line = line.decode()
        if re.search('MediaInfo Command line', decoded_line, re.IGNORECASE):
            return True
    return False
