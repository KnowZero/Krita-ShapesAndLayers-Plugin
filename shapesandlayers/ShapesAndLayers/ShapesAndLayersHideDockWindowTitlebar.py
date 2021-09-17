from krita import *
from PyQt5 import QtCore, QtGui, QtWidgets


class ShapesAndLayersHideDockWindowTitlebar():
    def __init__(self, caller, parent = None):
        super().__init__()
      
        settingsList = Krita.instance().readSetting("", "shapesAndLayersHideDockWindowTitlebar","").split(',')
        self.settings = { 'enabled': 0 } if len(settingsList) < 2 else { settingsList[i]: int(settingsList[i + 1]) for i in range(0, len(settingsList), 2) }
        
    def onLoad(self, window):
        self.qwin = window.qwindow()
        self.action = window.createAction("shapesAndLayersHideDockWindowTitlebar", "Hide Dock Window Titlebars", "tools/scripts/shapesAndLayers")
        self.action.setCheckable(True)
        self.action.triggered.connect(self.toggleVisibleTitlebars)
        
        self.dockerList = {}
        
        if self.settings['enabled']:
            self.action.setChecked(True)
            self.toggleVisibleTitlebars()
        
    def toggleVisibleTitlebars(self):
        dockers = self.qwin.findChildren(QtWidgets.QDockWidget)
        
        self.settings['enabled']=int(self.action.isChecked())
            
        Krita.instance().writeSetting("", "shapesAndLayersHideDockWindowTitlebar", ','.join("{!s},{!r}".format(k,v) for (k,v) in self.settings.items()) )
        
        if self.action.isChecked():
            for docker in dockers:
                titlebar = docker.titleBarWidget()
                if titlebar is not None and titlebar.findChild(QHBoxLayout) is None:
                    titlebar.setVisible(False)
                self.dockerList[id(docker)]={ 'func': functools.partial(self.toggleVisibility, docker),'policy': docker.contextMenuPolicy() }
                docker.setContextMenuPolicy(3)
                docker.customContextMenuRequested.connect(self.dockerList[id(docker)]['func'])
        else:
            for docker in dockers:
                titlebar = docker.titleBarWidget()
                if titlebar is not None:
                    docker.titleBarWidget().setVisible(True)
                docker.setContextMenuPolicy(self.dockerList[id(docker)]['policy'])
                docker.customContextMenuRequested.disconnect(self.dockerList[id(docker)]['func'])           
                
    def toggleVisibility(self, docker):
        if QtGui.QGuiApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
            docker.titleBarWidget().setVisible( docker.titleBarWidget().isVisible() is False )
        
         
