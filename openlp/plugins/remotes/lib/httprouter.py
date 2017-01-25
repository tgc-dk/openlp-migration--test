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
The :mod:`http` module contains the API web server. This is a lightweight web
server used by remotes to interact with OpenLP. It uses JSON to communicate with
the remotes.

*Routes:*

``/``
    Go to the web interface.

``/stage``
    Show the stage view.

``/files/{filename}``
    Serve a static file.

``/stage/api/poll``
    Poll to see if there are any changes. Returns a JSON-encoded dict of
    any changes that occurred::

        {"results": {"type": "controller"}}

    Or, if there were no results, False::

        {"results": False}

``/api/display/{hide|show}``
    Blank or unblank the screen.

``/api/alert``
    Sends an alert message to the alerts plugin. This method expects a
    JSON-encoded dict like this::

        {"request": {"text": "<your alert text>"}}

``/api/controller/{live|preview}/{action}``
    Perform ``{action}`` on the live or preview controller. Valid actions
    are:

    ``next``
        Load the next slide.

    ``previous``
        Load the previous slide.

    ``set``
        Set a specific slide. Requires an id return in a JSON-encoded dict like
        this::

            {"request": {"id": 1}}

    ``first``
        Load the first slide.

    ``last``
        Load the last slide.

    ``text``
        Fetches the text of the current song. The output is a JSON-encoded
        dict which looks like this::

            {"result": {"slides": ["...", "..."]}}

``/api/service/{action}``
    Perform ``{action}`` on the service manager (e.g. go live). Data is
    passed as a json-encoded ``data`` parameter. Valid actions are:

    ``next``
        Load the next item in the service.

    ``previous``
        Load the previews item in the service.

    ``set``
        Set a specific item in the service. Requires an id returned in a
        JSON-encoded dict like this::

            {"request": {"id": 1}}

    ``list``
        Request a list of items in the service. Returns a list of items in the
        current service in a JSON-encoded dict like this::

            {"results": {"items": [{...}, {...}]}}
