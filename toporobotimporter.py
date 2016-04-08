# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ToporobotImporter
                                 A QGIS plugin
 Imports Cave galleries from Toporobot 
                              -------------------
        begin                : 2014-01-04
        copyright            : (C) 2014 by Florian Hof
        email                : florian@speleo.ch
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import QgsGenericProjectionSelector
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from toporobotimporterdialog import ToporobotImporterDialog
import os.path
import topoReader
import topoDrawer


class ToporobotImporter:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'toporobotimporter_{0}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = ToporobotImporterDialog()

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/toporobotimporter/icon.png"),
            u"Toporobot Importer", self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Toporobot Importer", self.action)

        self.initGuiOfToporobotImporter()

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&Toporobot Importer", self.action)
        self.iface.removeToolBarIcon(self.action)

    # run method that performs all the real work
    def run(self):
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = 1 #self.dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code)
            pass

    # Below is the code that was not automatically generated
    
    def accept(self): # Called when "OK" button is pressed
        self.validateInputs()

    def initGuiOfToporobotImporter(self):
        ui = self.dlg.ui

        # set validators where required
        ui.leSRS.setValidator(QRegExpValidator(QRegExp("(^epsg:{1}\\s*\\d+)|(^\\+proj.*)", Qt.CaseInsensitive), ui.leSRS));
        
        # connect the buttons to actions
        QObject.connect(self.dlg, SIGNAL("accepted()"), self.accept)
        QObject.connect(ui.bBrowseToporobotText, SIGNAL("clicked()"), self.browseForInToporobotTextFileFunction(ui.leToporobotText))
        QObject.connect(ui.bBrowseToporobotCoord, SIGNAL("clicked()"), self.browseForInToporobotCoordFileFunction(ui.leToporobotCoord))
        QObject.connect(ui.bBrowseMergeMapping, SIGNAL("clicked()"), self.browseForInMergeMappingFileFunction(ui.leMergeMapping))
        self.outShapeFileFormWidgets = [
          (ui.leOutPoints, ui.bBrowseOutPoints, topoDrawer.StationsDrawer()),
          (ui.leOutAims, ui.bBrowseOutAims, topoDrawer.AimsDrawer()),
          (ui.leOutAimsSurface, ui.bBrowseOutAimsSurface, topoDrawer.AimsSurfaceDrawer()),
          (ui.leOutSeries, ui.bBrowseOutSeries, topoDrawer.SeriesDrawer()),
          (ui.leOutSeriesBorder, ui.bBrowseOutSeriesBorder, topoDrawer.SeriesSurfaceDrawer())]
        for (lineedit, button, drawer) in self.outShapeFileFormWidgets:
          QObject.connect(button, SIGNAL("clicked()"), self.browseForOutShapefileFunction(lineedit))
        QObject.connect(ui.bSRS, SIGNAL("clicked()"), self.browseForSRS)

        # init the dropdown with the possibly DEM layers
        self.rasterlayerband = [(-1, None, -1, '')]
        ui.cbDemLayer.addItem('----------');
        i = -1
        for layer in QgsMapLayerRegistry.instance().mapLayers().values():
          i = i + 1
          if layer.type() == layer.RasterLayer:
            if layer.bandCount() == 1: # first the one-band images, so should be a DEM
                self.rasterlayerband.append((i, layer, 1, layer.bandName(1)))
                ui.cbDemLayer.addItem(layer.name());
        i = -1
        for layer in QgsMapLayerRegistry.instance().mapLayers().values():
          i = i + 1
          if layer.type() == layer.RasterLayer:
            if layer.bandCount() > 1: # then the multi-bands images, just in case
              for j in range(layer.bandCount()):
                self.rasterlayerband.append((i, layer, j+1, layer.bandName(j+1)))
                ui.cbDemLayer.addItem(layer.name() + ' / ' + layer.bandName(j+1));
        ui.cbDemLayer.setCurrentIndex(0)
        self.dlg.repaint()
        
        
    def browseForInToporobotTextFileFunction(self, lineedit):
      return lambda: self.browseForInFile(lineedit, u"Input Toporobot .Text file", u"Toporobot (*.Text);;All (*.*)")

    def browseForInToporobotCoordFileFunction(self, lineedit):
      return lambda: self.browseForInFile(lineedit, u"Input Toporobot .Coord file", u"Toporobot (*.Coord);;All (*.*)")

    def browseForInMergeMappingFileFunction(self, lineedit):
      return lambda: self.browseForInFile(lineedit, u"Input Merge mapping file", u"Comma-separated values (*.csv);;All (*.*)")

    def browseForInFile(self, lineedit, caption, selectedFilter):
      filename = QFileDialog.getOpenFileName(self.dlg, caption,".", selectedFilter)
      filepath = QFileInfo(filename).absoluteFilePath()
      if filename:
        lineedit.clear()
        lineedit.insert(filepath)

    def browseForOutShapefile(self, lineedit):
      filename = QFileDialog.getSaveFileName(self.dlg, u"Output Shapefile", ".", u"Shapefiles (*.shp)")
      filepath = QFileInfo(filename).absoluteFilePath()
      if not filepath.lower().endswith(".shp"):
        filepath = filepath + ".shp"
      if filename:
        lineedit.clear()
        lineedit.insert(filepath)

    def browseForOutShapefileFunction(self, lineedit):
      return lambda: self.browseForOutShapefile(lineedit)

    def browseForSRS(self):
      srsSelector = QgsGenericProjectionSelector(self)
      srsSelector.setSelectedCrsName(self.leSRS.text())
      if srsSelector.exec_():
        self.dlg.ui.leSRS.clear()
        self.dlg.ui.leSRS.insert(srsSelector.selectedProj4String())
        
    def validateInputs(self):
      errorMsgs = []
      ui = self.dlg.ui
      if   ui.leToporobotText.text() == "":
        errorMsgs.append(u"The Toporobot .Text file has to be filled")
        #QMessageBox.information(self, self.dlg.windowTitle(), "The Toporobot .Text file has to be filled")
      if ui.leToporobotCoord.text() == "":
        errorMsgs.append(u"The Toporobot .Coord file has to be filled")
        #QMessageBox.information(self, self.dlg.windowTitle(), "The Toporobot .Coord file has to be filled")
      #elif self.cbAppend.checkState() == Qt.Checked and self.cbShowPoints.checkState() == Qt.Unchecked:
      #  QMessageBox.information(self, self.windowTitle(), u"Cannot append to an existing file if \""+unicode(self.cbShowPoints.text())+u"\" is not checked")
      nbOutFiles = 0
      for (lineedit, button, drawer) in self.outShapeFileFormWidgets:
        if lineedit.text() != "":
          outPath = lineedit.text()
          nbOutFiles += 1
          correspondingShownLayer = None
          for layer in QgsMapLayerRegistry.instance().mapLayers().values():
            if os.path.abspath(unicode(layer.source())) == os.path.abspath(unicode(outPath)):
              correspondingShownLayer = layer
              break
          if ui.rbOverride.isChecked():
            #if correspondingShownLayer is None:
            #  QMessageBox.information(self, self.windowTitle(), u"Cannot append to the file \""+unicode(outPath)+u"\" because it is not loaded in QGIS")
            if correspondingShownLayer is not None and correspondingShownLayer.wkbType() <> drawer.wkbType():
              errorMsgs.append(u"Cannot append to the file \""+unicode(outPath)+u"\" because its type is not compatible")
      if nbOutFiles == 0:
        errorMsgs.append(u"No output shapefile has been filled")
        #QMessageBox.information(self, self.windowTitle(), u"No output shapefile has been filled")
      if len(errorMsgs) > 0:
        QMessageBox.information(self.dlg, self.dlg.windowTitle(), u"\n".join(errorMsgs))
        return False
      else:
        return True
