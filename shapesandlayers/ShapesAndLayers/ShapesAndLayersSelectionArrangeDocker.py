from krita import *
from PyQt5 import uic


class shapesAndLayersSelectionArrangeDocker(DockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Selection Arrange Docker")
        self.centralWidget = uic.loadUi(os.path.dirname(os.path.realpath(__file__)) + '/SelectionArrangeDocker.ui')
        
        self.centralWidget.selObjectPosBtnGroup.buttonPressed.connect(self.slotAdjustToPositionPressed)
        self.centralWidget.selArrangeUndoBtn.pressed.connect(self.slotUndo)
        
        self.centralWidget.selArrangeUndoBtn.setEnabled(False)
        
        self.setWidget(self.centralWidget)
        
        self.cacheNode = None
        self.cacheNodeBounds = None
        self.pixelData = None
        
    def canvasChanged(self, canvas):
        pass
    
    def slotAdjustToPositionPressed(self, btn):
        btn.setDown(False)
        self.adjustToPosition( btn.objectName().replace('selObjectPos','').replace('Btn','') )
        
    def slotUndo(self):
        if self.cacheDoc and self.cacheNode and self.pixelData:
            doc = self.cacheDoc
            node = self.cacheNode
            
            self.clearNode(node)
            nodeBounds = self.cacheNodeBounds
            node.setPixelData(self.pixelData, int(nodeBounds.x()), int(nodeBounds.y()), int(nodeBounds.width()), int(nodeBounds.height()))
            self.pixelData = None
            self.centralWidget.selArrangeUndoBtn.setEnabled(False)
            doc.refreshProjection()
        
    def clearNode(self, node):
        nodeBounds = node.bounds()
        pcount = int(int(node.colorDepth().replace('F','').replace('U','')) / 2)
        node.setPixelData( (b'\x00' * int(pcount * nodeBounds.width() * nodeBounds.height()) ), int(nodeBounds.x()), int(nodeBounds.y()), int(nodeBounds.width()), int(nodeBounds.height()))
        
    def adjustToPosition(self, loc):
        doc = Krita.instance().activeDocument()
        node = doc.activeNode()
        sel = doc.selection()
        
        if not sel:
            QMessageBox.warning(Krita.instance().activeWindow().qwindow(), "Warning", "There is no selection!")
        elif node.type() != 'paintlayer':
            QMessageBox.warning(Krita.instance().activeWindow().qwindow(), "Warning", "Node must be a paint layer!")
        else:
            nodeBounds = node.bounds()
            selBounds = QRectF(sel.x(), sel.y(), sel.width(), sel.height())
            
            xDiff = 0
            yDiff = 0
            
            if 'W' in loc:
                xDiff = selBounds.x() - nodeBounds.x()
            elif 'E' in loc:
                xDiff = (selBounds.x() + selBounds.width()) - (nodeBounds.x() + nodeBounds.width())

            if 'N' in loc:
                yDiff = selBounds.y() - nodeBounds.y()
            elif 'S' in loc:
                yDiff = (selBounds.y() + selBounds.height()) - (nodeBounds.y() + nodeBounds.height())
            
            if loc == 'Center':
                xDiff = (selBounds.x() + (selBounds.width()/2)) - (nodeBounds.x() + (nodeBounds.width()/2))
                yDiff = (selBounds.y() + (selBounds.height()/2)) - (nodeBounds.y() + (nodeBounds.height()/2))
            
            
            self.cacheDoc = doc
            self.cacheNode = node
            self.cacheNodeBounds = nodeBounds
            self.pixelData = node.pixelData( nodeBounds.x(), nodeBounds.y(), nodeBounds.width(), nodeBounds.height() )
            
            self.clearNode(node)
            
            
            node.setPixelData(self.pixelData, int(nodeBounds.x() + xDiff), int(nodeBounds.y() + yDiff), int(nodeBounds.width()), int(nodeBounds.height()))
            self.centralWidget.selArrangeUndoBtn.setEnabled(True)
            
            doc.refreshProjection()

    
Krita.instance().addDockWidgetFactory(DockWidgetFactory("shapesAndLayersSelectionArrangeDocker", DockWidgetFactoryBase.DockRight, shapesAndLayersSelectionArrangeDocker)) 
