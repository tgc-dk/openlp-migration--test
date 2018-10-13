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

from openlp.core.lib.plugin import PluginStatus


log = logging.getLogger()


class State(object):

    __instance__ = None

    def __new__(cls):
        """
        Re-implement the __new__ method to make sure we create a true singleton.
        """
        if not cls.__instance__:
            cls.__instance__ = object.__new__(cls)
            cls.modules = {}
        return cls.__instance__

    def load_settings(self):
        self.modules = {}

    def save_settings(self):
        pass

    def add_service(self, name, order, status, dependance=None):
        if name not in self.modules:
            self.modules[name] = {'order': order, 'status': status, 'depemdancy': dependance}

    def is_service_active(self, name):
        return self.modules[name]['status'] == PluginStatus.Active

    def check_active_dependency(self, name):
        pass
