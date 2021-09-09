from krita import *
from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg, uic
import re
from xml.dom import minidom
import sip

class ShapesAndLayersVisibilityHelper():
    def __init__(self, caller, parent = None):
        super().__init__()
        self.caller = caller
        self.dlg = uic.loadUi(os.path.dirname(os.path.realpath(__file__)) + '/VisibilityHelper.ui')
        
        self.layerList = None
        settingsList = Krita.instance().readSetting("", "shapesandlayersVisibilityHelper","").split(',')
        self.settings = {
            'boolAutoSelectVisibleLayer': 0,
            'boolBlockInvisibileLayer': 0,
            'boolToggleVisibilityDrag': 0
            } if len(settingsList) < 2 else { settingsList[i]: int(settingsList[i + 1]) for i in range(0, len(settingsList), 2) }
        self.docName = ''
        
        self.enabledBindLayers = False
        
        self.layerChanges = {}
        
        self.clickEvent = False
        
        self.hoverToggleMode = [False,False]
        self.hoverToggleNodes = []
        
        self.currentLayer = None


    def onLoad(self, window):
        qwin = window.qwindow()
        
        subaction = window.createAction("shapesAndLayersVisibilityHelper", "Layer Visibility Helper...", "tools/scripts/shapesAndLayers")
        subaction.triggered.connect(self.slotVisibilityHelper)
        
        if self.settings['boolAutoSelectVisibleLayer'] or self.settings['boolBlockInvisibileLayer'] or self.settings['boolToggleVisibilityDrag']:
                self.bindLayerList(qwin)
                
        self.mdi = qwin.centralWidget().findChild(QtWidgets.QMdiArea)
        

        
        self.blockCanvas = None



    def slotVisibilityHelper(self):
        result = self.openDialog()
        self.caller.errCheck(result)

    def checkBlockCanvas(self, visible):
        
        if self.blockCanvas is None or sip.isdeleted(self.blockCanvas):
            self.subWindow = self.mdi.activeSubWindow()
            self.scrollArea = self.subWindow.findChild(QtWidgets.QAbstractScrollArea)
            self.blockCanvas = QtWidgets.QWidget(self.scrollArea)
        
            self.blockCanvas.setStyleSheet('background-color: rgba(100, 100, 100, 128)')
        
            self.blockCanvas.gridLayout = QtWidgets.QGridLayout(self.blockCanvas)
            self.blockCanvas.gridLayout.setSpacing(0)
            self.blockCanvas.gridLayout.setContentsMargins(0, 0, 0, 0)
        
            invisibleLayerBtn = QtWidgets.QPushButton("Make Layer Visible")
        
            invisibleLayerBtn.pressed.connect(self.makeLayerVisible) 
        
            self.blockCanvas.gridLayout.addWidget(invisibleLayerBtn)
        
            self.blockCanvas.resize(self.scrollArea.rect().width(),self.scrollArea.rect().height())


        if visible:
            self.blockCanvas.hide()
        else:
            self.blockCanvas.show()



      
    def makeLayerVisible(self):
        doc = Krita.instance().activeDocument()
        
        doc.activeNode().setVisible(True)
        doc.refreshProjection()
        
        self.blockCanvas.hide()

    def openDialog(self):
        self.dlg.boolAutoSelectVisibleLayer.setChecked(self.settings['boolAutoSelectVisibleLayer'])
        self.dlg.boolBlockInvisibileLayer.setChecked(self.settings['boolBlockInvisibileLayer'])
        self.dlg.boolToggleVisibilityDrag.setChecked(self.settings['boolToggleVisibilityDrag'])
        
        self.dlg.cmbBlockInvisibileLayer.setVisible(False)
        self.dlg.cmbToggleVisibilityDrag.setVisible(False)
        
        if self.dlg.exec_():
            self.settings = {
                'boolAutoSelectVisibleLayer': int(self.dlg.boolAutoSelectVisibleLayer.isChecked()),
                'boolBlockInvisibileLayer': int(self.dlg.boolBlockInvisibileLayer.isChecked()),
                'cmbBlockInvisibileLayer': int(self.dlg.cmbBlockInvisibileLayer.currentIndex()),
                'boolToggleVisibilityDrag': int(self.dlg.boolToggleVisibilityDrag.isChecked()),
                'cmbToggleVisibilityDrag': int(self.dlg.cmbToggleVisibilityDrag.currentIndex()),
            }
            
            Krita.instance().writeSetting("", "shapesandlayersVisibilityHelper", ','.join("{!s},{!r}".format(k,v) for (k,v) in self.settings.items()) )
            
            if self.settings['boolAutoSelectVisibleLayer'] or self.settings['boolBlockInvisibileLayer'] or self.settings['boolToggleVisibilityDrag']:
                self.bindLayerList(Krita.instance().activeWindow().qwindow())
                if self.settings['boolBlockInvisibileLayer']:
                    self.checkBlockCanvas( Krita.instance().activeDocument().activeNode().visible() )
            else:
                self.unbindLayerList()
            
        return { "status": 1 }

    def layerMap(self, idx, idxMap):
        parent = idx.parent()
        rows = self.layerList.model().rowCount(parent)
        
        idxMap.append( rows-1-idx.row() )
        
        if parent != QtCore.QModelIndex():
            self.layerMap(parent, idxMap)
        
        return idxMap
    
    def validateNode(self, doc,layerName, node, idx):
        idxMap = []
            
        self.layerMap(idx, idxMap)
            
        validIdxMap = True
        onNode = node
            
        for i in idxMap:
            if onNode.index() != i:
                validIdxMap = False
                break
            else:
                onNode = node.parentNode()

        if not validIdxMap:
            onNode = doc.rootNode()
            for i in reversed(idxMap):
                onNode = onNode.childNodes()[i]
            if onNode.name() == layerName: node = onNode
        
        return node
    
    def layerHover(self, idx):
        if not self.clickEvent: return

        if self.hoverToggleMode[0] is True:
            layerName = idx.data(0)
            doc = Krita.instance().activeDocument()
            
            node = self.validateNode(doc,layerName, doc.nodeByName(layerName),idx)

            node.setVisible(self.hoverToggleMode[1])
            #>self.hoverToggleNodes.append([node])

    
    def layerDataChanged(self, idx, idx2, urole = []):
        
    
        doc = Krita.instance().activeDocument()
        
        if doc is None: return


        node = doc.activeNode()
        
        if (doc.fileName() != self.docName):
            self.docName = doc.fileName()
            self.layerChanges = {}
            if self.blockCanvas is not None and not sip.isdeleted(self.blockCanvas): 
                self.blockCanvas.deleteLater()
        
        layerName = idx.data(0)
        layerVisible = not idx.data( Qt.UserRole + 6 )

       
        if self.settings['boolToggleVisibilityDrag'] and self.clickEvent and layerName in self.layerChanges and self.layerChanges[layerName]['visible'] is not layerVisible:
            self.hoverToggleNodes = []
            self.hoverToggleMode = [True, layerVisible]
            self.layerList.setDragEnabled(False)
        
        if self.settings['boolAutoSelectVisibleLayer'] and self.clickEvent and layerName in self.layerChanges and self.layerChanges[layerName]['visible'] is False and layerVisible is True:
            doc.setActiveNode( self.validateNode(doc,layerName, doc.nodeByName(layerName),idx) )


        if self.settings['boolBlockInvisibileLayer'] and layerName in self.layerChanges and self.layerChanges[layerName]['visible'] is not layerVisible:
            if idx.data( Qt.UserRole + 1 ):
                self.checkBlockCanvas(layerVisible)




        self.layerChanges[layerName] = { 'visible': layerVisible }
        
        self.layerChanged()
        
    def layerModelReset(self):
        self.layerChanged()


    def layerRemove(self, idx, first, last):
        self.layerChanged()

    def layerChanged(self):
        doc = Krita.instance().activeDocument()
        node = doc.activeNode()        

        if node is not None and (self.currentLayer is None or self.currentLayer != node.uniqueId()):
            self.currentLayer = node.uniqueId()
            if self.settings['boolBlockInvisibileLayer']:
                self.checkBlockCanvas(node.visible())

    def bindLayerList(self,qwin):
        if self.enabledBindLayers: return
        self.enabledBindLayers = True
        layerBox = qwin.findChild(QtWidgets.QDockWidget, "KisLayerBox")
        self.layerList = layerBox.findChild(QtWidgets.QTreeView,"listLayers")
        

        self.layerList.entered.connect(self.layerHover)
        self.layerList.model().sourceModel().dataChanged.connect(self.layerDataChanged)
        self.layerList.model().sourceModel().modelReset.connect(self.layerModelReset)
        self.layerList.model().sourceModel().rowsRemoved.connect(self.layerRemove)
        
        self.layerListFilter = self.layerListFilterClass(self)
        self.layerList.viewport().installEventFilter(self.layerListFilter)


    def unbindLayerList(self):
        if not self.enabledBindLayers: return
        self.layerList.entered.disconnect(self.layerHover)
        self.layerList.model().sourceModel().dataChanged.disconnect(self.layerDataChanged)
        self.layerList.model().sourceModel().modelReset.disconnect(self.layerModelReset)
        self.layerList.model().sourceModel().rowsRemoved.disconnect(self.layerRemove)
        
        self.layerList.viewport().removeEventFilter(self.layerListFilter)
        self.layerListFilter = None
       
        self.enabledBindLayers = False
        
    class layerListFilterClass(QtWidgets.QTreeView):
        def __init__(self, caller, parent=None):
            super().__init__()
            self.caller = caller
            
        def eventFilter(self, obj, event):
            if event.type() == 2:
                self.caller.clickEvent = True
                #print ("PRESS")
            elif event.type() == 3:
                if self.caller.hoverToggleMode[0] is True:
                    Krita.instance().activeDocument().refreshProjection()
                
                self.caller.hoverToggleMode = [False, False]
                self.caller.clickEvent = False
                if self.caller.layerList.dragEnabled is False: self.caller.layerList.setDragEnabled(True)
                
                #print ("RELEASE")
            return False
        
