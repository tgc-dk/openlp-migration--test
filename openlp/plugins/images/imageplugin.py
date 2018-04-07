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

from PyQt5 import QtGui

from openlp.core.api.http import register_endpoint
from openlp.core.common.i18n import UiIcons, translate
from openlp.core.common.settings import Settings
from openlp.core.lib import Plugin, StringContent, ImageSource, build_icon
from openlp.core.lib.db import Manager
from openlp.plugins.images.endpoint import api_images_endpoint, images_endpoint
from openlp.plugins.images.lib import ImageMediaItem, ImageTab, upgrade
from openlp.plugins.images.lib.db import init_schema

log = logging.getLogger(__name__)

__default_settings__ = {
    'images/db type': 'sqlite',
    'images/db username': '',
    'images/db password': '',
    'images/db hostname': '',
    'images/db database': '',
    'images/background color': '#000000',
    'images/last directory': None
}


class ImagePlugin(Plugin):
    log.info('Image Plugin loaded')

    def __init__(self):
        super(ImagePlugin, self).__init__('images', __default_settings__, ImageMediaItem, ImageTab)
        self.manager = Manager('images', init_schema, upgrade_mod=upgrade)
        self.weight = -7
        self.icon_path = UiIcons().picture
        self.icon = build_icon(self.icon_path)
        register_endpoint(images_endpoint)
        register_endpoint(api_images_endpoint)

    @staticmethod
    def about():
        about_text = translate('ImagePlugin', '<strong>Image Plugin</strong>'
                               '<br />The image plugin provides displaying of images.<br />One '
                               'of the distinguishing features of this plugin is the ability to '
                               'group a number of images together in the service manager, making '
                               'the displaying of multiple images easier. This plugin can also '
                               'make use of OpenLP\'s "timed looping" feature to create a slide '
                               'show that runs automatically. In addition to this, images from '
                               'the plugin can be used to override the current theme\'s '
                               'background, which renders text-based items like songs with the '
                               'selected image as a background instead of the background '
                               'provided by the theme.')
        return about_text

    def set_plugin_text_strings(self):
        """
        Called to define all translatable texts of the plugin.
        """
        # Name PluginList
        self.text_strings[StringContent.Name] = {
            'singular': translate('ImagePlugin', 'Image', 'name singular'),
            'plural': translate('ImagePlugin', 'Images', 'name plural')
        }
        # Name for MediaDockManager, SettingsManager
        self.text_strings[StringContent.VisibleName] = {'title': translate('ImagePlugin', 'Images', 'container title')}
        # Middle Header Bar
        tooltips = {
            'load': translate('ImagePlugin', 'Add new image(s).'),
            'import': '',
            'new': translate('ImagePlugin', 'Add a new image.'),
            'edit': translate('ImagePlugin', 'Edit the selected image.'),
            'delete': translate('ImagePlugin', 'Delete the selected image.'),
            'preview': translate('ImagePlugin', 'Preview the selected image.'),
            'live': translate('ImagePlugin', 'Send the selected image live.'),
            'service': translate('ImagePlugin', 'Add the selected image to the service.')
        }
        self.set_plugin_ui_text_strings(tooltips)

    def config_update(self):
        """
        Triggered by saving and changing the image border.  Sets the images in image manager to require updates. Actual
        update is triggered by the last part of saving the config.
        """
        log.info('Images config_update')
        background = QtGui.QColor(Settings().value(self.settings_section + '/background color'))
        self.image_manager.update_images_border(ImageSource.ImagePlugin, background)
