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

import logging

from PyQt5 import QtCore, QtWidgets

from openlp.core.common.settings import Settings
from openlp.core.lib import build_icon
from openlp.core.lib.ui import create_widget_action

log = logging.getLogger(__name__)


class SearchEdit(QtWidgets.QLineEdit):
    """
    This is a specialised QLineEdit with a "clear" button inside for searches.
    """
    searchTypeChanged = QtCore.pyqtSignal(QtCore.QVariant)
    cleared = QtCore.pyqtSignal()

    def __init__(self, parent, settings_section):
        """
        Constructor.
        """
        super().__init__(parent)
        self.settings_section = settings_section
        self._current_search_type = -1
        self.clear_button = QtWidgets.QToolButton(self)
        self.clear_button.setIcon(build_icon(':/system/clear_shortcut.png'))
        self.clear_button.setCursor(QtCore.Qt.ArrowCursor)
        self.clear_button.setStyleSheet('QToolButton { border: none; padding: 0px; }')
        self.clear_button.resize(18, 18)
        self.clear_button.hide()
        self.clear_button.clicked.connect(self._on_clear_button_clicked)
        self.textChanged.connect(self._on_search_edit_text_changed)
        self._update_style_sheet()
        self.setAcceptDrops(False)

    def _update_style_sheet(self):
        """
        Internal method to update the stylesheet depending on which widgets are available and visible.
        """
        frame_width = self.style().pixelMetric(QtWidgets.QStyle.PM_DefaultFrameWidth)
        right_padding = self.clear_button.width() + frame_width
        if hasattr(self, 'menu_button'):
            left_padding = self.menu_button.width()
            stylesheet = 'QLineEdit {{ padding-left:{left}px; padding-right: {right}px; }} '.format(left=left_padding,
                                                                                                    right=right_padding)
        else:
            stylesheet = 'QLineEdit {{ padding-right: {right}px; }} '.format(right=right_padding)
        self.setStyleSheet(stylesheet)
        msz = self.minimumSizeHint()
        self.setMinimumSize(max(msz.width(), self.clear_button.width() + (frame_width * 2) + 2),
                            max(msz.height(), self.clear_button.height() + (frame_width * 2) + 2))

    def resizeEvent(self, event):
        """
        Reimplemented method to react to resizing of the widget.

        :param event: The event that happened.
        """
        size = self.clear_button.size()
        frame_width = self.style().pixelMetric(QtWidgets.QStyle.PM_DefaultFrameWidth)
        self.clear_button.move(self.rect().right() - frame_width - size.width(),
                               (self.rect().bottom() + 1 - size.height()) // 2)
        if hasattr(self, 'menu_button'):
            size = self.menu_button.size()
            self.menu_button.move(self.rect().left() + frame_width + 2, (self.rect().bottom() + 1 - size.height()) // 2)

    def current_search_type(self):
        """
        Readonly property to return the current search type.
        """
        return self._current_search_type

    def set_current_search_type(self, identifier):
        """
        Set a new current search type.

        :param identifier: The search type identifier (int).
        """
        menu = self.menu_button.menu()
        for action in menu.actions():
            if identifier == action.data():
                self.setPlaceholderText(action.placeholder_text)
                self.menu_button.setDefaultAction(action)
                self._current_search_type = identifier
                Settings().setValue('{section}/last used search type'.format(section=self.settings_section), identifier)
                self.searchTypeChanged.emit(identifier)
                return True

    def set_search_types(self, items):
        """
        A list of tuples to be used in the search type menu. The first item in the list will be preselected as the
        default.

         :param items:     The list of tuples to use. The tuples should contain an integer identifier, an icon (QIcon
             instance or string) and a title for the item in the menu. In short, they should look like this::

                    (<identifier>, <icon>, <title>, <place holder text>)

                For instance::

                    (1, <QIcon instance>, "Titles", "Search Song Titles...")

                Or::

                    (2, ":/songs/authors.png", "Authors", "Search Authors...")
        """
        menu = QtWidgets.QMenu(self)
        for identifier, icon, title, placeholder in items:
            action = create_widget_action(
                menu, text=title, icon=icon, data=identifier, triggers=self._on_menu_action_triggered)
            action.placeholder_text = placeholder
        if not hasattr(self, 'menu_button'):
            self.menu_button = QtWidgets.QToolButton(self)
            self.menu_button.setIcon(build_icon(':/system/clear_shortcut.png'))
            self.menu_button.setCursor(QtCore.Qt.ArrowCursor)
            self.menu_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
            self.menu_button.setStyleSheet('QToolButton { border: none; padding: 0px 10px 0px 0px; }')
            self.menu_button.resize(QtCore.QSize(28, 18))
        self.menu_button.setMenu(menu)
        self.set_current_search_type(
            Settings().value('{section}/last used search type'.format(section=self.settings_section)))
        self.menu_button.show()
        self._update_style_sheet()

    def _on_search_edit_text_changed(self, text):
        """
        Internally implemented slot to react to when the text in the line edit has changed so that we can show or hide
        the clear button.

        :param text: A :class:`~PyQt5.QtCore.QString` instance which represents the text in the line edit.
        """
        self.clear_button.setVisible(bool(text))

    def _on_clear_button_clicked(self):
        """
        Internally implemented slot to react to the clear button being clicked to clear the line edit. Once it has
        cleared the line edit, it emits the ``cleared()`` signal so that an application can react to the clearing of the
        line edit.
        """
        self.clear()
        self.cleared.emit()

    def _on_menu_action_triggered(self):
        """
        Internally implemented slot to react to the select of one of the search types in the menu. Once it has set the
        correct action on the button, and set the current search type (using the list of identifiers provided by the
        developer), the ``searchTypeChanged(int)`` signal is emitted with the identifier.
        """
        for action in self.menu_button.menu().actions():
            # Why is this needed?
            action.setChecked(False)
        self.set_current_search_type(self.sender().data())
