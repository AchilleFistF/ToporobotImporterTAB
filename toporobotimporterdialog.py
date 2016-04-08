# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ToporobotImporterDialog
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

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_toporobotimporter import Ui_ToporobotImporter
from qgis.core import *
from qgis.gui import QgsGenericProjectionSelector
import os.path
import topoReader
import topoDrawer
# create the dialog for zoom to point


class ToporobotImporterDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_ToporobotImporter()
        self.ui.setupUi(self)

    # Below is the code that was not automatically generated

    def show(self):
        ui = self.ui

        # set validators where required
        ui.leSRS.setValidator(QRegExpValidator(QRegExp("(^epsg:{1}\\s*\\d+)|(^\\+proj.*)", Qt.CaseInsensitive), ui.leSRS));

        # connect the buttons to actions
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
        for j in reversed(range(ui.cbDemLayer.count())):
          ui.cbDemLayer.removeItem(j)
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
        self.repaint()

        # now really show
        super(ToporobotImporterDialog, self).show()

    def browseForInToporobotTextFileFunction(self, lineedit):
      return lambda: self.browseForInFile(lineedit, u"Input Toporobot .Text file", u"Toporobot (*.Text);;All (*.*)")

    def browseForInToporobotCoordFileFunction(self, lineedit):
      return lambda: self.browseForInFile(lineedit, u"Input Toporobot .Coord file", u"Toporobot (*.Coord);;All (*.*)")

    def browseForInMergeMappingFileFunction(self, lineedit):
      return lambda: self.browseForInFile(lineedit, u"Input Merge mapping file", u"Comma-separated values (*.csv);;All (*.*)")

    def browseForInFile(self, lineedit, caption, selectedFilter):
      filename = QFileDialog.getOpenFileName(self, caption,".", selectedFilter)
      filepath = QFileInfo(filename).absoluteFilePath()
      if filename:
        lineedit.clear()
        lineedit.insert(filepath)

    def browseForOutShapefile(self, lineedit):
      filename = QFileDialog.getSaveFileName(self, u"Output Shapefile", ".", u"Shapefiles (*.shp)")
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
        self.ui.leSRS.clear()
        self.ui.leSRS.insert(srsSelector.selectedProj4String())


    def done(self, resultCode):
        if resultCode == self.Accepted:
            if self.validateInputs():
                super(ToporobotImporterDialog, self).done(resultCode)
            else:
                pass # stay on the dialog, the user has to correct
        else:
            super(ToporobotImporterDialog, self).done(resultCode)

    def validateInputs(self):
      errorMsgs = []
      ui = self.ui
      if   ui.leToporobotText.text() == "":
        errorMsgs.append(u"The Toporobot .Text file has to be filled")
        #QMessageBox.information(self, self.windowTitle(), "The Toporobot .Text file has to be filled")
      if ui.leToporobotCoord.text() == "":
        errorMsgs.append(u"The Toporobot .Coord file has to be filled")
        #QMessageBox.information(self, self.windowTitle(), "The Toporobot .Coord file has to be filled")
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
        QMessageBox.information(self, self.windowTitle(), u"\n".join(errorMsgs))
        return False
      else:
        return True

