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
The :mod:`~openlp.core.ui.media` module contains classes and objects for media player integration.
"""
import logging

log = logging.getLogger(__name__ + '.__init__')


class MediaState(object):
    """
    An enumeration for possible States of the Media Player
    """
    Off = 0
    Loaded = 1
    Playing = 2
    Paused = 3
    Stopped = 4


class MediaType(object):
    """
    An enumeration of possible Media Types
    """
    Unused = 0
    Audio = 1
    Video = 2
    CD = 3
    DVD = 4
    Folder = 5


class ItemMediaInfo(object):
    """
    This class hold the media related info
    """
    file_info = None
    volume = 100
    is_background = False
    can_loop_playback = False
    length = 0
    start_time = 0
    end_time = 0
    title_track = 0
    is_playing = False
    timer = 1000
    audio_track = 0
    subtitle_track = 0
    media_type = MediaType()


def parse_optical_path(input_string):
    """
    Split the optical path info.

    :param input_string: The string to parse
    :return: The elements extracted from the string:  filename, title, audio_track, subtitle_track, start, end
    """
    log.debug('parse_optical_path, about to parse: "{text}"'.format(text=input_string))
    clip_info = input_string.split(sep=':')
    title = int(clip_info[1])
    audio_track = int(clip_info[2])
    subtitle_track = int(clip_info[3])
    start = float(clip_info[4])
    end = float(clip_info[5])
    clip_name = clip_info[6]
    filename = clip_info[7]
    # Windows path usually contains a colon after the drive letter
    if len(clip_info) > 8:
        filename += ':' + clip_info[8]
    return filename, title, audio_track, subtitle_track, start, end, clip_name


def format_milliseconds(milliseconds):
    """
    Format milliseconds into a human readable time string.
    :param milliseconds: Milliseconds to format
    :return: Time string in format: hh.mm.ss,ttt
    """
    milliseconds = int(milliseconds)
    seconds, millis = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return "{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}".format(hours=hours,
                                                                         minutes=minutes,
                                                                         seconds=seconds,
                                                                         millis=millis)
