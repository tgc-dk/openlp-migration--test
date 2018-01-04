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
    Package to test the openlp.core.widgets.views.
"""
from unittest import TestCase
from unittest.mock import MagicMock, patch

from PyQt5 import QtGui, QtWidgets

from openlp.core.common.registry import Registry
from openlp.core.lib import ServiceItem
from openlp.core.widgets.views import ListPreviewWidget
from tests.helpers.testmixin import TestMixin
from tests.utils.osdinteraction import read_service_from_file


class TestListPreviewWidget(TestCase, TestMixin):

    def setUp(self):
        """
        Create the UI.
        """
        Registry.create()
        self.setup_application()
        self.main_window = QtWidgets.QMainWindow()
        self.image = QtGui.QImage(1, 1, QtGui.QImage.Format_RGB32)
        self.image_manager = MagicMock()
        self.image_manager.get_image.return_value = self.image
        Registry().register('image_manager', self.image_manager)
        self.preview_widget = ListPreviewWidget(self.main_window, 2)

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault.
        """
        del self.preview_widget
        del self.main_window

    def test_initial_slide_count(self):
        """
        Test the initial slide count .
        """
        # GIVEN: A new ListPreviewWidget instance.
        # WHEN: No SlideItem has been added yet.
        # THEN: The count of items should be zero.
        assert self.preview_widget.slide_count() == 0, 'The slide list should be empty.'

    def test_initial_slide_number(self):
        """
        Test the initial current slide number.
        """
        # GIVEN: A new ListPreviewWidget instance.
        # WHEN: No SlideItem has been added yet.
        # THEN: The number of the current item should be -1.
        assert self.preview_widget.current_slide_number() == -1, 'The slide number should be -1.'

    def test_replace_service_item(self):
        """
        Test item counts and current number with a service item.
        """
        # GIVEN: A ServiceItem with two frames.
        service_item = ServiceItem(None)
        service = read_service_from_file('serviceitem_image_3.osj')
        with patch('os.path.exists'):
            service_item.set_from_service(service[0])
        # WHEN: Added to the preview widget.
        self.preview_widget.replace_service_item(service_item, 1, 1)
        # THEN: The slide count and number should fit.
        assert self.preview_widget.slide_count() == 2, 'The slide count should be 2.'
        assert self.preview_widget.current_slide_number() == 1, 'The current slide number should  be 1.'

    def test_change_slide(self):
        """
        Test the change_slide method.
        """
        # GIVEN: A ServiceItem with two frames content.
        service_item = ServiceItem(None)
        service = read_service_from_file('serviceitem_image_3.osj')
        with patch('os.path.exists'):
            service_item.set_from_service(service[0])
        # WHEN: Added to the preview widget and switched to the second frame.
        self.preview_widget.replace_service_item(service_item, 1, 0)
        self.preview_widget.change_slide(1)
        # THEN: The current_slide_number should reflect the change.
        assert self.preview_widget.current_slide_number() == 1, 'The current slide number should  be 1.'
