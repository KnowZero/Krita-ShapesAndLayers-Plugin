from krita import *
from PyQt5 import QtCore, QtGui, QtWidgets


class ShapesAndLayersHideDockWindowTitlebar():
    def __init__(self, caller, parent = None):
        super().__init__()
      
        settingsList = Krita.instance().readSetting("", "shapesAndLayersHideDockWindowTitlebar","").split(',')
        
        self.dockerList = {}
        
        self.settings = { 'enabled': 0 } if len(settingsList) < 2 else { settingsList[i]: int(settingsList[i + 1]) for i in range(0, len(settingsList), 2) }

       
    def onLoad(self, window):
        self.qwin = window.qwindow()
        self.action = window.createAction("shapesAndLayersHideDockWindowTitlebar", "Hide Dock Window Titlebars", "tools/scripts/shapesAndLayers")
        self.action.setCheckable(True)
        
        
        
        if self.settings['enabled']:
            self.action.setChecked(True)
            self.toggleVisibleTitlebars()
            
        self.action.triggered.connect(self.toggleVisibleTitlebars)
        

        
    def toggleVisibleTitlebars(self):
        dockers = self.qwin.findChildren(QtWidgets.QDockWidget)
        self.settings['enabled']=int(self.action.isChecked())
            
        Krita.instance().writeSetting("", "shapesAndLayersHideDockWindowTitlebar", ','.join("{!s},{!r}".format(k,v) for (k,v) in self.settings.items()) )
        
        if self.action.isChecked():
            for docker in dockers:
                titlebar = docker.titleBarWidget()
                self.dockerList[id(docker)]={ 'func': functools.partial(self.toggleVisibility, docker),'policy': docker.contextMenuPolicy(), 'dummy':None, 'titlebar':titlebar }
                if titlebar is not None:
                    children = docker.titleBarWidget().children()
                    if (next((w for w in children if type(w).__name__ == 'QHBoxLayout'), None) is None or (len(children) == 5 and next((w for w in children if w.metaObject().className() == 'KSqueezedTextLabel'), None) is not None)):
                        self.hideTitleBar(docker)
                        #titlebar.setVisible(False)
                
                docker.setContextMenuPolicy(3)
                docker.customContextMenuRequested.connect(self.dockerList[id(docker)]['func'])
        else:
            for docker in dockers:
                titlebar = docker.titleBarWidget()
                dockName = docker.objectName()
                if titlebar is not None and self.dockerList[id(docker)]['dummy']:
                    docker.setTitleBarWidget(self.dockerList[id(docker)]['titlebar'])
                    #docker.titleBarWidget().setVisible(True)
                docker.setContextMenuPolicy(self.dockerList[id(docker)]['policy'])
                docker.customContextMenuRequested.disconnect(self.dockerList[id(docker)]['func'])           
    
    def hideTitleBar(self, docker):
        titlebar = docker.titleBarWidget()

        if not self.dockerList[id(docker)]['dummy']:
            self.dockerList[id(docker)]['dummy'] = QWidget()
            self.dockerList[id(docker)]['dummy'].hide()
            self.dockerList[id(docker)]['dummy'].setObjectName('DummyTitleBar')

        docker.setTitleBarWidget(self.dockerList[id(docker)]['dummy'])
        
    
    def toggleVisibility(self, docker):
        if QGuiApplication.keyboardModifiers() == Qt.ControlModifier:
            if docker.titleBarWidget().objectName() != 'DummyTitleBar':
                self.hideTitleBar(docker)
            else:
                docker.setTitleBarWidget(self.dockerList[id(docker)]['titlebar'])
            #docker.titleBarWidget().setVisible( docker.titleBarWidget().isVisible() is False )

        
         
