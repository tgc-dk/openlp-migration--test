# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4
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

import os

class ConfigHelper(object):
    """
    Utility Helper to allow classes to find directories in a standard manner.
    """
    @staticmethod
    def get_registry_value(reg, key, value_name):
        k = _winreg.OpenKey(reg, key)
        value = _winreg.QueryValueEx(k, value_name)[0]
        _winreg.CloseKey(k)
        return value

    @staticmethod
    def getConfigPath():
        if os.name == 'nt':
            import _winreg
            reg = _winreg.ConnectRegistry(None, _winreg.HKEY_LOCAL_MACHINE)
            key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
            path = get_registry_value(reg, key, "Common AppData")
        elif os.name == 'posix':
            path = os.path.join(os.getenv('HOME'), ".openlp.org")
            #if os.path.exists(path) == False :
            #    raise Exception ('Configuration Directory does not Exist ')
        return path

    @staticmethod
    def getSongsFile():
        path = ConfigHelper.getConfigPath()
        songfile = os.path.join(path, ".openlp.org", "Data", "songs.olp")
        if os.path.exists(songfile):
            filename.set_filename(songfile)
        print songfile

    @staticmethod
    def getBiblePath():
        return os.path.join(ConfigHelper.getConfigPath(), "Data","Bibles")

    @staticmethod
    def getRegistry():
        """
        This static method loads the appropriate registry class based on the
        current operating system, and returns an instantiation of that class.
        """
        reg = None
        if os.name == 'nt':
            from winregistry import WinRegistry
            reg = WinRegistry()
        else:
            from linregistry import LinRegistry
            reg = LinRegistry()
        return reg
