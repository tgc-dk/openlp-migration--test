"""
OpenLP - Open Source Lyrics Projection
Copyright (c) 2008 Raoul Snyman
Portions copyright (c) 2008 Martin Thompson, Tim Bentley

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 59 Temple
Place, Suite 330, Boston, MA 02111-1307 USA
"""

import time
import sys
import os, os.path
from PyQt4 import QtGui, QtCore

mypath=os.path.split(os.path.abspath(__file__))[0]
sys.path.insert(0,(os.path.join(mypath, '..','..', '..','..')))
from openlp.core.ui import ServiceManager
from openlp.plugins.images import ImageServiceItem

import logging
logging.basicConfig(filename="test_service_manager.log",level=logging.INFO, filemode="w")

# # from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66062
# def whoami(depth=1):
#     return sys._getframe(depth).f_code.co_name
global app
global log
log=logging.getLogger("TestServiceManager")
class TestServiceManager_base:
    def __init__(self):
        pass
#         if not os.path.exists("test_results"):
#             os.mkdir("test_results")


    def setup_class(self):
        log.info( "class setup"+str(self))
        try:
            if app is None:
                app = QtGui.QApplication([])
        except UnboundLocalError:
            app = QtGui.QApplication([])
            

    def teardown_class(self):
        pass

    def setup_method(self, method):
        log.info("Setup method:"+str(method))
        self.expected_answer="Don't know yet"
        self.answer=None
        self.s=ServiceManager(None)
        log.info("--------------- Setup Done -------------")

    def teardown_method(self, method):
        self.s=None

    def test_easy(self):
        log.info("test_easy")
        item=ImageServiceItem(None)
        item.add("test.gif")
        self.s.addServiceItem(item)
        answer = self.s.oos_as_text()
        log.info("Answer = " + str(answer))
        lines=answer.split("\n")
        log.info("lines = " + str(lines))
        assert lines[0].startswith("# <openlp.plugins.images.imageserviceitem.ImageServiceItem object")
        assert lines[1] == "test.gif"
        log.info("done")
        
    def test_2items_as_separate_items(self):
        # If nothing is selected when item is added, a new base service item is added
        log.info("test_2items_as_separate_items")
        item=ImageServiceItem(None)
        item.add("test.gif")
        self.s.addServiceItem(item)
        item=ImageServiceItem(None)
        item.add("test2.gif")
        item.add("test3.gif")
        self.s.addServiceItem(item)
        answer = self.s.oos_as_text()
        log.info("Answer = " + str(answer))
        lines=answer.split("\n")
        log.info("lines = " + str(lines))
        assert lines[0].startswith("# <openlp.plugins.images.imageserviceitem.ImageServiceItem object")
        assert lines[1] == "test.gif"
        assert lines[2].startswith("# <openlp.plugins.images.imageserviceitem.ImageServiceItem object")
        assert lines[3] == "test2.gif"
        assert lines[4] == "test3.gif"
        log.info("done")
        
    def test_2items_merged(self):
        # If the first object is selected when item is added it should be extended
        log.info("test_2items_merged")
        item=ImageServiceItem(None)
        item.add("test.gif")
        # now select the line
        self.s.addServiceItem(item)
        item=ImageServiceItem(None)
        item.add("test2.gif")
        item.add("test3.gif")
        self.s.addServiceItem(item)
        answer = self.s.oos_as_text()
        log.info("Answer = " + str(answer))
        lines=answer.split("\n")
        log.info("lines = " + str(lines))
        assert lines[0].startswith("# <openlp.plugins.images.imageserviceitem.ImageServiceItem object")
        assert lines[1] == "test.gif"
        assert lines[2] == "test2.gif"
        assert lines[3] == "test3.gif"
        log.info("done")
        
#     def test_moving_selection(self):
#         log.info("test_easy")
#         item=ImageServiceItem(None)
#         item.add("test1.gif")
#         item.add("test2.gif")
#         item.add("test3.gif")
#         item.add("test2a.gif")
#         self.s.addServiceItem(item)
#         answer = self.s.oos_as_text()
#         log.info("Answer = " + str(answer))
#         lines=answer.split("\n")
#         log.info("lines = " + str(lines))
#         assert lines[0].startswith("# <openlp.plugins.images.imageserviceitem.ImageServiceItem object")
#         assert lines[1] == "test1.gif"
#         assert lines[2] == "test2.gif"
#         assert lines[3] == "test2a.gif"
#         assert lines[4] == "test3.gif"
#         log.info("done")
        
if __name__=="__main__":

    t=TestServiceManager_base()
    t.setup_class()
    t.setup_method(None)
    t.test_easy()
    t.teardown_method(None)
    print "Pass"
    log.info("Pass")
