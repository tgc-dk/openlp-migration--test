# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2016 OpenLP Developers                                   #
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
The :mod:`http` module contains the API web server. This is a lightweight web server used by remotes to interact
with OpenLP. It uses JSON to communicate with the remotes.
"""

import asyncio
import websockets
import logging
import time

from PyQt5 import QtCore

from openlp.core.common import Settings, RegistryProperties, OpenLPMixin
from openlp.core.lib.remote import OpenLPPoll


log = logging.getLogger(__name__)


class HttpThread(QtCore.QThread):
    """
    A special Qt thread class to allow the HTTP server to run at the same time as the UI.
    """
    def __init__(self, server):
        """
        Constructor for the thread class.

        :param server: The http server class.
        """
        super(HttpThread, self).__init__(None)
        self.http_server = server

    def run(self):
        """
        Run the thread.
        """
        self.http_server.start_server()

    def stop(self):
        self.http_server.stop = True


class OpenWSServer(RegistryProperties, OpenLPMixin):
    """
    Wrapper round a server instance
    """
    def __init__(self, secure=False):
        """
        Initialise the http server, and start the server of the correct type http / https
        """
        super(OpenWSServer, self).__init__()
        self.settings_section = 'remotes'
        self.secure = secure
        self.http_thread = HttpThread(self)
        self.http_thread.start()

    def start_server(self):
        """
        Start the correct server and save the handler
        """
        address = Settings().value(self.settings_section + '/ip address')
        is_secure = Settings().value(self.settings_section + '/https enabled')
        port = '4318'
        self.start_websocket_instance(address, port)
        # If web socket server start listening
        if hasattr(self, 'ws_server') and self.ws_server:
            event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(event_loop)
            event_loop.run_until_complete(self.ws_server)
            event_loop.run_forever()
        else:
            log.debug('Failed to start ws server on port {port}'.format(port=port))

    def start_websocket_instance(self, address, port):
        """
        Start the server

        :param address: The server address
        :param port: The run port
        """
        loop = 1
        while loop < 4:
            try:
                self.ws_server = websockets.serve(self.handle_websocket, address, port)
                log.debug("Web Socket Server started for class {address} {port}".format(address=address, port=port))
                break
            except Exception as e:
                log.error('Failed to start ws server {why}'.format(why=e))
                loop += 1
                time.sleep(0.1)

    @staticmethod
    async def handle_websocket(request, path):
        """
        Handle web socket requests and return the poll information.
        Check ever 0.5 seconds to get the latest postion and send if changed.
        Only gets triggered when 1st client attaches
        :param request: request from client
        :param path: not used - future to register for a different end point
        :return:
        """
        log.debug("web socket handler registered with client")
        previous_poll = None
        previous_main_poll = None
        if path == '/poll':
            while True:
                current_poll = OpenLPPoll().poll()
                if current_poll != previous_poll:
                    await request.send(current_poll)
                    previous_poll = current_poll
                await asyncio.sleep(0.2)
        elif path == '/main_poll':
            while True:
                main_poll = OpenLPPoll().main_poll()
                if main_poll != previous_main_poll:
                    await request.send(main_poll)
                    previous_main_poll = main_poll
                await asyncio.sleep(0.2)

    def stop_server(self):
        """
        Stop the server
        """
        if self.http_thread.isRunning():
            self.http_thread.stop()
        self.httpd = None
        log.debug('Stopped the server.')
