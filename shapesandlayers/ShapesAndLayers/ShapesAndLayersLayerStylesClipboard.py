from krita import *
from PyQt5 import QtWidgets

class ShapesAndLayersLayerStylesClipboard():
    def __init__(self, caller, parent = None):
        super().__init__()
      
        settingsList = Krita.instance().readSetting("", "shapesandlayersLayerStylesClipboard","").split(',')
        self.settings = { 'enabled': True } if len(settingsList) < 2 else { settingsList[i]: int(settingsList[i + 1]) for i in range(0, len(settingsList), 2) }  
        
        self.layerStyleClipboard = None
        self.layerStyleRemove = None
        
        self.pasteAction = None
        
        self.subActions = {}
        

    def onLoad(self, window):
        qwin = window.qwindow()
        self.bindMenuItem(window)
        if self.settings['enabled']:
            pass
        
    
    def bindMenuItem(self,window):
        qwin = window.qwindow()
        #qwin = Krita.instance().activeWindow().qwindow()
        box = qwin.findChild(QtWidgets.QDockWidget, "KisLayerBox")

        action = window.createAction("shapesandlayersLayerStylesClipboard", "Layer Style Clipboard", "Layer")
        menu = QtWidgets.QMenu("shapesAndLayersLayerStyles", window.qwindow())
        action.setMenu(menu)
        
        
        self.subActions['copy'] = window.createAction("shapesAndLayersCopyLayerStyle", "Copy Layer Style", "Layer/shapesandlayersLayerStylesClipboard")
        self.subActions['copy'].triggered.connect(self.copyLayerStyle)
        self.subActions['paste'] = window.createAction("shapesAndLayersPasteLayerStyle", "Paste Layer Style", "Layer/shapesandlayersLayerStylesClipboard")
        self.subActions['paste'].triggered.connect(self.pasteLayerStyle)
        self.subActions['cut'] = window.createAction("shapesAndLayersCutLayerStyle", "Cut Layer Style", "Layer/shapesandlayersLayerStylesClipboard")
        self.subActions['cut'].triggered.connect(self.cutLayerStyle)
        self.subActions['clear'] = window.createAction("shapesAndLayersClearLayerStyle", "Clear Layer Style", "Layer/shapesandlayersLayerStylesClipboard")
        self.subActions['clear'].triggered.connect(self.clearLayerStyle)
        
        action.hovered.connect(self.checkActiveLayer)

    def checkActiveLayer(self):
        if not self.subActions['copy'].isEnabled():
            if Krita.instance().activeDocument().activeNode().type().endswith('layer'):
                self.subActions['copy'].setEnabled(True)
                self.subActions['paste'].setEnabled(True)
                self.subActions['cut'].setEnabled(True)
                self.subActions['clear'].setEnabled(True)

    def cutLayerStyle(self):
        doc = Krita.instance().activeDocument()
        node = doc.activeNode()
        
        self.layerStyleClipboard = node.layerStyleToAsl()
        self.layerStyleRemove = node
        self.subActions['paste'].setText("Paste Layer Style ["+node.name()+"]")
    
    def copyLayerStyle(self):
        doc = Krita.instance().activeDocument()
        node = doc.activeNode()
        
        self.layerStyleClipboard = node.layerStyleToAsl()
        self.subActions['paste'].setText("Paste Layer Style ["+node.name()+"]")

    def pasteLayerStyle(self):
        win = Krita.instance().activeWindow()
        view = win.activeView()
        
        for node in view.selectedNodes():
            node.setLayerStyleFromAsl(self.layerStyleClipboard)
        
        if self.layerStyleRemove is not None:
            self.layerStyleRemove.setLayerStyleFromAsl('<asl><node type="Descriptor" name="" classId="null"></node></asl>')
            self.layerStyleRemove = None

    def clearLayerStyle(self):
        doc = Krita.instance().activeDocument()
        node = doc.activeNode()
        
        node.setLayerStyleFromAsl('<asl><node type="Descriptor" name="" classId="null"></node></asl>')

