<!DOCTYPE html>
<html>
<!--
###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2016 OpenLP Developers                                   #
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
-->
<head>
  <meta charset="utf-8" />
  <title>${stage_title}</title>
  <link rel="stylesheet" href="${static_url}/css/stage.css" />
  <link rel="shortcut icon" type="image/x-icon" href="/static/images/favicon.ico">
  <script type="text/javascript" src="${assets_url}/jquery.min.js"></script>
  <script type="text/javascript" src="${static_url}/js/stage.js"></script>
</head>
<body>
<input type="hidden" id="next-text" value="${next}" />
<div id="right">
  <div id="clock"></div>
  <div id="notes"></div>
</div>
<div id="verseorder"></div>
<div id="currentslide"></div>
<div id="nextslide"></div>
</body>
</html>
