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
This is the main window, where all the action happens.
"""
import logging
import os
import shutil
import sys
import time
from datetime import datetime
from distutils import dir_util
from distutils.errors import DistutilsFileError
from tempfile import gettempdir

from PyQt5 import QtCore, QtGui, QtWidgets

from openlp.core.api import websockets
from openlp.core.api.http import server
from openlp.core.common import is_win, is_macosx, add_actions
from openlp.core.common.actions import ActionList, CategoryOrder
from openlp.core.common.applocation import AppLocation
from openlp.core.common.i18n import LanguageManager, UiStrings, translate
from openlp.core.common.path import Path, copyfile, create_paths
from openlp.core.common.mixins import RegistryProperties
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.display.screens import ScreenList
from openlp.core.display.renderer import Renderer
from openlp.core.lib import PluginManager, ImageManager, PluginStatus, build_icon
from openlp.core.lib.ui import create_action
from openlp.core.projectors.manager import ProjectorManager
from openlp.core.ui import AboutForm, SettingsForm, ServiceManager, ThemeManager, LiveController, PluginForm, \
    ShortcutListForm, FormattingTagForm, PreviewController
from openlp.core.ui.firsttimeform import FirstTimeForm
from openlp.core.widgets.dialogs import FileDialog
from openlp.core.widgets.docks import OpenLPDockWidget, MediaDockManager
from openlp.core.ui.media import MediaController
from openlp.core.ui.printserviceform import PrintServiceForm
from openlp.core.ui.style import PROGRESSBAR_STYLE, get_library_stylesheet
from openlp.core.version import get_version


log = logging.getLogger(__name__)


class Ui_MainWindow(object):
    """
    This is the UI part of the main window.
    """
    def setupUi(self, main_window):
        """
        Set up the user interface
        """
        main_window.setObjectName('MainWindow')
        main_window.setWindowIcon(build_icon(':/icon/openlp-logo.svg'))
        main_window.setDockNestingEnabled(True)
        if is_macosx():
            main_window.setDocumentMode(True)
        # Set up the main container, which contains all the other form widgets.
        self.main_content = QtWidgets.QWidget(main_window)
        self.main_content.setObjectName('main_content')
        self.main_content_layout = QtWidgets.QHBoxLayout(self.main_content)
        self.main_content_layout.setSpacing(0)
        self.main_content_layout.setContentsMargins(0, 0, 0, 0)
        self.main_content_layout.setObjectName('main_content_layout')
        main_window.setCentralWidget(self.main_content)
        self.control_splitter = QtWidgets.QSplitter(self.main_content)
        self.control_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.control_splitter.setObjectName('control_splitter')
        self.main_content_layout.addWidget(self.control_splitter)
        # Create slide controllers
        PreviewController(self)
        LiveController(self)
        preview_visible = Settings().value('user interface/preview panel')
        live_visible = Settings().value('user interface/live panel')
        panel_locked = Settings().value('user interface/lock panel')
        # Create menu
        self.menu_bar = QtWidgets.QMenuBar(main_window)
        self.menu_bar.setObjectName('menu_bar')
        self.file_menu = QtWidgets.QMenu(self.menu_bar)
        self.file_menu.setObjectName('fileMenu')
        self.recent_files_menu = QtWidgets.QMenu(self.file_menu)
        self.recent_files_menu.setObjectName('recentFilesMenu')
        self.file_import_menu = QtWidgets.QMenu(self.file_menu)
        if not is_macosx():
            self.file_import_menu.setIcon(build_icon(u':/general/general_import.png'))
        self.file_import_menu.setObjectName('file_import_menu')
        self.file_export_menu = QtWidgets.QMenu(self.file_menu)
        if not is_macosx():
            self.file_export_menu.setIcon(build_icon(u':/general/general_export.png'))
        self.file_export_menu.setObjectName('file_export_menu')
        # View Menu
        self.view_menu = QtWidgets.QMenu(self.menu_bar)
        self.view_menu.setObjectName('viewMenu')
        self.view_mode_menu = QtWidgets.QMenu(self.view_menu)
        self.view_mode_menu.setObjectName('viewModeMenu')
        # Tools Menu
        self.tools_menu = QtWidgets.QMenu(self.menu_bar)
        self.tools_menu.setObjectName('tools_menu')
        # Settings Menu
        self.settings_menu = QtWidgets.QMenu(self.menu_bar)
        self.settings_menu.setObjectName('settingsMenu')
        self.settings_language_menu = QtWidgets.QMenu(self.settings_menu)
        self.settings_language_menu.setObjectName('settingsLanguageMenu')
        # Help Menu
        self.help_menu = QtWidgets.QMenu(self.menu_bar)
        self.help_menu.setObjectName('helpMenu')
        main_window.setMenuBar(self.menu_bar)
        self.status_bar = QtWidgets.QStatusBar(main_window)
        self.status_bar.setObjectName('status_bar')
        main_window.setStatusBar(self.status_bar)
        self.load_progress_bar = QtWidgets.QProgressBar(self.status_bar)
        self.load_progress_bar.setObjectName('load_progress_bar')
        self.status_bar.addPermanentWidget(self.load_progress_bar)
        self.load_progress_bar.hide()
        self.load_progress_bar.setValue(0)
        self.load_progress_bar.setStyleSheet(PROGRESSBAR_STYLE)
        self.default_theme_label = QtWidgets.QLabel(self.status_bar)
        self.default_theme_label.setObjectName('default_theme_label')
        self.status_bar.addPermanentWidget(self.default_theme_label)
        # Create the MediaManager
        self.media_manager_dock = OpenLPDockWidget(main_window, 'media_manager_dock',
                                                   ':/system/system_mediamanager.png')
        self.media_manager_dock.setStyleSheet(get_library_stylesheet())
        # Create the media toolbox
        self.media_tool_box = QtWidgets.QToolBox(self.media_manager_dock)
        self.media_tool_box.setObjectName('media_tool_box')
        self.media_manager_dock.setWidget(self.media_tool_box)
        main_window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.media_manager_dock)
        # Create the service manager
        self.service_manager_dock = OpenLPDockWidget(main_window, 'service_manager_dock',
                                                     ':/system/system_servicemanager.png')
        self.service_manager_contents = ServiceManager(self.service_manager_dock)
        self.service_manager_dock.setWidget(self.service_manager_contents)
        main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.service_manager_dock)
        # Create the theme manager
        self.theme_manager_dock = OpenLPDockWidget(main_window, 'theme_manager_dock',
                                                   ':/system/system_thememanager.png')
        self.theme_manager_contents = ThemeManager(self.theme_manager_dock)
        self.theme_manager_contents.setObjectName('theme_manager_contents')
        self.theme_manager_dock.setWidget(self.theme_manager_contents)
        main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.theme_manager_dock)
        # Create the projector manager
        self.projector_manager_dock = OpenLPDockWidget(parent=main_window,
                                                       name='projector_manager_dock',
                                                       icon=':/projector/projector_manager.png')
        self.projector_manager_contents = ProjectorManager(self.projector_manager_dock)
        self.projector_manager_contents.setObjectName('projector_manager_contents')
        self.projector_manager_dock.setWidget(self.projector_manager_contents)
        self.projector_manager_dock.setVisible(False)
        main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.projector_manager_dock)
        # Create the menu items
        action_list = ActionList.get_instance()
        action_list.add_category(UiStrings().File, CategoryOrder.standard_menu)
        self.file_new_item = create_action(main_window, 'fileNewItem', icon=':/general/general_new.png',
                                           can_shortcuts=True, category=UiStrings().File,
                                           triggers=self.service_manager_contents.on_new_service_clicked)
        self.file_open_item = create_action(main_window, 'fileOpenItem', icon=':/general/general_open.png',
                                            can_shortcuts=True, category=UiStrings().File,
                                            triggers=self.service_manager_contents.on_load_service_clicked)
        self.file_save_item = create_action(main_window, 'fileSaveItem', icon=':/general/general_save.png',
                                            can_shortcuts=True, category=UiStrings().File,
                                            triggers=self.service_manager_contents.decide_save_method)
        self.file_save_as_item = create_action(main_window, 'fileSaveAsItem', can_shortcuts=True,
                                               category=UiStrings().File,
                                               triggers=self.service_manager_contents.save_file_as)
        self.print_service_order_item = create_action(main_window, 'printServiceItem', can_shortcuts=True,
                                                      category=UiStrings().File,
                                                      triggers=lambda x: PrintServiceForm().exec())
        self.file_exit_item = create_action(main_window, 'fileExitItem', icon=':/system/system_exit.png',
                                            can_shortcuts=True,
                                            category=UiStrings().File, triggers=main_window.close)
        # Give QT Extra Hint that this is the Exit Menu Item
        self.file_exit_item.setMenuRole(QtWidgets.QAction.QuitRole)
        action_list.add_category(UiStrings().Import, CategoryOrder.standard_menu)
        self.import_theme_item = create_action(main_window, 'importThemeItem', category=UiStrings().Import,
                                               can_shortcuts=True)
        self.import_language_item = create_action(main_window, 'importLanguageItem')
        action_list.add_category(UiStrings().Export, CategoryOrder.standard_menu)
        self.export_theme_item = create_action(main_window, 'exportThemeItem', category=UiStrings().Export,
                                               can_shortcuts=True)
        self.export_language_item = create_action(main_window, 'exportLanguageItem')
        action_list.add_category(UiStrings().View, CategoryOrder.standard_menu)
        # Projector items
        self.import_projector_item = create_action(main_window, 'importProjectorItem', category=UiStrings().Import,
                                                   can_shortcuts=False)
        action_list.add_category(UiStrings().Import, CategoryOrder.standard_menu)
        self.view_projector_manager_item = create_action(main_window, 'viewProjectorManagerItem',
                                                         icon=':/projector/projector_manager.png',
                                                         checked=self.projector_manager_dock.isVisible(),
                                                         can_shortcuts=True,
                                                         category=UiStrings().View,
                                                         triggers=self.toggle_projector_manager)
        self.view_media_manager_item = create_action(main_window, 'viewMediaManagerItem',
                                                     icon=':/system/system_mediamanager.png',
                                                     checked=self.media_manager_dock.isVisible(),
                                                     can_shortcuts=True,
                                                     category=UiStrings().View, triggers=self.toggle_media_manager)
        self.view_theme_manager_item = create_action(main_window, 'viewThemeManagerItem', can_shortcuts=True,
                                                     icon=':/system/system_thememanager.png',
                                                     checked=self.theme_manager_dock.isVisible(),
                                                     category=UiStrings().View, triggers=self.toggle_theme_manager)
        self.view_service_manager_item = create_action(main_window, 'viewServiceManagerItem', can_shortcuts=True,
                                                       icon=':/system/system_servicemanager.png',
                                                       checked=self.service_manager_dock.isVisible(),
                                                       category=UiStrings().View, triggers=self.toggle_service_manager)
        self.view_preview_panel = create_action(main_window, 'viewPreviewPanel', can_shortcuts=True,
                                                checked=preview_visible, category=UiStrings().View,
                                                triggers=self.set_preview_panel_visibility)
        self.view_live_panel = create_action(main_window, 'viewLivePanel', can_shortcuts=True, checked=live_visible,
                                             category=UiStrings().View, triggers=self.set_live_panel_visibility)
        self.lock_panel = create_action(main_window, 'lockPanel', can_shortcuts=True, checked=panel_locked,
                                        category=UiStrings().View, triggers=self.set_lock_panel)
        action_list.add_category(UiStrings().ViewMode, CategoryOrder.standard_menu)
        self.mode_default_item = create_action(
            main_window, 'modeDefaultItem', checked=False, category=UiStrings().ViewMode, can_shortcuts=True)
        self.mode_setup_item = create_action(main_window, 'modeSetupItem', checked=False, category=UiStrings().ViewMode,
                                             can_shortcuts=True)
        self.mode_live_item = create_action(main_window, 'modeLiveItem', checked=True, category=UiStrings().ViewMode,
                                            can_shortcuts=True)
        self.mode_group = QtWidgets.QActionGroup(main_window)
        self.mode_group.addAction(self.mode_default_item)
        self.mode_group.addAction(self.mode_setup_item)
        self.mode_group.addAction(self.mode_live_item)
        self.mode_default_item.setChecked(True)
        action_list.add_category(UiStrings().Tools, CategoryOrder.standard_menu)
        self.tools_add_tool_item = create_action(main_window,
                                                 'toolsAddToolItem', icon=':/tools/tools_add.png',
                                                 category=UiStrings().Tools, can_shortcuts=True)
        self.tools_open_data_folder = create_action(main_window,
                                                    'toolsOpenDataFolder', icon=':/general/general_open.png',
                                                    category=UiStrings().Tools, can_shortcuts=True)
        self.tools_first_time_wizard = create_action(main_window,
                                                     'toolsFirstTimeWizard', icon=':/general/general_revert.png',
                                                     category=UiStrings().Tools, can_shortcuts=True)
        self.update_theme_images = create_action(main_window,
                                                 'updateThemeImages', category=UiStrings().Tools, can_shortcuts=True)
        action_list.add_category(UiStrings().Settings, CategoryOrder.standard_menu)
        self.settings_plugin_list_item = create_action(main_window,
                                                       'settingsPluginListItem',
                                                       icon=':/system/settings_plugin_list.png',
                                                       can_shortcuts=True,
                                                       category=UiStrings().Settings,
                                                       triggers=self.on_plugin_item_clicked)
        # i18n Language Items
        self.auto_language_item = create_action(main_window, 'autoLanguageItem', checked=LanguageManager.auto_language)
        self.language_group = QtWidgets.QActionGroup(main_window)
        self.language_group.setExclusive(True)
        self.language_group.setObjectName('languageGroup')
        add_actions(self.language_group, [self.auto_language_item])
        qm_list = LanguageManager.get_qm_list()
        saved_language = LanguageManager.get_language()
        for key in sorted(qm_list.keys()):
            language_item = create_action(main_window, key, checked=qm_list[key] == saved_language)
            add_actions(self.language_group, [language_item])
        self.settings_shortcuts_item = create_action(main_window, 'settingsShortcutsItem',
                                                     icon=':/system/system_configure_shortcuts.png',
                                                     category=UiStrings().Settings, can_shortcuts=True)
        # Formatting Tags were also known as display tags.
        self.formatting_tag_item = create_action(main_window, 'displayTagItem',
                                                 icon=':/system/tag_editor.png', category=UiStrings().Settings,
                                                 can_shortcuts=True)
        self.settings_configure_item = create_action(main_window, 'settingsConfigureItem',
                                                     icon=':/system/system_settings.png', can_shortcuts=True,
                                                     category=UiStrings().Settings)
        # Give QT Extra Hint that this is the Preferences Menu Item
        self.settings_configure_item.setMenuRole(QtWidgets.QAction.PreferencesRole)
        self.settings_import_item = create_action(main_window, 'settingsImportItem',
                                                  category=UiStrings().Import, can_shortcuts=True)
        self.settings_export_item = create_action(main_window, 'settingsExportItem',
                                                  category=UiStrings().Export, can_shortcuts=True)
        action_list.add_category(UiStrings().Help, CategoryOrder.standard_menu)
        self.about_item = create_action(main_window, 'aboutItem', icon=':/system/system_about.png',
                                        can_shortcuts=True, category=UiStrings().Help,
                                        triggers=self.on_about_item_clicked)
        # Give QT Extra Hint that this is an About Menu Item
        self.about_item.setMenuRole(QtWidgets.QAction.AboutRole)
        if is_win():
            self.local_help_file = AppLocation.get_directory(AppLocation.AppDir) / 'OpenLP.chm'
        elif is_macosx():
            self.local_help_file = AppLocation.get_directory(AppLocation.AppDir) / '..' / 'Resources' / 'OpenLP.help'
        self.user_manual_item = create_action(main_window, 'userManualItem', icon=':/system/system_help_contents.png',
                                              can_shortcuts=True, category=UiStrings().Help,
                                              triggers=self.on_help_clicked)
        self.web_site_item = create_action(main_window, 'webSiteItem', can_shortcuts=True, category=UiStrings().Help)
        # Shortcuts not connected to buttons or menu entries.
        self.search_shortcut_action = create_action(main_window,
                                                    'searchShortcut', can_shortcuts=True,
                                                    category=translate('OpenLP.MainWindow', 'General'),
                                                    triggers=self.on_search_shortcut_triggered)
        '''
        Leave until the import projector options are finished
        add_actions(self.file_import_menu, (self.settings_import_item, self.import_theme_item,
                    self.import_projector_item, self.import_language_item, None))
        '''
        add_actions(self.file_import_menu, (self.settings_import_item, self.import_theme_item,
                    self.import_language_item, None))
        add_actions(self.file_export_menu, (self.settings_export_item, self.export_theme_item,
                    self.export_language_item, None))
        add_actions(self.file_menu, (self.file_new_item, self.file_open_item,
                    self.file_save_item, self.file_save_as_item, self.recent_files_menu.menuAction(), None,
                    self.file_import_menu.menuAction(), self.file_export_menu.menuAction(), None,
                    self.print_service_order_item, self.file_exit_item))
        add_actions(self.view_mode_menu, (self.mode_default_item, self.mode_setup_item, self.mode_live_item))
        add_actions(self.view_menu, (self.view_mode_menu.menuAction(), None, self.view_media_manager_item,
                    self.view_projector_manager_item, self.view_service_manager_item, self.view_theme_manager_item,
                    None, self.view_preview_panel, self.view_live_panel, None, self.lock_panel))
        # i18n add Language Actions
        add_actions(self.settings_language_menu, (self.auto_language_item, None))
        add_actions(self.settings_language_menu, self.language_group.actions())
        # Qt on OS X looks for keywords in the menu items title to determine which menu items get added to the main
        # menu. If we are running on Mac OS X the menu items whose title contains those keywords but don't belong in the
        # main menu need to be marked as such with QAction.NoRole.
        if is_macosx():
            self.settings_shortcuts_item.setMenuRole(QtWidgets.QAction.NoRole)
            self.formatting_tag_item.setMenuRole(QtWidgets.QAction.NoRole)
        add_actions(self.settings_menu, (self.settings_plugin_list_item, self.settings_language_menu.menuAction(),
                    None, self.formatting_tag_item, self.settings_shortcuts_item, self.settings_configure_item))
        add_actions(self.tools_menu, (self.tools_add_tool_item, None))
        add_actions(self.tools_menu, (self.tools_open_data_folder, None))
        add_actions(self.tools_menu, (self.tools_first_time_wizard, None))
        add_actions(self.tools_menu, [self.update_theme_images])
        add_actions(self.help_menu, (self.user_manual_item, None, self.web_site_item, self.about_item))
        add_actions(self.menu_bar, (self.file_menu.menuAction(), self.view_menu.menuAction(),
                    self.tools_menu.menuAction(), self.settings_menu.menuAction(), self.help_menu.menuAction()))
        add_actions(self, [self.search_shortcut_action])
        # Initialise the translation
        self.retranslateUi(main_window)
        self.media_tool_box.setCurrentIndex(0)
        # Connect up some signals and slots
        self.file_menu.aboutToShow.connect(self.update_recent_files_menu)
        # Hide the entry, as it does not have any functionality yet.
        self.tools_add_tool_item.setVisible(False)
        self.import_language_item.setVisible(False)
        self.export_language_item.setVisible(False)
        self.set_lock_panel(panel_locked)
        self.settings_imported = False

    def retranslateUi(self, main_window):
        """
        Set up the translation system
        """
        main_window.setWindowTitle(UiStrings().OpenLP)
        self.file_menu.setTitle(translate('OpenLP.MainWindow', '&File'))
        self.file_import_menu.setTitle(translate('OpenLP.MainWindow', '&Import'))
        self.file_export_menu.setTitle(translate('OpenLP.MainWindow', '&Export'))
        self.recent_files_menu.setTitle(translate('OpenLP.MainWindow', '&Recent Services'))
        self.view_menu.setTitle(translate('OpenLP.MainWindow', '&View'))
        self.view_mode_menu.setTitle(translate('OpenLP.MainWindow', '&Layout Presets'))
        self.tools_menu.setTitle(translate('OpenLP.MainWindow', '&Tools'))
        self.settings_menu.setTitle(translate('OpenLP.MainWindow', '&Settings'))
        self.settings_language_menu.setTitle(translate('OpenLP.MainWindow', '&Language'))
        self.help_menu.setTitle(translate('OpenLP.MainWindow', '&Help'))
        self.media_manager_dock.setWindowTitle(translate('OpenLP.MainWindow', 'Library'))
        self.service_manager_dock.setWindowTitle(translate('OpenLP.MainWindow', 'Service'))
        self.theme_manager_dock.setWindowTitle(translate('OpenLP.MainWindow', 'Themes'))
        self.projector_manager_dock.setWindowTitle(translate('OpenLP.MainWindow', 'Projector Controller'))
        self.file_new_item.setText(translate('OpenLP.MainWindow', '&New Service'))
        self.file_new_item.setToolTip(UiStrings().NewService)
        self.file_new_item.setStatusTip(UiStrings().CreateService)
        self.file_open_item.setText(translate('OpenLP.MainWindow', '&Open Service'))
        self.file_open_item.setToolTip(UiStrings().OpenService)
        self.file_open_item.setStatusTip(translate('OpenLP.MainWindow', 'Open an existing service.'))
        self.file_save_item.setText(translate('OpenLP.MainWindow', '&Save Service'))
        self.file_save_item.setToolTip(UiStrings().SaveService)
        self.file_save_item.setStatusTip(translate('OpenLP.MainWindow', 'Save the current service to disk.'))
        self.file_save_as_item.setText(translate('OpenLP.MainWindow', 'Save Service &As...'))
        self.file_save_as_item.setToolTip(translate('OpenLP.MainWindow', 'Save Service As'))
        self.file_save_as_item.setStatusTip(translate('OpenLP.MainWindow',
                                            'Save the current service under a new name.'))
        self.print_service_order_item.setText(UiStrings().PrintService)
        self.print_service_order_item.setStatusTip(translate('OpenLP.MainWindow', 'Print the current service.'))
        self.file_exit_item.setText(translate('OpenLP.MainWindow', 'E&xit'))
        self.file_exit_item.setStatusTip(translate('OpenLP.MainWindow', 'Close OpenLP - Shut down the program.'))
        self.import_theme_item.setText(translate('OpenLP.MainWindow', '&Theme'))
        self.import_language_item.setText(translate('OpenLP.MainWindow', '&Language'))
        self.export_theme_item.setText(translate('OpenLP.MainWindow', '&Theme'))
        self.export_language_item.setText(translate('OpenLP.MainWindow', '&Language'))
        self.settings_shortcuts_item.setText(translate('OpenLP.MainWindow', 'Configure &Shortcuts...'))
        self.formatting_tag_item.setText(translate('OpenLP.MainWindow', 'Configure &Formatting Tags...'))
        self.settings_configure_item.setText(translate('OpenLP.MainWindow', '&Configure OpenLP...'))
        self.settings_export_item.setStatusTip(
            translate('OpenLP.MainWindow', 'Export settings to a *.config file.'))
        self.settings_export_item.setText(translate('OpenLP.MainWindow', 'Settings'))
        self.settings_import_item.setStatusTip(
            translate('OpenLP.MainWindow', 'Import settings from a *.config file previously exported from '
                                           'this or another machine.'))
        self.settings_import_item.setText(translate('OpenLP.MainWindow', 'Settings'))
        self.view_projector_manager_item.setText(translate('OpenLP.MainWindow', '&Projector Controller'))
        self.view_projector_manager_item.setToolTip(translate('OpenLP.MainWindow', 'Hide or show Projectors.'))
        self.view_projector_manager_item.setStatusTip(translate('OpenLP.MainWindow',
                                                                'Toggle visibility of the Projectors.'))
        self.view_media_manager_item.setText(translate('OpenLP.MainWindow', 'L&ibrary'))
        self.view_media_manager_item.setToolTip(translate('OpenLP.MainWindow', 'Hide or show the Library.'))
        self.view_media_manager_item.setStatusTip(translate('OpenLP.MainWindow',
                                                  'Toggle the visibility of the Library.'))
        self.view_theme_manager_item.setText(translate('OpenLP.MainWindow', '&Themes'))
        self.view_theme_manager_item.setToolTip(translate('OpenLP.MainWindow', 'Hide or show themes'))
        self.view_theme_manager_item.setStatusTip(translate('OpenLP.MainWindow',
                                                  'Toggle visibility of the Themes.'))
        self.view_service_manager_item.setText(translate('OpenLP.MainWindow', '&Service'))
        self.view_service_manager_item.setToolTip(translate('OpenLP.MainWindow', 'Hide or show Service.'))
        self.view_service_manager_item.setStatusTip(translate('OpenLP.MainWindow',
                                                    'Toggle visibility of the Service.'))
        self.view_preview_panel.setText(translate('OpenLP.MainWindow', '&Preview'))
        self.view_preview_panel.setToolTip(translate('OpenLP.MainWindow', 'Hide or show Preview.'))
        self.view_preview_panel.setStatusTip(
            translate('OpenLP.MainWindow', 'Toggle visibility of the Preview.'))
        self.view_live_panel.setText(translate('OpenLP.MainWindow', 'Li&ve'))
        self.view_live_panel.setToolTip(translate('OpenLP.MainWindow', 'Hide or show Live'))
        self.lock_panel.setText(translate('OpenLP.MainWindow', 'L&ock visibility of the panels'))
        self.lock_panel.setStatusTip(translate('OpenLP.MainWindow', 'Lock visibility of the panels.'))
        self.view_live_panel.setStatusTip(translate('OpenLP.MainWindow', 'Toggle visibility of the Live.'))
        self.settings_plugin_list_item.setText(translate('OpenLP.MainWindow', '&Manage Plugins'))
        self.settings_plugin_list_item.setStatusTip(translate('OpenLP.MainWindow', 'You can enable and disable plugins '
                                                                                   'from here.'))
        self.about_item.setText(translate('OpenLP.MainWindow', '&About'))
        self.about_item.setStatusTip(translate('OpenLP.MainWindow', 'More information about OpenLP.'))
        self.user_manual_item.setText(translate('OpenLP.MainWindow', '&User Manual'))
        self.search_shortcut_action.setText(UiStrings().Search)
        self.search_shortcut_action.setToolTip(
            translate('OpenLP.MainWindow', 'Jump to the search box of the current active plugin.'))
        self.web_site_item.setText(translate('OpenLP.MainWindow', '&Web Site'))
        for item in self.language_group.actions():
            item.setText(item.objectName())
            item.setStatusTip(translate('OpenLP.MainWindow',
                                        'Set the interface language to {name}').format(name=item.objectName()))
        self.auto_language_item.setText(translate('OpenLP.MainWindow', '&Autodetect'))
        self.auto_language_item.setStatusTip(translate('OpenLP.MainWindow', 'Use the system language, if available.'))
        self.tools_add_tool_item.setText(translate('OpenLP.MainWindow', 'Add &Tool...'))
        self.tools_add_tool_item.setStatusTip(translate('OpenLP.MainWindow',
                                                        'Add an application to the list of tools.'))
        self.tools_open_data_folder.setText(translate('OpenLP.MainWindow', 'Open &Data Folder...'))
        self.tools_open_data_folder.setStatusTip(translate('OpenLP.MainWindow',
                                                 'Open the folder where songs, bibles and other data resides.'))
        self.tools_first_time_wizard.setText(translate('OpenLP.MainWindow', 'Re-run First Time Wizard'))
        self.tools_first_time_wizard.setStatusTip(translate('OpenLP.MainWindow',
                                                  'Re-run the First Time Wizard, importing songs, Bibles and themes.'))
        self.update_theme_images.setText(translate('OpenLP.MainWindow', 'Update Theme Images'))
        self.update_theme_images.setStatusTip(translate('OpenLP.MainWindow',
                                                        'Update the preview images for all themes.'))
        self.mode_default_item.setText(translate('OpenLP.MainWindow', '&Show all'))
        self.mode_default_item.setStatusTip(translate('OpenLP.MainWindow', 'Reset the interface back to the '
                                                                           'default layout and show all the panels.'))
        self.mode_setup_item.setText(translate('OpenLP.MainWindow', '&Setup'))
        self.mode_setup_item.setStatusTip(translate('OpenLP.MainWindow', 'Use layout that focuses on setting'
                                                                         ' up the Service.'))
        self.mode_live_item.setText(translate('OpenLP.MainWindow', '&Live'))
        self.mode_live_item.setStatusTip(translate('OpenLP.MainWindow', 'Use layout that focuses on Live.'))


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow, RegistryProperties):
    """
    The main window.
    """
    log.info('MainWindow loaded')

    def __init__(self):
        """
        This constructor sets up the interface, the various managers, and the plugins.
        """
        super(MainWindow, self).__init__()
        Registry().register('main_window', self)
        self.version_thread = None
        self.version_worker = None
        self.clipboard = self.application.clipboard()
        self.arguments = ''.join(self.application.args)
        # Set up settings sections for the main application (not for use by plugins).
        self.ui_settings_section = 'user interface'
        self.general_settings_section = 'core'
        self.advanced_settings_section = 'advanced'
        self.shortcuts_settings_section = 'shortcuts'
        self.service_manager_settings_section = 'servicemanager'
        self.songs_settings_section = 'songs'
        self.themes_settings_section = 'themes'
        self.projector_settings_section = 'projector'
        self.players_settings_section = 'players'
        self.display_tags_section = 'displayTags'
        self.header_section = 'SettingsImport'
        self.recent_files = []
        self.timer_id = 0
        self.new_data_path = None
        self.copy_data = False
        Settings().set_up_default_values()
        self.about_form = AboutForm(self)
        MediaController()
        websockets.WebSocketServer()
        server.HttpServer()
        SettingsForm(self)
        self.formatting_tag_form = FormattingTagForm(self)
        self.shortcut_form = ShortcutListForm(self)
        # Set up the path with plugins
        PluginManager(self)
        ImageManager()
        Renderer()
        # Set up the interface
        self.setupUi(self)
        # Define the media Dock Manager
        self.media_dock_manager = MediaDockManager(self.media_tool_box)
        # Load settings after setupUi so default UI sizes are overwritten
        # Once settings are loaded update the menu with the recent files.
        self.update_recent_files_menu()
        self.plugin_form = PluginForm(self)
        # Set up signals and slots
        self.media_manager_dock.visibilityChanged.connect(self.view_media_manager_item.setChecked)
        self.service_manager_dock.visibilityChanged.connect(self.view_service_manager_item.setChecked)
        self.theme_manager_dock.visibilityChanged.connect(self.view_theme_manager_item.setChecked)
        self.projector_manager_dock.visibilityChanged.connect(self.view_projector_manager_item.setChecked)
        self.import_theme_item.triggered.connect(self.theme_manager_contents.on_import_theme)
        self.export_theme_item.triggered.connect(self.theme_manager_contents.on_export_theme)
        self.web_site_item.triggered.connect(self.on_help_web_site_clicked)
        self.tools_open_data_folder.triggered.connect(self.on_tools_open_data_folder_clicked)
        self.tools_first_time_wizard.triggered.connect(self.on_first_time_wizard_clicked)
        self.update_theme_images.triggered.connect(self.on_update_theme_images)
        self.formatting_tag_item.triggered.connect(self.on_formatting_tag_item_clicked)
        self.settings_configure_item.triggered.connect(self.on_settings_configure_item_clicked)
        self.settings_shortcuts_item.triggered.connect(self.on_settings_shortcuts_item_clicked)
        self.settings_import_item.triggered.connect(self.on_settings_import_item_clicked)
        self.settings_export_item.triggered.connect(self.on_settings_export_item_clicked)
        # i18n set signals for languages
        self.language_group.triggered.connect(LanguageManager.set_language)
        self.mode_default_item.triggered.connect(self.on_mode_default_item_clicked)
        self.mode_setup_item.triggered.connect(self.on_mode_setup_item_clicked)
        self.mode_live_item.triggered.connect(self.on_mode_live_item_clicked)
        # Media Manager
        self.media_tool_box.currentChanged.connect(self.on_media_tool_box_changed)
        self.application.set_busy_cursor()
        # Simple message boxes
        Registry().register_function('theme_update_global', self.default_theme_changed)
        Registry().register_function('config_screen_changed', self.screen_changed)
        Registry().register_function('bootstrap_post_set_up', self.bootstrap_post_set_up)
        # Reset the cursor
        self.application.set_normal_cursor()

    def bootstrap_post_set_up(self):
        """
        process the bootstrap post setup request
        """
        self.preview_controller.panel.setVisible(Settings().value('user interface/preview panel'))
        self.live_controller.panel.setVisible(Settings().value('user interface/live panel'))
        self.load_settings()
        self.restore_current_media_manager_item()
        Registry().execute('theme_update_global')

    def restore_current_media_manager_item(self):
        """
        Called on start up to restore the last active media plugin.
        """
        log.info('Load data from Settings')
        if Settings().value('advanced/save current plugin'):
            saved_plugin_id = Settings().value('advanced/current media plugin')
            if saved_plugin_id != -1:
                self.media_tool_box.setCurrentIndex(saved_plugin_id)

    def on_search_shortcut_triggered(self):
        """
        Called when the search shortcut has been pressed.
        """
        # Make sure the media_dock is visible.
        if not self.media_manager_dock.isVisible():
            self.media_manager_dock.setVisible(True)
        widget = self.media_tool_box.currentWidget()
        if widget:
            widget.on_focus()

    def on_media_tool_box_changed(self, index):
        """
        Focus a widget when the media toolbox changes.
        """
        widget = self.media_tool_box.widget(index)
        if widget:
            widget.on_focus()

    def on_new_version(self, version):
        """
        Notifies the user that a newer version of OpenLP is available.
        Triggered by delay thread and cannot display popup.

        :param version: The Version to be displayed.
        """
        log.debug('version_notice')
        version_text = translate('OpenLP.MainWindow', 'Version {new} of OpenLP is now available for download (you are '
                                 'currently running version {current}). \n\nYou can download the latest version from '
                                 'http://openlp.org/.').format(new=version, current=get_version()[u'full'])
        QtWidgets.QMessageBox.question(self, translate('OpenLP.MainWindow', 'OpenLP Version Updated'), version_text)

    def show(self):
        """
        Show the main form, as well as the display form
        """
        QtWidgets.QWidget.show(self)
        if self.live_controller.display.isVisible():
            self.live_controller.display.setFocus()
        self.activateWindow()
        if self.arguments:
            self.open_cmd_line_files(self.arguments)
        elif Settings().value(self.general_settings_section + '/auto open'):
            self.service_manager_contents.load_last_file()
        # This will store currently used layout preset so it remains enabled on next startup.
        # If any panel is enabled/disabled after preset is set, this setting is not saved.
        view_mode = Settings().value('{section}/view mode'.format(section=self.general_settings_section))
        if view_mode == 'default' and Settings().value('user interface/is preset layout'):
            self.mode_default_item.setChecked(True)
        elif view_mode == 'setup' and Settings().value('user interface/is preset layout'):
            self.set_view_mode(True, True, False, True, False, True)
            self.mode_setup_item.setChecked(True)
        elif view_mode == 'live' and Settings().value('user interface/is preset layout'):
            self.set_view_mode(False, True, False, False, True, True)
            self.mode_live_item.setChecked(True)

    def app_startup(self):
        """
        Give all the plugins a chance to perform some tasks at startup
        """
        self.application.process_events()
        for plugin in self.plugin_manager.plugins:
            if plugin.is_active():
                plugin.app_startup()
                self.application.process_events()

    def first_time(self):
        """
        Import themes if first time
        """
        self.application.process_events()
        for plugin in self.plugin_manager.plugins:
            if hasattr(plugin, 'first_time'):
                self.application.process_events()
                plugin.first_time()
        self.application.process_events()
        temp_path = Path(gettempdir(), 'openlp')
        temp_path.rmtree(True)

    def on_first_time_wizard_clicked(self):
        """
        Re-run the first time wizard.  Prompts the user for run confirmation.If wizard is run, songs, bibles and
        themes are imported.  The default theme is changed (if necessary).  The plugins in pluginmanager are
        set active/in-active to match the selection in the wizard.
        """
        answer = QtWidgets.QMessageBox.warning(self,
                                               translate('OpenLP.MainWindow', 'Re-run First Time Wizard?'),
                                               translate('OpenLP.MainWindow',
                                                         'Are you sure you want to re-run the First '
                                                         'Time Wizard?\n\nRe-running this wizard may make changes to '
                                                         'your current OpenLP configuration and possibly add songs to '
                                                         'your existing songs list and change your default theme.'),
                                               QtWidgets.QMessageBox.StandardButtons(QtWidgets.QMessageBox.Yes |
                                                                                     QtWidgets.QMessageBox.No),
                                               QtWidgets.QMessageBox.No)
        if answer == QtWidgets.QMessageBox.No:
            return
        first_run_wizard = FirstTimeForm(self)
        first_run_wizard.initialize(ScreenList())
        first_run_wizard.exec()
        if first_run_wizard.was_cancelled:
            return
        self.application.set_busy_cursor()
        self.first_time()
        # Check if Projectors panel should be visible or not after wizard.
        if Settings().value('projector/show after wizard'):
            self.projector_manager_dock.setVisible(True)
        else:
            self.projector_manager_dock.setVisible(False)
        for plugin in self.plugin_manager.plugins:
            self.active_plugin = plugin
            old_status = self.active_plugin.status
            self.active_plugin.set_status()
            if old_status != self.active_plugin.status:
                if self.active_plugin.status == PluginStatus.Active:
                    self.active_plugin.toggle_status(PluginStatus.Active)
                    self.active_plugin.app_startup()
                else:
                    self.active_plugin.toggle_status(PluginStatus.Inactive)
        # Set global theme and
        Registry().execute('theme_update_global')
        # Load the themes from files
        self.theme_manager_contents.load_first_time_themes()
        # Update the theme widget
        self.theme_manager_contents.load_themes()
        # Check if any Bibles downloaded.  If there are, they will be processed.
        Registry().execute('bibles_load_list', True)
        self.application.set_normal_cursor()

    def is_display_blank(self):
        """
        Check and display message if screen blank on setup.
        """
        settings = Settings()
        self.live_controller.main_display_set_background()
        if settings.value('{section}/screen blank'.format(section=self.general_settings_section)):
            if settings.value('{section}/blank warning'.format(section=self.general_settings_section)):
                QtWidgets.QMessageBox.question(self, translate('OpenLP.MainWindow', 'OpenLP Main Display Blanked'),
                                               translate('OpenLP.MainWindow', 'The Main Display has been blanked out'))

    def error_message(self, title, message):
        """
        Display an error message

        :param title: The title of the warning box.
        :param message: The message to be displayed.
        """
        if hasattr(self.application, 'splash'):
            self.application.splash.close()
        QtWidgets.QMessageBox.critical(self, title, message)

    def warning_message(self, title, message):
        """
        Display a warning message

        :param title:  The title of the warning box.
        :param message: The message to be displayed.
        """
        if hasattr(self.application, 'splash'):
            self.application.splash.close()
        QtWidgets.QMessageBox.warning(self, title, message)

    def information_message(self, title, message):
        """
        Display an informational message

        :param title: The title of the warning box.
        :param message: The message to be displayed.
        """
        if hasattr(self.application, 'splash'):
            self.application.splash.close()
        QtWidgets.QMessageBox.information(self, title, message)

    def on_help_web_site_clicked(self):
        """
        Load the OpenLP website
        """
        import webbrowser
        webbrowser.open_new('http://openlp.org/')

    def on_help_clicked(self):
        """
        If is_macosx or is_win, open the local OpenLP help file.
        Use the Online manual in other cases. (Linux)
        """
        if is_macosx() or is_win():
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(self.local_help_file)))
        else:
            import webbrowser
            webbrowser.open_new('http://manual.openlp.org/')

    def on_about_item_clicked(self):
        """
        Show the About form
        """
        self.about_form.exec()

    def on_plugin_item_clicked(self):
        """
        Show the Plugin form
        """
        self.plugin_form.load()
        self.plugin_form.exec()

    def on_tools_open_data_folder_clicked(self):
        """
        Open data folder
        """
        path = str(AppLocation.get_data_path())
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(path))

    def on_update_theme_images(self):
        """
        Updates the new theme preview images.
        """
        self.theme_manager_contents.update_preview_images()

    def on_formatting_tag_item_clicked(self):
        """
        Show the Settings dialog
        """
        self.formatting_tag_form.exec()

    def on_settings_configure_item_clicked(self):
        """
        Show the Settings dialog
        """
        self.settings_form.exec()

    def paintEvent(self, event):
        """
        We need to make sure, that the SlidePreview's size is correct.
        """
        self.preview_controller.preview_size_changed()
        self.live_controller.preview_size_changed()

    def on_settings_shortcuts_item_clicked(self):
        """
        Show the shortcuts dialog
        """
        if self.shortcut_form.exec():
            self.shortcut_form.save()

    def on_settings_import_item_clicked(self):
        """
        Import settings from an export INI file
        """
        answer = QtWidgets.QMessageBox.critical(self, translate('OpenLP.MainWindow', 'Import settings?'),
                                                translate('OpenLP.MainWindow', 'Are you sure you want to import '
                                                                               'settings?\n\n Importing settings will '
                                                                               'make permanent changes to your current '
                                                                               'OpenLP configuration.\n\n Importing '
                                                                               'incorrect settings may cause erratic '
                                                                               'behaviour or OpenLP to terminate '
                                                                               'abnormally.'),
                                                QtWidgets.QMessageBox.StandardButtons(QtWidgets.QMessageBox.Yes |
                                                                                      QtWidgets.QMessageBox.No),
                                                QtWidgets.QMessageBox.No)
        if answer == QtWidgets.QMessageBox.No:
            return
        import_file_path, filter_used = FileDialog.getOpenFileName(
            self,
            translate('OpenLP.MainWindow', 'Import settings'),
            None,
            translate('OpenLP.MainWindow', 'OpenLP Settings (*.conf)'))
        if import_file_path is None:
            return
        setting_sections = []
        # Add main sections.
        setting_sections.extend([self.general_settings_section])
        setting_sections.extend([self.advanced_settings_section])
        setting_sections.extend([self.ui_settings_section])
        setting_sections.extend([self.shortcuts_settings_section])
        setting_sections.extend([self.service_manager_settings_section])
        setting_sections.extend([self.themes_settings_section])
        setting_sections.extend([self.projector_settings_section])
        setting_sections.extend([self.players_settings_section])
        setting_sections.extend([self.display_tags_section])
        setting_sections.extend([self.header_section])
        setting_sections.extend(['crashreport'])
        # Add plugin sections.
        setting_sections.extend([plugin.name for plugin in self.plugin_manager.plugins])
        # Copy the settings file to the tmp dir, because we do not want to change the original one.
        temp_dir_path = Path(gettempdir(), 'openlp')
        create_paths(temp_dir_path)
        temp_config_path = temp_dir_path / import_file_path.name
        copyfile(import_file_path, temp_config_path)
        settings = Settings()
        import_settings = Settings(str(temp_config_path), Settings.IniFormat)

        log.info('hook upgrade_plugin_settings')
        self.plugin_manager.hook_upgrade_plugin_settings(import_settings)
        # Upgrade settings to prepare the import.
        if import_settings.can_upgrade():
            import_settings.upgrade_settings()
        # Lets do a basic sanity check. If it contains this string we can assume it was created by OpenLP and so we'll
        # load what we can from it, and just silently ignore anything we don't recognise.
        if import_settings.value('SettingsImport/type') != 'OpenLP_settings_export':
            QtWidgets.QMessageBox.critical(self, translate('OpenLP.MainWindow', 'Import settings'),
                                           translate('OpenLP.MainWindow', 'The file you have selected does not appear '
                                                                          'to be a valid OpenLP settings file.\n\n'
                                                                          'Processing has terminated and '
                                                                          'no changes have been made.'),
                                           QtWidgets.QMessageBox.StandardButtons(QtWidgets.QMessageBox.Ok))
            return
        import_keys = import_settings.allKeys()
        for section_key in import_keys:
            # We need to handle the really bad files.
            try:
                section, key = section_key.split('/')
            except ValueError:
                section = 'unknown'
                key = ''
            # Switch General back to lowercase.
            if section == 'General' or section == '%General':
                section = 'general'
                section_key = section + "/" + key
            # Make sure it's a valid section for us.
            if section not in setting_sections:
                continue
        # We have a good file, import it.
        for section_key in import_keys:
            if 'eneral' in section_key:
                section_key = section_key.lower()
            try:
                value = import_settings.value(section_key)
            except KeyError:
                value = None
                log.warning('The key "{key}" does not exist (anymore), so it will be skipped.'.format(key=section_key))
            if value is not None:
                settings.setValue('{key}'.format(key=section_key), value)
        now = datetime.now()
        settings.beginGroup(self.header_section)
        settings.setValue('file_imported', import_file_path)
        settings.setValue('file_date_imported', now.strftime("%Y-%m-%d %H:%M"))
        settings.endGroup()
        settings.sync()
        # We must do an immediate restart or current configuration will overwrite what was just imported when
        # application terminates normally.   We need to exit without saving configuration.
        QtWidgets.QMessageBox.information(self, translate('OpenLP.MainWindow', 'Import settings'),
                                          translate('OpenLP.MainWindow',
                                                    'OpenLP will now close.  Imported settings will '
                                                    'be applied the next time you start OpenLP.'))
        self.settings_imported = True
        self.clean_up()
        QtCore.QCoreApplication.exit()

    def on_settings_export_item_clicked(self):
        """
        Export settings to a .conf file in INI format
        """
        export_file_path, filter_used = FileDialog.getSaveFileName(
            self,
            translate('OpenLP.MainWindow', 'Export Settings File'),
            None,
            translate('OpenLP.MainWindow', 'OpenLP Settings (*.conf)'))
        if not export_file_path:
            return
        # Make sure it's a .conf file.
        export_file_path = export_file_path.with_suffix('.conf')
        self.save_settings()
        try:
            Settings().export(export_file_path)
        except OSError as ose:
            QtWidgets.QMessageBox.critical(self, translate('OpenLP.MainWindow', 'Export setting error'),
                                           translate('OpenLP.MainWindow',
                                                     'An error occurred while exporting the settings: {err}'
                                                     ).format(err=ose.strerror),
                                           QtWidgets.QMessageBox.StandardButtons(QtWidgets.QMessageBox.Ok))

    def on_mode_default_item_clicked(self):
        """
        Put OpenLP into "Default" view mode.
        """
        self.set_view_mode(True, True, True, True, True, True, 'default')
        Settings().setValue('user interface/is preset layout', True)
        Settings().setValue('projector/show after wizard', True)

    def on_mode_setup_item_clicked(self):
        """
        Put OpenLP into "Setup" view mode.
        """
        self.set_view_mode(True, True, False, True, False, True, 'setup')
        Settings().setValue('user interface/is preset layout', True)
        Settings().setValue('projector/show after wizard', True)

    def on_mode_live_item_clicked(self):
        """
        Put OpenLP into "Live" view mode.
        """
        self.set_view_mode(False, True, False, False, True, True, 'live')
        Settings().setValue('user interface/is preset layout', True)
        Settings().setValue('projector/show after wizard', True)

    def set_view_mode(self, media=True, service=True, theme=True, preview=True, live=True, projector=True, mode=''):
        """
        Set OpenLP to a different view mode.
        """
        if mode:
            settings = Settings()
            settings.setValue('{section}/view mode'.format(section=self.general_settings_section), mode)
        self.media_manager_dock.setVisible(media)
        self.service_manager_dock.setVisible(service)
        self.theme_manager_dock.setVisible(theme)
        self.projector_manager_dock.setVisible(projector)
        self.set_preview_panel_visibility(preview)
        self.set_live_panel_visibility(live)

    def screen_changed(self):
        """
        The screen has changed so we have to update components such as the renderer.
        """
        log.debug('screen_changed')
        self.application.set_busy_cursor()
        self.image_manager.update_display()
        self.renderer.update_display()
        self.preview_controller.screen_size_changed()
        self.live_controller.screen_size_changed()
        self.setFocus()
        self.activateWindow()
        self.application.set_normal_cursor()

    def closeEvent(self, event):
        """
        Hook to close the main window and display windows on exit
        """
        # The MainApplication did not even enter the event loop (this happens
        # when OpenLP is not fully loaded). Just ignore the event.
        if not self.application.is_event_loop_active:
            event.ignore()
            return
        # Sometimes the version thread hasn't finished, let's wait for it
        try:
            if self.version_thread and self.version_thread.isRunning():
                wait_dialog = QtWidgets.QProgressDialog('Waiting for some things to finish...', '', 0, 0, self)
                wait_dialog.setWindowModality(QtCore.Qt.WindowModal)
                wait_dialog.setAutoClose(False)
                wait_dialog.setCancelButton(None)
                wait_dialog.show()
                retry = 0
                while self.version_thread.isRunning() and retry < 50:
                    self.application.processEvents()
                    self.version_thread.wait(100)
                    retry += 1
                if self.version_thread.isRunning():
                    self.version_thread.terminate()
                wait_dialog.close()
        except RuntimeError:
            # Ignore the RuntimeError that is thrown when Qt has already deleted the C++ thread object
            pass
        # If we just did a settings import, close without saving changes.
        if self.settings_imported:
            self.clean_up(False)
            event.accept()
        if self.service_manager_contents.is_modified():
            ret = self.service_manager_contents.save_modified_service()
            if ret == QtWidgets.QMessageBox.Save:
                if self.service_manager_contents.decide_save_method():
                    self.clean_up()
                    event.accept()
                else:
                    event.ignore()
            elif ret == QtWidgets.QMessageBox.Discard:
                self.clean_up()
                event.accept()
            else:
                event.ignore()
        else:
            if Settings().value('advanced/enable exit confirmation'):
                msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Question,
                                                translate('OpenLP.MainWindow', 'Exit OpenLP'),
                                                translate('OpenLP.MainWindow', 'Are you sure you want to exit OpenLP?'),
                                                QtWidgets.QMessageBox.StandardButtons(QtWidgets.QMessageBox.Close |
                                                                                      QtWidgets.QMessageBox.Cancel),
                                                self)
                close_button = msg_box.button(QtWidgets.QMessageBox.Close)
                close_button.setText(translate('OpenLP.MainWindow', '&Exit OpenLP'))
                msg_box.setDefaultButton(QtWidgets.QMessageBox.Close)
                if msg_box.exec() == QtWidgets.QMessageBox.Close:
                    self.clean_up()
                    event.accept()
                else:
                    event.ignore()
            else:
                self.clean_up()
                event.accept()

    def clean_up(self, save_settings=True):
        """
        Runs all the cleanup code before OpenLP shuts down.

        :param save_settings: Switch to prevent saving settings. Defaults to **True**.
        """
        self.image_manager.stop_manager = True
        while self.image_manager.image_thread.isRunning():
            time.sleep(0.1)
        if save_settings:
            if Settings().value('advanced/save current plugin'):
                Settings().setValue('advanced/current media plugin', self.media_tool_box.currentIndex())
        # Call the cleanup method to shutdown plugins.
        log.info('cleanup plugins')
        self.plugin_manager.finalise_plugins()
        if save_settings:
            # Save settings
            self.save_settings()
        # Check if we need to change the data directory
        if self.new_data_path:
            self.change_data_directory()
        # Close down the display
        if self.live_controller.display:
            self.live_controller.display.close()
            self.live_controller.display = None
        # Clean temporary files used by services
        self.service_manager_contents.clean_up()
        if is_win():
            # Needed for Windows to stop crashes on exit
            Registry().remove('application')

    def set_service_modified(self, modified, file_name):
        """
        This method is called from the ServiceManager to set the title of the main window.

        :param modified: Whether or not this service has been modified.
        :param file_name: The file name of the service file.
        """
        if modified:
            title = '{title} - {name}*'.format(title=UiStrings().OpenLP, name=file_name)
        else:
            title = '{title} - {name}'.format(title=UiStrings().OpenLP, name=file_name)
        self.setWindowTitle(title)

    def show_status_message(self, message):
        """
        Show a message in the status bar
        """
        self.status_bar.showMessage(message)

    def default_theme_changed(self):
        """
        Update the default theme indicator in the status bar
        """
        theme_name = Settings().value('themes/global theme')
        self.default_theme_label.setText(translate('OpenLP.MainWindow',
                                                   'Default Theme: {theme}').format(theme=theme_name))

    def toggle_media_manager(self):
        """
        Toggle the visibility of the media manager
        """
        self.media_manager_dock.setVisible(not self.media_manager_dock.isVisible())
        Settings().setValue('user interface/is preset layout', False)

    def toggle_projector_manager(self):
        """
        Toggle visibility of the projector manager
        """
        self.projector_manager_dock.setVisible(not self.projector_manager_dock.isVisible())
        Settings().setValue('user interface/is preset layout', False)
        # Check/uncheck checkbox on First time wizard based on visibility of this panel.
        if not Settings().value('projector/show after wizard'):
            Settings().setValue('projector/show after wizard', True)
        else:
            Settings().setValue('projector/show after wizard', False)

    def toggle_service_manager(self):
        """
        Toggle the visibility of the service manager
        """
        self.service_manager_dock.setVisible(not self.service_manager_dock.isVisible())
        Settings().setValue('user interface/is preset layout', False)

    def toggle_theme_manager(self):
        """
        Toggle the visibility of the theme manager
        """
        self.theme_manager_dock.setVisible(not self.theme_manager_dock.isVisible())
        Settings().setValue('user interface/is preset layout', False)

    def set_preview_panel_visibility(self, visible):
        """
        Sets the visibility of the preview panel including saving the setting and updating the menu.

        :param visible: A bool giving the state to set the panel to
                True - Visible
                False - Hidden

        """
        self.preview_controller.panel.setVisible(visible)
        Settings().setValue('user interface/preview panel', visible)
        self.view_preview_panel.setChecked(visible)
        Settings().setValue('user interface/is preset layout', False)

    def set_lock_panel(self, lock):
        """
        Sets the ability to stop the toolbars being changed.
        """
        if lock:
            self.theme_manager_dock.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
            self.service_manager_dock.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
            self.media_manager_dock.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
            self.projector_manager_dock.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
            self.view_mode_menu.setEnabled(False)
            self.view_media_manager_item.setEnabled(False)
            self.view_service_manager_item.setEnabled(False)
            self.view_theme_manager_item.setEnabled(False)
            self.view_projector_manager_item.setEnabled(False)
            self.view_preview_panel.setEnabled(False)
            self.view_live_panel.setEnabled(False)
        else:
            self.theme_manager_dock.setFeatures(QtWidgets.QDockWidget.AllDockWidgetFeatures)
            self.service_manager_dock.setFeatures(QtWidgets.QDockWidget.AllDockWidgetFeatures)
            self.media_manager_dock.setFeatures(QtWidgets.QDockWidget.AllDockWidgetFeatures)
            self.projector_manager_dock.setFeatures(QtWidgets.QDockWidget.AllDockWidgetFeatures)
            self.view_mode_menu.setEnabled(True)
            self.view_media_manager_item.setEnabled(True)
            self.view_service_manager_item.setEnabled(True)
            self.view_theme_manager_item.setEnabled(True)
            self.view_projector_manager_item.setEnabled(True)
            self.view_preview_panel.setEnabled(True)
            self.view_live_panel.setEnabled(True)
        Settings().setValue('user interface/lock panel', lock)

    def set_live_panel_visibility(self, visible):
        """
        Sets the visibility of the live panel including saving the setting and updating the menu.


        :param visible: A bool giving the state to set the panel to
                True - Visible
                False - Hidden
        """
        self.live_controller.panel.setVisible(visible)
        Settings().setValue('user interface/live panel', visible)
        self.view_live_panel.setChecked(visible)
        Settings().setValue('user interface/is preset layout', False)

    def load_settings(self):
        """
        Load the main window settings.
        """
        log.debug('Loading QSettings')
        settings = Settings()
        # Remove obsolete entries.
        settings.remove('custom slide')
        settings.remove('service')
        settings.beginGroup(self.general_settings_section)
        self.recent_files = settings.value('recent files')
        settings.endGroup()
        settings.beginGroup(self.ui_settings_section)
        self.move(settings.value('main window position'))
        self.restoreGeometry(settings.value('main window geometry'))
        self.restoreState(settings.value('main window state'))
        self.live_controller.splitter.restoreState(settings.value('live splitter geometry'))
        self.preview_controller.splitter.restoreState(settings.value('preview splitter geometry'))
        self.control_splitter.restoreState(settings.value('main window splitter geometry'))
        # This needs to be called after restoreState(), because saveState() also saves the "Collapsible" property
        # which was True (by default) < OpenLP 2.1.
        self.control_splitter.setChildrenCollapsible(False)
        settings.endGroup()

    def save_settings(self):
        """
        Save the main window settings.
        """
        # Exit if we just did a settings import.
        if self.settings_imported:
            return
        log.debug('Saving QSettings')
        settings = Settings()
        settings.beginGroup(self.general_settings_section)
        settings.setValue('recent files', self.recent_files)
        settings.endGroup()
        settings.beginGroup(self.ui_settings_section)
        settings.setValue('main window position', self.pos())
        settings.setValue('main window state', self.saveState())
        settings.setValue('main window geometry', self.saveGeometry())
        settings.setValue('live splitter geometry', self.live_controller.splitter.saveState())
        settings.setValue('preview splitter geometry', self.preview_controller.splitter.saveState())
        settings.setValue('main window splitter geometry', self.control_splitter.saveState())
        settings.endGroup()

    def update_recent_files_menu(self):
        """
        Updates the recent file menu with the latest list of service files accessed.
        """
        recent_file_count = Settings().value('advanced/recent file count')
        self.recent_files_menu.clear()
        count = 0
        for recent_path in self.recent_files:
            if not recent_path.is_file():
                continue
            count += 1
            log.debug('Recent file name: {name}'.format(name=recent_path))
            action = create_action(self, '',
                                   text='&{n} {name}'.format(n=count, name=recent_path.name),
                                   data=recent_path, triggers=self.service_manager_contents.on_recent_service_clicked)
            self.recent_files_menu.addAction(action)
            if count == recent_file_count:
                break
        clear_recent_files_action = \
            create_action(self, '', text=translate('OpenLP.MainWindow', 'Clear List', 'Clear List of recent files'),
                          statustip=translate('OpenLP.MainWindow', 'Clear the list of recent files.'),
                          enabled=bool(self.recent_files), triggers=self.clear_recent_file_menu)
        add_actions(self.recent_files_menu, (None, clear_recent_files_action))

    def add_recent_file(self, filename):
        """
        Adds a service to the list of recently used files.

        :param filename: The service filename to add
        """
        # The max_recent_files value does not have an interface and so never gets
        # actually stored in the settings therefore the default value of 20 will
        # always be used.
        max_recent_files = Settings().value('advanced/max recent files')
        file_path = Path(filename)
        # Some cleanup to reduce duplication in the recent file list
        file_path = file_path.resolve()
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:max_recent_files]

    def clear_recent_file_menu(self):
        """
        Clears the recent files.
        """
        self.recent_files = []

    def display_progress_bar(self, size):
        """
        Make Progress bar visible and set size
        """
        self.load_progress_bar.show()
        self.load_progress_bar.setMaximum(size)
        self.load_progress_bar.setValue(0)
        self.application.process_events()

    def increment_progress_bar(self):
        """
        Increase the Progress Bar value by 1
        """
        self.load_progress_bar.setValue(self.load_progress_bar.value() + 1)
        self.application.process_events()

    def finished_progress_bar(self):
        """
        Trigger it's removal after 2.5 second
        """
        self.timer_id = self.startTimer(2500)

    def timerEvent(self, event):
        """
        Remove the Progress bar from view.
        """
        if event.timerId() == self.timer_id:
            self.timer_id = 0
            self.load_progress_bar.hide()
            # Sometimes the timer goes off as OpenLP is shutting down, and the application has already been deleted
            if self.application:
                self.application.process_events()

    def set_copy_data(self, copy_data):
        """
        Set the flag to copy the data
        """
        self.copy_data = copy_data

    def change_data_directory(self):
        """
        Change the data directory.
        """
        log.info('Changing data path to {newpath}'.format(newpath=self.new_data_path))
        old_data_path = AppLocation.get_data_path()
        # Copy OpenLP data to new location if requested.
        self.application.set_busy_cursor()
        if self.copy_data:
            log.info('Copying data to new path')
            try:
                self.show_status_message(
                    translate('OpenLP.MainWindow', 'Copying OpenLP data to new data directory location - {path} '
                              '- Please wait for copy to finish').format(path=self.new_data_path))
                dir_util.copy_tree(str(old_data_path), str(self.new_data_path))
                log.info('Copy successful')
            except (OSError, DistutilsFileError) as why:
                self.application.set_normal_cursor()
                log.exception('Data copy failed {err}'.format(err=str(why)))
                err_text = translate('OpenLP.MainWindow',
                                     'OpenLP Data directory copy failed\n\n{err}').format(err=str(why)),
                QtWidgets.QMessageBox.critical(self, translate('OpenLP.MainWindow', 'New Data Directory Error'),
                                               err_text,
                                               QtWidgets.QMessageBox.StandardButtons(QtWidgets.QMessageBox.Ok))
                return False
        else:
            log.info('No data copy requested')
        # Change the location of data directory in config file.
        settings = QtCore.QSettings()
        settings.setValue('advanced/data path', self.new_data_path)
        # Check if the new data path is our default.
        if self.new_data_path == AppLocation.get_directory(AppLocation.DataDir):
            settings.remove('advanced/data path')
        self.application.set_normal_cursor()

    def open_cmd_line_files(self, filename):
        """
        Open files passed in through command line arguments
        """
        if not isinstance(filename, str):
            filename = str(filename, sys.getfilesystemencoding())
        if filename.endswith(('.osz', '.oszl')):
            self.service_manager_contents.load_file(Path(filename))
