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


""" imports diagram graphics objects """

import math
from PyQt4.QtGui import ( QGraphicsRectItem, QGraphicsPathItem, QWidget,
                          QGraphicsView, QFont, QPen, QToolBar, QHBoxLayout,
                          QColor, QAction, QGraphicsItem, QPainterPath,
                          QGraphicsTextItem, QFontMetrics, QApplication,
                          QStyleOptionGraphicsItem, QPainter, QStyle, QImage )
from PyQt4.QtCore import Qt, QSize, QPointF, QRectF, pyqtSignal
from ui.mainwindowtabwidgetbase import MainWindowTabWidgetBase
from utils.pixmapcache import PixmapCache
from utils.globals import GlobalData



class ImportsDgmEdgeLabel( QGraphicsTextItem ):
    " Connector label "

    def __init__( self, edge, modObj ):
        text = edge.label.replace( '\\n', '\n' )
        QGraphicsTextItem.__init__( self, text )
        self.__modObj = modObj

        font = QFont( "Arial", 10 )
        self.setFont( font )

        metric = QFontMetrics( font )
        rec = metric.boundingRect( 0, 0, 10000, 10000, Qt.AlignLeft, text )

        self.setPos( edge.labelX - rec.width() / 2,
                     edge.labelY - rec.height() / 2 )

        # To make double click delivered
        self.setFlag( QGraphicsItem.ItemIsSelectable, True )
        return

    def paint( self, painter, option, widget ):
        """ Draws the edge text """

        # Hide the dotted outline
        itemOption = QStyleOptionGraphicsItem( option )
        if itemOption.state & QStyle.State_Selected != 0:
            itemOption.state = itemOption.state & ~QStyle.State_Selected

        QGraphicsTextItem.paint( self, painter, itemOption, widget )
        return

    def mouseDoubleClickEvent( self, event ):
        " Open the clicked file as the new one "

        # Jump to the first import statement
        line = self.__modObj.imports[ 0 ].line
        GlobalData().mainWindow.openFile( self.__modObj.refFile, line )
        return



class ImportsDgmDocConn( QGraphicsPathItem ):
    " Connection to a docstring note "

    def __init__( self, edge, modObj ):
        QGraphicsPathItem.__init__( self )
        self.__edge = edge
        self.__modObj = modObj

        startPoint = QPointF( edge.points[ 0 ][ 0 ], edge.points[ 0 ][ 1 ] )
        painterPath = QPainterPath( startPoint )

        index = 1
        while index + 3 <= len( edge.points ):
            painterPath.cubicTo(edge.points[index][0],  edge.points[index][1],
                                edge.points[index+1][0],edge.points[index+1][1],
                                edge.points[index+2][0],edge.points[index+2][1])
            index = index + 3
        if index + 2 <= len( edge.points ):
            painterPath.quadTo(edge.points[index+1][0], edge.points[index+1][1],
                               edge.points[index+2][0], edge.points[index+2][1])
            index = index + 2

        if index + 1 <= len( edge.points ):
            painterPath.lineTo(edge.points[index+1][0], edge.points[index+1][1])

        self.setPath( painterPath )
        return

    def paint( self, painter, option, widget ):
        """ Draws a curve and then adds an arrow """

        pen = QPen( QColor( 0, 0, 0) )
        pen.setWidth( 2 )
        pen.setStyle( Qt.DotLine )
        self.setPen( pen )

        QGraphicsPathItem.paint( self, painter, option, widget )
        return



