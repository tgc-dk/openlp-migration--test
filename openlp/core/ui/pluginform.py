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
The actual plugin view form
"""
import logging

from PyQt5 import QtCore, QtWidgets

from openlp.core.common import RegistryProperties, translate
from openlp.core.lib import PluginStatus
from .plugindialog import Ui_PluginViewDialog

log = logging.getLogger(__name__)


class PluginForm(QtWidgets.QDialog, Ui_PluginViewDialog, RegistryProperties):
    """
    The plugin form provides user control over the plugins OpenLP uses.
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(PluginForm, self).__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.active_plugin = None
        self.programatic_change = False
        self.setupUi(self)
        self.load()
        self._clear_details()
        # Right, now let's put some signals and slots together!
        self.plugin_list_widget.itemSelectionChanged.connect(self.on_plugin_list_widget_selection_changed)
        self.status_checkbox.stateChanged.connect(self.on_status_checkbox_changed)

    def load(self):
        """
        Load the plugin details into the screen
        """
        self.plugin_list_widget.clear()
        self.programatic_change = True
        self._clear_details()
        self.programatic_change = True
        plugin_list_width = 0
        for plugin in self.plugin_manager.plugins:
            item = QtWidgets.QListWidgetItem(self.plugin_list_widget)
            # We do this just to make 100% sure the status is an integer as
            # sometimes when it's loaded from the config, it isn't cast to int.
            plugin.status = int(plugin.status)
            # Set the little status text in brackets next to the plugin name.
            if plugin.status == PluginStatus.Disabled:
                status_text = translate('OpenLP.PluginForm', '{name} (Disabled)')
            elif plugin.status == PluginStatus.Active:
                status_text = translate('OpenLP.PluginForm', '{name} (Active)')
            else:
                # PluginStatus.Inactive
                status_text = translate('OpenLP.PluginForm', '{name} (Inactive)')
            item.setText(status_text.format(name=plugin.name_strings['singular']))
            # If the plugin has an icon, set it!
            if plugin.icon:
                item.setIcon(plugin.icon)
            self.plugin_list_widget.addItem(item)
            plugin_list_width = max(plugin_list_width, self.fontMetrics().width(
                translate('OpenLP.PluginForm', '{name} (Inactive)').format(name=plugin.name_strings['singular'])))
        self.plugin_list_widget.setFixedWidth(plugin_list_width + self.plugin_list_widget.iconSize().width() + 48)

    def _clear_details(self):
        """
        Clear the plugin details widgets
        """
        self.status_checkbox.setChecked(False)
        self.about_text_browser.setHtml('')
        self.status_checkbox.setEnabled(False)

    def _set_details(self):
        """
        Set the details of the currently selected plugin
        """
        log.debug('PluginStatus: {status}'.format(status=str(self.active_plugin.status)))
        self.about_text_browser.setHtml(self.active_plugin.about())
        self.programatic_change = True
        if self.active_plugin.status != PluginStatus.Disabled:
            self.status_checkbox.setChecked(self.active_plugin.status == PluginStatus.Active)
            self.status_checkbox.setEnabled(True)
        else:
            self.status_checkbox.setChecked(False)
            self.status_checkbox.setEnabled(False)
        self.programatic_change = False

    def on_plugin_list_widget_selection_changed(self):
        """
        If the selected plugin changes, update the form
        """
        if self.plugin_list_widget.currentItem() is None:
            self._clear_details()
            return
        plugin_name_singular = self.plugin_list_widget.currentItem().text().split('(')[0][:-1]
        self.active_plugin = None
        for plugin in self.plugin_manager.plugins:
            if plugin.name_strings['singular'] == plugin_name_singular:
                self.active_plugin = plugin
                break
        if self.active_plugin:
            self._set_details()
        else:
            self._clear_details()

    def on_status_checkbox_changed(self, status):
        """
        If the status of a plugin is altered, apply the change
        """
        if self.programatic_change or self.active_plugin is None:
            return
        if status:
            self.application.set_busy_cursor()
            self.active_plugin.toggle_status(PluginStatus.Active)
            self.application.set_normal_cursor()
            self.active_plugin.app_startup()
        else:
            self.active_plugin.toggle_status(PluginStatus.Inactive)
        status_text = translate('OpenLP.PluginForm', '{name} (Inactive)')
        if self.active_plugin.status == PluginStatus.Active:
            status_text = translate('OpenLP.PluginForm', '{name} (Active)')
        elif self.active_plugin.status == PluginStatus.Inactive:
            status_text = translate('OpenLP.PluginForm', '{name} (Inactive)')
        elif self.active_plugin.status == PluginStatus.Disabled:
            status_text = translate('OpenLP.PluginForm', '{name} (Disabled)')
        self.plugin_list_widget.currentItem().setText(
            status_text.format(name=self.active_plugin.name_strings['singular']))
