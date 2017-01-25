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
This module is responsible for generating the HTML for :class:`~openlp.core.ui.maindisplay`. The ``build_html`` function
is the function which has to be called from outside. The generated and returned HTML will look similar to this::

        <!DOCTYPE html>
        <html>
        <head>
        <title>OpenLP Display</title>
        <style>
        *{
            margin: 0;
            padding: 0;
            border: 0;
            overflow: hidden;
            -webkit-user-select: none;
        }
        body {
            background-color: #000000;
        }
        .size {
            position: absolute;
            left: 0px;
            top: 0px;
            width: 100%;
            height: 100%;
        }
        #black {
            z-index: 8;
            background-color: black;
            display: none;
        }
        #bgimage {
            z-index: 1;
        }
        #image {
            z-index: 2;
        }

        #videobackboard {
            z-index:3;
            background-color: #000000;
        }
        #video {
            background-color: #000000;
            z-index:4;
        }

        #flash {
            z-index:5;
        }

            #alert {
                position: absolute;
                left: 0px;
                top: 0px;
                z-index: 10;
                width: 100%;
                vertical-align: bottom;
                font-family: DejaVu Sans;
                font-size: 40pt;
                color: #ffffff;
                background-color: #660000;
                word-wrap: break-word;
            }

        #footer {
            position: absolute;
            z-index: 6;

            left: 10px;
            bottom: 0px;
            width: 1580px;
            font-family: Nimbus Sans L;
            font-size: 12pt;
            color: #FFFFFF;
            text-align: left;
            white-space: nowrap;

        }
        /* lyric css */

        .lyricstable {
            z-index: 5;
            position: absolute;
            display: table;
            left: 10px; top: 0px;
        }
        .lyricscell {
            display: table-cell;
            word-wrap: break-word;
            -webkit-transition: opacity 0.4s ease;
            white-space:pre-wrap; word-wrap: break-word; text-align: left; vertical-align: top; font-family: Nimbus
            Sans L; font-size: 40pt; color: #FFFFFF; line-height: 100%; margin: 0;padding: 0; padding-bottom: 0;
            padding-left: 4px; width: 1580px; height: 810px;
        }
        .lyricsmain {
             -webkit-text-stroke: 0.125em #000000; -webkit-text-fill-color: #FFFFFF;  text-shadow: #000000 5px 5px;
        }

        sup {
            font-size: 0.6em;
            vertical-align: top;
            position: relative;
            top: -0.3em;
        }
        /* Chords css */
        .chordline {
          line-height: 1.0em;
        }
        .chordline span.chord span {
          position: relative;
        }
        .chordline span.chord span strong {
          position: absolute;
          top: -0.8em;
          left: 0;
          font-size: 75%;
          font-weight: normal;
          line-height: normal;
          display: none;
        }
        .firstchordline {
            line-height: 1.0em;
        }
        </style>
        <script>
            var timer = null;
            var transition = false;

            function show_video(state, path, volume, loop, variable_value){
                // Sometimes  video.currentTime stops slightly short of video.duration and video.ended is intermittent!

                var video = document.getElementById('video');
                if(volume != null){
                    video.volume = volume;
                }
                switch(state){
                    case 'load':
                        video.src = 'file:///' + path;
                        if(loop == true) {
                            video.loop = true;
                        }
                        video.load();
                        break;
                    case 'play':
                        video.play();
                        break;
                    case 'pause':
                        video.pause();
                        break;
                    case 'stop':
                        show_video('pause');
                        video.currentTime = 0;
                        break;
                    case 'close':
                        show_video('stop');
                        video.src = '';
                        break;
                    case 'length':
                        return video.duration;
                    case 'current_time':
                        return video.currentTime;
                    case 'seek':
                        video.currentTime = variable_value;
                        break;
                    case 'isEnded':
                        return video.ended;
                    case 'setVisible':
                        video.style.visibility = variable_value;
                        break;
                    case 'setBackBoard':
                        var back = document.getElementById('videobackboard');
                        back.style.visibility = variable_value;
                        break;
               }
            }

            function getFlashMovieObject(movieName)
            {
                if (window.document[movieName]){
                    return window.document[movieName];
                }
                if (document.embeds && document.embeds[movieName]){
                    return document.embeds[movieName];
                }
            }

            function show_flash(state, path, volume, variable_value){
                var text = document.getElementById('flash');
                var flashMovie = getFlashMovieObject("OpenLPFlashMovie");
                var src = "src = 'file:///" + path + "'";
                var view_parm = " wmode='opaque'" + " width='100%%'" + " height='100%%'";
                var swf_parm = " name='OpenLPFlashMovie'" + " autostart='true' loop='false' play='true'" +
                    " hidden='false' swliveconnect='true' allowscriptaccess='always'" + " volume='" + volume + "'";

                switch(state){
                    case 'load':
                        text.innerHTML = "<embed " + src + view_parm + swf_parm + "/>";
                        flashMovie = getFlashMovieObject("OpenLPFlashMovie");
                        flashMovie.Play();
                        break;
                    case 'play':
                        flashMovie.Play();
                        break;
                    case 'pause':
                        flashMovie.StopPlay();
                        break;
                    case 'stop':
                        flashMovie.StopPlay();
                        tempHtml = text.innerHTML;
                        text.innerHTML = '';
                        text.innerHTML = tempHtml;
                        break;
                    case 'close':
                        flashMovie.StopPlay();
                        text.innerHTML = '';
                        break;
                    case 'length':
                        return flashMovie.TotalFrames();
                    case 'current_time':
                        return flashMovie.CurrentFrame();
                    case 'seek':
        //                flashMovie.GotoFrame(variable_value);
                        break;
                    case 'isEnded':
                        //TODO check flash end
                        return false;
                    case 'setVisible':
                        text.style.visibility = variable_value;
                        break;
                }
            }

            function show_alert(alerttext, position){
                var text = document.getElementById('alert');
                text.innerHTML = alerttext;
                if(alerttext == '') {
                    text.style.visibility = 'hidden';
                    return 0;
                }
                if(position == ''){
                    position = getComputedStyle(text, '').verticalAlign;
                }
                switch(position)
                {
                    case 'top':
                        text.style.top = '0px';
                        break;
                    case 'middle':
                        text.style.top = ((window.innerHeight - text.clientHeight) / 2)
                            + 'px';
                        break;
                    case 'bottom':
                        text.style.top = (window.innerHeight - text.clientHeight)
                            + 'px';
                        break;
                }
                text.style.visibility = 'visible';
                return text.clientHeight;
            }

            function update_css(align, font, size, color, bgcolor){
                var text = document.getElementById('alert');
                text.style.fontSize = size + "pt";
                text.style.fontFamily = font;
                text.style.color = color;
                text.style.backgroundColor = bgcolor;
                switch(align)
                {
                    case 'top':
                        text.style.top = '0px';
                        break;
                    case 'middle':
                        text.style.top = ((window.innerHeight - text.clientHeight) / 2)
                            + 'px';
                        break;
                    case 'bottom':
                        text.style.top = (window.innerHeight - text.clientHeight)
                            + 'px';
                        break;
                }
            }


            function show_image(src){
                var img = document.getElementById('image');
                img.src = src;
                if(src == '')
                    img.style.display = 'none';
                else
                    img.style.display = 'block';
            }

            function show_blank(state){
                var black = 'none';
                var lyrics = '';
                switch(state){
                    case 'theme':
                        lyrics = 'hidden';
                        break;
                    case 'black':
                        black = 'block';
                        break;
                    case 'desktop':
                        break;
                }
                document.getElementById('black').style.display = black;
                document.getElementById('lyricsmain').style.visibility = lyrics;
                document.getElementById('image').style.visibility = lyrics;
                document.getElementById('footer').style.visibility = lyrics;
            }

            function show_footer(footertext){
                document.getElementById('footer').innerHTML = footertext;
            }

            function show_text(new_text){
                var match = /-webkit-text-fill-color:[^;"]+/gi;
                if(timer != null)
                    clearTimeout(timer);
                /*
                QtWebkit bug with outlines and justify causing outline alignment
                problems. (Bug 859950) Surround each word with a <span> to workaround,
                but only in this scenario.
                */
                var txt = document.getElementById('lyricsmain');
                if(window.getComputedStyle(txt).textAlign == 'justify'){
                    if(window.getComputedStyle(txt).webkitTextStrokeWidth != '0px'){
                        new_text = new_text.replace(/(\s|&nbsp;)+(?![^<]*>)/g,
                            function(match) {
                                return '</span>' + match + '<span>';
                            });
                        new_text = '<span>' + new_text + '</span>';
                    }
                }
                text_fade('lyricsmain', new_text);
            }

            function text_fade(id, new_text){
                /*
                Show the text.
                */
                var text = document.getElementById(id);
                if(text == null) return;
                if(!transition){
                    text.innerHTML = new_text;
                    return;
                }
                // Fade text out. 0.1 to minimize the time "nothing" is shown on the screen.
                text.style.opacity = '0.1';
                // Fade new text in after the old text has finished fading out.
                timer = window.setTimeout(function(){_show_text(text, new_text)}, 400);
            }

            function _show_text(text, new_text) {
                /*
                Helper function to show the new_text delayed.
                */
                text.innerHTML = new_text;
                text.style.opacity = '1';
                // Wait until the text is completely visible. We want to save the timer id, to be able to call
                // clearTimeout(timer) when the text has changed before finishing fading.
                timer = window.setTimeout(function(){timer = null;}, 400);
            }

            function show_text_completed(){
                return (timer == null);
            }
        </script>
        </head>
        <body>
        <img id="bgimage" class="size" style="display:none;" />
        <img id="image" class="size" style="display:none;" />

        <div id="videobackboard" class="size" style="visibility:hidden"></div>
        <video id="video" class="size" style="visibility:hidden" autobuffer preload></video>

        <div id="flash" class="size" style="visibility:hidden"></div>

            <div id="alert" style="visibility:hidden"></div>

        <div class="lyricstable"><div id="lyricsmain" style="opacity:1" class="lyricscell lyricsmain"></div></div>
        <div id="footer" class="footer"></div>
        <div id="black" class="size"></div>
        </body>
        </html>
"""
import logging

from string import Template
from PyQt5 import QtWebKit

from openlp.core.common import Settings
from openlp.core.lib.theme import BackgroundType, BackgroundGradientType, VerticalType, HorizontalType

log = logging.getLogger(__name__)

HTML_SRC = Template("""
    <!DOCTYPE html>
    <html>
    <head>
    <title>OpenLP Display</title>
    <style>
    *{
        margin: 0;
        padding: 0;
        border: 0;
        overflow: hidden;
        -webkit-user-select: none;
    }
    body {
        ${bg_css};
    }
    .size {
        position: absolute;
        left: 0px;
        top: 0px;
        width: 100%;
        height: 100%;
    }
    #black {
        z-index: 8;
        background-color: black;
        display: none;
    }
    #bgimage {
        z-index: 1;
    }
    #image {
        z-index: 2;
    }
    ${css_additions}
    #footer {
        position: absolute;
        z-index: 6;
        ${footer_css}
    }
    /* lyric css */${lyrics_css}
    sup {
        font-size: 0.6em;
        vertical-align: top;
        position: relative;
        top: -0.3em;
    }
    /* Chords css */${chords_css}
    </style>
    <script>
        var timer = null;
        var transition = ${transitions};
        ${js_additions}

        function show_image(src){
            var img = document.getElementById('image');
            img.src = src;
            if(src == '')
                img.style.display = 'none';
            else
                img.style.display = 'block';
        }

        function show_blank(state){
            var black = 'none';
            var lyrics = '';
            switch(state){
                case 'theme':
                    lyrics = 'hidden';
                    break;
                case 'black':
                    black = 'block';
                    break;
                case 'desktop':
                    break;
            }
            document.getElementById('black').style.display = black;
            document.getElementById('lyricsmain').style.visibility = lyrics;
            document.getElementById('image').style.visibility = lyrics;
            document.getElementById('footer').style.visibility = lyrics;
        }

        function show_footer(footertext){
            document.getElementById('footer').innerHTML = footertext;
        }

        function show_text(new_text){
            var match = /-webkit-text-fill-color:[^;\"]+/gi;
            if(timer != null)
                clearTimeout(timer);
            /*
            QtWebkit bug with outlines and justify causing outline alignment
            problems. (Bug 859950) Surround each word with a <span> to workaround,
            but only in this scenario.
            */
            var txt = document.getElementById('lyricsmain');
            if(window.getComputedStyle(txt).textAlign == 'justify'){
                if(window.getComputedStyle(txt).webkitTextStrokeWidth != '0px'){
                    new_text = new_text.replace(/(\s|&nbsp;)+(?![^<]*>)/g,
                        function(match) {
                            return '</span>' + match + '<span>';
                        });
                    new_text = '<span>' + new_text + '</span>';
                }
            }
            text_fade('lyricsmain', new_text);
        }

        function text_fade(id, new_text){
            /*
            Show the text.
            */
            var text = document.getElementById(id);
            if(text == null) return;
            if(!transition){
                text.innerHTML = new_text;
                return;
            }
            // Fade text out. 0.1 to minimize the time "nothing" is shown on the screen.
            text.style.opacity = '0.1';
            // Fade new text in after the old text has finished fading out.
            timer = window.setTimeout(function(){_show_text(text, new_text)}, 400);
        }

        function _show_text(text, new_text) {
            /*
            Helper function to show the new_text delayed.
            */
            text.innerHTML = new_text;
            text.style.opacity = '1';
            // Wait until the text is completely visible. We want to save the timer id, to be able to call
            // clearTimeout(timer) when the text has changed before finishing fading.
            timer = window.setTimeout(function(){timer = null;}, 400);
        }

        function show_text_completed(){
            return (timer == null);
        }
    </script>
    </head>
    <body>
    <img id="bgimage" class="size" ${bg_image} />
    <img id="image" class="size" ${image} />
    ${html_additions}
    <div class="lyricstable"><div id="lyricsmain" style="opacity:1" class="lyricscell lyricsmain"></div></div>
    <div id="footer" class="footer"></div>
    <div id="black" class="size"></div>
    </body>
    </html>
    """)

LYRICS_SRC = Template("""
    .lyricstable {
        z-index: 5;
        position: absolute;
        display: table;
        ${stable}
    }
    .lyricscell {
        display: table-cell;
        word-wrap: break-word;
        -webkit-transition: opacity 0.4s ease;
        ${lyrics}
    }
    .lyricsmain {
       ${main}
    }
    table.line {}
    table.segment {
      float: left;
    }
    td.note {}
    td.lyrics {}
    """)

FOOTER_SRC = Template("""
    left: ${left}px;
    bottom: ${bottom}px;
    width: ${width}px;
    font-family: ${family};
    font-size: ${size}pt;
    color: ${color};
    text-align: left;
    white-space: ${space};
    """)

LYRICS_FORMAT_SRC = Template("""
    ${justify}word-wrap: break-word;
    text-align: ${align};
    vertical-align: ${valign};
    font-family: ${font};
    font-size: ${size}pt;
    color: ${color};
    line-height: ${line}%;
    margin: 0;
    padding: 0;
    padding-bottom: ${bottom};
    padding-left: ${left}px;
    width: ${width}px;
    height: ${height}px;${font_style}${font_weight}
    """)

CHORDS_FORMAT = Template("""
    .chordline {
      line-height: ${chord_line_height};
    }
    .chordline span.chord span {
      position: relative;
    }
    .chordline span.chord span strong {
      position: absolute;
      top: -0.8em;
      left: 0;
      font-size: 75%;
      font-weight: normal;
      line-height: normal;
      display: ${chords_display};
    }
    .firstchordline {
        line-height: ${first_chord_line_height};
    }""")


def build_html(item, screen, is_live, background, image=None, plugins=None):
    """
    Build the full web paged structure for display

    :param item: Service Item to be displayed
    :param screen: Current display information
    :param is_live: Item is going live, rather than preview/theme building
    :param background:  Theme background image - bytes
    :param image: Image media item - bytes
    :param plugins: The List of available plugins
    """
    width = screen['size'].width()
    height = screen['size'].height()
    theme_data = item.theme_data
    # Image generated and poked in
    if background:
        bgimage_src = 'src="data:image/png;base64,{image}"'.format(image=background)
    elif item.bg_image_bytes:
        bgimage_src = 'src="data:image/png;base64,{image}"'.format(image=item.bg_image_bytes)
    else:
        bgimage_src = 'style="display:none;"'
    if image:
        image_src = 'src="data:image/png;base64,{image}"'.format(image=image)
    else:
        image_src = 'style="display:none;"'
    css_additions = ''
    js_additions = ''
    html_additions = ''
    if plugins:
        for plugin in plugins:
            css_additions += plugin.get_display_css()
            js_additions += plugin.get_display_javascript()
            html_additions += plugin.get_display_html()
    return HTML_SRC.substitute(bg_css=build_background_css(item, width),
                               css_additions=css_additions,
                               footer_css=build_footer_css(item, height),
                               lyrics_css=build_lyrics_css(item),
                               transitions='true' if (theme_data and
                                                      theme_data.display_slide_transition and
                                                      is_live) else 'false',
                               js_additions=js_additions,
                               bg_image=bgimage_src,
                               image=image_src,
                               html_additions=html_additions,
                               chords_css=build_chords_css())


def webkit_version():
    """
    Return the Webkit version in use. Note method added relatively recently, so return 0 if prior to this
    """
    try:
        webkit_ver = float(QtWebKit.qWebKitVersion())
        log.debug('Webkit version = {version}'.format(version=webkit_ver))
    except AttributeError:
        webkit_ver = 0.0
    return webkit_ver


def build_background_css(item, width):
    """
    Build the background css

    :param item: Service Item containing theme and location information
    :param width:
    """
    width = int(width) // 2
    theme = item.theme_data
    background = 'background-color: black'
    if theme:
        if theme.background_type == BackgroundType.to_string(BackgroundType.Transparent):
            background = ''
        elif theme.background_type == BackgroundType.to_string(BackgroundType.Solid):
            background = 'background-color: {theme}'.format(theme=theme.background_color)
        else:
            if theme.background_direction == BackgroundGradientType.to_string(BackgroundGradientType.Horizontal):
                background = 'background: -webkit-gradient(linear, left top, left bottom, from({start}), to({end})) ' \
                    'fixed'.format(start=theme.background_start_color, end=theme.background_end_color)
            elif theme.background_direction == BackgroundGradientType.to_string(BackgroundGradientType.LeftTop):
                background = 'background: -webkit-gradient(linear, left top, right bottom, from({start}), to({end})) ' \
                    'fixed'.format(start=theme.background_start_color, end=theme.background_end_color)
            elif theme.background_direction == BackgroundGradientType.to_string(BackgroundGradientType.LeftBottom):
                background = 'background: -webkit-gradient(linear, left bottom, right top, from({start}), to({end})) ' \
                    'fixed'.format(start=theme.background_start_color, end=theme.background_end_color)
            elif theme.background_direction == BackgroundGradientType.to_string(BackgroundGradientType.Vertical):
                background = 'background: -webkit-gradient(linear, left top, right top, from({start}), to({end})) ' \
                    'fixed'.format(start=theme.background_start_color, end=theme.background_end_color)
            else:
                background = 'background: -webkit-gradient(radial, {width} 50%, 100, {width} 50%, {width}, ' \
                    'from({start}), to({end})) fixed'.format(width=width,
                                                             start=theme.background_start_color,
                                                             end=theme.background_end_color)
    return background


def build_lyrics_css(item):
    """
    Build the lyrics display css

    :param item: Service Item containing theme and location information
    """
    theme_data = item.theme_data
    lyricstable = ''
    lyrics = ''
    lyricsmain = ''
    if theme_data and item.main:
        lyricstable = 'left: {left}px; top: {top}px;'.format(left=item.main.x(), top=item.main.y())
        lyrics = build_lyrics_format_css(theme_data, item.main.width(), item.main.height())
        lyricsmain += build_lyrics_outline_css(theme_data)
        if theme_data.font_main_shadow:
            lyricsmain += ' text-shadow: {theme} {shadow}px ' \
                '{shadow}px;'.format(theme=theme_data.font_main_shadow_color,
                                     shadow=theme_data.font_main_shadow_size)
    return LYRICS_SRC.substitute(stable=lyricstable, lyrics=lyrics, main=lyricsmain)


def build_lyrics_outline_css(theme_data):
    """
    Build the css which controls the theme outline. Also used by renderer for splitting verses

    :param theme_data: Object containing theme information
    """
    if theme_data.font_main_outline:
        size = float(theme_data.font_main_outline_size) / 16
        fill_color = theme_data.font_main_color
        outline_color = theme_data.font_main_outline_color
        return ' -webkit-text-stroke: {size}em {color}; -webkit-text-fill-color: {fill}; '.format(size=size,
                                                                                                  color=outline_color,
                                                                                                  fill=fill_color)
    return ''


def build_lyrics_format_css(theme_data, width, height):
    """
    Build the css which controls the theme format. Also used by renderer for splitting verses

    :param theme_data: Object containing theme information
    :param width: Width of the lyrics block
    :param height: Height of the lyrics block
    """
    align = HorizontalType.Names[theme_data.display_horizontal_align]
    valign = VerticalType.Names[theme_data.display_vertical_align]
    left_margin = (int(theme_data.font_main_outline_size) * 2) if theme_data.font_main_outline else 0
    # fix tag incompatibilities
    justify = '' if (theme_data.display_horizontal_align == HorizontalType.Justify) else '    white-space: pre-wrap;\n'
    padding_bottom = '0.5em' if (theme_data.display_vertical_align == VerticalType.Bottom) else '0'
    return LYRICS_FORMAT_SRC.substitute(justify=justify,
                                        align=align,
                                        valign=valign,
                                        font=theme_data.font_main_name,
                                        size=theme_data.font_main_size,
                                        color=theme_data.font_main_color,
                                        line='{line:d}'.format(line=100 + int(theme_data.font_main_line_adjustment)),
                                        bottom=padding_bottom,
                                        left=left_margin,
                                        width=width,
                                        height=height,
                                        font_style='\n    font-style: italic;' if theme_data.font_main_italics else '',
                                        font_weight='\n    font-weight: bold;' if theme_data.font_main_bold else '')


def build_footer_css(item, height):
    """
    Build the display of the item footer

    :param item: Service Item to be processed.
    :param height:
    """
    theme = item.theme_data
    if not theme or not item.footer:
        return ''
    bottom = height - int(item.footer.y()) - int(item.footer.height())
    whitespace = 'normal' if Settings().value('themes/wrap footer') else 'nowrap'
    return FOOTER_SRC.substitute(left=item.footer.x(), bottom=bottom, width=item.footer.width(),
                                 family=theme.font_footer_name, size=theme.font_footer_size,
                                 color=theme.font_footer_color, space=whitespace)


def build_chords_css():
    if Settings().value('songs/mainview chords'):
        chord_line_height = '2.0em'
        chords_display = 'inline'
        first_chord_line_height = '2.1em'
    else:
        chord_line_height = '1.0em'
        chords_display = 'none'
        first_chord_line_height = '1.0em'
    return CHORDS_FORMAT.substitute(chord_line_height=chord_line_height, chords_display=chords_display,
                                    first_chord_line_height=first_chord_line_height)
