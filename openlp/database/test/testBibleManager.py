import random
import unittest

import os, os.path
import sys
mypath=os.path.split(os.path.abspath(__file__))[0]
sys.path.insert(0,(os.path.join(mypath, '..', '..','..')))

from openlp.database.BibleManager import *

class TestBibleManager(unittest.TestCase):
    
    def setUp(self):
        self.bm = BibleManager()

    def testGetBibles(self):
        # make sure the shuffled sequence does not lose any elements
        b = self.bm.getBibles()
        for b1 in b:
            print b1
            self.assert_(b1 in b)

    def testGetBooks(self):
        c = self.bm.getBibleBooks("NIV")
        for c1 in c:
            print c1
            self.assert_(c1 in c)
            
    def testGetBooks(self):
        self.failUnless(self.bm.getBookVerseCount("NIV", "GEN", 1) == 28, "Wrong Book Count")

    def testGetVerseText(self):
        c = self.bm.getVerseText("NIV","GEN",1,2,1)
        for c1 in c:
            print c1 
            self.assert_(c1 in c)
            
if __name__ == '__main__':
    unittest.main()
