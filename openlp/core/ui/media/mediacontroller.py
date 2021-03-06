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
The :mod:`~openlp.core.ui.media.mediacontroller` module contains a base class for media components and other widgets
related to playing media, such as sliders.
"""
import datetime
import logging

try:
    from pymediainfo import MediaInfo
    pymediainfo_available = True
except ImportError:
    pymediainfo_available = False

from subprocess import check_output
from PyQt5 import QtCore, QtWidgets

from openlp.core.state import State
from openlp.core.api.http import register_endpoint
from openlp.core.common.i18n import translate
from openlp.core.common.mixins import LogMixin, RegistryProperties
from openlp.core.common.registry import Registry, RegistryBase
from openlp.core.common.settings import Settings
from openlp.core.lib.serviceitem import ItemCapabilities
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.ui import DisplayControllerType
from openlp.core.ui.icons import UiIcons
from openlp.core.ui.media import MediaState, ItemMediaInfo, MediaType, parse_optical_path
from openlp.core.ui.media.endpoint import media_endpoint
from openlp.core.ui.media.vlcplayer import VlcPlayer, get_vlc
from openlp.core.widgets.toolbar import OpenLPToolbar

log = logging.getLogger(__name__)

TICK_TIME = 200


class MediaSlider(QtWidgets.QSlider):
    """
    Allows the mouse events of a slider to be overridden and extra functionality added
    """
    def __init__(self, direction, manager, controller):
        """
        Constructor
        """
        super(MediaSlider, self).__init__(direction)
        self.manager = manager
        self.controller = controller

    def mouseMoveEvent(self, event):
        """
        Override event to allow hover time to be displayed.

        :param event: The triggering event
        """
        time_value = QtWidgets.QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), event.x(), self.width())
        self.setToolTip('%s' % datetime.timedelta(seconds=int(time_value / 1000)))
        QtWidgets.QSlider.mouseMoveEvent(self, event)

    def mousePressEvent(self, event):
        """
        Mouse Press event no new functionality
        :param event: The triggering event
        """
        QtWidgets.QSlider.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """
        Set the slider position when the mouse is clicked and released on the slider.

        :param event: The triggering event
        """
        self.setValue(QtWidgets.QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), event.x(), self.width()))
        QtWidgets.QSlider.mouseReleaseEvent(self, event)


class MediaController(RegistryBase, LogMixin, RegistryProperties):
    """
    The implementation of the Media Controller. The Media Controller adds an own class for every Player.
    Currently these are QtWebkit, Phonon and Vlc. display_controllers are an array of controllers keyed on the
    slidecontroller or plugin which built them.

    ControllerType is the class containing the key values.

    media_players are an array of media players keyed on player name.

    current_media_players is an array of player instances keyed on ControllerType.

    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(MediaController, self).__init__(parent)

    def setup(self):
        self.vlc_player = None
        self.display_controllers = {}
        self.current_media_players = {}
        # Timer for video state
        self.live_timer = QtCore.QTimer()
        self.live_timer.setInterval(TICK_TIME)
        self.preview_timer = QtCore.QTimer()
        self.preview_timer.setInterval(TICK_TIME)
        # Signals
        self.live_timer.timeout.connect(self.media_state_live)
        self.preview_timer.timeout.connect(self.media_state_preview)
        Registry().register_function('playbackPlay', self.media_play_msg)
        Registry().register_function('playbackPause', self.media_pause_msg)
        Registry().register_function('playbackStop', self.media_stop_msg)
        Registry().register_function('playbackLoop', self.media_loop_msg)
        Registry().register_function('seek_slider', self.media_seek_msg)
        Registry().register_function('volume_slider', self.media_volume_msg)
        Registry().register_function('media_hide', self.media_hide)
        Registry().register_function('media_blank', self.media_blank)
        Registry().register_function('media_unblank', self.media_unblank)
        # Signals for background video
        Registry().register_function('songs_hide', self.media_hide)
        Registry().register_function('songs_blank', self.media_blank)
        Registry().register_function('songs_unblank', self.media_unblank)
        Registry().register_function('mediaitem_suffixes', self._generate_extensions_lists)
        register_endpoint(media_endpoint)

    def _generate_extensions_lists(self):
        """
        Set the active players and available media files
        """
        suffix_list = []
        self.audio_extensions_list = []
        if self.vlc_player.is_active:
            for item in self.vlc_player.audio_extensions_list:
                if item not in self.audio_extensions_list:
                    self.audio_extensions_list.append(item)
                    suffix_list.append(item[2:])
        self.video_extensions_list = []
        if self.vlc_player.is_active:
            for item in self.vlc_player.video_extensions_list:
                if item not in self.video_extensions_list:
                    self.video_extensions_list.append(item)
                    suffix_list.append(item[2:])
        self.service_manager.supported_suffixes(suffix_list)

    def bootstrap_initialise(self):
        """
        Check to see if we have any media Player's available.
        """
        self.setup()
        self.vlc_player = VlcPlayer(self)
        State().add_service("mediacontroller", 0)
        if get_vlc() and pymediainfo_available:
            State().update_pre_conditions("mediacontroller", True)
        else:
            State().missing_text("mediacontroller", translate('OpenLP.SlideController',
                                 "VLC or pymediainfo are missing, so you are unable to play any media"))
        self._generate_extensions_lists()
        return True

    def media_state_live(self):
        """
        Check if there is a running Live media Player and do updating stuff (e.g. update the UI)
        """
        display = self._define_display(self.display_controllers[DisplayControllerType.Live])
        if DisplayControllerType.Live in self.current_media_players:
            self.current_media_players[DisplayControllerType.Live].resize(display)
            self.current_media_players[DisplayControllerType.Live].update_ui(display)
            self.tick(self.display_controllers[DisplayControllerType.Live])
            if self.current_media_players[DisplayControllerType.Live].get_live_state() is not MediaState.Playing:
                self.live_timer.stop()
        else:
            self.live_timer.stop()
            self.media_stop(self.display_controllers[DisplayControllerType.Live])
            if self.display_controllers[DisplayControllerType.Live].media_info.can_loop_playback:
                self.media_play(self.display_controllers[DisplayControllerType.Live], True)

    def media_state_preview(self):
        """
        Check if there is a running Preview media Player and do updating stuff (e.g. update the UI)
        """
        display = self._define_display(self.display_controllers[DisplayControllerType.Preview])
        if DisplayControllerType.Preview in self.current_media_players:
            self.current_media_players[DisplayControllerType.Preview].resize(display)
            self.current_media_players[DisplayControllerType.Preview].update_ui(display)
            self.tick(self.display_controllers[DisplayControllerType.Preview])
            if self.current_media_players[DisplayControllerType.Preview].get_preview_state() is not MediaState.Playing:
                self.preview_timer.stop()
        else:
            self.preview_timer.stop()
            self.media_stop(self.display_controllers[DisplayControllerType.Preview])
            if self.display_controllers[DisplayControllerType.Preview].media_info.can_loop_playback:
                self.media_play(self.display_controllers[DisplayControllerType.Preview], True)

    def register_controller(self, controller):
        """
        Registers media controls where the players will be placed to run.

        :param controller: The controller where a player will be placed
        """
        self.display_controllers[controller.controller_type] = controller
        self.setup_generic_controls(controller)

    def setup_generic_controls(self, controller):
        """
        Set up controls on the control_panel for a given controller

        :param controller:  First element is the controller which should be used
        """
        controller.media_info = ItemMediaInfo()
        # Build a Media ToolBar
        controller.mediabar = OpenLPToolbar(controller)
        controller.mediabar.add_toolbar_action('playbackPlay', text='media_playback_play',
                                               icon=UiIcons().play,
                                               tooltip=translate('OpenLP.SlideController', 'Start playing media.'),
                                               triggers=controller.send_to_plugins)
        controller.mediabar.add_toolbar_action('playbackPause', text='media_playback_pause',
                                               icon=UiIcons().pause,
                                               tooltip=translate('OpenLP.SlideController', 'Pause playing media.'),
                                               triggers=controller.send_to_plugins)
        controller.mediabar.add_toolbar_action('playbackStop', text='media_playback_stop',
                                               icon=UiIcons().stop,
                                               tooltip=translate('OpenLP.SlideController', 'Stop playing media.'),
                                               triggers=controller.send_to_plugins)
        controller.mediabar.add_toolbar_action('playbackLoop', text='media_playback_loop',
                                               icon=UiIcons().repeat, checked=False,
                                               tooltip=translate('OpenLP.SlideController', 'Loop playing media.'),
                                               triggers=controller.send_to_plugins)
        controller.position_label = QtWidgets.QLabel()
        controller.position_label.setText(' 00:00 / 00:00')
        controller.position_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        controller.position_label.setToolTip(translate('OpenLP.SlideController', 'Video timer.'))
        controller.position_label.setMinimumSize(90, 0)
        controller.position_label.setObjectName('position_label')
        controller.mediabar.add_toolbar_widget(controller.position_label)
        # Build the seek_slider.
        controller.seek_slider = MediaSlider(QtCore.Qt.Horizontal, self, controller)
        controller.seek_slider.setMaximum(1000)
        controller.seek_slider.setTracking(True)
        controller.seek_slider.setMouseTracking(True)
        controller.seek_slider.setToolTip(translate('OpenLP.SlideController', 'Video position.'))
        controller.seek_slider.setGeometry(QtCore.QRect(90, 260, 221, 24))
        controller.seek_slider.setObjectName('seek_slider')
        controller.mediabar.add_toolbar_widget(controller.seek_slider)
        # Build the volume_slider.
        controller.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        controller.volume_slider.setTickInterval(10)
        controller.volume_slider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        controller.volume_slider.setMinimum(0)
        controller.volume_slider.setMaximum(100)
        controller.volume_slider.setTracking(True)
        controller.volume_slider.setToolTip(translate('OpenLP.SlideController', 'Audio Volume.'))
        controller.volume_slider.setValue(controller.media_info.volume)
        controller.volume_slider.setGeometry(QtCore.QRect(90, 160, 221, 24))
        controller.volume_slider.setObjectName('volume_slider')
        controller.mediabar.add_toolbar_widget(controller.volume_slider)
        controller.controller_layout.addWidget(controller.mediabar)
        controller.mediabar.setVisible(False)
        if not controller.is_live:
            controller.volume_slider.setEnabled(False)
        # Signals
        controller.seek_slider.valueChanged.connect(controller.send_to_plugins)
        controller.volume_slider.valueChanged.connect(controller.send_to_plugins)

    def setup_display(self, display, preview):
        """
        After a new display is configured, all media related widgets will be created too

        :param display:  Display on which the output is to be played
        :param preview: Whether the display is a main or preview display
        """
        # clean up possible running old media files
        self.finalise()
        display.has_audio = True
        if display.is_live and preview:
            return
        if preview:
            display.has_audio = False
        self.vlc_player.setup(display)

    def set_controls_visible(self, controller, value):
        """
        After a new display is configured, all media related widget will be created too

        :param controller: The controller on which controls act.
        :param value: control name to be changed.
        """
        # Generic controls
        controller.mediabar.setVisible(value)
        if controller.is_live and controller.display:
            if self.current_media_players and value:
                controller.display.set_transparency(False)

    @staticmethod
    def resize(display, player):
        """
        After Mainwindow changes or Splitter moved all related media widgets have to be resized

        :param display: The display on which output is playing.
        :param player:  The player which is doing the playing.
        """
        player.resize(display)

    def video(self, source, service_item, hidden=False, video_behind_text=False):
        """
        Loads and starts a video to run with the option of sound

        :param source: Where the call originated form
        :param service_item: The player which is doing the playing
        :param hidden: The player which is doing the playing
        :param video_behind_text: Is the video to be played behind text.
        """
        is_valid = True
        controller = self.display_controllers[source]
        # stop running videos
        self.media_reset(controller)
        controller.media_info = ItemMediaInfo()
        controller.media_info.volume = controller.volume_slider.value()
        controller.media_info.is_background = video_behind_text
        # background will always loop video.
        controller.media_info.can_loop_playback = video_behind_text
        if service_item.is_capable(ItemCapabilities.HasBackgroundAudio):
            controller.media_info.file_info = service_item.background_audio
        else:
            controller.media_info.file_info = [service_item.get_frame_path()]
        display = self._define_display(controller)
        if controller.is_live:
            # if this is an optical device use special handling
            if service_item.is_capable(ItemCapabilities.IsOptical):
                log.debug('video is optical and live')
                path = service_item.get_frame_path()
                (name, title, audio_track, subtitle_track, start, end, clip_name) = parse_optical_path(path)
                is_valid = self.media_setup_optical(name, title, audio_track, subtitle_track, start, end, display,
                                                    controller)
            else:
                log.debug('video is not optical and live')
                controller.media_info.length = service_item.media_length
                is_valid = self._check_file_type(controller, display)
            display.override['theme'] = ''
            display.override['video'] = True
            if controller.media_info.is_background:
                # ignore start/end time
                controller.media_info.start_time = 0
                controller.media_info.end_time = 0
            else:
                controller.media_info.start_time = service_item.start_time
                controller.media_info.end_time = service_item.end_time
        elif controller.preview_display:
            if service_item.is_capable(ItemCapabilities.IsOptical):
                log.debug('video is optical and preview')
                path = service_item.get_frame_path()
                (name, title, audio_track, subtitle_track, start, end, clip_name) = parse_optical_path(path)
                is_valid = self.media_setup_optical(name, title, audio_track, subtitle_track, start, end, display,
                                                    controller)
            else:
                log.debug('video is not optical and preview')
                controller.media_info.length = service_item.media_length
                is_valid = self._check_file_type(controller, display)
        if not is_valid:
            # Media could not be loaded correctly
            critical_error_message_box(translate('MediaPlugin.MediaItem', 'Unsupported File'),
                                       translate('MediaPlugin.MediaItem', 'Unsupported File'))
            return False
        log.debug('video mediatype: ' + str(controller.media_info.media_type))
        # dont care about actual theme, set a black background
        if controller.is_live and not controller.media_info.is_background:
            display.frame.evaluateJavaScript('show_video("setBackBoard", null, null,"visible");')
        # now start playing - Preview is autoplay!
        autoplay = False
        # Preview requested
        if not controller.is_live:
            autoplay = True
        # Visible or background requested or Service Item wants to autostart
        elif not hidden or controller.media_info.is_background or service_item.will_auto_start:
            autoplay = True
        # Unblank on load set
        elif Settings().value('core/auto unblank'):
            autoplay = True
        if autoplay:
            if not self.media_play(controller):
                critical_error_message_box(translate('MediaPlugin.MediaItem', 'Unsupported File'),
                                           translate('MediaPlugin.MediaItem', 'Unsupported File'))
                return False
        self.set_controls_visible(controller, True)
        log.debug('use %s controller' % self.current_media_players[controller.controller_type].display_name)
        return True

    @staticmethod
    def media_length(media_path):
        """
        Uses Media Info to obtain the media length

        :param media_path: The file path to be checked..
        """
        if MediaInfo.can_parse():
            media_data = MediaInfo.parse(media_path)
        else:
            xml = check_output(['mediainfo', '-f', '--Output=XML', '--Inform=OLDXML', media_path])
            if not xml.startswith(b'<?xml'):
                xml = check_output(['mediainfo', '-f', '--Output=XML', media_path])
            media_data = MediaInfo(xml.decode("utf-8"))
        # duration returns in milli seconds
        return media_data.tracks[0].duration

    def media_setup_optical(self, filename, title, audio_track, subtitle_track, start, end, display, controller):
        """
        Setup playback of optical media

        :param filename: Path of the optical device/drive.
        :param title: The main/title track to play.
        :param audio_track: The audio track to play.
        :param subtitle_track: The subtitle track to play.
        :param start: Start position in milliseconds.
        :param end: End position in milliseconds.
        :param display: The display to play the media.
        :param controller: The media controller.
        :return: True if setup succeeded else False.
        """
        # stop running videos
        self.media_reset(controller)
        # Setup media info
        controller.media_info = ItemMediaInfo()
        controller.media_info.file_info = QtCore.QFileInfo(filename)
        if audio_track == -1 and subtitle_track == -1:
            controller.media_info.media_type = MediaType.CD
        else:
            controller.media_info.media_type = MediaType.DVD
        controller.media_info.start_time = start
        controller.media_info.end_time = end
        controller.media_info.length = (end - start)
        controller.media_info.title_track = title
        controller.media_info.audio_track = audio_track
        controller.media_info.subtitle_track = subtitle_track
        # When called from mediaitem display is None
        if display is None:
            display = controller.preview_display
        self.vlc_player.load(display)
        self.resize(display, self.vlc_player)
        self.current_media_players[controller.controller_type] = self.vlc_player
        if audio_track == -1 and subtitle_track == -1:
            controller.media_info.media_type = MediaType.CD
        else:
            controller.media_info.media_type = MediaType.DVD
        return True

    def _check_file_type(self, controller, display):
        """
        Select the correct media Player type from the prioritized Player list

        :param controller: First element is the controller which should be used
        :param display: Which display to use
        """
        for file in controller.media_info.file_info:
            if file.is_file:
                suffix = '*%s' % file.suffix.lower()
                player = self.vlc_player
                file = str(file)
                if suffix in player.video_extensions_list:
                    if not controller.media_info.is_background or controller.media_info.is_background and \
                            player.can_background:
                        self.resize(display, player)
                        if player.load(display, file):
                            self.current_media_players[controller.controller_type] = player
                            controller.media_info.media_type = MediaType.Video
                            return True
                if suffix in player.audio_extensions_list:
                    if player.load(display, file):
                        self.current_media_players[controller.controller_type] = player
                        controller.media_info.media_type = MediaType.Audio
                        return True
            else:
                player = self.vlc_player
                file = str(file)
                if player.can_folder:
                    self.resize(display, player)
                    if player.load(display, file):
                        self.current_media_players[controller.controller_type] = player
                        controller.media_info.media_type = MediaType.Video
                        return True
        return False

    def media_play_msg(self, msg, status=True):
        """
        Responds to the request to play a loaded video

        :param msg: First element is the controller which should be used
        :param status:
        """
        self.media_play(msg[0], status)

    def on_media_play(self):
        """
        Responds to the request to play a loaded video from the web.

        :param msg: First element is the controller which should be used
        """
        self.media_play(Registry().get('live_controller'), False)

    def media_play(self, controller, first_time=True):
        """
        Responds to the request to play a loaded video

        :param controller: The controller to be played
        :param first_time:
        """
        controller.seek_slider.blockSignals(True)
        controller.volume_slider.blockSignals(True)
        display = self._define_display(controller)
        if not self.current_media_players[controller.controller_type].play(display):
            controller.seek_slider.blockSignals(False)
            controller.volume_slider.blockSignals(False)
            return False
        if controller.media_info.is_background:
            self.media_volume(controller, 0)
        else:
            self.media_volume(controller, controller.media_info.volume)
        if first_time:
            if not controller.media_info.is_background:
                display.frame.evaluateJavaScript('show_blank("desktop");')
            self.current_media_players[controller.controller_type].set_visible(display, True)
            controller.mediabar.actions['playbackPlay'].setVisible(False)
            controller.mediabar.actions['playbackPause'].setVisible(True)
            controller.mediabar.actions['playbackStop'].setDisabled(False)
        if controller.is_live:
            if controller.hide_menu.defaultAction().isChecked() and not controller.media_info.is_background:
                controller.hide_menu.defaultAction().trigger()
            # Start Timer for ui updates
            if not self.live_timer.isActive():
                self.live_timer.start()
        else:
            # Start Timer for ui updates
            if not self.preview_timer.isActive():
                self.preview_timer.start()
        controller.seek_slider.blockSignals(False)
        controller.volume_slider.blockSignals(False)
        controller.media_info.is_playing = True
        display = self._define_display(controller)
        display.setVisible(True)
        return True

    def tick(self, controller):
        """
        Add a tick while the media is playing but only count if not paused

        :param controller:  The Controller to be processed
        """
        start_again = False
        if controller.media_info.is_playing and controller.media_info.length > 0:
            if controller.media_info.timer > controller.media_info.length:
                self.media_stop(controller, True)
                if controller.media_info.can_loop_playback:
                    start_again = True
            controller.media_info.timer += TICK_TIME
            seconds = controller.media_info.timer // 1000
            minutes = seconds // 60
            seconds %= 60
            total_seconds = controller.media_info.length // 1000
            total_minutes = total_seconds // 60
            total_seconds %= 60
            controller.position_label.setText(' %02d:%02d / %02d:%02d' %
                                              (minutes, seconds, total_minutes, total_seconds))
        if start_again:
            self.media_play(controller, True)

    def media_pause_msg(self, msg):
        """
        Responds to the request to pause a loaded video

        :param msg: First element is the controller which should be used
        """
        self.media_pause(msg[0])

    def on_media_pause(self):
        """
        Responds to the request to pause a loaded video from the web.

        :param msg: First element is the controller which should be used
        """
        self.media_pause(Registry().get('live_controller'))

    def media_pause(self, controller):
        """
        Responds to the request to pause a loaded video

        :param controller: The Controller to be paused
        """
        display = self._define_display(controller)
        if controller.controller_type in self.current_media_players:
            self.current_media_players[controller.controller_type].pause(display)
            controller.mediabar.actions['playbackPlay'].setVisible(True)
            controller.mediabar.actions['playbackStop'].setDisabled(False)
            controller.mediabar.actions['playbackPause'].setVisible(False)
            controller.media_info.is_playing = False

    def media_loop_msg(self, msg):
        """
        Responds to the request to loop a loaded video

        :param msg: First element is the controller which should be used
        """
        self.media_loop(msg[0])

    @staticmethod
    def media_loop(controller):
        """
        Responds to the request to loop a loaded video

        :param controller: The controller that needs to be stopped
        """
        controller.media_info.can_loop_playback = not controller.media_info.can_loop_playback
        controller.mediabar.actions['playbackLoop'].setChecked(controller.media_info.can_loop_playback)

    def media_stop_msg(self, msg):
        """
        Responds to the request to stop a loaded video

        :param msg: First element is the controller which should be used
        """
        self.media_stop(msg[0])

    def on_media_stop(self):
        """
        Responds to the request to stop a loaded video from the web.

        :param msg: First element is the controller which should be used
        """
        self.media_stop(Registry().get('live_controller'))

    def media_stop(self, controller, looping_background=False):
        """
        Responds to the request to stop a loaded video

        :param controller: The controller that needs to be stopped
        :param looping_background: The background is looping so do not blank.
        """
        display = self._define_display(controller)
        if controller.controller_type in self.current_media_players:
            if not looping_background:
                display.frame.evaluateJavaScript('show_blank("black");')
            self.current_media_players[controller.controller_type].stop(display)
            self.current_media_players[controller.controller_type].set_visible(display, False)
            controller.seek_slider.setSliderPosition(0)
            total_seconds = controller.media_info.length // 1000
            total_minutes = total_seconds // 60
            total_seconds %= 60
            controller.position_label.setText(' %02d:%02d / %02d:%02d' %
                                              (0, 0, total_minutes, total_seconds))
            controller.mediabar.actions['playbackPlay'].setVisible(True)
            controller.mediabar.actions['playbackStop'].setDisabled(True)
            controller.mediabar.actions['playbackPause'].setVisible(False)
            controller.media_info.is_playing = False
            controller.media_info.timer = 1000
            controller.media_timer = 0

    def media_volume_msg(self, msg):
        """
        Changes the volume of a running video

        :param msg: First element is the controller which should be used
        """
        controller = msg[0]
        vol = msg[1][0]
        self.media_volume(controller, vol)

    def media_volume(self, controller, volume):
        """
        Changes the volume of a running video

        :param controller: The Controller to use
        :param volume: The volume to be set
        """
        log.debug('media_volume %d' % volume)
        display = self._define_display(controller)
        self.current_media_players[controller.controller_type].volume(display, volume)
        controller.volume_slider.setValue(volume)

    def media_seek_msg(self, msg):
        """
        Responds to the request to change the seek Slider of a loaded video via a message

        :param msg: First element is the controller which should be used
            Second element is a list with the seek value as first element
        """
        controller = msg[0]
        seek_value = msg[1][0]
        self.media_seek(controller, seek_value)

    def media_seek(self, controller, seek_value):
        """
        Responds to the request to change the seek Slider of a loaded video

        :param controller: The controller to use.
        :param seek_value: The value to set.
        """
        display = self._define_display(controller)
        self.current_media_players[controller.controller_type].seek(display, seek_value)
        controller.media_info.timer = seek_value

    def media_reset(self, controller):
        """
        Responds to the request to reset a loaded video
        :param controller: The controller to use.
        """
        self.set_controls_visible(controller, False)
        display = self._define_display(controller)
        if controller.controller_type in self.current_media_players:
            display.override = {}
            self.current_media_players[controller.controller_type].reset(display)
            self.current_media_players[controller.controller_type].set_visible(display, False)
            display.frame.evaluateJavaScript('show_video("setBackBoard", null, null, "hidden");')
            del self.current_media_players[controller.controller_type]

    def media_hide(self, msg):
        """
        Hide the related video Widget

        :param msg: First element is the boolean for Live indication
        """
        is_live = msg[1]
        if not is_live:
            return
        display = self._define_display(self.live_controller)
        if self.live_controller.controller_type in self.current_media_players and \
                self.current_media_players[self.live_controller.controller_type].get_live_state() == MediaState.Playing:
            self.media_pause(display.controller)
            self.current_media_players[self.live_controller.controller_type].set_visible(display, False)

    def media_blank(self, msg):
        """
        Blank the related video Widget

        :param msg: First element is the boolean for Live indication
            Second element is the hide mode
        """
        is_live = msg[1]
        hide_mode = msg[2]
        if not is_live:
            return
        Registry().execute('live_display_hide', hide_mode)
        display = self._define_display(self.live_controller)
        if self.live_controller.controller_type in self.current_media_players and \
                self.current_media_players[self.live_controller.controller_type].get_live_state() == MediaState.Playing:
            self.media_pause(display.controller)
            self.current_media_players[self.live_controller.controller_type].set_visible(display, False)

    def media_unblank(self, msg):
        """
        Unblank the related video Widget

        :param msg: First element is not relevant in this context
            Second element is the boolean for Live indication
        """
        Registry().execute('live_display_show')
        is_live = msg[1]
        if not is_live:
            return
        display = self._define_display(self.live_controller)
        if self.live_controller.controller_type in self.current_media_players and \
                self.current_media_players[self.live_controller.controller_type].get_live_state() != \
                MediaState.Playing:
            if self.media_play(display.controller):
                self.current_media_players[self.live_controller.controller_type].set_visible(display, True)
                # Start Timer for ui updates
                if not self.live_timer.isActive():
                    self.live_timer.start()

    def finalise(self):
        """
        Reset all the media controllers when OpenLP shuts down
        """
        self.live_timer.stop()
        self.preview_timer.stop()
        for controller in self.display_controllers:
            self.media_reset(self.display_controllers[controller])

    @staticmethod
    def _define_display(controller):
        """
        Extract the correct display for a given controller

        :param controller:  Controller to be used
        """
        if controller.is_live:
            return controller.display
        return controller.preview_display
