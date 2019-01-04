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
The :mod:`core` module provides state management

All the core functions of the OpenLP application including the GUI, settings,
logging and a plugin framework are contained within the openlp.core module.
"""
import logging

from openlp.core.common.registry import Registry
from openlp.core.common.mixins import LogMixin
from openlp.core.lib.plugin import PluginStatus


log = logging.getLogger()


class StateModule(LogMixin):
    def __init__(self):
        """
        """
        super(StateModule, self).__init__()
        self.name = None
        self.order = 0
        self.is_plugin = None
        self.status = PluginStatus.Inactive
        self.pass_preconditions = False
        self.requires = None
        self.required_by = None
        self.text = None


class State(LogMixin):

    __instance__ = None

    def __new__(cls):
        """
        Re-implement the __new__ method to make sure we create a true singleton.
        """
        if not cls.__instance__:
            cls.__instance__ = object.__new__(cls)
        return cls.__instance__

    def load_settings(self):
        self.modules = {}

    def save_settings(self):
        pass

    def add_service(self, name, order, is_plugin=False, status=PluginStatus.Active, requires=None):
        """
        Add a module to the array and lod dependancies.  There will only be one item per module
        :param name: Module name
        :param order: Order to display
        :param is_plugin: Am I a plugin
        :param status: The active status
        :param requires: Module name this requires
        :return:
        """
        if name not in self.modules:
            state = StateModule()
            state.name = name
            state.order = order
            state.is_plugin = is_plugin
            state.status = status
            state.requires = requires
            state.required_by = []
            self.modules[name] = state
            if requires and requires in self.modules:
                if requires not in self.modules[requires].required_by:
                    self.modules[requires].required_by.append(name)

    def missing_text(self, name, text):
        """
        Updates the preconditions state of a module

        :param name: Module name
        :param text: Module missing text
        :return:
        """
        self.modules[name].text = text

    def get_text(self):
        """
        return an string of error text
        :return: a string of text
        """
        error_text = ''
        for mod in self.modules:
            if self.modules[mod].text:
                error_text = error_text + self.modules[mod].text + '\n'
        return error_text

    def update_pre_conditions(self, name, status):
        """
        Updates the preconditions state of a module

        :param name: Module name
        :param status: Module new status
        :return:
        """
        self.modules[name].pass_preconditions = status
        if self.modules[name].is_plugin:
            plugin = Registry().get('{mod}_plugin'.format(mod=name))
            if status:
                self.log_debug('Plugin {plugin} active'.format(plugin=str(plugin.name)))
                plugin.set_status()
            else:
                plugin.status = PluginStatus.Disabled

    def flush_preconditions(self):
        """
        Now all modules are loaded lets update all the preconditions.

        :return:
        """
        for mods in self.modules:
            for req in self.modules[mods].required_by:
                self.modules[req].pass_preconditions = self.modules[mods].pass_preconditions
        plugins_list = sorted(self.modules, key=lambda state: self.modules[state].order)
        mdl = {}
        for pl in plugins_list:
            mdl[pl] = self.modules[pl]
        self.modules = mdl

    def is_module_active(self, name):
        return self.modules[name].status == PluginStatus.Active

    def check_preconditions(self, name):
        """
        Checks is a modules preconditions have been met and that of a required by module

        :param name: Module name
        :return: True / False
        """
        if self.modules[name].requires is None:
            return self.modules[name].pass_preconditions
        else:
            mod = self.modules[name].requires
            return self.modules[mod].pass_preconditions

    def list_plugins(self, a=None):
        """
        Return a list of plugins
        :return: an array of plugins
        """
        plugins = []
        if a == 1:
            assert {} == self.modules
        for mod in self.modules:
            if self.modules[mod].is_plugin:
                plugins.append(Registry().get('{mod}_plugin'.format(mod=mod)))
        return plugins
