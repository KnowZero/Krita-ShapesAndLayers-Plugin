from krita import *
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import json

class ShapesAndLayersShowEraser():
    def __init__(self, caller, parent = None):
        super().__init__()
        self.caller=caller
        self.dlg=None
        
      
        settingsData = Krita.instance().readSetting("", "shapesAndLayersShowEraser","")
        if settingsData.startswith('{'):
            self.settings = json.loads(settingsData)
        else:
            settingsList = settingsData.split(',')

            if len(settingsList) >= 2:
                self.settings = { settingsList[i]: int(settingsList[i + 1]) for i in range(0, len(settingsList), 2) }
                self.settings['boolEnableCursorAdjust'] = 0
            else:
                self.settings = {
                    'enabled': 0,
                    'boolEnableCursorAdjust': 0
                }
        
        self.eraserMode = False
        self.adjustMode = False
        self.eraserStatus = None
        
        self.canvasZoomWidget = None
        self.canvasZoomLevel = 100.0
        
        self.cursorAdjustOptions = [
            'Default Size',
            'Adjust Size',
            'Hide'
        ]
        
        self.cursorSizes = [
                16,
                32,
                48,
                64,
                96,
                128,
                256
        ]
        
        self.eraserCursorCache = {}
        
        self.defaultEraserCursor = os.path.dirname(os.path.realpath(__file__)) + '/eraser_cursor.svg'
  
        if 'cursorFile' in self.settings and self.settings['cursorFile'] != '':
            self.eraserCursorFile = self.settings['cursorFile']
        else:
            self.eraserCursorFile = self.defaultEraserCursor
        
        self.resetCursorSize()
        
        
    def resetCursorSize(self):
        self.currentCursorSize = 32 if QApplication.primaryScreen().size().width() <= 3000 else 64
        
        
        #self.eraserCursorCache[str(self.currentCursorSize)] = QCursor(QIcon(self.eraserCursorFile).pixmap(QSize(self.currentCursorSize,self.currentCursorSize)))
        #self.currentEraserCursor = self.eraserCursorCache[str(self.currentCursorSize)]
        self.currentEraserCursor = QCursor(QIcon(self.eraserCursorFile).pixmap(QSize(self.currentCursorSize,self.currentCursorSize)))

        

        
    def onLoad(self, window):
        qwin = window.qwindow()
        self.mdiFilter = self.mdiFilterClass(self)
        self.action = window.createAction("shapesAndLayersShowEraser", "Show Eraser Cursor", "tools/scripts/shapesAndLayers")
        
        
        
        menu = QtWidgets.QMenu("shapesAndLayersShowEraser", window.qwindow())
        self.action.setMenu(menu)
        
        
        
        self.subaction1 = window.createAction("shapesAndLayersShowEraserEnable", "Enable", "tools/scripts/shapesAndLayers/shapesAndLayersShowEraser")
        self.subaction1.setCheckable(True)
        

        
        subaction2 = window.createAction("shapesAndLayersShowEraserConfig", "Configure...", "tools/scripts/shapesAndLayers/shapesAndLayersShowEraser")

        
        subaction2.triggered.connect(self.slotOpenConfig)

        centralWidget = qwin.centralWidget()
        if centralWidget is not None:
            self.mdi = centralWidget.findChild(QMdiArea)
        else:
            for win in QApplication.topLevelWidgets():
                winName = win.objectName()
                if winName.startswith('MainWindow'):
                    mdi = win.findChild(QMdiArea)
                    if mdi:
                        self.mdi = mdi
                        break

        if self.settings['enabled'] == 1:
            self.notify = Krita.instance().notifier()
            self.notify.setActive(True)
            self.notify.windowCreated.connect(self.windowCreatedSetup)
        else:
            self.subaction1.toggled.connect(self.toggleShowEraserEnable)
            



    def slotOpenConfig(self):
        result = self.openDialog()
        self.caller.errCheck(result)
    
    def windowCreatedSetup(self):
        self.subaction1.setChecked(True)
        self.toggleShowEraserEnable(True,1)
        self.subaction1.toggled.connect(self.toggleShowEraserEnable)
        self.notify.windowCreated.disconnect(self.windowCreatedSetup)
        
        
    def openDialog(self, show = True):
        if not self.dlg:
            self.dlg = uic.loadUi(os.path.dirname(os.path.realpath(__file__)) + '/ShowEraser.ui')
            
            self.dlg.cursorFileBtn.clicked.connect(self.slotGetCustomCursorPath)
            self.dlg.clearCursorFileBtn.clicked.connect(self.slotClearCustomCursorPath)
            
            for opt in self.cursorAdjustOptions:
                self.dlg.lessThanAdjustCmb.addItem(opt)
                self.dlg.moreThanAdjustCmb.addItem(opt)
                self.dlg.defaultSizeAdjustCmb.addItem(opt)
                
            for opt in self.cursorSizes:
                self.dlg.defaultSizeCmb.addItem(str(opt))
                self.dlg.lessThanAdjustCmb.addItem('Static: ' + str(opt))
                self.dlg.moreThanAdjustCmb.addItem('Static: ' + str(opt))
                self.dlg.defaultSizeAdjustCmb.addItem('Static: ' + str(opt))
        
        if 'cursorFile' in self.settings and self.settings['cursorFile'] != '':
            self.dlg.cursorFileLabel.setToolTip(self.settings['cursorFile'])
            self.dlg.cursorFileLabel.setText(self.settings['cursorFile'])
            
        self.dlg.boolEnableCursorAdjust.setChecked(self.settings['boolEnableCursorAdjust'])
        
        
        


            
        
        if self.settings['boolEnableCursorAdjust'] == 1:
            self.dlg.intLessThan.setValue(self.settings['intLessThan'])
            self.dlg.intMoreThan.setValue(self.settings['intMoreThan'])
        
            self.dlg.lessThanAdjustCmb.setCurrentIndex(self.dlg.lessThanAdjustCmb.findText(self.settings['lessThanAdjustCmb']))
            self.dlg.moreThanAdjustCmb.setCurrentIndex(self.dlg.moreThanAdjustCmb.findText(self.settings['moreThanAdjustCmb']))
        
            self.dlg.defaultSizeCmb.setCurrentIndex(self.dlg.defaultSizeCmb.findText(self.settings['defaultSizeCmb']))
            self.dlg.defaultSizeAdjustCmb.setCurrentIndex(self.dlg.defaultSizeAdjustCmb.findText(self.settings['defaultSizeAdjustCmb']))

        if show: 
            if self.dlg.exec_():
                self.settings['cursorFile'] = self.dlg.cursorFileLabel.toolTip()
                self.settings['boolEnableCursorAdjust'] = 1 if self.dlg.boolEnableCursorAdjust.isChecked() else 0
                self.settings['intLessThan'] = self.dlg.intLessThan.value()
                self.settings['intMoreThan'] = self.dlg.intMoreThan.value()
                self.settings['lessThanAdjustCmb'] = self.dlg.lessThanAdjustCmb.currentText()
                self.settings['moreThanAdjustCmb'] = self.dlg.moreThanAdjustCmb.currentText()
                self.settings['defaultSizeCmb'] = self.dlg.defaultSizeCmb.currentText()
                self.settings['defaultSizeAdjustCmb'] = self.dlg.defaultSizeAdjustCmb.currentText()
                
                Krita.instance().writeSetting("", "shapesAndLayersShowEraser", json.dumps(self.settings) )
                
                if self.settings['boolEnableCursorAdjust'] == 1:
                    self.bindCanvasZoom()
                    self.adjustMode = True
                elif self.adjustMode is True:
                    self.unbindCanvasZoom()
                    self.adjustMode = False
                
                self.eraserCursorFile = self.settings['cursorFile'] if self.settings['cursorFile'] != '' else self.defaultEraserCursor
                #self.eraserCursorCache = {}
                self.resetCursorSize()
                
        return { "status": 1 }   

    def slotClearCustomCursorPath(self):
        self.dlg.cursorFileLabel.setToolTip('')
        self.dlg.cursorFileLabel.setText('Custom Cursor')


    def slotGetCustomCursorPath(self):
        fileDlg = QFileDialog()
        fileDlg.setFileMode(QFileDialog.ExistingFile)
        fileDlg.setNameFilter("SVG and PNG files (*.svg *.png)")

        if fileDlg.exec_():
            files = fileDlg.selectedFiles()
            if len(files) > 0:
                self.dlg.cursorFileLabel.setToolTip(files[0])
                self.dlg.cursorFileLabel.setText(files[0])




        
    def toggleShowEraserEnable(self, status, source = 0):
        if source == 0:
            self.settings['enabled']=int(self.subaction1.isChecked())
            Krita.instance().writeSetting("", "shapesAndLayersShowEraser", json.dumps(self.settings) )
            #Krita.instance().writeSetting("", "shapesAndLayersShowEraser", ','.join("{!s},{!r}".format(k,v) for (k,v) in self.settings.items()) )
        
        if status is True:
            
            Krita.instance().action('erase_action').toggled.connect(self.toggleBindEraser)

            
            for item in Krita.instance().action('erase_action').associatedWidgets():
                if isinstance(item, QToolButton):
                    self.eraserBtn = item
                    break
                
            
            self.toolChangeFilter = self.toolChangeFilterClass(self)
            
            for item in Krita.instance().action('InteractionTool').associatedWidgets():
                if isinstance(item, QWidget):
                    self.toolBoxWidget = item
                    break
            self.toolBoxWidget.installEventFilter(self.toolChangeFilter)
            
            if self.eraserBtn.isEnabled():
                self.eraserStatus=False
                doc = Krita.instance().activeDocument()
                if doc:
                    node = doc.activeNode()
                    if node and node.type() == 'paintlayer':
                        self.toggleBindEraser(True)
                
                
        else:
            Krita.instance().action('erase_action').toggled.disconnect(self.toggleBindEraser)
            self.toggleBindEraser(False)

   
    
    def toggleBindEraser(self, status, source = 0):
        self.eraserStatus=status
        subWindow = self.mdi.currentSubWindow()
        
        if status is True:
            #print ("BIND ERASER!", source)
            self.mdi.viewport().installEventFilter(self.mdiFilter)
            self.setEraserCursor(1)
            if source == 0:
                self.toolBoxWidget.installEventFilter(self.toolChangeFilter)
        else:
            #print ("UNBIND ERASER!", source)
            self.mdi.viewport().removeEventFilter(self.mdiFilter)
            self.setEraserCursor(0)
            if source == 0:
                self.toolBoxWidget.removeEventFilter(self.toolChangeFilter)

    def bindCanvasZoom(self):
        qwin = Krita.instance().activeWindow().qwindow()
        self.canvasZoomWidget = qwin.statusBar().findChild(QCompleter).parent().parent()
        self.canvasZoomWidget.currentTextChanged.connect(self.slotCanvasZoom)

    def unbindCanvasZoom(self):
        qwin = Krita.instance().activeWindow().qwindow()
        self.canvasZoomWidget = qwin.statusBar().findChild(QCompleter).parent().parent()
        self.canvasZoomWidget.currentTextChanged.disconnect(self.slotCanvasZoom)
        
    def slotCanvasZoom(self, text):
        text = text.replace(',','').replace('%','').replace('.','')
        if text.isnumeric():
            #print ("ZOOM!", text)
            self.setEraserCursor(2)

    def setEraserCursor(self, mode = 0):
        #print ("set cursor", mode)
        if mode == 1 or (mode == 2 and self.eraserMode is True):
            self.eraserMode = True
            if self.settings['boolEnableCursorAdjust'] == 0:
                newCursorSize = str(self.currentCursorSize)
            else:
                adjustMode = None
                if not self.canvasZoomWidget:
                    qwin = Krita.instance().activeWindow().qwindow()
                    completer = qwin.statusBar().findChild(QCompleter)
                    if completer:
                        self.canvasZoomWidget = completer.parent().parent()
                        
                if self.canvasZoomWidget:
                    self.canvasZoomLevel = float(self.canvasZoomWidget.currentText().replace(',','').replace('%',''))
                else:
                    self.canvasZoomLevel = 100
                
                if self.settings['intLessThan'] > self.canvasZoomLevel:
                    adjustMode = self.settings['lessThanAdjustCmb']
                elif self.settings['intMoreThan'] < self.canvasZoomLevel:
                    adjustMode = self.settings['moreThanAdjustCmb']
                else:
                    adjustMode = self.settings['defaultSizeAdjustCmb']
                    
                adjustList = adjustMode.split(': ')
                newCursorSize = int(self.settings['defaultSizeCmb'])
                #print ("ADJUST", adjustList[0])
                
                if adjustList[0] == 'Hide':
                    QApplication.restoreOverrideCursor()
                    QApplication.setOverrideCursor(Qt.BlankCursor)
                    newCursorSize = 0
                elif adjustList[0] == 'Adjust Size':
                    newCursorSize = newCursorSize*(self.canvasZoomLevel/100)
                    
                elif adjustList[0] == 'Static':
                    newCursorSize = adjustList[1]
            
            
            if int(newCursorSize) > 0:
                #if newCursorSize not in self.eraserCursorCache:
                #    self.eraserCursorCache[newCursorSize] = QCursor(QIcon(self.eraserCursorFile).pixmap(QSize( int(newCursorSize) , int(newCursorSize) )))
                #    self.currentEraserCursor = self.eraserCursorCache[newCursorSize]
                if newCursorSize != self.currentCursorSize:
                    self.currentEraserCursor = QCursor(QIcon(self.eraserCursorFile).pixmap(QSize( int(newCursorSize) , int(newCursorSize) )))
                
                self.currentCursorSize = newCursorSize
                QApplication.restoreOverrideCursor()
                QApplication.setOverrideCursor(self.currentEraserCursor)
                
        else:
            self.eraserMode = False
            QApplication.restoreOverrideCursor()
            QApplication.restoreOverrideCursor()

    class toolChangeFilterClass(QWidget):
        def __init__(self, caller, parent=None):
            super().__init__()
            self.caller = caller
            
        def eventFilter(self, obj, event):
            if event.type() == 113:
                eraserStatus = self.caller.eraserStatus
                if eraserStatus is None: return False
                eraserEnabled = self.caller.eraserBtn.isEnabled()
                doc = Krita.instance().activeDocument()
                if doc:
                    node = doc.activeNode()
                    if node and node.type() != 'paintlayer':
                        eraserEnabled = False
                
                if eraserStatus is False and eraserEnabled:
                    #print ("ERASER EVENT!" ,obj)
                    self.caller.toggleBindEraser(True,1)
                elif eraserStatus is True and not eraserEnabled:
                    self.caller.toggleBindEraser(False,1)
                    
            return False
            
    class mdiFilterClass(QWidget):
        def __init__(self, caller, parent=None):
            super().__init__()
            self.caller = caller
            
        def eventFilter(self, obj, event):
            if event.type() == 10:
                #print ("Event", event.type(), obj)
                self.caller.setEraserCursor(1)
            elif event.type() == 11:
                #print ("Event", event.type(), obj)
                self.caller.setEraserCursor(0)
                
            return False
