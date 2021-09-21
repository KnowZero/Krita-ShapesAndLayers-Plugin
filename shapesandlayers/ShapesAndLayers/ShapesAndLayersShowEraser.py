from krita import *
from PyQt5 import QtCore, QtGui, QtWidgets


class ShapesAndLayersShowEraser():
    def __init__(self, caller, parent = None):
        super().__init__()
      
        settingsList = Krita.instance().readSetting("", "shapesAndLayersShowEraser","").split(',')
        self.settings = { 'enabled': 0 } if len(settingsList) < 2 else { settingsList[i]: int(settingsList[i + 1]) for i in range(0, len(settingsList), 2) }
        
        self.eraserStatus = None
        
        self.eraserCursor = QtGui.QCursor(QtGui.QIcon(os.path.dirname(os.path.realpath(__file__)) + '/eraser_cursor.svg').pixmap(
                QtCore.QSize(32,32) if QtWidgets.QApplication.primaryScreen().size().width() <= 3000 else QtCore.QSize(64,64)  
                ))
        
    def onLoad(self, window):
        qwin = window.qwindow()
        self.action = window.createAction("shapesAndLayersShowEraser", "Show Eraser Cursor", "tools/scripts/shapesAndLayers")
        self.action.setCheckable(True)
        self.action.toggled.connect(self.toggleShowEraser)
        
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

    
    def windowCreatedSetup(self):
        self.action.setChecked(True)
        self.notify.windowCreated.disconnect(self.windowCreatedSetup)

    
    def toggleShowEraser(self, status, source = 0):
        if source == 0:
            self.settings['enabled']=int(self.action.isChecked())
            Krita.instance().writeSetting("", "shapesAndLayersShowEraser", ','.join("{!s},{!r}".format(k,v) for (k,v) in self.settings.items()) )
        
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
            self.toolBoxWidget.removeEventFilter(self.toolChangeFilter)

            
    def toggleBindEraser(self, status, source = 0):
        self.eraserStatus=status
        subWindow = self.mdi.currentSubWindow()
        
        if status is True:
            #print ("BIND ERASER!", source)
            self.mdiFilter = self.mdiFilterClass(self)
            self.mdi.viewport().installEventFilter(self.mdiFilter)
            if source == 0:
                self.toolBoxWidget.installEventFilter(self.toolChangeFilter)
        else:
            #print ("UNBIND ERASER!", source)
            self.mdi.viewport().removeEventFilter(self.mdiFilter)
            if source == 0:
                self.toolBoxWidget.removeEventFilter(self.toolChangeFilter)


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
                QApplication.setOverrideCursor(self.caller.eraserCursor)
            elif event.type() == 11:
                #print ("Event", event.type(), obj)
                QApplication.restoreOverrideCursor()
                QApplication.restoreOverrideCursor()
                
            return False
