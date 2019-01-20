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
"""
Provide plugin management
"""
import os

from PyQt5 import QtWidgets

from openlp.core.state import State
from openlp.core.common import extension_loader
from openlp.core.common.applocation import AppLocation
from openlp.core.common.i18n import translate, UiStrings
from openlp.core.common.mixins import LogMixin, RegistryProperties
from openlp.core.common.registry import RegistryBase
from openlp.core.lib.plugin import Plugin, PluginStatus


class PluginManager(RegistryBase, LogMixin, RegistryProperties):
    """
    This is the Plugin manager, which loads all the plugins,
    and executes all the hooks, as and when necessary.
    """
    def __init__(self, parent=None):
        """
        The constructor for the plugin manager. Passes the controllers on to
        the plugins for them to interact with via their ServiceItems.
        """
        super(PluginManager, self).__init__(parent)
        self.log_info('Plugin manager Initialising')
        self.log_debug('Base path {path}'.format(path=AppLocation.get_directory(AppLocation.PluginsDir)))
        self.plugins = []
        self.log_info('Plugin manager Initialised')

    def bootstrap_initialise(self):
        """
        Bootstrap all the plugin manager functions
        Scan a directory for objects inheriting from the ``Plugin`` class.
        """
        glob_pattern = os.path.join('plugins', '*', '[!.]*plugin.py')
        extension_loader(glob_pattern)
        plugin_classes = Plugin.__subclasses__()
        for p in plugin_classes:
            try:
                p()
                self.log_debug('Loaded plugin {plugin}'.format(plugin=str(p)))
            except TypeError:
                self.log_exception('Failed to load plugin {plugin}'.format(plugin=str(p)))

    def bootstrap_post_set_up(self):
        """
        Bootstrap all the plugin manager functions
        """
        self.hook_settings_tabs()
        # Find and insert media manager items
        self.hook_media_manager()
        # Call the hook method to pull in import menus.
        self.hook_import_menu()
        # Call the hook method to pull in export menus.
        self.hook_export_menu()
        # Call the hook method to pull in tools menus.
        self.hook_tools_menu()
        # Call the initialise method to setup plugins.
        self.initialise_plugins()

    def bootstrap_completion(self):
        """
        Give all the plugins a chance to perform some tasks at startup
        """
        self.application.process_events()
        for plugin in State().list_plugins():
            if plugin and plugin.is_active():
                plugin.app_startup()
                self.application.process_events()

    @staticmethod
    def hook_media_manager():
        """
        Create the plugins' media manager items.
        """
        for plugin in State().list_plugins():
            if plugin and plugin.status is not PluginStatus.Disabled:
                plugin.create_media_manager_item()

    def hook_settings_tabs(self):
        """
        Loop through all the plugins. If a plugin has a valid settings tab
        item, add it to the settings tab.
        Tabs are set for all plugins not just Active ones

        """
        for plugin in State().list_plugins():
            if plugin and plugin.status is not PluginStatus.Disabled:
                plugin.create_settings_tab(self.settings_form)

    def hook_import_menu(self):
        """
        Loop through all the plugins and give them an opportunity to add an
        item to the import menu.

        """
        for plugin in State().list_plugins():
            if plugin and plugin.status is not PluginStatus.Disabled:
                plugin.add_import_menu_item(self.main_window.file_import_menu)

    def hook_export_menu(self):
        """
        Loop through all the plugins and give them an opportunity to add an
        item to the export menu.
        """
        for plugin in State().list_plugins():
            if plugin and plugin.status is not PluginStatus.Disabled:
                plugin.add_export_menu_item(self.main_window.file_export_menu)

    def hook_tools_menu(self):
        """
        Loop through all the plugins and give them an opportunity to add an
        item to the tools menu.
        """
        for plugin in State().list_plugins():
            if plugin and plugin.status is not PluginStatus.Disabled:
                plugin.add_tools_menu_item(self.main_window.tools_menu)

    @staticmethod
    def hook_upgrade_plugin_settings(settings):
        """
        Loop through all the plugins and give them an opportunity to upgrade their settings.

        :param settings: The Settings object containing the old settings.
        """
        for plugin in State().list_plugins():
            if plugin and plugin.status is not PluginStatus.Disabled:
                plugin.upgrade_settings(settings)

    def initialise_plugins(self):
        """
        Loop through all the plugins and give them an opportunity to initialise themselves.
        """
        uninitialised_plugins = []
        for plugin in State().list_plugins():
            if plugin:
                self.log_info('initialising plugins {plugin} in a {state} state'.format(plugin=plugin.name,
                                                                                        state=plugin.is_active()))
                if plugin.is_active():
                    try:
                        plugin.initialise()
                        self.log_info('Initialisation Complete for {plugin}'.format(plugin=plugin.name))
                    except Exception:
                        uninitialised_plugins.append(plugin.name.title())
                        self.log_exception('Unable to initialise plugin {plugin}'.format(plugin=plugin.name))
        display_text = ''
        if uninitialised_plugins:
            display_text = translate('OpenLP.PluginManager', 'Unable to initialise the following plugins:') + \
                '\n\n'.join(uninitialised_plugins) + '\n\n'
        error_text = State().get_text()
        if error_text:
            display_text = display_text + error_text + '\n'
        if display_text:
            display_text = display_text + translate('OpenLP.PluginManager', 'See the log file for more details')
            QtWidgets.QMessageBox.critical(None, UiStrings().Error, display_text,
                                           QtWidgets.QMessageBox.StandardButtons(QtWidgets.QMessageBox.Ok))

    def finalise_plugins(self):
        """
        Loop through all the plugins and give them an opportunity to clean themselves up
        """
        for plugin in State().list_plugins():
            if plugin and plugin.is_active():
                plugin.finalise()
                self.log_info('Finalisation Complete for {plugin}'.format(plugin=plugin.name))

    @staticmethod
    def get_plugin_by_name(name):
        """
        Return the plugin which has a name with value ``name``.
        """
        for plugin in State().list_plugins():
            if plugin and plugin.name == name:
                return plugin
        return None

    @staticmethod
    def new_service_created():
        """
        Loop through all the plugins and give them an opportunity to handle a new service
        """
        for plugin in State().list_plugins():
            if plugin.is_active():
                plugin.new_service_created()