class ImportsDgmDependConn( QGraphicsPathItem ):
    " Connection to a dependency module "

    def __init__( self, edge, modObj, connObj ):
        QGraphicsPathItem.__init__( self )
        self.__edge = edge
        self.__modObj = modObj
        self.__connObj = connObj

        startPoint = QPointF( edge.points[ 0 ][ 0 ], edge.points[ 0 ][ 1 ] )
        painterPath = QPainterPath( startPoint )

        index = 1
        while index + 3 <= len( edge.points ):
            painterPath.cubicTo(edge.points[index][0],  edge.points[index][1],
                                edge.points[index+1][0],edge.points[index+1][1],
                                edge.points[index+2][0],edge.points[index+2][1])
            index = index + 3
        if index + 2 <= len( edge.points ):
            painterPath.quadTo(edge.points[index+1][0], edge.points[index+1][1],
                               edge.points[index+2][0], edge.points[index+2][1])
            index = index + 2

        if index + 1 <= len( edge.points ):
            painterPath.lineTo(edge.points[index+1][0], edge.points[index+1][1])

        lastIndex = len( edge.points ) - 1
        self.addArrow( painterPath,
                       edge.points[lastIndex-1][0],
                       edge.points[lastIndex-1][1],
                       edge.points[lastIndex][0],
                       edge.points[lastIndex][1] )

        self.setPath( painterPath )
        return

    def addArrow( self, painterPath, startX, startY, endX, endY ):
        """
        Add arrows to the edges
        http://kapo-cpp.blogspot.com/2008/10/drawing-arrows-with-cairo.html
        """

        arrowLength  = 12.0
        arrowDegrees = 0.15      # Radian

        angle = math.atan2( endY - startY, endX - startX ) + math.pi
        arrowX1 = endX + arrowLength * math.cos(angle - arrowDegrees)
        arrowY1 = endY + arrowLength * math.sin(angle - arrowDegrees)
        arrowX2 = endX + arrowLength * math.cos(angle + arrowDegrees)
        arrowY2 = endY + arrowLength * math.sin(angle + arrowDegrees)

        painterPath.moveTo( endX, endY )
        painterPath.lineTo( arrowX1, arrowY1 )
        painterPath.moveTo( endX, endY )
        painterPath.lineTo( arrowX2, arrowY2 )

        return

    def paint( self, painter, option, widget ):
        """ Draws a curve and then adds an arrow """

        pen = QPen( QColor( 0, 0, 0) )
        pen.setWidth( 2 )
        self.setPen( pen )

        painter.setRenderHint( QPainter.Antialiasing, True )
        QGraphicsPathItem.paint( self, painter, option, widget )
        return


class ImportsDgmUnknownModule( QGraphicsRectItem ):
    " Unknown module "

    def __init__( self, node ):
        QGraphicsRectItem.__init__( self )
        self.__node = node

        posX = node.posX - node.width / 2.0
        posY = node.posY - node.height / 2.0
        QGraphicsRectItem.__init__( self, posX, posY,
                                    node.width, node.height )
        pen = QPen( QColor( 153, 0, 0 ) )
        pen.setWidth( 2 )
        self.setPen( pen )

        self.setBrush( QColor( 216, 216, 207 ) )
        return

    def paint( self, painter, option, widget ):
        """ Draws a filled rectangle and then adds a title """

        # Draw the rectangle
        QGraphicsRectItem.paint( self, painter, option, widget )

        # Draw text over the rectangle
        font = QFont( "Arial", 10 )
        font.setBold( True )
        painter.setFont( font )
        painter.setPen( QPen( QColor( 90, 90, 88 ) ) )
        painter.drawText( self.__node.posX - self.__node.width / 2.0,
                          self.__node.posY - self.__node.height / 2.0,
                          self.__node.width, self.__node.height,
                          Qt.AlignCenter, self.__node.label )
        return


class ImportsDgmBuiltInModule( QGraphicsRectItem ):
    " Built-in module "

    def __init__( self, node ):
        QGraphicsRectItem.__init__( self )
        self.__node = node

        posX = node.posX - node.width / 2.0
        posY = node.posY - node.height / 2.0
        QGraphicsRectItem.__init__( self, posX, posY,
                                    node.width, node.height )
        pen = QPen( QColor( 0, 0, 0) )
        pen.setWidth( 2 )
        self.setPen( pen )

        self.setBrush( QColor( 216, 216, 207 ) )
        return

    def paint( self, painter, option, widget ):
        """ Draws a filled rectangle and then adds a title """

        # Draw the rectangle
        QGraphicsRectItem.paint( self, painter, option, widget )

        # Draw text over the rectangle
        font = QFont( "Arial", 10 )
        font.setBold( True )
        painter.setFont( font )
        painter.setPen( QPen( QColor( 90, 90, 88 ) ) )
        painter.drawText( self.__node.posX - self.__node.width / 2.0,
                          self.__node.posY - self.__node.height / 2.0,
                          self.__node.width, self.__node.height,
                          Qt.AlignCenter, self.__node.label )

        pixmap = PixmapCache().getPixmap( "binarymod.png" )
        pixmapPosX = self.__node.posX + self.__node.width / 2.0 - \
                     pixmap.width() / 2.0
        pixmapPosY = self.__node.posY - self.__node.height / 2.0 - \
                     pixmap.height() / 2.0
        painter.setRenderHint( QPainter.SmoothPixmapTransform )
        painter.drawPixmap( pixmapPosX, pixmapPosY, pixmap )
        return


