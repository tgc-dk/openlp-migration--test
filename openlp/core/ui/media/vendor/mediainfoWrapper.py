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
The :mod:`~openlp.core.ui.media.mediainfo` module contains code to run mediainfo
on a media file and obtain information related to the requested media.
"""
from pymediainfo import MediaInfo
from subprocess import check_output
import sys


class MediaInfoWrapper(object):

    @staticmethod
    def parse(filename):
        if MediaInfo.can_parse():
            return MediaInfo.parse(filename)
        else:
            xml = check_output(['mediainfo', '-f', '--Output=XML', '--Inform=OLDXML', filename])
            if not xml.startswith(b'<?xml'):
                xml = check_output(['mediainfo', '-f', '--Output=XML', filename])
            return MediaInfo(xml)
