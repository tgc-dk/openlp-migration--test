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

import logging
from lxml import etree, objectify

from openlp.core.common import translate
from openlp.core.lib.ui import critical_error_message_box
from openlp.plugins.bibles.lib.db import BibleDB, BiblesResourcesDB


log = logging.getLogger(__name__)


class ZefaniaBible(BibleDB):
    """
    Zefania Bible format importer class.
    """
    def __init__(self, parent, **kwargs):
        """
        Constructor to create and set up an instance of the ZefaniaBible class. This class is used to import Bibles
        from ZefaniaBible's XML format.
        """
        log.debug(self.__class__.__name__)
        BibleDB.__init__(self, parent, **kwargs)
        self.filename = kwargs['filename']

    def do_import(self, bible_name=None):
        """
        Loads a Bible from file.
        """
        log.debug('Starting Zefania import from "%s"' % self.filename)
        if not isinstance(self.filename, str):
            self.filename = str(self.filename, 'utf8')
        import_file = None
        success = True
        try:
            # NOTE: We don't need to do any of the normal encoding detection here, because lxml does it's own encoding
            # detection, and the two mechanisms together interfere with each other.
            import_file = open(self.filename, 'rb')
            zefania_bible_tree = etree.parse(import_file)
            # Find bible language
            language_id = None
            language = zefania_bible_tree.xpath("/XMLBIBLE/INFORMATION/language/text()")
            if language:
                language_id = BiblesResourcesDB.get_language(language[0])
            # The language couldn't be detected, ask the user
            if not language_id:
                language_id = self.get_language(bible_name)
            if not language_id:
                log.error('Importing books from "%s" failed' % self.filename)
                return False
            num_books = int(zefania_bible_tree.xpath("count(//BIBLEBOOK)"))
            # Strip tags we don't use - keep content
            etree.strip_tags(zefania_bible_tree, ('STYLE', 'GRAM', 'NOTE', 'SUP', 'XREF'))
            # Strip tags we don't use - remove content
            etree.strip_elements(zefania_bible_tree, ('PROLOG', 'REMARK', 'CAPTION', 'MEDIA'), with_tail=False)
            xmlbible = zefania_bible_tree.getroot()
            for BIBLEBOOK in xmlbible:
                book_ref_id = self.get_book_ref_id_by_name(str(BIBLEBOOK.get('bname')), num_books)
                if not book_ref_id:
                    book_ref_id = self.get_book_ref_id_by_localised_name(str(BIBLEBOOK.get('bname')))
                if not book_ref_id:
                    log.error('Importing books from "%s" failed' % self.filename)
                    return False
                book_details = BiblesResourcesDB.get_book_by_id(book_ref_id)
                db_book = self.create_book(book_details['name'], book_ref_id, book_details['testament_id'])
                for CHAPTER in BIBLEBOOK:
                    if self.stop_import_flag:
                        break
                    chapter_number = CHAPTER.get("cnumber")
                    for VERS in CHAPTER:
                        verse_number = VERS.get("vnumber")
                        self.create_verse(db_book.id, chapter_number, verse_number, VERS.text.replace('<BR/>', '\n'))
                    self.wizard.increment_progress_bar(
                        translate('BiblesPlugin.Zefnia', 'Importing %(bookname)s %(chapter)s...' %
                                  {'bookname': db_book.name, 'chapter': chapter_number}))
                self.session.commit()
            self.application.process_events()
        except Exception as e:
            critical_error_message_box(
                message=translate('BiblesPlugin.ZefaniaImport',
                                  'Incorrect Bible file type supplied. Zefania Bibles may be '
                                  'compressed. You must decompress them before import.'))
            log.exception(str(e))
            success = False
        finally:
            if import_file:
                import_file.close()
        if self.stop_import_flag:
            return False
        else:
            return success