class ImportsDgmSystemWideModule( QGraphicsRectItem ):
    " Systemwide module "

    def __init__( self, node, refFile, docstring ):
        QGraphicsRectItem.__init__( self )
        self.__node = node
        self.__refFile = refFile
        self.__docstring = docstring

        posX = node.posX - node.width / 2.0
        posY = node.posY - node.height / 2.0
        QGraphicsRectItem.__init__( self, posX, posY,
                                    node.width, node.height )
        pen = QPen( QColor( 0, 0, 0) )
        pen.setWidth( 2 )
        self.setPen( pen )

        self.__setTooltip()
        self.setBrush( QColor( 220, 255, 220 ) )

        # System modules are clickable
        self.setFlag( QGraphicsItem.ItemIsSelectable, True )
        return

    def __setTooltip( self ):
        " Sets the module tooltip "
        tooltip = ""
        if self.__refFile != "":
            tooltip = self.__refFile
        if self.__docstring != "":
            if tooltip != "":
                tooltip += "\n\n"
            tooltip += self.__docstring
        self.setToolTip( tooltip )
        return

    def paint( self, painter, option, widget ):
        """ Draws a filled rectangle and then adds a title """

        # Hide the dotted outline for clickable system modules
        itemOption = QStyleOptionGraphicsItem( option )
        if itemOption.state & QStyle.State_Selected != 0:
            itemOption.state = itemOption.state & ~QStyle.State_Selected

        # Draw the rectangle
        QGraphicsRectItem.paint( self, painter, itemOption, widget )

        # Draw text over the rectangle
        font = QFont( "Arial", 10 )
        font.setBold( True )
        painter.setFont( font )
        painter.drawText( self.__node.posX - self.__node.width / 2.0,
                          self.__node.posY - self.__node.height / 2.0,
                          self.__node.width, self.__node.height,
                          Qt.AlignCenter, self.__node.label )

        pixmap = PixmapCache().getPixmap( "systemmod.png" )
        pixmapPosX = self.__node.posX + self.__node.width / 2.0 - \
                     pixmap.width() / 2.0
        pixmapPosY = self.__node.posY - self.__node.height / 2.0 - \
                     pixmap.height() / 2.0
        painter.setRenderHint( QPainter.SmoothPixmapTransform )
        painter.drawPixmap( pixmapPosX, pixmapPosY, pixmap )
        return

    def mouseDoubleClickEvent( self, event ):
        """ Open the clicked file as the new one """
        if self.__refFile != "":
            GlobalData().mainWindow.openFile( self.__refFile, -1 )
        return


