# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2014 Raoul Snyman                                        #
# Portions copyright (c) 2008-2014 Tim Bentley, Gerald Britton, Jonathan      #
# Corwin, Samuel Findlay, Michael Gorven, Scott Guerrieri, Matthias Hub,      #
# Meinert Jordan, Armin Köhler, Erik Lundin, Edwin Lunando, Brian T. Meyer.   #
# Joshua Miller, Stevan Pettit, Andreas Preikschat, Mattias Põldaru,          #
# Christian Richter, Philip Ridout, Simon Scudder, Jeffrey Smith,             #
# Maikel Stuivenberg, Martin Thompson, Jon Tibble, Dave Warnock,              #
# Frode Woldsund, Martin Zibricky, Patrick Zimmermann                         #
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
This module contains tests for the PdfController
"""
import os
import shutil
from unittest import TestCase, SkipTest
from tempfile import mkstemp, mkdtemp

from PyQt4 import QtGui

from openlp.plugins.presentations.lib.pdfcontroller import PdfController, PdfDocument
from tests.functional import MagicMock
from openlp.core.common import Settings
from openlp.core.lib import ScreenList
from tests.utils.constants import TEST_RESOURCES_PATH

__default_settings__ = {
    'presentations/enable_pdf_program': False
}


class TestPdfController(TestCase):
    """
    Test the PdfController.
    """
    def setUp(self):
        """
        Set up the components need for all tests.
        """
        self.fd, self.ini_file = mkstemp('.ini')
        Settings().set_filename(self.ini_file)
        self.application = QtGui.QApplication.instance()
        ScreenList.create(self.application.desktop())
        Settings().extend_default_settings(__default_settings__)
        self.temp_folder = mkdtemp()
        self.thumbnail_folder = mkdtemp()

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.application
        try:
            os.unlink(self.ini_file)
            shutil.rmtree(self.thumbnail_folder)
            shutil.rmtree(self.temp_folder)
        except OSError:
            pass

    def constructor_test(self):
        """
        Test the Constructor from the PdfController
        """
        # GIVEN: No presentation controller
        controller = None

        # WHEN: The presentation controller object is created
        controller = PdfController(plugin=MagicMock())

        # THEN: The name of the presentation controller should be correct
        self.assertEqual('Pdf', controller.name, 'The name of the presentation controller should be correct')

    def load_pdf_test(self):
        """
        Test loading of a Pdf using the PdfController
        """
        # GIVEN: A Pdf-file
        test_file = os.path.join(TEST_RESOURCES_PATH, 'presentations', 'pdf_test1.pdf')

        # WHEN: The Pdf is loaded
        controller = PdfController(plugin=MagicMock())
        if not controller.check_available():
            raise SkipTest('Could not detect mudraw or ghostscript, so skipping PDF test')
        controller.temp_folder = self.temp_folder
        controller.thumbnail_folder = self.thumbnail_folder
        document = PdfDocument(controller, test_file)
        loaded = document.load_presentation()

        # THEN: The load should succeed and we should be able to get a pagecount
        self.assertTrue(loaded, 'The loading of the PDF should succeed.')
        self.assertEqual(3, document.get_slide_count(), 'The pagecount of the PDF should be 3.')