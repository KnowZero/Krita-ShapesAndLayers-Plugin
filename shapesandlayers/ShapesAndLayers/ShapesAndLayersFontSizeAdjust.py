from krita import *
from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg, uic
import re
from xml.dom import minidom

class ShapesAndLayersFontSizeAdjust(QtWidgets.QDialog):
    def __init__(self, caller, parent = None):
        super().__init__(parent)
        self.shapeListData = []
        self.activeProcess = False
        self.checkAll = True

    def fillShapeList(self, layer, shapes, depth):
        for i in range(len(shapes)):
            shape = shapes[i]
            if isinstance(shape, GroupShape):
                item = QtWidgets.QListWidgetItem( Krita.instance().icon("merge-layer-below"), layer.name() + ' - ['+str(depth)+'] '+ (shape.name() or 'SubGroup '+str(depth)+'-'+str(i+1))  )
                if depth > 1: 
                    item.setForeground( QtGui.QBrush( QtGui.QColor(50,50,50) ) )
                else:
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                    item.setCheckState(QtCore.Qt.Checked)
                self.listTextItems.addItem( item )

                self.shapeListData.append( { 'depth': depth, 'layer': layer, 'shape':shape } )
                
                self.fillShapeList( layer, shape.children(), depth+1 )
            elif isinstance(shape, Shape) and shape.type() == 'KoSvgTextShapeID':

              
                item = QtWidgets.QListWidgetItem( Krita.instance().icon("draw-text"), layer.name() + ' - ['+str(depth)+'] '+ (shape.name() or "Shape "+str(i))  )

                if depth > 1: 
                    item.setForeground( QtGui.QBrush( QtGui.QColor(50,50,50) ) )
                else:
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                    item.setCheckState(QtCore.Qt.Checked)
                    
                self.listTextItems.addItem( item )
                

                self.shapeListData.append( { 'depth': depth, 'layer': layer, 'shape':shape } )

    def fillShapeListLayers(self, nodes):
        for layer in nodes:
            if layer.type() == 'grouplayer':
                self.fillShapeListLayers(layer.childNodes())
            elif layer.type() == 'vectorlayer':
                self.fillShapeList( layer, layer.shapes(), 1 )
                
    def fontResize(self, adjustOp, adjustAmount, orgSize):
        if adjustOp == 0: return  orgSize + adjustAmount
        elif adjustOp == 1: return orgSize / adjustAmount
        elif adjustOp == 2: return orgSize * adjustAmount
        elif adjustOp == 3 and orgSize > adjustAmount: return orgSize - adjustAmount
        elif adjustOp == 4: return adjustAmount
        else: return orgSize
    
                
    def runProcess(self):
        if self.activeProcess is False:
            self.activeProcess = True
            self.btnFontAdjustRunProcess.setText('Stop')
            self.btnFontAdjustRunProcess.setIcon(Krita.instance().icon("media-playback-stop"))
            
            adjustOp = self.cmbFontAdjustOperator.currentIndex()
            adjustAmount = float(self.floatAdjustFontAmount.value())
            
            doneColor = QtGui.QBrush( QtGui.QColor(0,200,0) )
            
            svgHeader = ''
            layerUUID = ''
            
            for i in range(len(self.shapeListData)):
                item = self.listTextItems.item(i)
                if item.checkState() == QtCore.Qt.Checked:
                    currentLayer = self.shapeListData[i]['layer']
                    uuid = currentLayer.uniqueId()
                    if layerUUID != uuid:
                        layerUUID = uuid
                        svgHeader = re.compile('(^.*?\<svg.*?["\']\\s*\>).*$', re.DOTALL).sub(r'\1', currentLayer.toSvg())
                    
                    shape = self.shapeListData[i]['shape']
                    svgContent = svgHeader+shape.toSvg(True,False)+'</svg>'
                    svgDom = minidom.parseString(svgContent)
                    for node in svgDom.getElementsByTagName('text'):
                        fontSize = node.getAttribute("font-size") if node.hasAttribute("font-size") else 10;
                        node.setAttribute('font-size', str(self.fontResize( adjustOp, adjustAmount, float(fontSize) )) )
                        for subnode in node.getElementsByTagName('tspan'):
                            if subnode.hasAttribute("font-size"):
                                subnode.setAttribute('font-size', str(self.fontResize( adjustOp, adjustAmount, float(subnode.getAttribute('font-size')) )) )
                    
                    shape.remove()
                    shapes = currentLayer.addShapesFromSvg(svgDom.toxml())
                    if shapes[0]:
                        self.shapeListData[i]['shape'] = shapes[0]
                        item.setForeground( doneColor )

        self.activeProcess = False
        self.btnFontAdjustRunProcess.setText('Start')
        self.btnFontAdjustRunProcess.setIcon(Krita.instance().icon("media-playback-start"))
        
    def toggleCheck(self):
        for i in range(len(self.shapeListData)):
            item = self.listTextItems.item(i)
            if item.flags() & QtCore.Qt.ItemIsUserCheckable:
                item.setCheckState( QtCore.Qt.Unchecked if self.checkAll else QtCore.Qt.Checked )

        self.checkAll = False if self.checkAll else True;
         
  
    def openDialog(self):
        self.currentDocument = Krita.instance().activeDocument()
        if not self.currentDocument: return { "error": "No Document is loaded" }
        
        uic.loadUi(os.path.dirname(os.path.realpath(__file__)) + '/FontSizeAdjust.ui', self)
        
        self.fillShapeListLayers( self.currentDocument.rootNode().childNodes() )
        
        self.btnFontAdjustRunProcess.clicked.connect(self.runProcess)
        self.btnToggleCheckAll.clicked.connect(self.toggleCheck)
        
        self.exec_()
        return { "status": 1 }        
        

 
