import os 
import sys 
import cv2
from PyQt5 import QtGui as gui
import PyQt5.QtWidgets as widgets
from PyQt5.QtWidgets import QApplication as app
from PyQt5.QtWidgets import QWidget as widget
import PyQt5.QtCore as QtCore
import BoundingBox as BB
from BoundingBox import TaggedObject as obj
from SelectorLayover import SelectorOverlay as SO
from AnnotationScreen import AnnotaionScreen as AnotScreen
from Generators.Generator import Generator as Generator

class StartScreen(widget):
           
    def __init__(self):
        super(StartScreen, self).__init__()
        self.setWindowTitle("Folder Path")
        self.options = {'box_height':0,'box_width': 0}
        self.build_params = {'FOLDER PATH':'','ANNOTATION PATH':''}
        self.dims = {'left': 50, 'right': 50,
                     'top': 10, 'width': 500, 'height': 550}
        self.GridCell = {
            'verticle': self.dims['height']/20, 'horizontal': self.dims['width']/20}
        self.setGeometry(self.GridCell['horizontal']*5,self.GridCell['verticle']*16,self.GridCell['horizontal']*20,self.GridCell['verticle']*16)
        self.Fixed = False
        self.generator = Generator()
        self.Screen()

    def seletFolderInput(self):
        dir = widgets.QFileDialog.getExistingDirectory(self, 
                      "Open Save Directory", options=widgets.QFileDialog.DontUseNativeDialog)
        if dir != '':
            self.InputPathField.setText(dir+'/')
    
    def fixedBoxCheckedHandler(self):
        if not self.FixedBoxChecked.isChecked():
            self.BoundingBoxHeightField.setReadOnly(True)
            self.BoundingBoxWidthField.setReadOnly(True)
        else:
            self.BoundingBoxHeightField.setReadOnly(False)
            self.BoundingBoxWidthField.setReadOnly(False)
    
    def seletFolderAnnotation(self):
        dir = widgets.QFileDialog.getExistingDirectory(self, 
                      "Open Save Directory", options=widgets.QFileDialog.DontUseNativeDialog)
        if dir != '':
            self.AnnotationsPathField.setText(dir+'/')
        
    def Navigate(self):
        self.generator.setFormat(self.FileFormatOptions.currentText())
        self.build_params['FOLDER PATH'] =  str(self.InputPathField.text())
        self.build_params['ANNOTATION PATH'] = str(self.AnnotationsPathField.text())
        if self.build_params['FOLDER PATH'] == '' and self.build_params['ANNOTATION PATH'] == '':
            self.InputLabel.setText("** Can't be empty enter FOLDER PATH **")
            self.InputLabel.setText("** Can't be empty enter  PATH **")
        elif self.build_params['FOLDER PATH'] == '':
            self.InputLabel.setText("** Can't be empty enter FOLDER PATH **")
        elif self.build_params['ANNOTATION PATH'] == '':
            self.AnnotationsLabel.setText("** Can't be empty enter PATH **")
        else:
            if os.path.isdir(self.build_params['FOLDER PATH']):
                contains_jpeg = False
                for file in os.listdir(self.build_params['FOLDER PATH']):
                    if '.jpeg' in file or ".JPG" in file  or ".PNG" in file or ".png" in file or ".jpg" in file or ".JPEG" in file:
                        contains_jpeg = True 
                if not contains_jpeg:
                    self.InputLabel.setText("**NO IMAGES IN THE SPECIFIED FOLDER **")
                    return 
                if os.path.isdir(self.build_params['ANNOTATION PATH']):
                    self.cams = AnotScreen(self.build_params['FOLDER PATH'],self.build_params['ANNOTATION PATH'],self.BoundingBoxWidthField.text(),self.BoundingBoxHeightField.text(),self.generator,self.FixedBoxChecked.isChecked())
                    self.cams.show()
                    self.close()                                   
                else:
                    os.mkdir(self.build_params['ANNOTATION PATH'])
                    return 
            else:
                self.InputLabel.setText("**FOLDER DOESN'T EXIST**")  
                return

    def addFileFormatOptions(self):
        options = self.generator.getAllFormats()
        for option in options:
            self.FileFormatOptions.addItem(option)

    def Screen(self):
        GoButton = widgets.QPushButton('GO',self)
        SelectButton = widgets.QPushButton('Select',self)
        SelectButton2 = widgets.QPushButton('Select',self)
        fileFormatLabel = widgets.QLabel('Format:',self)
        self.FixedBoxChecked = widgets.QCheckBox('Fixed Size Bounding Box ',self)
        self.FileFormatOptions = widgets.QComboBox(self)
        self.addFileFormatOptions()
        self.InputPathField = widgets.QLineEdit(self)
        self.AnnotationsPathField = widgets.QLineEdit(self)
        self.BoundingBoxWidthField = widgets.QLineEdit(self)
        self.WidthLabel = widgets.QLabel('Width:',self)
        self.HeightLabel = widgets.QLabel('Height:',self)
        self.BoundingBoxHeightField = widgets.QLineEdit(self)
        self.InputLabel = widgets.QLabel('Images Path', self)
        self.AnnotationsLabel = widgets.QLabel('Annotations Path', self)
        self.InputLabel.move(self.GridCell['horizontal']
                        * 1, self.GridCell['verticle']*1)
        self.AnnotationsLabel.move(self.GridCell['horizontal']
                        * 1, self.GridCell['verticle']*4.5)                        
        GoButton.move(self.GridCell['horizontal']
                        * 15.75, self.GridCell['verticle']*14)                        
        SelectButton.move(self.GridCell['horizontal']
                        * 15.75, self.GridCell['verticle']*3.2)   
        SelectButton2.move(self.GridCell['horizontal']
                        * 15.75, self.GridCell['verticle']*6.7)                                                    
        self.InputPathField.resize(
            self.GridCell['horizontal']*18, self.GridCell['verticle']*1)
        self.BoundingBoxWidthField.resize(
            self.GridCell['horizontal']*5, self.GridCell['verticle']*1)
        self.BoundingBoxHeightField.resize(
            self.GridCell['horizontal']*5, self.GridCell['verticle']*1)
        self.AnnotationsPathField.resize(
            self.GridCell['horizontal']*18, self.GridCell['verticle']*1)
        self.InputPathField.move(
            self.GridCell['horizontal']*1, self.GridCell['verticle']*2)
        self.AnnotationsPathField.move(
            self.GridCell['horizontal']*1, self.GridCell['verticle']*5.5)
        self.BoundingBoxWidthField.move(
            self.GridCell['horizontal']*3, self.GridCell['verticle']*10)            
        self.BoundingBoxHeightField.move(
            self.GridCell['horizontal']*14, self.GridCell['verticle']*10)                
        self.FixedBoxChecked.move(
            self.GridCell['horizontal']*1, self.GridCell['verticle']*8.5)            
        self.WidthLabel.move(
            self.GridCell['horizontal']*1, self.GridCell['verticle']*10)
        self.HeightLabel.move(
            self.GridCell['horizontal']*11.8, self.GridCell['verticle']*10)
        self.FileFormatOptions.move(
            self.GridCell['horizontal']*3.5, self.GridCell['verticle']*14)
        fileFormatLabel.move(
            self.GridCell['horizontal']*1, self.GridCell['verticle']*14)
        self.FixedBoxChecked.stateChanged.connect(self.fixedBoxCheckedHandler)
        SelectButton.clicked.connect(self.seletFolderInput)
        SelectButton2.clicked.connect(self.seletFolderAnnotation)
        GoButton.clicked.connect(self.Navigate)

    
if __name__ == "__main__":
    App = app(sys.argv) 
    stream = QtCore.QFile("themes/Diffnes/Diffnes.qss")
    stream.open(QtCore.QIODevice.ReadOnly)
    App.setStyleSheet(QtCore.QTextStream(stream).readAll())
    w = StartScreen()
    w.show()
    sys.exit(App.exec_())