class ImportsDgmDetailedModuleBase( QGraphicsRectItem ):
    " Base class which calculates section heights "

    def __init__( self, node, refFile, srcobj, deviceDPI ):
        self.__node = node
        self.__srcobj = srcobj
        self.__refFile = refFile

        self.__pixelsPerLine = self.calcPixelsPerLine()

        posX = node.posX - node.width / 2.0
        posY = node.posY - node.height / 2.0
        QGraphicsRectItem.__init__( self, posX, posY,
                                    node.width, node.height )
        pen = QPen( QColor( 0, 0, 0 ) )
        pen.setWidth( 2 )
        self.setPen( pen )

        self.__setTooltip()

        # To make double click delivered
        self.setFlag( QGraphicsItem.ItemIsSelectable, True )
        return

    def calcPixelsPerLine( self ):
        " Provides the module section heights "

        self.__lines = [ self.__srcobj.title, None ]
        for klass in self.__srcobj.classes:
            self.__lines.append( klass.name )
        self.__lines.append( None )
        for func in self.__srcobj.funcs:
            self.__lines.append( func.name )
        self.__lines.append( None )
        for glob in self.__srcobj.globs:
            self.__lines.append( glob.name )

        # One line a spare for half a line at the top and half a line at the
        # bottom
        return int( float( self.__node.height ) / \
                    float( len( self.__lines ) + 1 ) )

    def __setTooltip( self ):
        " Sets the module tooltip "
        tooltip = ""
        if self.__refFile != "":
            tooltip = self.__refFile
        if self.__srcobj.docstring != "":
            if tooltip != "":
                tooltip += "\n\n"
            tooltip += self.__srcobj.docstring
        self.setToolTip( tooltip )
        return

    def paint( self, painter, option, widget ):
        " Draws a filled rectangle, adds title, classes/funcs/globs sections "

        # Hide the dotted outline
        itemOption = QStyleOptionGraphicsItem( option )
        if itemOption.state & QStyle.State_Selected != 0:
            itemOption.state = itemOption.state & ~QStyle.State_Selected

        # Draw the rectangle
        QGraphicsRectItem.paint( self, painter, itemOption, widget )


        # Start from the bottom to automatically take potential spare
        # pixels for the title
        font = QFont( "Arial", 10 )
        painter.setFont( font )
        posX = self.__node.posX - self.__node.width / 2.0
        posY = self.__node.posY + self.__node.height / 2.0 - 1.5 * self.__pixelsPerLine

        occupiedPixels = 0
        for index in xrange( len( self.__lines ) - 1, 0, -1 ):
            if self.__lines[ index ] is None:
                # Draw a separation line
                painter.drawLine( posX + 1, posY + self.__pixelsPerLine / 2.0,
                                  posX + self.__node.width,
                                  posY + self.__pixelsPerLine / 2.0)
            elif self.__lines[ index ] != "":
                # Draw a text line
                # Sometimes the bottom part of 'g' is not drawn so I add 2
                # spare pixels.
                painter.drawText( int( posX ), int( posY ),
                                  int( self.__node.width ), self.__pixelsPerLine + 2,
                                  Qt.AlignCenter, self.__lines[ index ] )
            occupiedPixels += self.__pixelsPerLine
            posY -= self.__pixelsPerLine

        # Draw the title in bold
        font.setBold( True )
        painter.setFont( font )

        available = self.__node.height - occupiedPixels
        posY = self.__node.posY - self.__node.height / 2.0
        painter.drawText( int( posX ), int( posY ),
                          int( self.__node.width ), int( available ),
                          Qt.AlignCenter, self.__lines[ 0 ] )
        return

    def mouseDoubleClickEvent( self, event ):
        " Open the clicked file as the new one "
        GlobalData().mainWindow.openFile( self.__refFile, -1 )
        return


class ImportsDgmModuleOfInterest( ImportsDgmDetailedModuleBase ):
    " Module of interest "

    def __init__( self, node, refFile, srcobj, deviceDPI ):
        ImportsDgmDetailedModuleBase.__init__( self, node, refFile,
                                               srcobj, deviceDPI )
        self.setBrush( QColor( 224, 236, 255 ) )
        return



class ImportsDgmOtherPrjModule( ImportsDgmDetailedModuleBase ):
    " Other in-project module "

    def __init__( self, node, refFile, srcobj, deviceDPI ):
        ImportsDgmDetailedModuleBase.__init__( self, node, refFile,
                                               srcobj, deviceDPI )
        self.setBrush( QColor( 240, 240, 110 ) )
        return


class ImportsDgmDocNote( QGraphicsRectItem ):
    " Docstring box "

    def __init__( self, node, refFile, srcobj ):
        QGraphicsRectItem.__init__( self )
        self.__node = node
        self.__srcobj = srcobj
        self.__refFile = refFile

        posX = node.posX - node.width / 2.0
        posY = node.posY - node.height / 2.0
        QGraphicsRectItem.__init__( self, posX, posY,
                                    node.width, node.height )
        pen = QPen( QColor( 0, 0, 0) )
        pen.setWidth( 2 )
        self.setPen( pen )

        # To make double click delivered
        self.setFlag( QGraphicsItem.ItemIsSelectable, True )

        self.setBrush( QColor( 253, 245, 145 ) )
        return

    def paint( self, painter, option, widget ):
        """ Draws a filled rectangle and then adds a title """

        # Hide the dotted outline
        itemOption = QStyleOptionGraphicsItem( option )
        if itemOption.state & QStyle.State_Selected != 0:
            itemOption.state = itemOption.state & ~QStyle.State_Selected

        # Draw the rectangle
        QGraphicsRectItem.paint( self, painter, itemOption, widget )

        # Draw text over the rectangle
        font = QFont( "Arial", 10 )
        painter.setFont( font )
        painter.drawText( self.__node.posX - self.__node.width / 2.0,
                          self.__node.posY - self.__node.height / 2.0,
                          self.__node.width, self.__node.height,
                          Qt.AlignCenter, self.__srcobj.text )

        pixmap = PixmapCache().getPixmap( "docstring.png" )
        pixmapPosX = self.__node.posX + self.__node.width / 2.0 - \
                     pixmap.width() / 2.0
        pixmapPosY = self.__node.posY - self.__node.height / 2.0 - \
                     pixmap.height() / 2.0
        painter.setRenderHint( QPainter.SmoothPixmapTransform )
        painter.drawPixmap( pixmapPosX, pixmapPosY, pixmap )
        return

    def mouseDoubleClickEvent( self, event ):
        """ Open the clicked file as the new one """
        GlobalData().mainWindow.openFile( self.__refFile,
                                          self.__srcobj.line )
        return



