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
The :mod:`openlp.core.utils` module provides the utility libraries for OpenLP.
"""
import hashlib
import logging
import sys
import time
from random import randint

import requests

from openlp.core.common import trace_error_handler
from openlp.core.common.registry import Registry

log = logging.getLogger(__name__ + '.__init__')

USER_AGENTS = {
    'win32': [
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.71 Safari/537.36'
    ],
    'darwin': [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) '
        'Chrome/26.0.1410.43 Safari/537.31',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/536.11 (KHTML, like Gecko) '
        'Chrome/20.0.1132.57 Safari/536.11',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/536.11 (KHTML, like Gecko) '
        'Chrome/20.0.1132.47 Safari/536.11',
    ],
    'linux2': [
        'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.22 (KHTML, like Gecko) Ubuntu Chromium/25.0.1364.160 '
        'Chrome/25.0.1364.160 Safari/537.22',
        'Mozilla/5.0 (X11; CrOS armv7l 2913.260.0) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.99 '
        'Safari/537.11',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.27 (KHTML, like Gecko) Chrome/26.0.1389.0 Safari/537.27'
    ],
    'default': [
        'Mozilla/5.0 (X11; NetBSD amd64; rv:18.0) Gecko/20130120 Firefox/18.0'
    ]
}
CONNECTION_TIMEOUT = 30
CONNECTION_RETRIES = 2


def get_user_agent():
    """
    Return a user agent customised for the platform the user is on.
    """
    browser_list = USER_AGENTS.get(sys.platform, None)
    if not browser_list:
        browser_list = USER_AGENTS['default']
    random_index = randint(0, len(browser_list) - 1)
    return browser_list[random_index]


def get_web_page(url, headers=None, update_openlp=False, proxies=None):
    """
    Attempts to download the webpage at url and returns that page or None.

    :param url: The URL to be downloaded.
    :param header:  An optional HTTP header to pass in the request to the web server.
    :param update_openlp: Tells OpenLP to update itself if the page is successfully downloaded.
        Defaults to False.
    """
    if not url:
        return None
    if not headers:
        headers = {}
    if 'user-agent' not in [key.lower() for key in headers.keys()]:
        headers['User-Agent'] = get_user_agent()
    log.debug('Downloading URL = %s' % url)
    retries = 0
    while retries < CONNECTION_RETRIES:
        try:
            response = requests.get(url, headers=headers, proxies=proxies, timeout=float(CONNECTION_TIMEOUT))
            log.debug('Downloaded page {url}'.format(url=response.url))
            break
        except OSError:
            # For now, catch OSError. All requests errors inherit from OSError
            log.exception('Unable to connect to {url}'.format(url=url))
            response = None
            if retries >= CONNECTION_RETRIES:
                raise ConnectionError('Unable to connect to {url}, see log for details'.format(url=url))
            retries += 1
        except:
            # Don't know what's happening, so reraise the original
            log.exception('Unknown error when trying to connect to {url}'.format(url=url))
            raise
    if update_openlp:
        Registry().get('application').process_events()
    if not response or not response.text:
        log.error('{url} could not be downloaded'.format(url=url))
        return None
    return response.text


def get_url_file_size(url):
    """
    Get the size of a file.

    :param url: The URL of the file we want to download.
    """
    retries = 0
    while True:
        try:
            response = requests.head(url, timeout=float(CONNECTION_TIMEOUT), allow_redirects=True)
            return int(response.headers['Content-Length'])
        except OSError:
            if retries > CONNECTION_RETRIES:
                raise ConnectionError('Unable to download {url}'.format(url=url))
            else:
                retries += 1
                time.sleep(0.1)
                continue


def url_get_file(callback, url, file_path, sha256=None):
    """"
    Download a file given a URL.  The file is retrieved in chunks, giving the ability to cancel the download at any
    point. Returns False on download error.

    :param callback: the class which needs to be updated
    :param url: URL to download
    :param file_path: Destination file
    :param sha256: The check sum value to be checked against the download value
    """
    block_count = 0
    block_size = 4096
    retries = 0
    log.debug('url_get_file: %s', url)
    while retries < CONNECTION_RETRIES:
        try:
            with file_path.open('wb') as saved_file:
                response = requests.get(url, timeout=float(CONNECTION_TIMEOUT), stream=True)
                if sha256:
                    hasher = hashlib.sha256()
                # Download until finished or canceled.
                for chunk in response.iter_content(chunk_size=block_size):
                    if callback.was_cancelled:
                        break
                    saved_file.write(chunk)
                    if sha256:
                        hasher.update(chunk)
                    block_count += 1
                    callback._download_progress(block_count, block_size)
                response.close()
            if sha256 and hasher.hexdigest() != sha256:
                log.error('sha256 sums did not match for file %s, got %s, expected %s', file_path, hasher.hexdigest(),
                          sha256)
                if file_path.exists():
                    file_path.unlink()
                return False
            break
        except OSError:
            trace_error_handler(log)
            if retries > CONNECTION_RETRIES:
                if file_path.exists():
                    file_path.unlink()
                return False
            else:
                retries += 1
                time.sleep(0.1)
                continue
    if callback.was_cancelled and file_path.exists():
        file_path.unlink()
    return True


__all__ = ['get_web_page']
