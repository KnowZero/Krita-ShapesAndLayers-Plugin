from krita import *
from .ShapesAndLayersSplit import *
from .ShapesAndLayersFontSizeAdjust import *
from .ShapesAndLayersVisibilityHelper import *
from .ShapesAndLayersLayerStylesClipboard import *
from .ShapesAndLayersHideDockWindowTitlebar import *
from .ShapesAndLayersFontManagerHelper import *
from .ShapesAndLayersShowEraser import *
from .ShapesAndLayersShapesAsLayers import *
from .ShapesAndLayersSelectionArrangeDocker import *

class ShapesAndLayers(Extension):
    def __init__(self, parent):
        super().__init__(parent) 
        if int(Krita.instance().version().split(".")[0]) >= 5:
            self.visibilityHelper = ShapesAndLayersVisibilityHelper(self)
            self.layerStylesClipboard = ShapesAndLayersLayerStylesClipboard(self)
            self.hideDockWindowTitlebar = ShapesAndLayersHideDockWindowTitlebar(self)
            self.fontManagerHelper = ShapesAndLayersFontManagerHelper(self)
            self.showEraser = ShapesAndLayersShowEraser(self)

    def setup(self):
        pass

    def createActions(self, window):
        if int(Krita.instance().version().split(".")[0]) >= 5:
            action1 = window.createAction("shapesAndLayersSplitShapesFromLayer", "Split Vector Shapes Into Layers...", "Layer/LayerSplitAlpha")
            action1.triggered.connect(self.slotSplitLayer)
        
            action2 = window.createAction("shapesAndLayers", "Shapes And Layers", "tools/scripts")
            menu = QtWidgets.QMenu("shapesAndLayers", window.qwindow())
            action2.setMenu(menu)
        
            subaction1 = window.createAction("shapesAndLayersFontAdjust", "Adjust Font Sizes...", "tools/scripts/shapesAndLayers")
            subaction1.triggered.connect(self.slotFontAdjust)

            self.visibilityHelper.onLoad(window)
            self.layerStylesClipboard.onLoad(window)
            self.hideDockWindowTitlebar.onLoad(window)
            self.fontManagerHelper.onLoad(window)
            self.showEraser.onLoad(window)

    
    def versionCheck(self):
        if int(Krita.instance().version().split(".")[0]) < 5:
            QtWidgets.QMessageBox.warning(Krita.instance().activeWindow().qwindow(), "Error", "Shapes And Layers extension requires Krita version 5.0 and above")
            return False
        return True
    
    def slotSplitLayer(self):
        if not self.versionCheck(): return
        sl = ShapesAndLayersSplit(self)
        
        result = sl.openDialog()
        self.errCheck(result)

    def slotFontAdjust(self):
        if not self.versionCheck(): return
        fsa = ShapesAndLayersFontSizeAdjust(self)
        
        result = fsa.openDialog()
        self.errCheck(result)


        
    def errCheck(self, result):
        if 'error' in result:
            QtWidgets.QMessageBox.warning(Krita.instance().activeWindow().qwindow(), "Error", result['error'])

# And add the extension to Krita's list of extensions:
app = Krita.instance()
extension = ShapesAndLayers(parent=app) #instantiate your class
app.addExtension(extension)