class DiagramWidget( QGraphicsView ):
    " Widget to show a generated diagram "

    escapePressed = pyqtSignal()

    def __init__( self, parent = None ):
        QGraphicsView.__init__( self, parent )
#        self.setRenderHint( QPainter.Antialiasing )
#        self.setRenderHint( QPainter.TextAntialiasing )
        return

    def keyPressEvent( self, event ):
        """ Handles the key press events """
        if event.key() == Qt.Key_Escape:
            self.escapePressed.emit()
            event.accept()
        elif event.key() == Qt.Key_C and \
             event.modifiers() == Qt.ControlModifier:
            self.onCopy()
            event.accept()
        else:
            QGraphicsView.keyPressEvent( self, event )
        return

    def setScene( self, scene ):
        " Sets the scene to display "
        scene.setBackgroundBrush( GlobalData().skin.nolexerPaper )
        QGraphicsView.setScene( self, scene )
        return

    def resetZoom( self ):
        " Resets the zoom "
        # I don't really understand how it works
        # Taken from here:
        # http://cep.xor.aps.anl.gov/software/qt4-x11-4.2.2-browser/d9/df9/qgraphicsview_8cpp-source.html
        unity = self.matrix().mapRect( QRectF( 0, 0, 1, 1 ) )
        self.scale( 1 / unity.width(), 1 / unity.height() )
        return

    def zoomIn( self ):
        """ Zoom when a button clicked """
        factor = 1.41 ** (120.0/240.0)
        self.scale( factor, factor )
        return

    def zoomOut( self ):
        """ Zoom when a button clicked """
        factor = 1.41 ** (-120.0/240.0)
        self.scale( factor, factor )
        return

    def wheelEvent( self, event ):
        """ Mouse wheel event """
        if QApplication.keyboardModifiers() == Qt.ControlModifier:
            factor = 1.41 ** ( event.delta() / 240.0 )
            self.scale( factor, factor )
        else:
            QGraphicsView.wheelEvent( self, event )
        return

    def __getImage( self ):
        " Renders the diagram to an image "
        scene = self.scene()
        image = QImage( scene.width(), scene.height(),
                        QImage.Format_ARGB32_Premultiplied )
        painter = QPainter( image )
        # If switched on then rectangles edges will not be sharp
        # painter.setRenderHint( QPainter.Antialiasing )
        scene.render( painter )
        painter.end()
        return image

    def onCopy( self ):
        " Copies the diagram to the exchange buffer "
        QApplication.clipboard().setImage( self.__getImage() )
        return

    def onSaveAs( self, fName ):
        " Saves the rendered image to a file "
        self.__getImage().save( fName, "PNG" )
        return



