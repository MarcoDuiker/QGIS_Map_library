# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MapLibrary
                                 A QGIS plugin
 a map library which makes it easy to add much used maps to your project
                               -------------------
        begin                : 2019-02-15
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Marco Duiker - MD-kwadraat
        email                : md@md-kwadraat.nl
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import ast
import os.path
import re
import json
import pathlib
import tempfile

import qgis.PyQt.QtCore
from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion,\
                             QCoreApplication, QUrl, QTimer
from qgis.PyQt.QtGui import QIcon, QDesktopServices
from qgis.PyQt.QtWidgets import QAction, QApplication, QTreeWidget, \
                            QTreeWidgetItem, QMessageBox, QDialogButtonBox, \
                            QCompleter, QFileDialog, QTreeWidgetItemIterator
from qgis.core import Qgis, QgsMessageLog, QgsProject, QgsLayerDefinition, QgsSettings
from qgis.gui import QgsMessageBar

# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the dialogs
from .map_library_dialog import MapLibraryDialog
from .map_library_settings_dialog import MapLibrarySettingsDialog

from .network import networkaccessmanager

import numpy as np

__author__ = 'Marco Duiker MD-kwadraat'
__date__ = 'Februari 2019'

class MapLibrary:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        
        self.iface = iface
        self.settings = QgsSettings()
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QgsSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'MapLibrary_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = MapLibraryDialog()
        self.settings_dlg = MapLibrarySettingsDialog()

        self.actions = []
        self.menu = self.tr(u'&Map Library')

        self.toolbar = self.iface.addToolBar(u'MapLibrary')
        self.toolbar.setObjectName(u'MapLibrary')
        
        self.layerTree_items = [ 
             "name",            # name of category or layer
             "description",     # a short description shown in the lib
                                # used as well for metadata on the layer
             "keywords",        # for searching in the lib
             "connection",      # QGIS data connection string or path to qlr
             "provider",        # QGIS layer provider or `qlr` for qlr files
             "on_select_message",# a message shown when the layer is selected
             "on_load_message",  # a message shown when the layer is loaded
             "metadata_url"     # presented in lib as well as used as identifier
                                # for the layer in the QGIS metadata tab
        ]                       # first two items are shown in tree
                                # rest of the items are hidden
        
        
        # Translate the headers of the treewidget.
        # items are managed manualy in the 'i18n/MapLibrary_{}.ts files'
        # add at least "name" and "description" items with translation to 
        # those files.
        # See the i18n/MapLibrary_nl.ts for an example.
        header_labels = []
        for item in self.layerTree_items:
            header_labels.append(self.tr(item))
            
        self.layerTree = self.dlg.layer_twg
        self.layerTree.setHeaderLabels(header_labels)
        for c in range(2,len(self.layerTree_items)):
            self.layerTree.hideColumn(c)
        self.layerTree.setColumnWidth(0,300)
        
        self.project = QgsProject.instance()
        self.nam = networkaccessmanager.NetworkAccessManager()
        self.library_tree_filled = False
        self.last_search_string = None
        
        # some signals and slots
        self.layerTree.itemSelectionChanged.connect(self.update_buttons)
        self.layerTree.itemDoubleClicked.connect(self.add_layer)
                
        self.layerTree.keyUp.connect(self.on_key_up)
        self.layerTree.keyDown.connect(self.on_key_down)
        self.dlg.search_ldt.textChanged.connect(self.find_next_item)
        self.dlg.search_ldt.returnPressed.connect(self.on_return)
        self.dlg.close_btn.clicked.connect(self.close_dialog)
        self.dlg.add_btn.clicked.connect(self.add_layer)
        self.dlg.metadata_btn.clicked.connect(self.show_metadata)
        
        self.settings_dlg.browse_btn.clicked.connect(self.choose_file)
        
        #enable/ disable buttons
        self.dlg.metadata_btn.setEnabled(False)
        self.dlg.add_btn.setEnabled(False)

        # add a message bar to the dialog for the on select messages
        self.dlg_msg_bar = QgsMessageBar()
        self.dlg.layout().insertWidget(0, self.dlg_msg_bar)

        refresh_interval = self.read_refresh_interval(os.path.join(self.plugin_dir, 'libs', 'libs.json'))
        if refresh_interval is not None:
            self.timer = QTimer()
            self.timer.timeout.connect(self.reload_library)
            self.timer.start(refresh_interval * 60000)

        self.found_items = []
        self.dlgclosed = False

    def read_refresh_interval(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            refresh_interval = data.get('LibrariesRefreshInterval')
            return refresh_interval

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('MapLibrary', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """
        Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToWebMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/map_library/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Map Library'),
            callback=self.run,
            parent=self.iface.mainWindow())
            
        icon_path = ':/plugins/map_library/settings.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Settings'),
            callback=self.run_settings,
            add_to_toolbar=False,
            status_tip=self.tr(u'Map Library settings'),
            parent=self.iface.mainWindow())
                   
        icon_path = ':/plugins/map_library/help.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Help'),
            callback=self.show_help,
            add_to_toolbar=False,
            status_tip=self.tr(u'Show help'),
            parent=self.iface.mainWindow())
            
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr(u'&Map Library'),
                action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar
        if self.timer: self.timer.stop()
        
    def close_dialog(self):
        
        self.layerTree.clear()
        self.library_tree_filled = False
        self.dlg.close()
        self.dlgclosed = True # set a flag to know, that the dialog is closed (and needs to be refilled when reopen it)

    def reload_library(self):
        
        if self.dlg.isVisible():
            self.layerTree.clear()
            self.library_tree_filled = False
            self.run()
       
    def find_next_item(self):
        '''
        Finds search string in tree view
        '''
        self.tree_items = []
        self.dlg.search_ldt.setStyleSheet("QLineEdit {color: black;}")

        # Iterate over all tree items for new search
        it = QTreeWidgetItemIterator(self.layerTree)
        while it.value():
            item = it.value()
            item.setHidden(False)
            self.layerTree.expandItem(item)
            self.tree_items.append(item)
            it += 1

        searchString = self.dlg.search_ldt.text()

        # Reset search and filtering for short search strings
        if len(searchString) < 3:
            for item in self.tree_items:
                item.setHidden(False)
                self.layerTree.collapseItem(item)                
            return

        # Get search results
        if not self.last_search_string == searchString: 
            self.last_search_string = searchString
            self.search_index = 0
            self.found_items = []
            for column in range(0,len(self.layerTree_items)):
                self.found_items = self.found_items + self.layerTree.findItems(
                    searchString, 
                    QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive, 
                    column)

            self.found_items = self.get_unique_found_items(self.found_items)
            if self.found_items:
                self.layerTree.setCurrentItem(self.found_items[self.search_index])
            else:
                self.dlg.search_ldt.setStyleSheet("QLineEdit {color: red;}")
        else:
            try:
                self.layerTree.setCurrentItem(self.found_items[self.search_index])
            except:
                self.dlg.search_ldt.setStyleSheet("QLineEdit {color: red;}")

        if self.valueToBool(self.settings.value("MapLibrary/filter", False)):
            # Filter search results
            if self.found_items:
                self.items_to_hide = np.setdiff1d(
                    self.tree_items,
                    self.found_items)
                # Hide items
                for item in self.tree_items:
                    self.hide_item_and_children(item)        

    def get_unique_found_items(self,found_items):
        indexes = np.unique(found_items, return_index=True)[1]
        return[found_items[index] for index in sorted(indexes)]

    def hide_item_and_children(self,item):
        if item.childCount() == 0:
            if item in self.items_to_hide:
                item.setHidden(True)
        else:
            if self.are_all_children_hidden(item):
                if item in self.items_to_hide:
                    item.setHidden(True)
            else:
                for n in range(0, item.childCount()):
                    self.hide_item_and_children(item.child(n))
                    if n == item.childCount()-1:
                        if self.are_all_children_hidden(item):
                            if item in self.items_to_hide:
                                item.setHidden(True)
                   
    def are_all_children_hidden(self, item):
        for n in range(0, item.childCount()):
            if not item.child(n).isHidden():
                return False
        return True
    
    def go_to_next_result(self):
        if self.valueToBool(self.settings.value("MapLibrary/filter", False)):
            self.layerTree.setCurrentItem(self.layerTree.itemBelow(self.layerTree.currentItem()))
        else:
            try:
                self.search_index = self.search_index + 1
                self.layerTree.setCurrentItem(
                    self.found_items[self.search_index])
            except:
                self.search_index = 0
                self.layerTree.setCurrentItem(
                    self.found_items[self.search_index])

    def props_from_tree_item(self, item):
        '''
        Creates a dict from the columns in the layerTree widget
        '''
        
        d = {}
        for i,key in enumerate(self.layerTree_items):
            d[key] = item.text(i)
        return d
           
    def update_buttons(self):
        '''
        Updates the buttons on selection change.
        '''
        
        if not self.layerTree.selectedItems():
            return

        layer_props = self.props_from_tree_item(self.layerTree.selectedItems()[0])
        
        if layer_props["provider"]:
            self.dlg.add_btn.setEnabled(True)
        else:
            self.dlg.add_btn.setEnabled(False)
        if layer_props['metadata_url']:
            self.dlg.metadata_btn.setEnabled(True)
        else:
            self.dlg.metadata_btn.setEnabled(False)

        if layer_props['on_select_message']:
            self.show_layer_message(layer_props['on_select_message'], 'select')
            
    def get_text_contents_from_path(self, path):
        '''
        Gets the text content from a path.
        May be a local path, or an url
        '''
        
        txt = None
        if path[0:4].lower() == 'http':
            QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            try:
                (response, content) = self.nam.request(path)
                txt = content.decode("utf-8")
            except Exception as e:
                self.iface.messageBar().pushMessage("Error",
                    self.tr(u'Reading file ') + path + 
                    self.tr(u'failed. ') +
                    self.tr(u'See message log for more info.'), 
                    level = Qgis.Critical)
                QgsMessageLog.logMessage(u'Error reading file ' + str(e), 'Map Library')    
            finally:
                QApplication.restoreOverrideCursor()
        else:
            if (not os.path.exists(path)) \
            and os.path.exists(os.path.join(self.plugin_dir, path)):
               # path is relative to plugin dir
               path = os.path.join(self.plugin_dir, path)
            try:
                with open(path,'r',encoding='utf-8') as f:
                    txt = f.read()
            except Exception as e:
                self.iface.messageBar().pushMessage("Error",
                    self.tr(u'Reading file ') + path + 
                    self.tr(u'failed. ') +
                    self.tr(u'See message log for more info.'), 
                    level = Qgis.Critical)
                QgsMessageLog.logMessage(u'Error reading file ' + str(e), 'Map Library')
        return txt
        
    def show_metadata(self):
        '''
        Shows the metadata of a layer in the browser
        '''
        
        selectedItem = self.layerTree.selectedItems()[0]
        layer_props = self.props_from_tree_item(selectedItem)
        
        QDesktopServices().openUrl(QUrl(layer_props['metadata_url']))
        

    def add_layer_by_connection(self, layer_props):
        '''
        Adds chosen layer to project by means of a connection string
        '''
        
        supported_vector_providers = ["delimitedtext","gpx","ogr","postgres",
                                      "spatialite","WFS"]
        supported_raster_providers = ["gdal","wcs","wms"]
        
        layer = None
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        if layer_props['provider'] in supported_vector_providers:
            if not layer_props['provider'].lower() == "wfs":
                # we have a file. might be local to plugin folder
                if not os.path.exists(layer_props['connection']) \
                and os.path.exists(os.path.join(self.plugin_dir,
                                                layer_props['connection'])):
                        path = os.path.join(self.plugin_dir,
                                            layer_props['connection'])
                else:
                    path = layer_props['connection']
            try:
                layer = self.iface.addVectorLayer(path, 
                                                  layer_props['name'], 
                                                  layer_props['provider'])
            except Exception as e:
                self.iface.messageBar().pushMessage("Error",
                    self.tr(u'Loading layer failed. ') + 
                    self.tr(u'See message log for more info.'), 
                    level = Qgis.Critical)
                QgsMessageLog.logMessage(u'Loading vector layer failed: ' + str(e), 
                                          'Map Library')
            finally:
                QApplication.restoreOverrideCursor()
        elif layer_props['provider'] in supported_raster_providers:
            try:
                if layer_props['provider'].lower() == 'gdal':
                    layer = self.iface.addRasterLayer(layer_props['connection'], 
                                                      layer_props['name'])
                else:
                    layer = self.iface.addRasterLayer(layer_props['connection'], 
                                                      layer_props['name'],
                                                      layer_props['provider'])
            except Exception as e:
                self.iface.messageBar().pushMessage("Error",
                    self.tr(u'Loading layer failed. ') + 
                    self.tr(u'See message log for more info.'), 
                    level = Qgis.Critical)
                QgsMessageLog.logMessage(u'Loading raster layer failed: ' + str(e), 
                                          'Map Library')
            finally:
                QApplication.restoreOverrideCursor()
        else:
            QApplication.restoreOverrideCursor()
            self.iface.messageBar().pushMessage("Error",
                self.tr(u'Loading layer failed. '), 
                self.tr(u'Layer provider "') + layer_props['provider'] + \
                    self.tr(u'" not supported.'), 
                level = Qgis.Critical)
            return

        if not layer or not layer.isValid():
            self.iface.messageBar().pushMessage("Error",
                self.tr(u'Loading layer failed. '), 
                level = Qgis.Critical)
                

    def add_layer_by_qlr(self, layer_props):
        '''
        Adds chosen layer to project by a local or remote qlr file
        '''

        path = None
        if not layer_props['connection'][0:4].lower() == 'http':
            path = layer_props['connection']
            if (not os.path.exists(path)) \
            and os.path.exists(os.path.join(self.plugin_dir, path)):
               # path is relative to plugin dir
               # WE SHOULD MAKE THSI RELATIVE TO current_library.json
               path = os.path.join(self.plugin_dir, path)
            if not os.path.exists(path):
                # we don't get exceptions then
                self.iface.messageBar().pushMessage("Error",
                    self.tr(u'Loading layer failed. ') +
                    self.tr(u'See message log for more info.'), 
                    level = Qgis.Critical)
                QgsMessageLog.logMessage(u'Loading layer failed. ' +
                                         u'File not found: ' + str(path), 
                                         'Map Library')
                return
        else:      
            # the python bindings do not work with a QDomDocument :-(
            # we might start using this cache folder to our advantage,
            # by looking up in the cache first.
            try:
                qlr_content = self.get_text_contents_from_path(
                                    layer_props['connection'])
                path = os.path.join(self.plugin_dir,'libs','cache',
                                    os.path.basename(layer_props['connection']))
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(qlr_content)
            except Exception as e:
                self.iface.messageBar().pushMessage("Error",
                    self.tr(u'Loading layer failed. ') + 
                    self.tr(u'See message log for more info.'), 
                    level = Qgis.Critical)
                QgsMessageLog.logMessage(u'Loading layer from qlr failed: ' + str(e), 
                                          'Map Library')
                return
        if path:
            QgsLayerDefinition.loadLayerDefinition(
                    path, 
                    self.project, 
                    self.project.layerTreeRoot())
                

    def add_layer(self, item = None, column = None):
        '''
        Adds chosen layer to the project
        '''
        
        selectedItem = self.layerTree.selectedItems()[0]
        layer_props = self.props_from_tree_item(selectedItem)
        
        QgsMessageLog.logMessage(u'Adding layer ' + str(layer_props), 
                                          'Map Library')
        
        if layer_props:
            if layer_props['provider'].lower() == 'qlr':
                self.add_layer_by_qlr(layer_props)
            else:
                self.add_layer_by_connection(layer_props)

            if layer_props['on_load_message']:
                self.show_layer_message(layer_props['on_load_message'], 'load')
                
            # we might add something here for a "most recent layers" section
            # this should be persistent between sessions, so added to QgsSettings
            # dataFromChild()
            # dataToChild()
            # selectedItemCopy = selectedItem.clone()
            
            #def writeSettings(self):
                #settings = QtCore.QgsSettings()
                #settings.beginGroup("TreeWidget")
                #settings.setValue("items", TreeWidget.dataFromChild(
                #                               self.invisibleRootItem()))
                #settings.endGroup()

    def show_layer_message(self, message, context):
        '''
        Shows a message bar in either the map view or the dialog,
        based on the defined layer properties and the context.

        context = select: message bar in dialog
        contect = load: the main message bar
        '''

        levels = {  'Info':         Qgis.Info,
                    'Warning':      Qgis.Warning,
                    'Critical':     Qgis.Critical,
                    'Succes':       Qgis.Success
        }

        level = 'Info'
        duration = 0
        
        if message.startswith('{') and message.endswith('}'):
            # create a dict from this string
            try:
                message = ast.literal_eval(message)
            except:
                QgsMessageLog.logMessage(u'Error interpreting message definition %s.' % message, 
                                          'Map Library') 
                
        if type(message) == str:
            msg = message
        else:
            if 'msg' in message:
                msg = message['msg']
            else:
                QgsMessageLog.logMessage(u'Error showing message; Message string not found.', 
                                          'Map Library') 
            if 'level' in message:
                QgsMessageLog.logMessage(u'Error in message level; level %s not defined.' % level, 
                                          'Map Library') 
                level =  message['level']
            if 'duration' in message \
            and type(message['duration']) == int:
                duration = message['duration']
        
        if not level in levels:
            level = 'Info'

        if context == 'select':
            self.dlg_msg_bar.pushMessage( msg, 
                                          level=levels[level], 
                                          duration=duration )  
        if context == 'load':
            self.iface.messageBar().pushMessage(  msg, 
                                                  level=levels[level], 
                                                  duration=duration )  


    def add_lib_to_tree(self, name, path):
        '''
        Loads a lib into the lib tree.
        Returns all keys, values and the like as entries for wordlist completer
        '''
        
        def fill_tree(item, value):
            '''
            fills the treeview from the json tree definition
            '''

            def new_item(parent, text, val = None, meta_items = []):
                child = QTreeWidgetItem( [text] + meta_items)
                if not ("connection" in meta_items and "provider" in meta_items):
                    # we have no layer
                    fill_tree(child, val)
                parent.addChild(child)
                
            if value is None: 
                return
            elif isinstance(value, dict):
                if self.valueToBool(self.settings.value("MapLibrary/sort", True)):
                    items = sorted(value.items())
                else:
                    items = value.items()
                #for key, val in sorted(value.items()):
                for key, val in items:
                    meta_items = []
                    if "description" in val or ("connection" in val and "provider" in val):
                        # we have a description on a group or a layer
                        for key_name in self.layerTree_items[1:]:
                            if key_name in val:
                                if isinstance(val[key_name], (list, tuple)):
                                    meta_items.append(",".join(val[key_name]))
                                elif isinstance(val[key_name], (dict)):
                                    # sadly we cannot insert a dict here, so we
                                    # convert it to a string. Later we need to reverse!
                                    meta_items.append(str(val[key_name]))
                                else:
                                    meta_items.append(val[key_name])
                            else:
                                meta_items.append("")
                        new_item(item, str(key), val, meta_items)
                    elif not key in self.layerTree_items[1:]:
                        # skip these items, they always belong in the columns 1:
                        new_item(item, str(key), val)
            elif isinstance(value, (list, tuple)):
                for val in value:
                    text = (str(val) if not isinstance(val, (dict, list, tuple))
                            else '[%s]' % type(val).__name__)
                    new_item(item, text, val) 
            else:
                new_item(item, str(value))

        json_tree = self.get_text_contents_from_path(path)
        tree = json.loads(json_tree)
        fill_tree(self.layerTree.invisibleRootItem(), {name: tree})
        
        return re.split(r'\s+', re.sub(r'[{:}\[\],\`\"]', ' ', json_tree).strip())

    def run(self):
        """
        Load the library tree, and show it to the user.
        
        We do this only once on opening the dialog, so we keep plugin load time
        low.
        """   
        self.layerTree.clear()
        if not self.library_tree_filled or self.dlgclosed or not self.dlg.isVisible():
            libs_def_file = self.settings.value("MapLibrary/lib_path", None)
            if not libs_def_file:
                libs_def_file = os.path.join(self.plugin_dir, 'libs', 'libs.json')

            word_list = []
            try:
                json_tree = self.get_text_contents_from_path(libs_def_file)
                libs = json.loads(json_tree)
                for name, path in libs.items():
                    if not name == "LibrariesRefreshInterval":
                        word_list = word_list + self.add_lib_to_tree(name, path)
                completer = QCompleter(set([x.lower() for x in word_list]))
                completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
                self.dlg.search_ldt.setCompleter(completer)
                self.library_tree_filled = True
            except Exception as e:
                self.iface.messageBar().pushMessage("Error",
                    self.tr(u'Initializing Library failed. ') + 
                    self.tr(u'See message log for more info.'), 
                    level = Qgis.Critical)
                QgsMessageLog.logMessage(u'Error Initializing Library ' + str(e), 
                                        'Map Library')
                        
            self.dlg.show()


    def choose_file(self):
        '''
        Allows the user to choose a local path for the lib.
        '''
        
        path = QFileDialog.getOpenFileName(
                    caption = self.tr(u"Select Map Library:"), 
                    directory = os.path.join(self.plugin_dir, 'libs'), 
                    filter = '*.json')[0]       
        self.settings_dlg.lib_path_ldt.setText(path)
        # we might make this a relative path to the plugin dir, 
        # but why bother?


    def run_settings(self):
        '''
        Shows the settings dialog
        '''
        # Close main dialog and reset search string before editing settings dialog to force reload
        self.close_dialog()
        self.last_search_string = ""
        self.dlg.search_ldt.setText("")

        self.settings_dlg.sort_cbx.setChecked(self.valueToBool(self.settings.value(
            "MapLibrary/sort", True)))
        self.settings_dlg.filter_cbx.setChecked(self.valueToBool(self.settings.value(
            "MapLibrary/filter", False)))
        self.settings_dlg.lib_path_ldt.setText(self.settings.value(
            "MapLibrary/lib_path", ""))
        if self.settings_dlg.lib_path_ldt.text() == "":
            self.settings_dlg.lib_path_ldt.setPlaceholderText("https://")
        self.settings_dlg.show()
        
        result = self.settings_dlg.exec_()
        if result:
            self.layerTree.clear()
            self.library_tree_filled = False
            path = unicode(self.settings_dlg.lib_path_ldt.text())
            if path[0:4] == 'http':
                # urlEncode?
                pass
            else:
                # make more canonical?
                pass
            self.settings.setValue("MapLibrary/lib_path", path)
            self.settings.setValue("MapLibrary/sort", 
                                   self.settings_dlg.sort_cbx.isChecked())
            self.settings.setValue("MapLibrary/filter", 
                                   self.settings_dlg.filter_cbx.isChecked())

    @staticmethod
    def valueToBool(value):
        if isinstance(value, bool):
            return value
        else:
            return value.lower() == 'true'

    def show_help(self):
        '''
        Shows the help
        '''

        QDesktopServices().openUrl(QUrl.fromLocalFile( \
            os.path.join("file://", self.plugin_dir, 'help/build/html', \
                         'index.html')))

    def on_key_up(self):
        if self.valueToBool(self.settings.value("MapLibrary/filter", False)):
            self.layerTree.setCurrentItem(self.layerTree.itemAbove(self.layerTree.currentItem()))

    def on_key_down(self):
        if self.valueToBool(self.settings.value("MapLibrary/filter", False)):
            self.go_to_next_result()
    
    def on_return(self):
        if self.valueToBool(self.settings.value("MapLibrary/filter", False)):
            if not self.layerTree.hasFocus():
                self.layerTree.setFocus()
                self.search_index = - 1
        self.go_to_next_result()
