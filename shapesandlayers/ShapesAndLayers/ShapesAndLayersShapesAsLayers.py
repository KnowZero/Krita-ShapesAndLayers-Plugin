from krita import *
from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg, uic


class shapesAndLayersShapesAsLayers(DockWidget):
    TOOLACTION_BINDS = [
        'clear',
        'edit_cut',
        'edit_paste',
        'edit_undo',
        'edit_redo',
            
        'object_order_back',
        'object_order_front',
        'object_group',
        'object_ungroup'
    ]
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shapes As Layers")
        self.centralWidget = None
        
        self.centralWidget = uic.loadUi(os.path.dirname(os.path.realpath(__file__)) + '/ShapesAsLayers.ui')
        
        self.centralWidget.listShapes.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.centralWidget.setEnabled(False)
        
        self.setWidget(self.centralWidget)
        
        self.xSpinBoxFilter = self.xSpinBoxFilterClass(self)
        
        self.shapeListData = []
        self.selectList = {}
        self.blockSelect = False
        self.editMode = False
        
        
        self.notify = Krita.instance().notifier()
        self.notify.setActive(True)
        self.notify.windowCreated.connect(self.windowCreatedSetup)

    
    def windowCreatedSetup(self):
        self.notify.windowCreated.disconnect(self.windowCreatedSetup)
        
        self.qwin = Krita.instance().activeWindow().qwindow()
        layerBox = self.qwin.findChild(QtWidgets.QDockWidget, "KisLayerBox")
        self.layerList = layerBox.findChild(QTreeView,"listLayers")


        self.currentDocument = None
        self.currentLayer = None
        self.currentLayerUUID = None
        
        #self.centralWidget.listShapes.setColumnWidth(0,10)
        #self.centralWidget.listShapes.setColumnWidth(1,10)

        header = self.centralWidget.listShapes.header()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        #header.setMinimumSectionSize(20)
        #header.resizeSection(0, 20)
        #header.resizeSection(1, 20)
        
        self.layerList.model().sourceModel().dataChanged.connect(self.layerChanged)
        self.layerList.model().sourceModel().modelReset.connect(self.layerChangedReset)
        self.layerList.model().sourceModel().rowsRemoved.connect(self.layerChanged)
        
        self.centralWidget.listShapes.itemClicked.connect(self.shapeLayerClicked)
        self.centralWidget.listShapes.itemSelectionChanged.connect(self.shapeSelectionChanged)
        
        self.centralWidget.editBtn.clicked.connect(self.openEditDialog)
        
        
        toolBox = self.qwin.findChild(QtWidgets.QDockWidget, "ToolBox")
        toolButton = self.qwin.findChild(QtWidgets.QToolButton, "InteractionTool")
        toolButton.toggled.connect(self.toolChanged)
        
    def toolChanged(self, status):
        if Krita.instance().activeDocument() is None:
            self.cleanup()
            return
        print ("BIND SHAPE", status)
        
        geoWidget = self.qwin.findChild(QWidget,'DefaultToolGeometryWidget')
        self.xSpinBox = geoWidget.findChild(QDoubleSpinBox, 'positionXSpinBox')
        
        if status is True:
            for action in self.TOOLACTION_BINDS:
                Krita.instance().action(action).triggered.connect(self.shapeChanged)
                self.xSpinBox.installEventFilter(self.xSpinBoxFilter)

            if self.currentLayer is not None and self.currentLayer.type() == 'vectorlayer':
                self.reloadShapeLayers()
        else:
            for action in self.TOOLACTION_BINDS:
                Krita.instance().action(action).triggered.disconnect(self.shapeChanged)
                
            self.xSpinBox.removeEventFilter(self.xSpinBoxFilter)

        self.editMode = status
        self.centralWidget.setEnabled(status)

        

    def shapeLayerClicked(self, item, col):
        i = item.data(2, 101)
        shape = self.shapeListData[i]['shape']
        visible = True if shape.visible() else False
        
        if col == 0:
            shape.setVisible(not visible)
            shape.update()
            item.setIcon(0, Krita.instance().icon('visible' if not visible else 'novisible' ) )

    def layerChangedReset(self):
        #print ("RESET!")
        self.cleanup()
        self.layerChanged()

    def layerChanged(self):
        #print ("PRELAYER CHANGED!", self.centralWidget.listShapes.selectedItems() )
        if self.currentDocument is None:
            self.currentLayer = None
            self.currentLayerUUID = None
            self.currentDocument = Krita.instance().activeDocument()
            self.centralWidget.listShapes.clear()
        
        activeNode = self.currentDocument.activeNode()
        if activeNode is None:
            self.cleanup()
            return
        
        activeNodeUUID = activeNode.uniqueId()
        
        if self.currentLayerUUID != activeNodeUUID:
            #print ("LAYER CHANGED!")
            self.currentLayer = activeNode
            self.currentLayerUUID = activeNodeUUID
            
            if self.currentLayer.type() == 'vectorlayer':
                if self.editMode is True:
                    self.centralWidget.setEnabled(True)
                self.reloadShapeLayers()
            else:
                self.reloadShapeLayers(False)
            
    def reloadShapeLayers(self, fill = True):
        self.shapeListData = []
        self.selectList = {}
        self.centralWidget.listShapes.clear()
        
        if fill and self.currentLayer and self.currentLayer.type() == 'vectorlayer':
            self.blockSelect = True
            absoluteTransform = QTransform()
            self.fillShapeList( absoluteTransform, self.currentLayer.shapes(), 1 )
            self.blockSelect = False
        
    def fillShapeList(self, absoluteTransform, shapes, depth, parentItem = None):
        for i in range(len(shapes)-1,-1,-1):
            shape = shapes[i]
            if isinstance(shape, GroupShape):
                #if self.maxGroupDepth < depth: self.maxGroupDepth = depth


                item = QTreeWidgetItem(0)
                item.setText(2, '['+str(depth)+'] '+ (shape.name() or 'SubGroup '+str(depth)+'-'+str(i+1))  )
                item.setIcon(0, Krita.instance().icon('visible' if shape.visible() else 'novisible' ) )
                item.setIcon(1, Krita.instance().icon("grouplayer"))
                item.setData(2, 101, len(self.shapeListData) )
               
                if parentItem:
                    parentItem.addChild(item)
                else:
                    self.centralWidget.listShapes.addTopLevelItem( item )

                if shape.isSelected():
                    item.setSelected(True)
                    self.selectList[str(len(self.shapeListData))]=item
                
                newAbsoluteTransform = absoluteTransform * shape.transformation()
                self.shapeListData.append( { 'depth': depth, 'shape':shape, 'transform': newAbsoluteTransform } )
                
                self.fillShapeList( newAbsoluteTransform, shape.children(), depth+1, item)
            elif isinstance(shape, Shape):
                #if self.topLevelGroupDepth > depth: self.topLevelGroupDepth = depth-1
                
                item = QTreeWidgetItem(1)
                item.setText(2, '['+str(depth)+'] '+ (shape.name() or "Shape "+str(i)))
                item.setIcon(0, Krita.instance().icon('visible' if shape.visible() else 'novisible' ) )
                item.setIcon(1, Krita.instance().icon("vectorLayer"))
                item.setData(2, 101, len(self.shapeListData) )

                if parentItem:
                    parentItem.addChild(item)
                else:
                    self.centralWidget.listShapes.addTopLevelItem( item )

                if shape.isSelected():
                    item.setSelected(True)
                    self.selectList[str(len(self.shapeListData))]=item

                shapeTransform = shape.transformation() * absoluteTransform
                self.shapeListData.append( { 'depth': depth, 'shape':shape, 'transform': shapeTransform } )

    def shapeSelectionChanged(self):
        if self.blockSelect is True: return
        if not Krita.instance().action('InteractionTool').isChecked():
            #print ("TRIGGER!")
            Krita.instance().action('InteractionTool').trigger()
        
        for i in self.selectList:
            shape = self.shapeListData[int(i)]['shape']
            
            shape.deselect()
        
        #print ("SHAPE CHANGE:", len(self.selectList), len(self.shapeListData) )
        
        self.selectList = {}
        
        for item in self.centralWidget.listShapes.selectedItems():
            i = item.data(2, 101)
            if i is not None:
                shape = self.shapeListData[i]['shape']
                self.selectList[str(i)]=item
            
                shape.select()
            else:
                print ("NOT FOUND SHAPE")

    def shapeChanged(self):
        #print ("SHAPE CHANGE!")
        self.currentDocument.waitForDone()
        QTimer.singleShot(500, self.reloadShapeLayers)
        
    def cleanup(self):
        self.currentDocument = None
        self.centralWidget.listShapes.clear()
        self.selectList={}
        self.shapeListData=[]
        self.centralWidget.setEnabled(False)
        
        
    def openEditDialog(self):
        self.editDlg = QDialog()
        
        selected = self.centralWidget.listShapes.selectedItems()
        if len(selected) <= 0: return
        
        layout = QVBoxLayout()
        #buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        #buttonBox.accepted.connect(self.editShape)
        buttonBox.rejected.connect(self.editDlg.hide)
        
        i = selected[0].data(2, 101)
        shape = self.shapeListData[i]['shape']
        
        textBox = QPlainTextEdit()
        textBox.setPlainText( shape.toSvg(True,False) )
        
        layout.addWidget(textBox)
        layout.addWidget(buttonBox)
        
        self.editDlg.setLayout(layout)
        
        self.editDlg.show()
        
    def editShape(self):
        self.editDlg.hide()

    def canvasChanged(self, canvas):
        pass


    class xSpinBoxFilterClass(QDoubleSpinBox):
        def __init__(self, caller, parent=None):
            super().__init__()
            self.caller = caller
            
        def eventFilter(self, obj, event):
            if event.type() == 98:
                #print ("Event", event.type(), obj)
                self.caller.shapeChanged()
                
            return False

Krita.instance().addDockWidgetFactory(DockWidgetFactory("shapesAndLayersShapesAsLayers", DockWidgetFactoryBase.DockRight, shapesAndLayersShapesAsLayers)) 
