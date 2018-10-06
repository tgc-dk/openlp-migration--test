# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

# The MIT License
#
# Copyright (c) 2010-2014, Patrick Altman <paltman@gmail.com>
# Copyright (c) 2016-2018, OpenLP Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# http://www.opensource.org/licenses/mit-license.php

"""
The :mod:`~openlp.core.ui.media.mediainfo` module contains code to run mediainfo
on a media file and obtain information related to the requested media.
"""
import json
import os
from subprocess import check_output

from bs4 import BeautifulSoup, NavigableString

ENV_DICT = os.environ


class Track(object):

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except:
            pass
        return None

    def __init__(self, xml_dom_fragment):
        self.xml_dom_fragment = xml_dom_fragment
        self.track_type = xml_dom_fragment.attrs['type']
        for el in self.xml_dom_fragment.children:
            if not isinstance(el, NavigableString):
                node_name = el.name.lower().strip().strip('_')
                if node_name == 'id':
                    node_name = 'track_id'
                node_value = el.string
                other_node_name = "other_%s" % node_name
                if getattr(self, node_name) is None:
                    setattr(self, node_name, node_value)
                else:
                    if getattr(self, other_node_name) is None:
                        setattr(self, other_node_name, [node_value, ])
                    else:
                        getattr(self, other_node_name).append(node_value)

        for o in [d for d in self.__dict__.keys() if d.startswith('other_')]:
            try:
                primary = o.replace('other_', '')
                setattr(self, primary, int(getattr(self, primary)))
            except:
                for v in getattr(self, o):
                    try:
                        current = getattr(self, primary)
                        setattr(self, primary, int(v))
                        getattr(self, o).append(current)
                        break
                    except:
                        pass

    def __repr__(self):
        return "<Track track_id='{0}', track_type='{1}'>".format(self.track_id, self.track_type)

    def to_data(self):
        data = {}
        for k, v in self.__dict__.items():
            if k != 'xml_dom_fragment':
                data[k] = v
        return data


class MediaInfoWrapper(object):

    def __init__(self, xml):
        self.xml_dom = xml
        xml_types = (str,)     # no unicode type in python3
        if isinstance(xml, xml_types):
            self.xml_dom = MediaInfoWrapper.parse_xml_data_into_dom(xml)

    @staticmethod
    def parse_xml_data_into_dom(xml_data):
        return BeautifulSoup(xml_data, "xml")

    @staticmethod
    def parse(filename, environment=ENV_DICT):
        xml = check_output(['mediainfo', '-f', '--Output=XML', '--Inform=OLDXML', filename])
        if not xml.startswith(b'<?xml'):
            xml = check_output(['mediainfo', '-f', '--Output=XML', filename])
        xml_dom = MediaInfoWrapper.parse_xml_data_into_dom(xml)
        return MediaInfoWrapper(xml_dom)

    def _populate_tracks(self):
        if self.xml_dom is None:
            return
        for xml_track in self.xml_dom.Mediainfo.File.find_all("track"):
            self._tracks.append(Track(xml_track))

    @property
    def tracks(self):
        if not hasattr(self, "_tracks"):
            self._tracks = []
        if len(self._tracks) == 0:
            self._populate_tracks()
        return self._tracks

    def to_data(self):
        data = {'tracks': []}
        for track in self.tracks:
            data['tracks'].append(track.to_data())
        return data

    def to_json(self):
        return json.dumps(self.to_data())
