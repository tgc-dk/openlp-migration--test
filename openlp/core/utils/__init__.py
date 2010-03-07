# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2010 Raoul Snyman                                        #
# Portions copyright (c) 2008-2010 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Maikel Stuivenberg, Martin Thompson, Jon Tibble,   #
# Carsten Tinggaard                                                           #
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
import logging
import urllib2
from datetime import datetime

log = logging.getLogger(__name__)

def check_latest_version(config, current_version):
    version_string = current_version
    #set to prod in the distribution confif file.
    last_test = config.get_config(u'last version test', datetime.now().date())
    this_test = unicode(datetime.now().date())
    config.set_config(u'last version test', this_test)
    if last_test != this_test:
        version_string = u''
        req = urllib2.Request(u'http://www.openlp.org/files/version.txt')
        req.add_header(u'User-Agent', u'OpenLP/%s' % current_version)
        try:
            handle = urllib2.urlopen(req, None)
            html = handle.read()
            version_string = unicode(html).rstrip()
        except IOError, e:
            if hasattr(e, u'reason'):
                log.exception(u'Reason for failure: %s', e.reason)
    return version_string

def get_config_directory():
    path = u''
    if os.name == u'nt':
        path = os.path.join(os.getenv(u'APPDATA'), u'openlp')
    elif os.name == u'mac':
        path = os.path.join(os.getenv(u'HOME'), u'Library',
            u'Application Support', u'openlp')
    else:
        try:
            from xdg import BaseDirectory
            path = os.path.join(BaseDirectory.xdg_config_home, u'openlp')
        except ImportError:
            path = os.path.join(os.getenv(u'HOME'), u'.openlp')
    return path

def get_data_directory():
    path = u''
    if os.name == u'nt':
        # ask OS for path to application data, set on Windows XP and Vista
        path = os.path.join(os.getenv(u'APPDATA'), u'openlp', u'data')
    elif os.name == u'mac':
        path = os.path.join(os.getenv(u'HOME'), u'Library',
            u'Application Support', u'openlp', u'Data')
    else:
        try:
            from xdg import BaseDirectory
            path = os.path.join(BaseDirectory.xdg_data_home, u'openlp')
        except ImportError:
            path = os.path.join(os.getenv(u'HOME'), u'.openlp', u'data')
    return path

from registry import Registry
from confighelper import ConfigHelper

__all__ = [u'Registry', u'ConfigHelper', u'get_config_directory',
           u'get_data_directory', u'check_latest_version']
