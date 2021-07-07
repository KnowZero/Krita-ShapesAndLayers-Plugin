from krita import *
from .ShapesAndLayersSplit import *
from .ShapesAndLayersFontSizeAdjust import *

class ShapesAndLayers(Extension):
    def __init__(self, parent):
        super().__init__(parent) 

    def setup(self):
        pass

    def createActions(self, window):
        action1 = window.createAction("shapesAndLayersSplitShapesFromLayer", "Split Vector Shapes Into Layers...", "Layer/LayerSplitAlpha")
        action1.triggered.connect(self.splitLayer)
        
        
        action2 = window.createAction("shapesAndLayers", "Shapes And Layers", "tools/scripts")
        menu = QtWidgets.QMenu("shapesAndLayers", window.qwindow())
        action2.setMenu(menu)
        
        
        subaction1 = window.createAction("shapesAndLayersfontAdjust", "Adjust Font Sizes...", "tools/scripts/shapesAndLayers")
        subaction1.triggered.connect(self.fontAdjust)

    
    def versionCheck(self):
        if int(Krita.instance().version().split(".")[0]) < 5:
            QtWidgets.QMessageBox.warning(Krita.instance().activeWindow().qwindow(), "Error", "Shapes And Layers extension requires Krita version 5.0 and above")
            return False
        return True
    
    def splitLayer(self):
        if not self.versionCheck(): return
        sl = ShapesAndLayersSplit(self)
        
        result = sl.openDialog()
        if 'error' in result: QtWidgets.QMessageBox.warning(Krita.instance().activeWindow().qwindow(), "Error", result['error'])

    def fontAdjust(self):
        if not self.versionCheck(): return
        sl = ShapesAndLayersFontSizeAdjust(self)
        
        result = sl.openDialog()
        if 'error' in result: QtWidgets.QMessageBox.warning(Krita.instance().activeWindow().qwindow(), "Error", result['error'])


# And add the extension to Krita's list of extensions:
app = Krita.instance()
extension = ShapesAndLayers(parent=app) #instantiate your class
app.addExtension(extension)
