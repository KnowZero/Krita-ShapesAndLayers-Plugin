from krita import *
from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg, uic
import re
from xml.dom import minidom

class ShapesAndLayersSplit(QtWidgets.QDialog):
    def __init__(self, caller, parent = None):
        super().__init__(parent)
        self.currentDocument = None
        self.currentLayer = None
        
        self.maxGroupDepth = 0
        self.topLevelGroupDepth = 99999
        self.svgHeader = ''
        self.shapeListData = []

    def transformToMatrix(self,t):
        return list(map(lambda x: str(x), [ t.m11(), t.m12(), t.m21(), t.m22(), t.dx(), t.dy() ]))

    def fillShapeList(self, absoluteTransform, shapes, depth):
        for i in range(len(shapes)):
            shape = shapes[i]
            if isinstance(shape, GroupShape):
                if self.maxGroupDepth < depth: self.maxGroupDepth = depth


                item = QtWidgets.QListWidgetItem( Krita.instance().icon("groupOpened"), '['+str(depth)+'] '+ (shape.name() or 'SubGroup '+str(depth)+'-'+str(i+1))  )
                self.listShapes.addItem( item )
                
                newAbsoluteTransform = absoluteTransform * shape.transformation()
                self.shapeListData.append( { 'depth': depth, 'shape':shape, 'transform': newAbsoluteTransform } )
                
                self.fillShapeList( newAbsoluteTransform, shape.children(), depth+1 )
            elif isinstance(shape, Shape):
                if self.topLevelGroupDepth > depth: self.topLevelGroupDepth = depth-1
                
                item = QtWidgets.QListWidgetItem( Krita.instance().icon("vectorLayer"), '['+str(depth)+'] '+ (shape.name() or "Shape "+str(i))  )
                self.listShapes.addItem( item )
                
                shapeTransform = shape.transformation() * absoluteTransform
                self.shapeListData.append( { 'depth': depth, 'shape':shape, 'transform': shapeTransform } )


            
    
    def highlightItems(self):
        limitDepth = self.intSetSplitGroupDepth.value()+1
        
        for i in range(len(self.shapeListData)):
            color = QtGui.QColor(0,200,0) if limitDepth >= self.shapeListData[i]['depth'] else QtGui.QColor(50,50,50);
            self.listShapes.item(i).setForeground( QtGui.QBrush( color ) )

    
    def fillGroupWithLayers(self, groupLayer, absoluteTransform, shapes, depth):
        limitDepth = self.intSetSplitGroupDepth.value()
        
        for i in range(len(shapes)):
            shape = shapes[i]
            if isinstance(shape, GroupShape) and limitDepth >= depth:
                newGroupLayer = self.currentDocument.createGroupLayer(shape.name() or 'SubGroup '+str(depth)+'-'+str(i+1))
                newAbsoluteTransform = absoluteTransform * shape.transformation()
      
                self.fillGroupWithLayers(newGroupLayer, newAbsoluteTransform, shape.children(), depth+1)
                groupLayer.addChildNode(newGroupLayer, None)
            else:
                svgContent = self.svgHeader+shape.toSvg(True,False)+'</svg>'
                layerName = shape.name() or 'Shape '+str(i+1)
                shapeTransform = shape.transformation() * absoluteTransform

                svgRoot = minidom.parseString(svgContent).documentElement
                matrix = self.transformToMatrix(shapeTransform)
        
                svgRoot.childNodes[-1].setAttribute('transform',  'matrix('+ ','.join(matrix) +')' )
                
                if self.cmbLayerOutputType.currentIndex() == 0:
                    newLayer = self.currentDocument.createVectorLayer(layerName)
                    
                    newLayer.addShapesFromSvg(svgRoot.toxml())
                    
                    #newShapes = newLayer.addShapesFromSvg(svgContent)
                    #newShapes[0].setTransformation(shapeTransform)
                    #newShapes[0].update()
                    
                    groupLayer.addChildNode(newLayer, None)
                    
                elif self.cmbLayerOutputType.currentIndex() == 1:
                    newLayer = self.currentDocument.createNode(layerName, "paintlayer")
                    
                    w = self.currentDocument.width()
                    h = self.currentDocument.height()
                    
                    image = self.svgToImage(svgRoot.toxml(), w, h)

                    ptr = image.constBits()
                    ptr.setsize(image.byteCount())
        
                    newLayer.setPixelData(bytes(ptr.asarray()),0,0,w,h)
                    groupLayer.addChildNode(newLayer, None)
                    
    
    def svgToImage(self, svgContent, w, h):
        svgrenderer = QtSvg.QSvgRenderer(bytearray(svgContent, encoding='utf-8'))
        image = QtGui.QImage(w, h, QtGui.QImage.Format_ARGB32)
        image.fill(0x00000000)
        svgrenderer.render(QtGui.QPainter(image))
        
        return image
    
    def previewItem(self, i):
        shape = self.shapeListData[i]['shape']
        svgContent = self.svgHeader+shape.toSvg(True,False)+'</svg>'
        
        self.lblPreviewShape.setText("")
        
        svgRoot = minidom.parseString(svgContent).documentElement
        matrix = self.transformToMatrix(self.shapeListData[i]['transform'])
        
        svgRoot.childNodes[-1].setAttribute('transform',  'matrix('+ ','.join(matrix) +')' )
        
        w = self.lblPreviewShape.width()
        h = self.lblPreviewShape.height()
        self.lblPreviewShape.setScaledContents( True );
        
        pixmap = QtGui.QPixmap.fromImage( self.svgToImage( svgRoot.toxml(), w, h ) )
      
        self.lblPreviewShape.setPixmap( pixmap )
        self.lblPreviewShape.setFixedWidth(w)
        self.lblPreviewShape.setFixedHeight(h)

    def openDialog(self):
        self.currentDocument = Krita.instance().activeDocument()
        if not self.currentDocument: return { "error": "No Document is loaded" }
        self.currentLayer = self.currentDocument.activeNode()
        if not self.currentLayer: return { "error": "No Layer is selected" }
        if self.currentLayer.type() != "vectorlayer": return { "error": "Invalid Layer is selected" }

        uic.loadUi(os.path.dirname(os.path.realpath(__file__)) + '/SplitLayer.ui', self)
        
        self.lblLayerName.setText( 'Layer Name: ' + self.currentLayer.name() )
        
        self.svgHeader = re.compile('(^.*?\<svg.*?["\']\\s*\>).*$', re.DOTALL).sub(r'\1', self.currentLayer.toSvg())

        self.shapeListData = []
        self.maxGroupDepth = 0
        self.topLevelGroupDepth = 99999
        
        absoluteTransform = QtGui.QTransform()
        
        self.fillShapeList( absoluteTransform, self.currentLayer.shapes(), 1 )
        self.intSetSplitGroupDepth.setValue(self.topLevelGroupDepth)
        self.highlightItems()
        
        self.lblLayerInfo.setText( 'Found top-level group depth of ' + str(self.topLevelGroupDepth) + ' and total group depth of ' + str(self.maxGroupDepth) )
        
        self.listShapes.currentRowChanged.connect(self.previewItem)
        self.intSetSplitGroupDepth.valueChanged.connect(self.highlightItems)
        
        if self.exec_():
            groupLayer = self.currentDocument.createGroupLayer(self.currentLayer.name() + ' Group')
            absoluteTransform = QtGui.QTransform()
            self.fillGroupWithLayers(groupLayer, absoluteTransform, self.currentLayer.shapes(), 1)
            self.currentLayer.parentNode().addChildNode(groupLayer, self.currentLayer)
            self.currentDocument.refreshProjection()
            
            if self.cmbInputLayerHandler.currentIndex() == 0:
                self.currentLayer.setVisible(False)
            elif self.cmbInputLayerHandler.currentIndex() == 1:
                self.currentLayer.remove()
        return { "status": 1 }
