# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

import json
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
import os


def assert_length(expected, iterable, msg=None):
    if len(iterable) != expected:
        if not msg:
            msg = 'Expected length {expected}, got {got}'.format(expected=expected, got=len(iterable))
        raise AssertionError(msg)


def convert_file_service_item(test_path, name, row=0):
    service_file = os.path.join(test_path, name)
    open_file = open(service_file, 'r')
    try:
        items = json.load(open_file)
        first_line = items[row]
    except OSError:
        first_line = ''
    finally:
        open_file.close()
    return first_line


def load_external_result_data(file_path):
    """
    A method to load and return an object containing the song data from an external file.

    :param openlp.core.common.path.Path file_path: The path of the file to load
    """
    return json.loads(file_path.read_bytes().decode())
