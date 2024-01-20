from krita import *
from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg, uic
import os
import json
import re
from xml.dom import minidom

class ShapesAndLayersFontManagerHelper():
    def __init__(self, caller, parent = None):
        super().__init__()
        self.caller=caller
        self.dlg=None
        self.fontdb=None
        self.watcher=None
        self.importFontList = []
        self.fontDict = {
            'T': {},
            'D': {}
        }

        self.blockDirChange = 0
        #self.enableWatchTempFontDir = False
        #self.tempFontDir = None
        
        settingsData = Krita.instance().readSetting("", "shapesandlayersFontManagerHelper","")
        
        if settingsData.startswith('{'):
            self.settings = json.loads(settingsData)
        else:
            self.settings = {
                'tempFontDir': '',
                'enableWatchTempFontDir': 0
            }
        

    def onLoad(self, window):
        qwin = window.qwindow()
        
        subaction = window.createAction("shapesAndLayersFontManagerHelper", "Font Manager Helper...", "tools/scripts/shapesAndLayers")
        subaction.triggered.connect(self.slotFontManagerHelper)
        
        if self.settings['tempFontDir'] != '' and self.settings['enableWatchTempFontDir'] == 1:
            self.fontdb = QtGui.QFontDatabase()
            self.watcher = QFileSystemWatcher()
            self.slotTempFontDirChanged(self.settings['tempFontDir'])
            self.watcher.directoryChanged.connect(self.slotTempFontDirChanged)
            if not self.watcher.addPath(self.settings['tempFontDir']):
                QMessageBox.warning(Krita.instance().activeWindow().qwindow(), "ShapesAndLayers Font Manager Helper", "Failed to set up watcher for directory: "+self.settings['tempFontDir'])


    def slotFontManagerHelper(self):
        result = self.openDialog()
        self.caller.errCheck(result)
        
    def slotGetFontPath(self):
        fileDlg = QFileDialog()
        fileDlg.setFileMode(QFileDialog.ExistingFiles)
        fileDlg.setNameFilter("Font Files (*.ttf *.otf)")

        if fileDlg.exec_():
            self.importFontList = fileDlg.selectedFiles()
            i = len(self.importFontList)
            if i > 0:
                self.dlg.fontPathLabel.setText( self.importFontList[0] + ('' if i == 1 else ' + ' + str(i-1) + ' fonts') )
        else:
            self.importFontList = []
        
        self.dlg.importFontBtn.setEnabled(True)
            
    def slotImportFonts(self):
        for font in self.importFontList:
            if font in self.fontDict['T']:
                if not self.fontdb.removeApplicationFont(font):
                    QMessageBox.warning(Krita.instance().activeWindow().qwindow(), "Error", "Failed to reload font: "+font)
                    continue
            
            
            fontId = self.fontdb.addApplicationFont(font)
            if fontId >= 0:
                self.fontDict['T'][font]={ 'id':fontId, 'families':self.fontdb.applicationFontFamilies(fontId) }
            else:
                QMessageBox.warning(Krita.instance().activeWindow().qwindow(), "Error", "Failed to load font: "+font)
        
        self.importFontList=[]
        self.dlg.fontPathLabel.setText('Select a font')
        self.updateFontList()
        self.dlg.importFontBtn.setEnabled(False)

    def slotReloadSystemFonts(self):
        fontDirs = QStandardPaths.standardLocations(QStandardPaths.FontsLocation)
        
        for fontDir in fontDirs:
            for filename in os.listdir(fontDir):
                fontPath = os.path.join(fpath, filename)
            '''
            fontId = self.fontdb.addApplicationFont(fontPath)
            
            if fontId >= 0: 
                fontFamilies = self.fontdb.applicationFontFamilies(fontId)

            else:
                QMessageBox.warning(Krita.instance().activeWindow().qwindow(), "Error", "Failed to load font: "+fontPath)

            '''

    def slotGetTempFontDir(self):
        fileDlg = QFileDialog()
        fileDlg.setFileMode(QFileDialog.DirectoryOnly)
        fileDlg.setNameFilter("Font Files (*.ttf *.otf)")

        if fileDlg.exec_():
            self.settings['tempFontDir'] = fileDlg.selectedFiles()[0]
            self.dlg.watchTempFontDirLabel.setText(self.settings['tempFontDir'])
        else:
            self.settings['tempFontDir'] = ''
            
        Krita.instance().writeSetting("", "shapesandlayersFontManagerHelper", json.dumps(self.settings) )
        self.slotTempFontDirChanged(self.settings['tempFontDir'])
            
            
    def slotWatchTempFontDir(self):
        if self.settings['tempFontDir'] == '':
            QMessageBox.warning(Krita.instance().activeWindow().qwindow(), "Error", "No directory was selected!")
            return
        #self.openDialog(False)
            
        self.dlg.toggleWatchTempFontDirBtn.setEnabled(False)

        if self.watcher is None:
            self.watcher = QFileSystemWatcher()
            
        if self.settings['enableWatchTempFontDir'] == 0:
            self.dlg.watchTempFontDirBtn.setEnabled(False)
            
            self.watcher.directoryChanged.connect(self.slotTempFontDirChanged)
            if not self.watcher.addPath(self.settings['tempFontDir']):
                QMessageBox.warning(Krita.instance().activeWindow().qwindow(), "Error", "Failed to set up watcher for directory: "+self.settings['tempFontDir'])
            
            self.dlg.toggleWatchTempFontDirBtn.setText('Stop Watching')
            self.dlg.toggleWatchTempFontDirBtn.setIcon(QIcon.fromTheme('media-playback-stop'))
            self.settings['enableWatchTempFontDir']=1
            Krita.instance().writeSetting("", "shapesandlayersFontManagerHelper", json.dumps(self.settings) )
            self.dlg.toggleWatchTempFontDirBtn.setEnabled(True)
        else:
            self.watcher.directoryChanged.disconnect(self.slotTempFontDirChanged)
            if not self.watcher.removePath(self.settings['tempFontDir']):
                QMessageBox.warning(Krita.instance().activeWindow().qwindow(), "Error", "Failed to stop watcher for directory: "+self.settings['tempFontDir'])
            
            self.dlg.toggleWatchTempFontDirBtn.setText('Start Watching')
            self.dlg.toggleWatchTempFontDirBtn.setIcon(QIcon.fromTheme('media-playback-start'))
            self.dlg.toggleWatchTempFontDirBtn.setEnabled(True)
            self.settings['enableWatchTempFontDir']=0
            Krita.instance().writeSetting("", "shapesandlayersFontManagerHelper", json.dumps(self.settings) )
            self.dlg.watchTempFontDirBtn.setEnabled(True)

    def slotTempFontDirChanged(self, path):
        self.blockDirChange += 1
        if self.blockDirChange > 1: return
        #print ("DIR CHANGED!", path)
        newList = {}
        updatedItems = 0
        it = QDirIterator(self.settings['tempFontDir'], ['*.ttf','*.otf'],  QDir.Files)
        while it.hasNext():
            font = it.next()
            if font in self.fontDict['D']:
                newList[font]=1
            else:
                newList[font]=2
                fontId = self.fontdb.addApplicationFont(font)
                #print ("NEW FONT!", font, fontId)
                if fontId >= 0:
                    self.fontDict['D'][font]={ 'id':fontId, 'families':self.fontdb.applicationFontFamilies(fontId) }
                    updatedItems += 1
        
        for font in list(self.fontDict['D'].keys()):
            if font not in newList:
                #print("REMOVE FONT", font)
                if self.fontdb.removeApplicationFont(self.fontDict['D'][font]['id']):
                    del self.fontDict['D'][font]
                    updatedItems += 1
        #print ("UPDATED FONTS", updatedItems)
        if updatedItems > 0:
            if self.dlg: self.updateFontList()
        if self.blockDirChange >= 1:
            self.blockDirChange=0
            if self.blockDirChange > 1:
                self.slotTempFontDirChanged(path)
            



    def updateFontList(self):
        self.dlg.fontList.clear()
        for i, font in enumerate(self.fontDict['T']):
            self.fontDict['T'][font]['row']=i
            rowItem = QListWidgetItem(QIcon('folder'),"",self.dlg.fontList)
            rowContent = self.RowItem(self, rowItem, font,'T')
            
            rowItem.setSizeHint(rowContent.sizeHint())
            self.dlg.fontList.addItem(rowItem)
            self.dlg.fontList.setItemWidget(rowItem, rowContent)

        for i, font in enumerate(self.fontDict['D']):
            self.fontDict['D'][font]['row']=i
            rowItem = QListWidgetItem(QIcon('folder'),"",self.dlg.fontList)
            rowContent = self.RowItem(self, rowItem, font,'D')
            
            rowItem.setSizeHint(rowContent.sizeHint())
            self.dlg.fontList.addItem(rowItem)
            self.dlg.fontList.setItemWidget(rowItem, rowContent)
        
    def openDialog(self, show = True):
        if not self.dlg:
            if not self.fontdb: self.fontdb = QtGui.QFontDatabase()
            #print ( self.fontdb.families() )
            self.dlg = uic.loadUi(os.path.dirname(os.path.realpath(__file__)) + '/FontManagerHelper.ui')
            
            self.dlg.loadedFontsLabel.setVisible(False)
            self.dlg.reloadSystemFontsBtn.setVisible(False)
            self.dlg.watchSystemFontDirBtn.setVisible(False)
            
            if self.settings['tempFontDir'] != '':
                self.dlg.watchTempFontDirLabel.setText(self.settings['tempFontDir'])

            if self.settings['enableWatchTempFontDir'] == 1:
                self.dlg.toggleWatchTempFontDirBtn.setText('Stop Watching')
                self.dlg.toggleWatchTempFontDirBtn.setIcon(QIcon.fromTheme('media-playback-stop'))
                self.updateFontList()


            self.dlg.fontPathBtn.clicked.connect(self.slotGetFontPath)
            self.dlg.importFontBtn.clicked.connect(self.slotImportFonts)
            self.dlg.reloadSystemFontsBtn.clicked.connect(self.slotReloadSystemFonts)
            
            self.dlg.watchTempFontDirBtn.clicked.connect(self.slotGetTempFontDir)
            self.dlg.toggleWatchTempFontDirBtn.clicked.connect(self.slotWatchTempFontDir)
            
            self.dlg.importFontBtn.setEnabled(False)
            flags = self.dlg.windowFlags()
            self.dlg.setWindowFlags(flags | Qt.Tool)

        if show: self.dlg.show()
        return { "status": 1 }        
        

    class RowItem(QWidget):
        def __init__(self, caller, rowItem, fontPath, fontPrivateType, parent=None):
            super().__init__(parent)
            self.caller = caller
            self.rowItem = rowItem
            self.fontPath = fontPath
            self.fontPrivateType = fontPrivateType


            self.row = QHBoxLayout()
            
            self.viewFont = QPushButton(QIcon.fromTheme('document-print-preview'),"View")
            self.applyFont = QPushButton(QIcon.fromTheme('format-text-color'),"Apply")
            
            fontDir, fontFileName = os.path.split(self.fontPath)
            
            self.removeFont = QPushButton(QIcon.fromTheme('edit-delete'),"Remove")
            showFonts = []
            
            
            for fontFamily in self.caller.fontDict[self.fontPrivateType][self.fontPath]['families']:
                showFonts.append('<span style="font-family: '+fontFamily+'">'+fontFamily+'</span>')

            self.row.addWidget(QLabel( '<b>'+fontFileName+'</b> - '+ ','.join(showFonts) +'<br><font size=1>'+fontDir+'</font>' ), 10)
            self.row.addWidget(QLabel(fontPrivateType), 1)
            self.row.addWidget(self.viewFont,3)
            self.row.addWidget(self.applyFont,3)
            self.row.addWidget(self.removeFont,3)
            
            self.viewFont.clicked.connect(self.slotViewFont)
            self.applyFont.clicked.connect(self.slotApplyFont)
            self.removeFont.clicked.connect(self.slotRemoveFont)

            self.setLayout(self.row)
            
            
            
        def slotViewFont(self):
            QtGui.QDesktopServices.openUrl(QUrl(self.fontPath))
        
        def slotApplyFont(self):
            doc = Krita.instance().activeDocument()
            currentLayer = doc.activeNode()
            selectedShape = None

            if currentLayer.type() == 'vectorlayer':
                svgHeader = re.compile('(^.*?\<svg.*?["\']\\s*\>).*$', re.DOTALL).sub(r'\1', currentLayer.toSvg())
                fontFamily = self.caller.fontDict[self.fontPrivateType][self.fontPath]['families']

                for shape in currentLayer.shapes():
                    if shape.isSelected() and shape.type() == 'KoSvgTextShapeID':
                        selectedShape = shape
                        break
                        
            if selectedShape:
                svgContent = svgHeader+shape.toSvg(True,False)+'</svg>'
                svgDom = minidom.parseString(svgContent)
                for node in svgDom.getElementsByTagName('text'):
                    node.setAttribute('font-family', fontFamily[0] )
                    node.setAttribute('style',re.sub('font-family:.*?(;|$)','font-family: '+fontFamily[0]+';',node.getAttribute("style") )  )
                    for subnode in node.getElementsByTagName('tspan'):
                        if subnode.hasAttribute("font-family"):
                            subnode.setAttribute('font-family', fontFamily[0] )
                        if subnode.hasAttribute("style"):
                            subnode.setAttribute('style',re.sub('font-family:.*?(;|$)','font-family: '+fontFamily[0]+';',subnode.getAttribute("style") )  )

                selectedShape.remove()
                shapes = currentLayer.addShapesFromSvg(svgDom.toxml())
                doc.refreshProjection()
                shapes[0].select()
            else:
                QMessageBox.warning(Krita.instance().activeWindow().qwindow(), "Error", "No Text Shape is selected to apply")

        
        def slotRemoveFont(self):
            if self.fontPrivateType == 'D' and self.caller.settings['enableWatchTempFontDir'] == 1:
                reply = QMessageBox.question(Krita.instance().activeWindow().qwindow(), "Confirm", "You are removing a font that belongs to a watched directory, are you sure you wish to permanently delete this font from the directory?", QMessageBox.Yes, QMessageBox.No )
                
                if reply == QMessageBox.Yes and os.path.exists(self.fontPath):
                    os.remove(self.fontPath)
                return
                
            if self.caller.fontdb.removeApplicationFont(self.caller.fontDict[self.fontPrivateType][self.fontPath]['id']):
                del self.caller.fontDict[self.fontPrivateType][self.fontPath]
                self.caller.updateFontList()
            else:
                QMessageBox.warning(Krita.instance().activeWindow().qwindow(), "Error", "Failed to remove font: "+font)

