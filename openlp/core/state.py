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
        self.status = PluginStatus.Inactive
        self.pass_preconditions = True
        self.requires = None
        self.required_by = None


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

    def add_service(self, name, order, status=PluginStatus.Active, requires=None):
        """
        Add a module to the array and lod dependancies.  There will only be one item per module
        :param name: Module name
        :param order: Order fo display
        :param status: The active status
        :param requires: Module name this requires
        :return:
        """
        if name not in self.modules:
            state = StateModule()
            state.name = name
            state.order = order
            state.status = status
            state.requires = requires
            state.required_by = []
            self.modules[name] = state
            if requires and requires in self.modules:
                if requires not in self.modules[requires].required_by:
                    self.modules[requires].required_by.append(name)

    def update_pre_conditions(self, name, status):
        """
        Updates the preconditions state of a module

        :param name: Module name
        :param status: Module new status
        :return:
        """
        self.modules[name].pass_preconditions = status

    def flush_preconditions(self):
        """
        Now all modules are loaded lets update all the preconditions.

        :return:
        """
        for mods in self.modules:
            for req in self.modules[mods].required_by:
                self.modules[req].pass_preconditions = self.modules[mods].pass_preconditions

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
