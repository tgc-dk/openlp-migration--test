# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2010 Raoul Snyman                                        #
# Portions copyright (c) 2008-2010 Tim Bentley, Jonathan Corwin, Michael      #
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

import logging

from PyQt4 import QtCore

from openlp.core.lib import Renderer, ThemeLevel, ServiceItem
from openlp.core.ui import MainDisplay

log = logging.getLogger(__name__)

class RenderManager(object):
    """
    Class to pull all Renderer interactions into one place. The plugins will
    call helper methods to do the rendering but this class will provide
    display defense code.

    ``theme_manager``
        The ThemeManager instance, used to get the current theme details.

    ``screens``
        Contains information about the Screens.

    ``screen_number``
        Defaults to *0*. The index of the output/display screen.
    """
    log.info(u'RenderManager Loaded')

    def __init__(self, theme_manager, screens):
        """
        Initialise the render manager.
        """
        log.debug(u'Initilisation started')
        self.screens = screens
        self.display = MainDisplay(self, screens, False)
        self.display.setup()
        self.theme_manager = theme_manager
        self.renderer = Renderer()
        self.calculate_default(self.screens.current[u'size'])
        self.theme = u''
        self.service_theme = u''
        self.theme_level = u''
        self.override_background = None
        self.themedata = None
        self.alertTab = None

        # TODO make external and configurable in alpha 4
        self.html_expands = []

        self.html_expands.append({u'desc':u'Red', u'start tag':u'{r}', \
                                  u'start html':u'<font color=red>', \
                                  u'end tag':u'{/r}', u'end html':u'</font>', \
                                  u'protected':False})
        self.html_expands.append({u'desc':u'Black', u'start tag':u'{b}', \
                                  u'start html':u'<font color=black>', \
                                  u'end tag':u'{/b}', u'end html':u'</font>', \
                                  u'protected':False})
        self.html_expands.append({u'desc':u'Blue', u'start tag':u'{bl}', \
                                  u'start html':u'<font color=blue>', \
                                  u'end tag':u'{/bl}', u'end html':u'</font>', \
                                  u'protected':False})
        self.html_expands.append({u'desc':u'Yellow', u'start tag':u'{y}', \
                                  u'start html':u'<font color=yellow>', \
                                  u'end tag':u'{/y}', u'end html':u'</font>', \
                                  u'protected':False})
        self.html_expands.append({u'desc':u'Green', u'start tag':u'{g}', \
                                  u'start html':u'<font color=green>', \
                                  u'end tag':u'{/g}', u'end html':u'</font>', \
                                  u'protected':False})
        self.html_expands.append({u'desc':u'Pink', u'start tag':u'{pk}', \
                                  u'start html':u'<font color=#CC33CC>', \
                                  u'end tag':u'{/pk}', u'end html':u'</font>', \
                                  u'protected':False})
        self.html_expands.append({u'desc':u'Orange', u'start tag':u'{o}', \
                                  u'start html':u'<font color=#CC0033>', \
                                  u'end tag':u'{/o}', u'end html':u'</font>', \
                                  u'protected':False})
        self.html_expands.append({u'desc':u'Purple', u'start tag':u'{pp}', \
                                  u'start html':u'<font color=#9900FF>', \
                                  u'end tag':u'{/pp}', u'end html':u'</font>', \
                                  u'protected':False})
        self.html_expands.append({u'desc':u'White', u'start tag':u'{w}', \
                                  u'start html':u'<font color=white>', \
                                  u'end tag':u'{/w}', u'end html':u'</font>', \
                                  u'protected':False})
        self.html_expands.append({u'desc':u'Superscript', u'start tag':u'{su}', \
                                  u'start html':u'<sup>', \
                                  u'end tag':u'{/su}', u'end html':u'</sup>', \
                                  u'protected':True})
        self.html_expands.append({u'desc':u'Subscript', u'start tag':u'{sb}', \
                                  u'start html':u'<sub>', \
                                  u'end tag':u'{/sb}', u'end html':u'</sub>', \
                                  u'protected':True})
        self.html_expands.append({u'desc':u'Paragraph', u'start tag':u'{p}', \
                                  u'start html':u'<p>', \
                                  u'end tag':u'{/p}', u'end html':u'</p>', \
                                  u'protected':True})
        self.html_expands.append({u'desc':u'Bold', u'start tag':u'{st}', \
                                  u'start html':u'<strong>', \
                                  u'end tag':u'{/st}', \
                                  u'end html':u'</strong>', \
                                  u'protected':True})
        self.html_expands.append({u'desc':u'Italics', u'start tag':u'{it}', \
                                  u'start html':u'<em>', \
                                  u'end tag':u'{/it}', u'end html':u'</em>', \
                                  u'protected':True})

    def update_display(self):
        """
        Updates the render manager's information about the current screen.
        """
        log.debug(u'Update Display')
        self.calculate_default(self.screens.current[u'size'])
        self.display = MainDisplay(self, self.screens, False)
        self.display.setup()
        self.renderer.bg_frame = None

    def set_global_theme(self, global_theme, theme_level=ThemeLevel.Global):
        """
        Set the global-level theme and the theme level.

        ``global_theme``
            The global-level theme to be set.

        ``theme_level``
            Defaults to *``ThemeLevel.Global``*. The theme level, can be
            ``ThemeLevel.Global``, ``ThemeLevel.Service`` or
            ``ThemeLevel.Song``.
        """
        self.global_theme = global_theme
        self.theme_level = theme_level

    def set_service_theme(self, service_theme):
        """
        Set the service-level theme.

        ``service_theme``
            The service-level theme to be set.
        """
        self.service_theme = service_theme

    def set_override_theme(self, theme, overrideLevels=False):
        """
        Set the appropriate theme depending on the theme level.
        Called by the service item when building a display frame

        ``theme``
            The name of the song-level theme. None means the service
            item wants to use the given value.
        """
        log.debug(u'set override theme to %s', theme)
        theme_level = self.theme_level
        if overrideLevels:
            theme_level = ThemeLevel.Song
        if theme_level == ThemeLevel.Global:
            self.theme = self.global_theme
        elif theme_level == ThemeLevel.Service:
            if self.service_theme == u'':
                self.theme = self.global_theme
            else:
                self.theme = self.service_theme
        else:
            if theme:
                self.theme = theme
            elif theme_level == ThemeLevel.Song or \
                theme_level == ThemeLevel.Service:
                if self.service_theme == u'':
                    self.theme = self.global_theme
                else:
                    self.theme = self.service_theme
            else:
                self.theme = self.global_theme
        if self.theme != self.renderer.theme_name or self.themedata is None \
            or overrideLevels:
            log.debug(u'theme is now %s', self.theme)
            if overrideLevels:
                self.themedata = theme
            else:
                self.themedata = self.theme_manager.getThemeData(self.theme)
            self.calculate_default(self.screens.current[u'size'])
            self.renderer.set_theme(self.themedata)
            self.build_text_rectangle(self.themedata)
            self.renderer.set_frame_dest(self.width, self.height)
        return self.renderer._rect, self.renderer._rect_footer

    def build_text_rectangle(self, theme):
        """
        Builds a text block using the settings in ``theme``
        and the size of the display screen.height.

        ``theme``
            The theme to build a text block for.
        """
        log.debug(u'build_text_rectangle')
        main_rect = None
        footer_rect = None
        if not theme.font_main_override:
            main_rect = QtCore.QRect(10, 0,
                            self.width - 20, self.footer_start)
        else:
            main_rect = QtCore.QRect(theme.font_main_x, theme.font_main_y,
                theme.font_main_width - 1, theme.font_main_height - 1)
        if not theme.font_footer_override:
            footer_rect = QtCore.QRect(10, self.footer_start,
                            self.width - 20, self.height - self.footer_start)
        else:
            footer_rect = QtCore.QRect(theme.font_footer_x,
                theme.font_footer_y, theme.font_footer_width - 1,
                theme.font_footer_height - 1)
        self.renderer.set_text_rectangle(main_rect, footer_rect)

    def generate_preview(self, themedata):
        """
        Generate a preview of a theme.

        ``themedata``
            The theme to generated a preview for.
        """
        log.debug(u'generate preview')
        # set the default image size for previews
        self.calculate_default(self.screens.preview[u'size'])
        verse = u'Amazing Grace!\n'\
        'How sweet the sound\n'\
        'To save a wretch like me;\n'\
        'I once was lost but now am found,\n'\
        'Was blind, but now I see.'
        footer = []
        footer.append(u'Amazing Grace (John Newton)' )
        footer.append(u'Public Domain')
        footer.append(u'CCLI 123456')
        # Previews do not need the transition switched on!
        themedata.display_slideTransition = False
        # build a service item to generate preview
        serviceItem = ServiceItem()
        serviceItem.theme = themedata
        serviceItem.add_from_text(u'', verse, footer)
        serviceItem.render_manager = self
        serviceItem.raw_footer = footer
        serviceItem.render(True)
        self.display.buildHtml(serviceItem)
        frame, raw_html = serviceItem.get_rendered_frame(0)
        preview = self.display.text(raw_html)
        # Reset the real screen size for subsequent render requests
        self.calculate_default(self.screens.current[u'size'])
        return preview

    def format_slide(self, words, line_break):
        """
        Calculate how much text can fit on a slide.

        ``words``
            The words to go on the slides.
        """
        log.debug(u'format slide')
        self.build_text_rectangle(self.themedata)
        return self.renderer.format_slide(words, line_break)

    def calculate_default(self, screen):
        """
        Calculate the default dimentions of the screen.

        ``screen``
            The QSize of the screen.
        """
        log.debug(u'calculate default %s', screen)
        self.width = screen.width()
        self.height = screen.height()
        self.screen_ratio = float(self.height) / float(self.width)
        log.debug(u'calculate default %d, %d, %f',
            self.width, self.height, self.screen_ratio )
        # 90% is start of footer
        self.footer_start = int(self.height * 0.90)

    def clean(self, text):
        """
        Remove Tags from text for display
        """
        text = text.replace(u'<br>', u'\n')
        for tag in self.html_expands:
            text = text.replace(tag[u'start tag'], u'')
            text = text.replace(tag[u'end tag'], u'')
        return text

    def expand(self, text):
        """
        Expand tags HTML for display
        """
        for tag in self.html_expands:
            text = text.replace(tag[u'start tag'], tag[u'start html'])
            text = text.replace(tag[u'end tag'], tag[u'end html'])
        return text
