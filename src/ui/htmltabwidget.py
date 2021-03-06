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

""" HTML viewer tab widget """


import os.path
from PyQt4.QtGui import QFrame, QHBoxLayout, QDesktopServices, QMenu, QFont
from ui.mainwindowtabwidgetbase import MainWindowTabWidgetBase
from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4.QtWebKit import QWebView, QWebPage
from utils.globals import GlobalData


class HTMLViewer( QWebView ):
    " HTML viewer (web browser) "

    escapePressed = pyqtSignal()

    def __init__( self, parent = None ):
        QWebView.__init__( self, parent )

    def keyPressEvent( self, event ):
        " Handles the key press events "
        if event.key() == Qt.Key_Escape:
            self.escapePressed.emit()
            event.accept()
        else:
            QWebView.keyPressEvent( self, event )
        return

    def contextMenuEvent( self, event ):
        " Disables the default menu "
        testContent = self.page().mainFrame().hitTestContent( event.pos() )
        if testContent.linkUrl():
            menu = QMenu( self )
            menu.addAction( self.pageAction( QWebPage.CopyLinkToClipboard ) )
            menu.popup( self.mapToGlobal( event.pos() ) )
        elif self.page().selectedText() != "":
            menu = QMenu( self )
            menu.addAction( self.pageAction( QWebPage.Copy ) )
            menu.popup( self.mapToGlobal( event.pos() ) )
        return

    def zoomTo( self, zoomFactor ):
        """ Scales the font in accordance to the given zoom factor.
            It is mostly used in diff viewers """
        font = QFont( GlobalData().skin.nolexerFont )
        origPointSize = font.pointSize()
        newPointSize = origPointSize + zoomFactor
        self.setTextSizeMultiplier( float( newPointSize ) /
                                    float( origPointSize ) )
        return



class HTMLTabWidget( MainWindowTabWidgetBase, QFrame ):
    " The widget which displays a RO HTML page "

    escapePressed = pyqtSignal()

    def __init__( self, parent = None ):

        MainWindowTabWidgetBase.__init__( self )
        QFrame.__init__( self, parent )

        self.setFrameShape( QFrame.StyledPanel )
        layout = QHBoxLayout( self )
        layout.setMargin( 0 )

        self.__editor = HTMLViewer( self )
        self.__editor.escapePressed.connect( self.__onEsc )
        layout.addWidget( self.__editor )

        self.__fileName = ""
        self.__shortName = ""
        self.__encoding = "n/a"
        return

    def __onEsc( self ):
        " Triggered when Esc is pressed "
        self.escapePressed.emit()
        return

    def setHTML( self, content ):
        " Sets the content from the given string "
        self.__editor.setHtml( content )
        self.__connectPage()
        return

    def getHTML( self ):
        " Provides the currently shown HTML "
        return self.__editor.page().mainFrame().toHtml()

    def loadFormFile( self, path ):
        " Loads the content from the given file "
        f = open( path, 'r' )
        content = f.read()
        f.close()
        self.setHTML( content )
        self.__connectPage()
        self.__fileName = path
        self.__shortName = os.path.basename( path )
        return

    def __connectPage( self ):
        " Connects the current web page to the links delegate "
        self.__editor.page().setLinkDelegationPolicy(
                                QWebPage.DelegateAllLinks )
        self.__editor.linkClicked.connect( QDesktopServices.openUrl )
        return

    def zoomTo( self, zoomFactor ):
        self.__editor.zoomTo( zoomFactor )
        return

    def getViewer( self ):
        " Provides the QWebView "
        return self.__editor

    def setFocus( self ):
        " Overridden setFocus "
        self.__editor.setFocus()
        return

    def isModified( self ):
        " Tells if the file is modifed "
        return False

    def getRWMode( self ):
        " Tells the read/write mode "
        return "RO"

    def getType( self ):
        " Tells the widget type "
        return MainWindowTabWidgetBase.HTMLViewer

    def getLanguage( self ):
        " Tells the content language "
        return "HTML"

    def getFileName( self ):
        " Tells what file name of the widget "
        return self.__fileName

    def setFileName( self, path ):
        " Sets the file name "
        self.__fileName = path
        self.__shortName = os.path.basename( path )
        return

    def getEol( self ):
        " Tells the EOL style "
        return "n/a"

    def getLine( self ):
        " Tells the cursor line "
        return "n/a"

    def getPos( self ):
        " Tells the cursor column "
        return "n/a"

    def getEncoding( self ):
        " Tells the content encoding "
        return self.__encoding

    def setEncoding( self, newEncoding ):
        " Sets the encoding - used for Diff files "
        self.__encoding = newEncoding
        return

    def getShortName( self ):
        " Tells the display name "
        return self.__shortName

    def setShortName( self, name ):
        " Sets the display name "
        self.__shortName = name
        return

