#
# -*- coding: utf-8 -*-
#
# codimension - graphics python two-way code editor and analyzer
# Copyright (C) 2010  Sergey Satskiy <sergey.satskiy@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# $Id$
#

#
# The file was taken from eric 4.4.3 and adopted for codimension.
# Original copyright:
# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

" File system browser with module browsing capabilities "

from utils.pixmapcache      import PixmapCache
from utils.globals          import GlobalData
from filesystembrowsermodel import FileSystemBrowserModel
from filesbrowserbase       import FilesBrowser


class FileSystemBrowser( FilesBrowser ):
    " File system tree browser "

    def __init__( self, parent = None ):

        FilesBrowser.__init__( self, FileSystemBrowserModel(), False, parent )

        self.setWindowTitle( 'Filesystem browser' )
        self.setWindowIcon( PixmapCache().getIcon( 'icon.png' ) )

        GlobalData().project.fsChanged.connect( self._onFSChanged )
        return

    def removeToplevelDir( self ):
        " Handles the Remove from toplevel popup menu entry "

        index = self.currentIndex()
        dname = self.model().item( index ).getPath()
        GlobalData().project.removeTopLevelDir( dname )
        sindex = self.model().mapToSource( index )
        self.model().sourceModel().removeTopLevelDir( sindex )
        return

    def addToplevelDir( self ):
        " Handles the Add as toplevel directory popup menu entry "

        index = self.currentIndex()
        dname = self.model().item( index ).getPath()
        GlobalData().project.addTopLevelDir( dname )
        self.model().sourceModel().addTopLevelDir( dname )
        self.layoutDisplay()
        return

    def reload( self ):
        " Reloads the filesystem view "
        self.model().sourceModel().populateModel()
        self.model().reset()
        self.layoutDisplay()
        return
