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
Package to test the openlp.core.ui.slidecontroller package.
"""
from unittest import TestCase, skipUnless
from unittest.mock import MagicMock, patch

from PyQt5 import QtCore

from openlp.core.common import is_macosx
from openlp.core.common.path import Path
from openlp.core.common.registry import Registry
from openlp.core.display.screens import ScreenList
from openlp.core.lib import PluginManager
from openlp.core.ui import MainDisplay, AudioPlayer
from openlp.core.ui.maindisplay import TRANSPARENT_STYLESHEET, OPAQUE_STYLESHEET

from tests.helpers.testmixin import TestMixin

if is_macosx():
    from ctypes import pythonapi, c_void_p, c_char_p, py_object
    from sip import voidptr
    from objc import objc_object
    from AppKit import NSMainMenuWindowLevel, NSWindowCollectionBehaviorManaged


class TestMainDisplay(TestCase, TestMixin):

    def setUp(self):
        """
        Set up the components need for all tests.
        """
        # Mocked out desktop object
        self.desktop = MagicMock()
        self.desktop.primaryScreen.return_value = 0
        self.desktop.screenCount.return_value = 2
        self.desktop.screenGeometry.side_effect = lambda x: {0: QtCore.QRect(0, 0, 1024, 768),
                                                             1: QtCore.QRect(0, 0, 1024, 768)}[x]
        self.screens = ScreenList.create(self.desktop)
        Registry.create()
        self.registry = Registry()
        self.setup_application()
        Registry().register('application', self.app)
        self.mocked_audio_player = patch('openlp.core.ui.maindisplay.AudioPlayer')
        self.mocked_audio_player.start()

    def tearDown(self):
        """
        Delete QApplication.
        """
        self.mocked_audio_player.stop()
        del self.screens

    def test_initial_main_display(self):
        """
        Test the initial Main Display state
        """
        # GIVEN: A new SlideController instance.
        display = MagicMock()
        display.is_live = True

        # WHEN: The default controller is built.
        main_display = MainDisplay(display)

        # THEN: The controller should be a live controller.
        self.assertEqual(main_display.is_live, True, 'The main display should be a live controller')

    def test_set_transparency_enabled(self):
        """
        Test setting the display to be transparent
        """
        # GIVEN: An instance of MainDisplay
        display = MagicMock()
        main_display = MainDisplay(display)

        # WHEN: Transparency is enabled
        main_display.set_transparency(True)

        # THEN: The transparent stylesheet should be used
        self.assertEqual(TRANSPARENT_STYLESHEET, main_display.styleSheet(),
                         'The MainDisplay should use the transparent stylesheet')
        self.assertFalse(main_display.autoFillBackground(),
                         'The MainDisplay should not have autoFillBackground set')
        self.assertTrue(main_display.testAttribute(QtCore.Qt.WA_TranslucentBackground),
                        'The MainDisplay should have a translucent background')

    def test_set_transparency_disabled(self):
        """
        Test setting the display to be opaque
        """
        # GIVEN: An instance of MainDisplay
        display = MagicMock()
        main_display = MainDisplay(display)

        # WHEN: Transparency is disabled
        main_display.set_transparency(False)

        # THEN: The opaque stylesheet should be used
        self.assertEqual(OPAQUE_STYLESHEET, main_display.styleSheet(),
                         'The MainDisplay should use the opaque stylesheet')
        self.assertFalse(main_display.testAttribute(QtCore.Qt.WA_TranslucentBackground),
                         'The MainDisplay should not have a translucent background')

    def test_css_changed(self):
        """
        Test that when the CSS changes, the plugins are looped over and given an opportunity to update the CSS
        """
        # GIVEN: A mocked list of plugins, a mocked display and a MainDisplay
        mocked_songs_plugin = MagicMock()
        mocked_bibles_plugin = MagicMock()
        mocked_plugin_manager = MagicMock()
        mocked_plugin_manager.plugins = [mocked_songs_plugin, mocked_bibles_plugin]
        Registry().register('plugin_manager', mocked_plugin_manager)
        display = MagicMock()
        main_display = MainDisplay(display)
        # This is set up dynamically, so we need to mock it out for now
        main_display.frame = MagicMock()

        # WHEN: The css_changed() method is triggered
        main_display.css_changed()

        # THEN: The plugins should have each been given an opportunity to add their bit to the CSS
        mocked_songs_plugin.refresh_css.assert_called_with(main_display.frame)
        mocked_bibles_plugin.refresh_css.assert_called_with(main_display.frame)

    @skipUnless(is_macosx(), 'Can only run test on Mac OS X due to pyobjc dependency.')
    def test_macosx_display_window_flags_state(self):
        """
        Test that on Mac OS X we set the proper window flags
        """
        # GIVEN: A new SlideController instance on Mac OS X.
        self.screens.set_current_display(0)
        display = MagicMock()

        # WHEN: The default controller is built.
        main_display = MainDisplay(display)

        # THEN: The window flags should be the same as those needed on Mac OS X.
        self.assertEqual(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint | QtCore.Qt.NoDropShadowWindowHint,
                         main_display.windowFlags(),
                         'The window flags should be Qt.Window, Qt.FramelessWindowHint, and Qt.NoDropShadowWindowHint.')

    @skipUnless(is_macosx(), 'Can only run test on Mac OS X due to pyobjc dependency.')
    def test_macosx_display(self):
        """
        Test display on Mac OS X
        """
        # GIVEN: A new SlideController instance on Mac OS X.
        self.screens.set_current_display(0)
        display = MagicMock()

        # WHEN: The default controller is built and a reference to the underlying NSView is stored.
        main_display = MainDisplay(display)
        try:
            nsview_pointer = main_display.winId().ascapsule()
        except:
            nsview_pointer = voidptr(main_display.winId()).ascapsule()
        pythonapi.PyCapsule_SetName.restype = c_void_p
        pythonapi.PyCapsule_SetName.argtypes = [py_object, c_char_p]
        pythonapi.PyCapsule_SetName(nsview_pointer, c_char_p(b"objc.__object__"))
        pyobjc_nsview = objc_object(cobject=nsview_pointer)

        # THEN: The window level and collection behavior should be the same as those needed for Mac OS X.
        self.assertEqual(pyobjc_nsview.window().level(), NSMainMenuWindowLevel + 2,
                         'Window level should be NSMainMenuWindowLevel + 2')
        self.assertEqual(pyobjc_nsview.window().collectionBehavior(), NSWindowCollectionBehaviorManaged,
                         'Window collection behavior should be NSWindowCollectionBehaviorManaged')

    @patch('openlp.core.ui.maindisplay.Settings')
    def test_show_display_startup_logo(self, MockedSettings):
        # GIVEN: Mocked show_display, setting for logo visibility
        display = MagicMock()
        main_display = MainDisplay(display)
        main_display.frame = MagicMock()
        main_display.isHidden = MagicMock()
        main_display.isHidden.return_value = True
        main_display.setVisible = MagicMock()
        mocked_settings = MagicMock()
        mocked_settings.value.return_value = False
        MockedSettings.return_value = mocked_settings
        main_display.shake_web_view = MagicMock()

        # WHEN: show_display is called.
        main_display.show_display()

        # THEN: setVisible should had been called with "True"
        main_display.setVisible.assert_called_once_with(True)

    @patch('openlp.core.ui.maindisplay.Settings')
    def test_show_display_hide_startup_logo(self, MockedSettings):
        # GIVEN: Mocked show_display, setting for logo visibility
        display = MagicMock()
        main_display = MainDisplay(display)
        main_display.frame = MagicMock()
        main_display.isHidden = MagicMock()
        main_display.isHidden.return_value = False
        main_display.setVisible = MagicMock()
        mocked_settings = MagicMock()
        mocked_settings.value.return_value = False
        MockedSettings.return_value = mocked_settings
        main_display.shake_web_view = MagicMock()

        # WHEN: show_display is called.
        main_display.show_display()

        # THEN: setVisible should had not been called
        main_display.setVisible.assert_not_called()

    @patch('openlp.core.ui.maindisplay.Settings')
    @patch('openlp.core.ui.maindisplay.build_html')
    def test_build_html_no_video(self, MockedSettings, Mocked_build_html):
        # GIVEN: Mocked display
        display = MagicMock()
        mocked_media_controller = MagicMock()
        Registry.create()
        Registry().register('media_controller', mocked_media_controller)
        main_display = MainDisplay(display)
        main_display.frame = MagicMock()
        mocked_settings = MagicMock()
        mocked_settings.value.return_value = False
        MockedSettings.return_value = mocked_settings
        main_display.shake_web_view = MagicMock()
        service_item = MagicMock()
        mocked_plugin = MagicMock()
        display.plugin_manager = PluginManager()
        display.plugin_manager.plugins = [mocked_plugin]
        main_display.web_view = MagicMock()

        # WHEN: build_html is called with a normal service item and a non video theme.
        main_display.build_html(service_item)

        # THEN: the following should had not been called
        self.assertEquals(main_display.web_view.setHtml.call_count, 1, 'setHTML should be called once')
        self.assertEquals(main_display.media_controller.video.call_count, 0,
                          'Media Controller video should not have been called')

    @patch('openlp.core.ui.maindisplay.Settings')
    @patch('openlp.core.ui.maindisplay.build_html')
    def test_build_html_video(self, MockedSettings, Mocked_build_html):
        # GIVEN: Mocked display
        display = MagicMock()
        mocked_media_controller = MagicMock()
        Registry.create()
        Registry().register('media_controller', mocked_media_controller)
        main_display = MainDisplay(display)
        main_display.frame = MagicMock()
        mocked_settings = MagicMock()
        mocked_settings.value.return_value = False
        MockedSettings.return_value = mocked_settings
        main_display.shake_web_view = MagicMock()
        service_item = MagicMock()
        service_item.theme_data = MagicMock()
        service_item.theme_data.background_type = 'video'
        service_item.theme_data.theme_name = 'name'
        service_item.theme_data.background_filename = Path('background_filename')
        mocked_plugin = MagicMock()
        display.plugin_manager = PluginManager()
        display.plugin_manager.plugins = [mocked_plugin]
        main_display.web_view = MagicMock()

        # WHEN: build_html is called with a normal service item and a video theme.
        main_display.build_html(service_item)

        # THEN: the following should had not been called
        self.assertEquals(main_display.web_view.setHtml.call_count, 1, 'setHTML should be called once')
        self.assertEquals(main_display.media_controller.video.call_count, 1,
                          'Media Controller video should have been called once')


def test_calling_next_item_in_playlist():
    """
    Test the AudioPlayer.next() method
    """
    # GIVEN: An instance of AudioPlayer with a mocked out playlist
    audio_player = AudioPlayer(None)

    # WHEN: next is called.
    with patch.object(audio_player, 'playlist') as mocked_playlist:
        audio_player.next()

    # THEN: playlist.next should had been called once.
    mocked_playlist.next.assert_called_once_with()
