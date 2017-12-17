#!/usr/bin/env python3
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
The entrypoint for OpenLP
"""
import faulthandler
import multiprocessing
import sys

from openlp.core.app import main
from openlp.core.common import is_win, is_macosx
from openlp.core.common.applocation import AppLocation
from openlp.core.common.path import create_paths


def set_up_fault_handling():
    """
    Set up the Python fault handler
    """
    # Create the cache directory if it doesn't exist, and enable the fault handler to log to an error log file
    create_paths(AppLocation.get_directory(AppLocation.CacheDir))
    faulthandler.enable(open(str(AppLocation.get_directory(AppLocation.CacheDir) / 'error.log'), 'wb'))


if __name__ == '__main__':
    """
    Instantiate and run the application.
    """
    faulthandler.enable()
    set_up_fault_handling()
    # Add support for using multiprocessing from frozen Windows executable (built using PyInstaller),
    # see https://docs.python.org/3/library/multiprocessing.html#multiprocessing.freeze_support
    if is_win():
        multiprocessing.freeze_support()
    # Mac OS X passes arguments like '-psn_XXXX' to the application. This argument is actually a process serial number.
    # However, this causes a conflict with other OpenLP arguments. Since we do not use this argument we can delete it
    # to avoid any potential conflicts.
    if is_macosx():
        sys.argv = [x for x in sys.argv if not x.startswith('-psn')]
    main()
