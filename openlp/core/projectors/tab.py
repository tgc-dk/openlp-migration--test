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
The :mod:`openlp.core.ui.projector.tab` module provides the settings tab in the settings dialog.
"""
import logging

from PyQt5 import QtWidgets

from openlp.core.common.i18n import UiStrings, translate
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.lib.settingstab import SettingsTab
from openlp.core.ui.icons import UiIcons
from openlp.core.projectors import DialogSourceStyle

log = logging.getLogger(__name__)
log.debug('projectortab module loaded')


class ProjectorTab(SettingsTab):
    """
    Openlp Settings -> Projector settings
    """
    def __init__(self, parent):
        """
        ProjectorTab initialization

        :param parent: Parent widget
        """
        self.icon_path = UiIcons().projector
        self.udp_listeners = {}  # Key on port number
        projector_translated = translate('OpenLP.ProjectorTab', 'Projector')
        super(ProjectorTab, self).__init__(parent, 'Projector', projector_translated)
        Registry().register_function('udp_broadcast_add', self.add_udp_listener)
        Registry().register_function('udp_broadcast_remove', self.remove_udp_listener)

    def setupUi(self):
        """
        Setup the UI
        """
        self.setObjectName('ProjectorTab')
        super(ProjectorTab, self).setupUi()
        self.connect_box = QtWidgets.QGroupBox(self.left_column)
        self.connect_box.setObjectName('connect_box')
        self.connect_box_layout = QtWidgets.QFormLayout(self.connect_box)
        self.connect_box_layout.setObjectName('connect_box_layout')
        # Start comms with projectors on startup
        self.connect_on_startup = QtWidgets.QCheckBox(self.connect_box)
        self.connect_on_startup.setObjectName('connect_on_startup')
        self.connect_box_layout.addRow(self.connect_on_startup)
        # Socket timeout
        self.socket_timeout_label = QtWidgets.QLabel(self.connect_box)
        self.socket_timeout_label.setObjectName('socket_timeout_label')
        self.socket_timeout_spin_box = QtWidgets.QSpinBox(self.connect_box)
        self.socket_timeout_spin_box.setObjectName('socket_timeout_spin_box')
        self.socket_timeout_spin_box.setMinimum(2)
        self.socket_timeout_spin_box.setMaximum(10)
        self.connect_box_layout.addRow(self.socket_timeout_label, self.socket_timeout_spin_box)
        # Poll interval
        self.socket_poll_label = QtWidgets.QLabel(self.connect_box)
        self.socket_poll_label.setObjectName('socket_poll_label')
        self.socket_poll_spin_box = QtWidgets.QSpinBox(self.connect_box)
        self.socket_poll_spin_box.setObjectName('socket_timeout_spin_box')
        self.socket_poll_spin_box.setMinimum(5)
        self.socket_poll_spin_box.setMaximum(60)
        self.connect_box_layout.addRow(self.socket_poll_label, self.socket_poll_spin_box)
        self.left_layout.addWidget(self.connect_box)
        # Source input select dialog box type
        self.dialog_type_label = QtWidgets.QLabel(self.connect_box)
        self.dialog_type_label.setObjectName('dialog_type_label')
        self.dialog_type_combo_box = QtWidgets.QComboBox(self.connect_box)
        self.dialog_type_combo_box.setObjectName('dialog_type_combo_box')
        self.dialog_type_combo_box.addItems(['', ''])
        self.connect_box_layout.addRow(self.dialog_type_label, self.dialog_type_combo_box)
        self.left_layout.addStretch()
        self.dialog_type_combo_box.activated.connect(self.on_dialog_type_combo_box_changed)
        # Enable/disable listening on UDP ports for PJLink2 broadcasts
        self.udp_broadcast_listen = QtWidgets.QCheckBox(self.connect_box)
        self.udp_broadcast_listen.setObjectName('udp_broadcast_listen')
        self.connect_box_layout.addRow(self.udp_broadcast_listen)
        # Connect on LKUP packet received (PJLink v2+ only)
        self.connect_on_linkup = QtWidgets.QCheckBox(self.connect_box)
        self.connect_on_linkup.setObjectName('connect_on_linkup')
        self.connect_box_layout.addRow(self.connect_on_linkup)

    def retranslateUi(self):
        """
        Translate the UI on the fly
        """
        self.tab_title_visible = UiStrings().Projectors
        self.connect_box.setTitle(
            translate('OpenLP.ProjectorTab', 'Communication Options'))
        self.connect_on_startup.setText(
            translate('OpenLP.ProjectorTab', 'Connect to projectors on startup'))
        self.socket_timeout_label.setText(
            translate('OpenLP.ProjectorTab', 'Socket timeout (seconds)'))
        self.socket_poll_label.setText(
            translate('OpenLP.ProjectorTab', 'Poll time (seconds)'))
        self.dialog_type_label.setText(
            translate('Openlp.ProjectorTab', 'Source select dialog interface'))
        self.dialog_type_combo_box.setItemText(DialogSourceStyle.Tabbed,
                                               translate('OpenLP.ProjectorTab', 'Tabbed dialog box'))
        self.dialog_type_combo_box.setItemText(DialogSourceStyle.Single,
                                               translate('OpenLP.ProjectorTab', 'Single dialog box'))
        self.connect_on_linkup.setText(
            translate('OpenLP.ProjectorTab', 'Connect to projector when LINKUP received (v2 only)'))
        self.udp_broadcast_listen.setText(
            translate('OpenLP.ProjectorTab', 'Enable listening for PJLink2 broadcast messages'))
        log.debug('PJLink settings tab initialized')

    def load(self):
        """
        Load the projector settings on startup
        """
        self.connect_on_startup.setChecked(Settings().value('projector/connect on start'))
        self.socket_timeout_spin_box.setValue(Settings().value('projector/socket timeout'))
        self.socket_poll_spin_box.setValue(Settings().value('projector/poll time'))
        self.dialog_type_combo_box.setCurrentIndex(Settings().value('projector/source dialog type'))
        self.udp_broadcast_listen.setChecked(Settings().value('projector/udp broadcast listen'))
        self.connect_on_linkup.setChecked(Settings().value('projector/connect when LKUP received'))

    def save(self):
        """
        Save the projector settings
        """
        Settings().setValue('projector/connect on start', self.connect_on_startup.isChecked())
        Settings().setValue('projector/socket timeout', self.socket_timeout_spin_box.value())
        Settings().setValue('projector/poll time', self.socket_poll_spin_box.value())
        Settings().setValue('projector/source dialog type', self.dialog_type_combo_box.currentIndex())
        Settings().setValue('projector/connect when LKUP received', self.connect_on_linkup.isChecked())
        Settings().setValue('projector/udp broadcast listen', self.udp_broadcast_listen.isChecked())
        self.call_udp_listener()

    def on_dialog_type_combo_box_changed(self):
        self.dialog_type = self.dialog_type_combo_box.currentIndex()

    def add_udp_listener(self, port, callback):
        """
        Add new UDP listener to list
        """
        if port in self.udp_listeners:
            log.warning('Port {port} already in list - not adding'.format(port=port))
            return
        self.udp_listeners[port] = callback
        log.debug('PJLinkSettings: new callback list: {port}'.format(port=self.udp_listeners.keys()))

    def remove_udp_listener(self, port):
        """
        Remove UDP listener from list
        """
        if port not in self.udp_listeners:
            log.warning('Port {port} not in list - ignoring'.format(port=port))
            return
        # Turn off listener before deleting
        self.udp_listeners[port](checked=False)
        del self.udp_listeners[port]
        log.debug('PJLinkSettings: new callback list: {port}'.format(port=self.udp_listeners.keys()))

    def call_udp_listener(self):
        """
        Call listeners to update UDP listen setting
        """
        if len(self.udp_listeners) < 1:
            log.warning('PJLinkSettings: No callers - returning')
            return
        log.debug('PJLinkSettings: Calling UDP listeners')
        for call in self.udp_listeners:
            self.udp_listeners[call](checked=self.udp_broadcast_listen.isChecked())
