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

" Codimension garbage collector plugin implementation "


import gc, logging, ConfigParser
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QDialog
from plugins.categories.wizardiface import WizardInterface
from configdlg import GCPluginConfigDialog



class GCPlugin( WizardInterface ):
    """ Codimension garbage collector plugin """

    def __init__( self ):
        WizardInterface.__init__( self )
        self.__where = GCPluginConfigDialog.SILENT
        return

    @staticmethod
    def isIDEVersionCompatible( ideVersion ):
        """ Codimension makes this call before activating a plugin.
            The passed ideVersion is a string representing
            the current IDE version.
            True should be returned if the plugin is compatible with the IDE.
        """
        return True

    def activate( self, ideSettings, ideGlobalData ):
        """ The plugin may override the method to do specific
            plugin activation handling.

            ideSettings - reference to the IDE Settings singleton
                          see codimension/src/utils/settings.py
            ideGlobalData - reference to the IDE global settings
                            see codimension/src/utils/globals.py

            Note: if overriden do not forget to call the
                  base class activate() """
        WizardInterface.activate( self, ideSettings, ideGlobalData )

        self.__where = self.__getConfiguredWhere()

        self.connect( self.ide.editorsManager, SIGNAL( 'tabClosed' ),
                      self.__collectGarbage )
        self.ide.project.projectChanged.connect( self.__collectGarbage )
        return

    def deactivate( self ):
        """ The plugin may override the method to do specific
            plugin deactivation handling.
            Note: if overriden do not forget to call the
                  base class deactivate() """

        self.ide.project.projectChanged.disconnect( self.__collectGarbage )
        self.disconnect( self.ide.editorsManager, SIGNAL( 'tabClosed' ),
                         self.__collectGarbage )

        WizardInterface.deactivate( self )
        return

    def getConfigFunction( self ):
        """ The plugin can provide a function which will be called when the
            user requests plugin configuring.
            If a plugin does not require any config parameters then None
            should be returned.
            By default no configuring is required.
        """
        return self.configure

    def populateMainMenu( self, parentMenu ):
        """ The main menu looks as follows:
            Plugins
                - Plugin manager (fixed item)
                - Separator (fixed item)
                - <Plugin #1 name> (this is the parentMenu passed)
                ...
            If no items were populated by the plugin then there will be no
            <Plugin #N name> menu item shown.
            It is suggested to insert plugin configuration item here if so.
        """
        parentMenu.addAction( "Configure", self.configure )
        parentMenu.addAction( "Collect garbage", self.__collectGarbage )
        return

    def populateFileContextMenu( self, parentMenu ):
        """ The file context menu shown in the project viewer window will have
            an item with a plugin name and subitems which are populated here.
            If no items were populated then the plugin menu item will not be
            shown.
            When a callback is called the corresponding menu item will have
            attached data with an absolute path to the item.
        """
        # No file context menu is required
        return

    def populateDirectoryContextMenu( self, parentMenu ):
        """ The directory context menu shown in the project viewer window will have
            an item with a plugin name and subitems which are populated here.
            If no items were populated then the plugin menu item will not be
            shown.
            When a callback is called the corresponding menu item will have
            attached data with an absolute path to the directory.
        """
        # No directory context menu is required
        return

    def populateBufferContextMenu( self, parentMenu ):
        """ The buffer context menu shown for the current edited/viewed file
            will have an item with a plugin name and subitems which are populated here.
            If no items were populated then the plugin menu item will not be
            shown.
            Note: when a buffer context menu is selected by the user it always
                  refers to the current widget. To get access to the current
                  editing widget the plugin can use:
                  self.ide.currentEditorWidget
                  The widget could be of different types and some circumstances should
                  be considered, e.g.:
                  - it could be a new file which has not been saved yet
                  - it could be modified
                  - it could be that the disk file has already been deleted
                  - etc.
                  Having the current widget reference the plugin is able to retrieve
                  the infirmation it needs.
        """
        parentMenu.addAction( "Configure", self.configure )
        parentMenu.addAction( "Collect garbage", self.__collectGarbage )
        return


    def configure( self ):
        " Configures the garbage collector plugin "
        dlg = GCPluginConfigDialog( self.__where )
        if dlg.exec_() == QDialog.Accepted:
            newWhere = dlg.getCheckedOption()
            if newWhere != self.__where:
                self.__where = newWhere
                self.__saveConfiguredWhere()
        return

    def __getConfigFile( self ):
        " Provides a directory name where a configuration is stored "
        return self.ide.settingsDir + "gc.plugin.conf"

    def __getConfiguredWhere( self ):
        " Provides the saved configured value "
        try:
            config = ConfigParser.ConfigParser()
            config.read( [ self.__getConfigFile() ] )
            value = int( config.get( "general", "where" ) )
            if value < GCPluginConfigDialog.SILENT or \
               value > GCPluginConfigDialog.LOG:
                return GCPluginConfigDialog.SILENT
            return value
        except:
            return GCPluginConfigDialog.SILENT

    def __saveConfiguredWhere( self ):
        " Saves the configured where "
        try:
            f = open( self.__getConfigFile(), "w" )
            f.write( "# Autogenerated GC plugin config file\n"
                     "[general]\n"
                     "where=" + str( self.__where ) + "\n" )
            f.close()
        except:
            pass

    def __collectGarbage( self, ignored = None ):
        " Collects garbage "
        collected = []
        l0, l1, l2 = gc.get_count()

        if l0 > 0:
            collected.append( gc.collect( 0 ) )
            if l1 > 0:
                collected.append( gc.collect( 1 ) )
                if l2 > 0:
                    collected.append( gc.collect( 2 ) )

        if self.__where == GCPluginConfigDialog.SILENT:
            return

        message = ""
        if collected:
            for index in xrange( len( collected ) ):
                if collected[ index ] == 0:
                    continue
                if message:
                    message += ", "
                message += "generation " + str( index ) + ": " + \
                           str( collected[ index ] )
            if message:
                message = "GC objects: " + message
        else:
            message = "No GC objects"

        if not message:
            return

        if self.__where == GCPluginConfigDialog.STATUS_BAR:
            # Display it for 5 seconds
            self.ide.showStatusBarMessage( message, 0, 5000 )
        else:
            logging.info( message )
        return

