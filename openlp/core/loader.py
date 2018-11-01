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
The :mod:`~openlp.core.loader` module provides a bootstrap for the singleton classes
"""

from openlp.core.state import State
from openlp.core.ui.media.mediacontroller import MediaController
from openlp.core.lib.pluginmanager import PluginManager
from openlp.core.display.renderer import Renderer
from openlp.core.lib.imagemanager import ImageManager
from openlp.core.ui.slidecontroller import LiveController, PreviewController


def loader():
    """
    God class to load all the components which are registered with the Registry

    :return: None
    """
    State().load_settings()
    MediaController()
    PluginManager()
    # Set up the path with plugins
    ImageManager()
    Renderer()
    # Create slide controllers
    PreviewController()
    LiveController()