class ImportDgmTabWidget( QWidget, MainWindowTabWidgetBase ):
    " Widget for an editors manager "

    escapePressed = pyqtSignal()

    def __init__( self, parent = None ):
        MainWindowTabWidgetBase.__init__( self )
        QWidget.__init__( self, parent )

        self.__viewer = DiagramWidget( self )
        self.__viewer.escapePressed.connect( self.__onEsc )

        self.__createLayout()
        return

    def __createLayout( self ):
        " Creates the toolbar and layout "

        # Buttons
        printButton = QAction( PixmapCache().getIcon( 'printer.png' ),
                               'Print', self )
        #printButton.setShortcut( 'Ctrl+' )
        printButton.triggered.connect( self.__onPrint )

        printPreviewButton = QAction( \
                PixmapCache().getIcon( 'printpreview.png' ),
                'Print preview', self )
        #printPreviewButton.setShortcut( 'Ctrl+' )
        printPreviewButton.triggered.connect( self.__onPrintPreview )

        fixedSpacer = QWidget()
        fixedSpacer.setFixedHeight( 16 )

        zoomInButton = QAction( PixmapCache().getIcon( 'zoomin.png' ),
                                'Zoom in (Ctrl+=)', self )
        zoomInButton.setShortcut( 'Ctrl+=' )
        zoomInButton.triggered.connect( self.onZoomIn )

        zoomOutButton = QAction( PixmapCache().getIcon( 'zoomout.png' ),
                                'Zoom out (Ctrl+-)', self )
        zoomOutButton.setShortcut( 'Ctrl+-' )
        zoomOutButton.triggered.connect( self.onZoomOut )

        zoomResetButton = QAction( PixmapCache().getIcon( 'zoomreset.png' ),
                                   'Zoom reset (Ctrl+0)', self )
        zoomResetButton.setShortcut( 'Ctrl+0' )
        zoomResetButton.triggered.connect( self.onZoomReset )


        # Toolbar
        toolbar = QToolBar( self )
        toolbar.setOrientation( Qt.Vertical )
        toolbar.setMovable( False )
        toolbar.setAllowedAreas( Qt.RightToolBarArea )
        toolbar.setIconSize( QSize( 16, 16 ) )
        toolbar.setFixedWidth( 28 )
        toolbar.setContentsMargins( 0, 0, 0, 0 )
        #toolbar.addAction( printPreviewButton )
        #toolbar.addAction( printButton )
        #toolbar.addWidget( fixedSpacer )
        toolbar.addAction( zoomInButton )
        toolbar.addAction( zoomOutButton )
        toolbar.addAction( zoomResetButton )

        hLayout = QHBoxLayout()
        hLayout.setContentsMargins( 0, 0, 0, 0 )
        hLayout.setSpacing( 0 )
        hLayout.addWidget( self.__viewer )
        hLayout.addWidget( toolbar )

        self.setLayout( hLayout )
        return

    def setFocus( self ):
        " Overridden setFocus "
        self.__viewer.setFocus()
        return

    def setScene( self, scene ):
        " Sets the graphics scene to display "
        self.__viewer.setScene( scene )
        return

    def __onPrint( self ):
        " Triggered on the 'print' button "
        pass

    def __onPrintPreview( self ):
        " Triggered on the 'print preview' button "
        pass

    def onZoomIn( self ):
        " Triggered on the 'zoom in' button "
        self.__viewer.zoomIn()
        return

    def onZoomOut( self ):
        " Triggered on the 'zoom out' button "
        self.__viewer.zoomOut()
        return

    def onZoomReset( self ):
        " Triggered on the 'zoom reset' button "
        self.__viewer.resetZoom()
        return

    def __onEsc( self ):
        " Triggered when Esc is pressed "
        self.escapePressed.emit()
        return

    def onCopy( self ):
        " Copies the diagram to the exchange buffer "
        self.__viewer.onCopy()
        return

    def onSaveAs( self, fName ):
        " Saves the diagram into the given file "
        self.__viewer.onSaveAs( fName )
        return


    # Mandatory interface part is below

    def isModified( self ):
        " Tells if the file is modified "
        return False

    def getRWMode( self ):
        " Tells if the file is read only "
        return "RO"

    def getType( self ):
        " Tells the widget type "
        return MainWindowTabWidgetBase.GeneratedDiagram

    def getLanguage( self ):
        " Tells the content language "
        return "Diagram"

    def getFileName( self ):
        " Tells what file name of the widget content "
        return "N/A"

    def setFileName( self, name ):
        " Sets the file name - not applicable"
        raise Exception( "Setting a file name for a diagram is not applicable" )

    def getEol( self ):
        " Tells the EOL style "
        return "N/A"

    def getLine( self ):
        " Tells the cursor line "
        return "N/A"

    def getPos( self ):
        " Tells the cursor column "
        return "N/A"

    def getEncoding( self ):
        " Tells the content encoding "
        return "N/A"

    def setEncoding( self, newEncoding ):
        " Sets the new encoding - not applicable for the diagram viewer "
        return

    def getShortName( self ):
        " Tells the display name "
        return "Imports diagram"

    def setShortName( self, name ):
        " Sets the display name - not applicable "
        raise Exception( "Setting a file name for a diagram is not applicable" )

