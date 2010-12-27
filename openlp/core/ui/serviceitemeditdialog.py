# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2011 Raoul Snyman                                        #
# Portions copyright (c) 2008-2011 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Meinert Jordan, Andreas Preikschat, Christian      #
# Richter, Philip Ridout, Maikel Stuivenberg, Martin Thompson, Jon Tibble,    #
# Carsten Tinggaard, Frode Woldsund                                           #
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

from PyQt4 import QtCore, QtGui

from openlp.core.lib import translate

class Ui_ServiceItemEditDialog(object):
    def setupUi(self, serviceItemEditDialog):
        serviceItemEditDialog.setObjectName(u'serviceItemEditDialog')
        serviceItemEditDialog.resize(386, 272)
        self.layoutWidget = QtGui.QWidget(serviceItemEditDialog)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 20, 351, 241))
        self.layoutWidget.setObjectName(u'layoutWidget')
        self.outerLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.outerLayout.setObjectName(u'outerLayout')
        self.topLayout = QtGui.QHBoxLayout()
        self.topLayout.setObjectName(u'topLayout')
        self.listWidget = QtGui.QListWidget(self.layoutWidget)
        self.listWidget.setAlternatingRowColors(True)
        self.listWidget.setObjectName(u'listWidget')
        self.topLayout.addWidget(self.listWidget)
        self.buttonLayout = QtGui.QVBoxLayout()
        self.buttonLayout.setObjectName(u'buttonLayout')
        self.deleteButton = QtGui.QPushButton(self.layoutWidget)
        self.deleteButton.setObjectName(u'deleteButton')
        self.buttonLayout.addWidget(self.deleteButton)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.buttonLayout.addItem(spacerItem)
        self.upButton = QtGui.QPushButton(self.layoutWidget)
        self.upButton.setText(u'')
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(u':/services/service_up.png'),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.upButton.setIcon(icon)
        self.upButton.setObjectName(u'upButton')
        self.buttonLayout.addWidget(self.upButton)
        self.downButton = QtGui.QPushButton(self.layoutWidget)
        self.downButton.setText(u'')
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(u':/services/service_down.png'),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.downButton.setIcon(icon)
        self.downButton.setObjectName(u'downButton')
        self.buttonLayout.addWidget(self.downButton)
        self.topLayout.addLayout(self.buttonLayout)
        self.outerLayout.addLayout(self.topLayout)
        self.buttonBox = QtGui.QDialogButtonBox(self.layoutWidget)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel |
            QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(u'buttonBox')
        self.outerLayout.addWidget(self.buttonBox)

        self.retranslateUi(serviceItemEditDialog)
        QtCore.QMetaObject.connectSlotsByName(serviceItemEditDialog)

    def retranslateUi(self, serviceItemEditDialog):
        serviceItemEditDialog.setWindowTitle(
            translate('OpenLP.ServiceItemEditForm', 'Reorder Service Item'))
        self.deleteButton.setText(translate('OpenLP.ServiceItemEditForm',
            'Delete'))