"""
import base64
import json
import logging
import os
import re
import urllib.request
import urllib.error
from urllib.parse import urlparse, parse_qs

from mako.template import Template

from openlp.core.common import RegistryProperties, AppLocation, Settings, translate, UiStrings
from openlp.core.lib import PluginStatus, StringContent, image_to_byte, ItemCapabilities, create_thumb

log = logging.getLogger(__name__)
FILE_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.jpg': 'image/jpeg',
    '.gif': 'image/gif',
    '.ico': 'image/x-icon',
    '.png': 'image/png'
}


class HttpRouter(RegistryProperties):
    """
    This code is called by the HttpServer upon a request and it processes it based on the routing table.
    This code is stateless and is created on each request.
    Some variables may look incorrect but this extends BaseHTTPRequestHandler.
    """
    def initialise(self):
        """
        Initialise the router stack and any other variables.
        """
        auth_code = "{user}:{password}".format(user=Settings().value('remotes/user id'),
                                               password=Settings().value('remotes/password'))
        try:
            self.auth = base64.b64encode(auth_code)
        except TypeError:
            self.auth = base64.b64encode(auth_code.encode()).decode()
        self.default_route = {'function': self.serve_file, 'secure': False}
        self.routes = [
            ('^/$', {'function': self.serve_file, 'secure': False}),
            ('^/(stage)$', {'function': self.serve_file, 'secure': False}),
            ('^/(stage)/(.*)$', {'function': self.stages, 'secure': False}),
            ('^/(chords)$', {'function': self.serve_file, 'secure': False}),
            ('^/(main)$', {'function': self.serve_file, 'secure': False}),
            (r'^/(\w+)/thumbnails([^/]+)?/(.*)$', {'function': self.serve_thumbnail, 'secure': False}),
            (r'^/api/poll$', {'function': self.poll, 'secure': False}),
            (r'^/main/poll$', {'function': self.main_poll, 'secure': False}),
            (r'^/main/image$', {'function': self.main_image, 'secure': False}),
            (r'^/api/controller/(live|preview)/text$', {'function': self.controller_text, 'secure': False}),
            (r'^/api/controller/(live|preview)/(.*)$', {'function': self.controller, 'secure': True}),
            (r'^/api/service/list$', {'function': self.service_list, 'secure': False}),
            (r'^/api/service/(.*)$', {'function': self.service, 'secure': True}),
            (r'^/api/display/(hide|show|blank|theme|desktop)$', {'function': self.display, 'secure': True}),
            (r'^/api/alert$', {'function': self.alert, 'secure': True}),
            (r'^/api/plugin/(search)$', {'function': self.plugin_info, 'secure': False}),
            (r'^/api/(.*)/search$', {'function': self.search, 'secure': False}),
            (r'^/api/(.*)/live$', {'function': self.go_live, 'secure': True}),
            (r'^/api/(.*)/add$', {'function': self.add_to_service, 'secure': True})
        ]
        self.settings_section = 'remotes'
        self.translate()
        self.html_dir = os.path.join(AppLocation.get_directory(AppLocation.PluginsDir), 'remotes', 'html')
        self.config_dir = os.path.join(AppLocation.get_data_path(), 'stages')

    def do_post_processor(self):
        """
        Handle the POST amd GET requests placed on the server.
        """
        if self.path == '/favicon.ico':
            return
        if not hasattr(self, 'auth'):
            self.initialise()
        function, args = self.process_http_request(self.path)
        if not function:
            self.do_http_error()
            return
        self.authorised = self.headers['Authorization'] is None
        if function['secure'] and Settings().value(self.settings_section + '/authentication enabled'):
            if self.headers['Authorization'] is None:
                self.do_authorisation()
                self.wfile.write(bytes('no auth header received', 'UTF-8'))
            elif self.headers['Authorization'] == 'Basic {auth}'.format(auth=self.auth):
                self.do_http_success()
                self.call_function(function, *args)
            else:
                self.do_authorisation()
                self.wfile.write(bytes(self.headers['Authorization'], 'UTF-8'))
                self.wfile.write(bytes(' not authenticated', 'UTF-8'))
        else:
            self.call_function(function, *args)

    def call_function(self, function, *args):
        """
        Invoke the route function passing the relevant values

        :param function: The function to be called.
        :param args: Any passed data.
        """
        response = function['function'](*args)
        if response:
            self.wfile.write(response)
            return

    def process_http_request(self, url_path, *args):
        """
        Common function to process HTTP requests

        :param url_path: The requested URL.
        :param args: Any passed data.
        """
        self.request_data = None
        url_path_split = urlparse(url_path)
        url_query = parse_qs(url_path_split.query)
        # Get data from HTTP request
        if self.command == 'GET':
            if 'data' in url_query.keys():
                self.request_data = url_query['data'][0]
        elif self.command == 'POST':
            content_len = int(self.headers['content-length'])
            self.request_data = self.rfile.read(content_len).decode("utf-8")
        for route, func in self.routes:
            match = re.match(route, url_path_split.path)
            if match:
                log.debug('Route "{route}" matched "{path}"'.format(route=route, path=url_path))
                args = []
                for param in match.groups():
                    args.append(param)
                return func, args
        return self.default_route, [url_path_split.path]

    def set_cache_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")

    def do_http_success(self):
        """
        Create a success http header.
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.set_cache_headers()
        self.end_headers()

    def do_json_header(self):
        """
        Create a header for JSON messages
        """
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.set_cache_headers()
        self.end_headers()

    def do_http_error(self):
        """
        Create a error http header.
        """
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.set_cache_headers()
        self.end_headers()

    def do_authorisation(self):
        """
        Create a needs authorisation http header.
        """
        self.send_response(401)
        header = 'Basic realm=\"{}\"'.format(UiStrings().OLPV2)
        self.send_header('WWW-Authenticate', header)
        self.send_header('Content-type', 'text/html')
        self.set_cache_headers()
        self.end_headers()

    def do_not_found(self):
        """
        Create a not found http header.
        """
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.set_cache_headers()
        self.end_headers()
        self.wfile.write(bytes('<html><body>Sorry, an error occurred </body></html>', 'UTF-8'))

    def _get_service_items(self):
        """
        Read the service item in use and return the data as a json object
        """
        service_items = []
        if self.live_controller.service_item:
            current_unique_identifier = self.live_controller.service_item.unique_identifier
        else:
            current_unique_identifier = None
        for item in self.service_manager.service_items:
            service_item = item['service_item']
            service_items.append({
                'id': str(service_item.unique_identifier),
                'title': str(service_item.get_display_title()),
                'plugin': str(service_item.name),
                'notes': str(service_item.notes),
                'selected': (service_item.unique_identifier == current_unique_identifier)
            })
        return service_items

    def translate(self):
        """
        Translate various strings in the mobile app.
        """
        remote = translate('RemotePlugin.Mobile', 'Remote')
        stage = translate('RemotePlugin.Mobile', 'Stage View')
        chords = translate('RemotePlugin.Mobile', 'Chords View')
        live = translate('RemotePlugin.Mobile', 'Live View')
        self.template_vars = {
            'app_title': "{main} {remote}".format(main=UiStrings().OLPV2x, remote=remote),
            'stage_title': "{main} {stage}".format(main=UiStrings().OLPV2x, stage=stage),
            'chords_title': "{main} {chords}".format(main=UiStrings().OLPV2x, chords=chords),
            'live_title': "{main} {live}".format(main=UiStrings().OLPV2x, live=live),
            'service_manager': translate('RemotePlugin.Mobile', 'Service Manager'),
            'slide_controller': translate('RemotePlugin.Mobile', 'Slide Controller'),
            'alerts': translate('RemotePlugin.Mobile', 'Alerts'),
            'search': translate('RemotePlugin.Mobile', 'Search'),
            'home': translate('RemotePlugin.Mobile', 'Home'),
            'refresh': translate('RemotePlugin.Mobile', 'Refresh'),
            'blank': translate('RemotePlugin.Mobile', 'Blank'),
            'theme': translate('RemotePlugin.Mobile', 'Theme'),
            'desktop': translate('RemotePlugin.Mobile', 'Desktop'),
            'show': translate('RemotePlugin.Mobile', 'Show'),
            'prev': translate('RemotePlugin.Mobile', 'Prev'),
            'next': translate('RemotePlugin.Mobile', 'Next'),
            'text': translate('RemotePlugin.Mobile', 'Text'),
            'show_alert': translate('RemotePlugin.Mobile', 'Show Alert'),
            'go_live': translate('RemotePlugin.Mobile', 'Go Live'),
            'add_to_service': translate('RemotePlugin.Mobile', 'Add to Service'),
            'add_and_go_to_service': translate('RemotePlugin.Mobile', 'Add &amp; Go to Service'),
            'no_results': translate('RemotePlugin.Mobile', 'No Results'),
            'options': translate('RemotePlugin.Mobile', 'Options'),
            'service': translate('RemotePlugin.Mobile', 'Service'),
            'slides': translate('RemotePlugin.Mobile', 'Slides'),
            'settings': translate('RemotePlugin.Mobile', 'Settings'),
        }

    def stages(self, url_path, file_name):
        """
        Allow Stage view to be delivered with custom views.

        :param url_path: base path of the URL. Not used but passed by caller
        :param file_name: file name with path
        :return:
        """
        log.debug('serve file request {name}'.format(name=file_name))
        parts = file_name.split('/')
        if len(parts) == 1:
            file_name = os.path.join(parts[0], 'stage.html')
        elif len(parts) == 3:
            file_name = os.path.join(parts[1], parts[2])
        path = os.path.normpath(os.path.join(self.config_dir, file_name))
        if not path.startswith(self.config_dir):
            return self.do_not_found()
        return self._process_file(path)

    def _process_file(self, path):
        """
        Common file processing code

        :param path: path to file to be loaded
        :return: web resource to be loaded
        """
        content = None
        ext, content_type = self.get_content_type(path)
        file_handle = None
        try:
            if ext == '.html':
                variables = self.template_vars
                content = Template(filename=path, input_encoding='utf-8', output_encoding='utf-8').render(**variables)
            else:
                file_handle = open(path, 'rb')
                log.debug('Opened {path}'.format(path=path))
                content = file_handle.read()
        except IOError:
            log.exception('Failed to open {path}'.format(path=path))
            return self.do_not_found()
        finally:
            if file_handle:
                file_handle.close()
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
        return content

    def serve_file(self, file_name=None):
        """
        Send a file to the socket. For now, just a subset of file types and must be top level inside the html folder.
        If subfolders requested return 404, easier for security for the present.

        Ultimately for i18n, this could first look for xx/file.html before falling back to file.html.
        where xx is the language, e.g. 'en'
        """
        log.debug('serve file request {name}'.format(name=file_name))
        if not file_name:
            file_name = 'index.html'
        if '.' not in file_name:
            file_name += '.html'
        if file_name.startswith('/'):
            file_name = file_name[1:]
        path = os.path.normpath(os.path.join(self.html_dir, file_name))
        if not path.startswith(self.html_dir):
            return self.do_not_found()
        return self._process_file(path)

    def get_content_type(self, file_name):
        """
        Examines the extension of the file and determines what the content_type should be, defaults to text/plain
        Returns the extension and the content_type

        :param file_name: name of file
        """
        ext = os.path.splitext(file_name)[1]
        content_type = FILE_TYPES.get(ext, 'text/plain')
        return ext, content_type

    def serve_thumbnail(self, controller_name=None, dimensions=None, file_name=None):
        """
        Serve an image file. If not found return 404.

        :param file_name: file name to be served
        :param dimensions: image size
        :param controller_name: controller to be called
        """
        log.debug('serve thumbnail {cname}/thumbnails{dim}/{fname}'.format(cname=controller_name,
                                                                           dim=dimensions,
                                                                           fname=file_name))
        supported_controllers = ['presentations', 'images']
        # -1 means use the default dimension in ImageManager
        width = -1
        height = -1
        if dimensions:
            match = re.search('(\d+)x(\d+)', dimensions)
            if match:
                # let's make sure that the dimensions are within reason
                width = sorted([10, int(match.group(1)), 1000])[1]
                height = sorted([10, int(match.group(2)), 1000])[1]
        content = ''
        content_type = None
        if controller_name and file_name:
            if controller_name in supported_controllers:
                full_path = urllib.parse.unquote(file_name)
                if '..' not in full_path:  # no hacking please
                    full_path = os.path.normpath(os.path.join(AppLocation.get_section_data_path(controller_name),
                                                              'thumbnails/' + full_path))
                    if os.path.exists(full_path):
                        path, just_file_name = os.path.split(full_path)
                        self.image_manager.add_image(full_path, just_file_name, None, width, height)
                        ext, content_type = self.get_content_type(full_path)
                        image = self.image_manager.get_image(full_path, just_file_name, width, height)
                        content = image_to_byte(image, False)
        if len(content) == 0:
            return self.do_not_found()
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
        return content

    def poll(self):
        """
        Poll OpenLP to determine the current slide number and item name.
        """
        result = {
            'service': self.service_manager.service_id,
            'slide': self.live_controller.selected_row or 0,
            'item': self.live_controller.service_item.unique_identifier if self.live_controller.service_item else '',
            'twelve': Settings().value('remotes/twelve hour'),
            'blank': self.live_controller.blank_screen.isChecked(),
            'theme': self.live_controller.theme_screen.isChecked(),
            'display': self.live_controller.desktop_screen.isChecked(),
            'version': 2,
            'isSecure': Settings().value(self.settings_section + '/authentication enabled'),
            'isAuthorised': self.authorised,
            'chordNotation': Settings().value('songs/chord notation'),
        }
        self.do_json_header()
        return json.dumps({'results': result}).encode()

    def main_poll(self):
        """
        Poll OpenLP to determine the current slide count.
        """
        result = {
            'slide_count': self.live_controller.slide_count
        }
        self.do_json_header()
        return json.dumps({'results': result}).encode()

    def main_image(self):
        """
        Return the latest display image as a byte stream.
        """
        result = {
            'slide_image': 'data:image/png;base64,' + str(image_to_byte(self.live_controller.slide_image))
        }
        self.do_json_header()
        return json.dumps({'results': result}).encode()

    def display(self, action):
        """
        Hide or show the display screen.
        This is a cross Thread call and UI is updated so Events need to be used.

        :param action: This is the action, either ``hide`` or ``show``.
        """
        self.live_controller.slidecontroller_toggle_display.emit(action)
        self.do_json_header()
        return json.dumps({'results': {'success': True}}).encode()

    def alert(self):
        """
        Send an alert.
        """
        plugin = self.plugin_manager.get_plugin_by_name("alerts")
        if plugin.status == PluginStatus.Active:
            try:
                text = json.loads(self.request_data)['request']['text']
            except KeyError:
                return self.do_http_error()
            text = urllib.parse.unquote(text)
            self.alerts_manager.alerts_text.emit([text])
            success = True
        else:
            success = False
        self.do_json_header()
        return json.dumps({'results': {'success': success}}).encode()

    def controller_text(self, var):
        """
        Perform an action on the slide controller.

        :param var: variable - not used
        """
        log.debug("controller_text var = {var}".format(var=var))
        current_item = self.live_controller.service_item
        data = []
        if current_item:
            for index, frame in enumerate(current_item.get_frames()):
                item = {}
                # Handle text (songs, custom, bibles)
                if current_item.is_text():
                    if frame['verseTag']:
                        item['tag'] = str(frame['verseTag'])
                    else:
                        item['tag'] = str(index + 1)
                    item['chords_text'] = str(frame['chords_text'])
                    item['text'] = str(frame['text'])
                    item['html'] = str(frame['html'])
                # Handle images, unless a custom thumbnail is given or if thumbnails is disabled
                elif current_item.is_image() and not frame.get('image', '') and Settings().value('remotes/thumbnails'):
                    item['tag'] = str(index + 1)
                    thumbnail_path = os.path.join('images', 'thumbnails', frame['title'])
                    full_thumbnail_path = os.path.join(AppLocation.get_data_path(), thumbnail_path)
                    # Create thumbnail if it doesn't exists
                    if not os.path.exists(full_thumbnail_path):
                        create_thumb(current_item.get_frame_path(index), full_thumbnail_path, False)
                    item['img'] = urllib.request.pathname2url(os.path.sep + thumbnail_path)
                    item['text'] = str(frame['title'])
                    item['html'] = str(frame['title'])
                else:
                    # Handle presentation etc.
                    item['tag'] = str(index + 1)
                    if current_item.is_capable(ItemCapabilities.HasDisplayTitle):
                        item['title'] = str(frame['display_title'])
                    if current_item.is_capable(ItemCapabilities.HasNotes):
                        item['slide_notes'] = str(frame['notes'])
                    if current_item.is_capable(ItemCapabilities.HasThumbnails) and \
                            Settings().value('remotes/thumbnails'):
                        # If the file is under our app directory tree send the portion after the match
                        data_path = AppLocation.get_data_path()
                        if frame['image'][0:len(data_path)] == data_path:
                            item['img'] = urllib.request.pathname2url(frame['image'][len(data_path):])
                    item['text'] = str(frame['title'])
                    item['html'] = str(frame['title'])
                item['selected'] = (self.live_controller.selected_row == index)
                data.append(item)
        json_data = {'results': {'slides': data}}
        if current_item:
            json_data['results']['item'] = self.live_controller.service_item.unique_identifier
        self.do_json_header()
        return json.dumps(json_data).encode()

    def controller(self, display_type, action):
        """
        Perform an action on the slide controller.

        :param display_type: This is the type of slide controller, either ``preview`` or ``live``.
        :param action: The action to perform.
        """
        event = getattr(self.live_controller, 'slidecontroller_{display}_{action}'.format(display=display_type,
                                                                                          action=action))
        if self.request_data:
            try:
                data = json.loads(self.request_data)['request']['id']
            except KeyError:
                return self.do_http_error()
            log.info(data)
            # This slot expects an int within a list.
            event.emit([data])
        else:
            event.emit()
        json_data = {'results': {'success': True}}
        self.do_json_header()
        return json.dumps(json_data).encode()

    def service_list(self):
        """
        Handles requests for service items in the service manager

        """
        self.do_json_header()
        return json.dumps({'results': {'items': self._get_service_items()}}).encode()

    def service(self, action):
        """
        Handles requests for service items in the service manager

        :param action: The action to perform.
        """
        event = getattr(self.service_manager, 'servicemanager_{action}_item'.format(action=action))
        if self.request_data:
            try:
                data = int(json.loads(self.request_data)['request']['id'])
            except KeyError:
                return self.do_http_error()
            event.emit(data)
        else:
            event.emit()
        self.do_json_header()
        return json.dumps({'results': {'success': True}}).encode()

    def plugin_info(self, action):
        """
        Return plugin related information, based on the action.

        :param action: The action to perform. If *search* return a list of plugin names which support search.
        """
        if action == 'search':
            searches = []
            for plugin in self.plugin_manager.plugins:
                if plugin.status == PluginStatus.Active and plugin.media_item and plugin.media_item.has_search:
                    searches.append([plugin.name, str(plugin.text_strings[StringContent.Name]['plural'])])
            self.do_json_header()
            return json.dumps({'results': {'items': searches}}).encode()

    def search(self, plugin_name):
        """
        Return a list of items that match the search text.

        :param plugin_name: The plugin name to search in.
        """
        try:
            text = json.loads(self.request_data)['request']['text']
        except KeyError:
            return self.do_http_error()
        text = urllib.parse.unquote(text)
        plugin = self.plugin_manager.get_plugin_by_name(plugin_name)
        if plugin.status == PluginStatus.Active and plugin.media_item and plugin.media_item.has_search:
            results = plugin.media_item.search(text, False)
        else:
            results = []
        self.do_json_header()
        return json.dumps({'results': {'items': results}}).encode()

    def go_live(self, plugin_name):
        """
        Go live on an item of type ``plugin``.

        :param plugin_name: name of plugin
        """
        try:
            request_id = json.loads(self.request_data)['request']['id']
        except KeyError:
            return self.do_http_error()
        plugin = self.plugin_manager.get_plugin_by_name(plugin_name)
        if plugin.status == PluginStatus.Active and plugin.media_item:
            getattr(plugin.media_item, '{name}_go_live'.format(name=plugin_name)).emit([request_id, True])
        return self.do_http_success()

    def add_to_service(self, plugin_name):
        """
        Add item of type ``plugin_name`` to the end of the service.

        :param plugin_name: name of plugin to be called
        """
        try:
            request_id = json.loads(self.request_data)['request']['id']
        except KeyError:
            return self.do_http_error()
        plugin = self.plugin_manager.get_plugin_by_name(plugin_name)
        if plugin.status == PluginStatus.Active and plugin.media_item:
            item_id = plugin.media_item.create_item_from_id(request_id)
            getattr(plugin.media_item, '{name}_add_to_service'.format(name=plugin_name)).emit([item_id, True])
        self.do_http_success()
