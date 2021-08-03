from krita import *
from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg, uic
import re
from xml.dom import minidom

class ShapesAndLayersLayerStylesClipboard():
    def __init__(self, caller, parent = None):
        super().__init__()
      
        settingsList = Krita.instance().readSetting("", "shapesandlayersCopyLayerStyles","").split(',')
        self.settings = { 'enabled': True } if len(settingsList) < 2 else { settingsList[i]: int(settingsList[i + 1]) for i in range(0, len(settingsList), 2) }  
        
        self.layerStyleClipboard = None
        self.layerStyleRemove = None
        
        self.pasteAction = None
        

    def onLoad(self, window):
        qwin = window.qwindow()
        self.bindMenuItem(window)
        if self.settings['enabled']:
            pass
        
    
    def bindMenuItem(self,window):
        qwin = window.qwindow()
        #qwin = Krita.instance().activeWindow().qwindow()
        box = qwin.findChild(QtWidgets.QDockWidget, "KisLayerBox")

        action = window.createAction("shapesAndLayersStyles", "Layer Style Clipboard", "Layer")
        menu = QtWidgets.QMenu("shapesAndLayersStyles", window.qwindow())
        action.setMenu(menu)
        
        subaction1 = window.createAction("shapesAndLayersCopyLayerStyle", "Copy Layer Style", "Layer/shapesAndLayersStyles")
        subaction1.triggered.connect(self.copyLayerStyle)
        self.pasteAction = window.createAction("shapesAndLayersPasteLayerStyle", "Paste Layer Style", "Layer/shapesAndLayersStyles")
        self.pasteAction.triggered.connect(self.pasteLayerStyle)
        subaction3 = window.createAction("shapesAndLayersCutLayerStyle", "Cut Layer Style", "Layer/shapesAndLayersStyles")
        subaction3.triggered.connect(self.cutLayerStyle)
        subaction4 = window.createAction("shapesAndLayersClearLayerStyle", "Clear Layer Style", "Layer/shapesAndLayersStyles")
        subaction4.triggered.connect(self.clearLayerStyle)


    def cutLayerStyle(self):
        doc = Krita.instance().activeDocument()
        node = doc.activeNode()
        
        self.layerStyleClipboard = node.layerStyleToAsl()
        self.layerStyleRemove = node
        self.pasteAction.setText("Paste Layer Style ["+node.name()+"]")
    
    def copyLayerStyle(self):
        doc = Krita.instance().activeDocument()
        node = doc.activeNode()
        
        self.layerStyleClipboard = node.layerStyleToAsl()
        self.pasteAction.setText("Paste Layer Style ["+node.name()+"]")

    def pasteLayerStyle(self):
        doc = Krita.instance().activeDocument()
        node = doc.activeNode()
        
        node.setLayerStyleFromAsl(self.layerStyleClipboard)
        
        if self.layerStyleRemove is not None:
            self.layerStyleRemove.setLayerStyleFromAsl('<asl><node type="Descriptor" name="" classId="null"></node></asl>')
            self.layerStyleRemove = None

    def clearLayerStyle(self):
        doc = Krita.instance().activeDocument()
        node = doc.activeNode()
        
        node.setLayerStyleFromAsl('<asl><node type="Descriptor" name="" classId="null"></node></asl>')

