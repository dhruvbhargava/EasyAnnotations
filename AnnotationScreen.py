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
# from Generators import Generator  as gen

class AnnotaionScreen(widget):
    def __init__(self,Image_folder_path,Annotation_folder_path,bbox_width,bbox_height,Generator,fixed = False):
        super(AnnotaionScreen, self).__init__()
        self.Fixed = fixed
        self.ImageDirectory = Image_folder_path
        self.bboxRatios = [bbox_width,bbox_height]
        self.CurrentStatusLabel = widgets.QLabel('',self)
        self.SaveAnnotationPath = Annotation_folder_path
        self.Image_List = []
        self.FileGen = Generator
        self.XML_GEN_DONE  = False
        for file in os.listdir(self.ImageDirectory):
           if '.jpeg' in file or ".JPG" in file  or ".PNG" in file or ".png" in file or ".jpg" in file or ".JPEG" in file:
                    self.Image_List.append(file)
        self.curr_image_path = os.path.join(self.ImageDirectory,self.Image_List[0])
        self.curr_image_meta = []
        self.Image_cv2 = cv2.imread(self.curr_image_path)
        self.ShapeActual = self.Image_cv2.shape
        self.Image_cv2 = cv2.resize(self.Image_cv2,(int(self.Image_cv2.shape[1]/2),int(self.Image_cv2.shape[0]/2)))
        self.dims = {'left': 50, 'right': 50,
                     'top': 10, 'width': (self.Image_cv2.shape[1])*1.2, 'height': (self.Image_cv2.shape[0])*1.5}
        self.GridCell = {
            'verticle': self.dims['height']/20, 'horizontal': self.dims['width']/20}
        self.setWindowTitle("TransformTool")
        self.Image = widgets.QLabel(self)
        self.pmi = gui.QImage(
        self.Image_cv2.data, self.Image_cv2.shape[1], self.Image_cv2.shape[0], self.Image_cv2.shape[1]*3, gui.QImage.Format_RGB888)
        self.rubberband = widgets.QRubberBand(widgets.QRubberBand.Rectangle,self)
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.currentTransform = ''
        self.setGeometry(self.dims['left'], self.dims['top'],
                         self.dims['width'], self.dims['height'])                 
        if self.Fixed:
            self.Image.mousePressEvent = self.renderFixedBox
        elif not self.Fixed:
            self.mousePressEvent = self.variableBoxInit
            self.mouseMoveEvent = self.buildVariableBox
            self.mouseReleaseEvent = self.renderVariableBox
        self.Home()                         

    def renderFixedBox(self,event):
        center = {'x':event.pos().x(),'y':event.pos().y()}
        self.Image_cv2 ,topleft,bottomright= BB.DrawBoxFixed(self.Image_cv2,center,self.bboxRatios)
        self.curr_image_meta.append(obj("person",topleft,bottomright))#make this label
        self.loadScreen(read = False)

    def checkValidArea(self,pos):
        if(pos.x()<self.GridCell['horizontal']*1 or pos.x()>self.GridCell['horizontal']*1+self.Image_cv2.shape[1]):
            return 0
        if(pos.y()<self.GridCell['verticle']*3 or pos.y()>self.GridCell['verticle']*3+self.Image_cv2.shape[0]):
            return 0
        return 1
    
    def variableBoxInit(self, event):
        self.origin = event.pos()
        if(not self.checkValidArea(self.origin) or self.Fixed):
            return
        self.rubberband.setGeometry(
            QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberband.show()
    
    def buildVariableBox(self, event):
        if self.rubberband.isVisible():
            curr = event.pos()
            if(not self.checkValidArea(curr) or self.Fixed):
                return
            self.rubberband.setGeometry(
                QtCore.QRect(self.origin, curr).normalized())

    def renderVariableBox(self, event):
        if(self.Fixed):
            return
        if self.rubberband.isVisible():
            self.rubberband.hide()
        coords = []
        coords.append(self.origin.x()-self.GridCell['horizontal'])
        coords.append(self.origin.y()-(self.GridCell['verticle']*3))
        coords.append(event.pos().x()-self.GridCell['horizontal'])
        coords.append(event.pos().y()-(self.GridCell['verticle']*3))
        self.Image_cv2 ,topleft,bottomright= BB.DrawBoxVariable(self.Image_cv2,coords)
        self.curr_image_meta.append(obj("person",topleft,bottomright))
        self.loadScreen(read = False)
    
    def handleNext(self):
        self.XML_GEN_DONE = False
        self.CurrentStatusLabel.setText('')
        self.curr_image_meta = []
        self.Image_List.remove(self.curr_image_path.split('/')[-1])
        if len(self.Image_List) == 0:
            self.close()
            exit()
        self.curr_image_path = os.path.join(self.ImageDirectory,self.Image_List[0])
        self.loadScreen(True)

    def handleGenerate(self):
        if self.curr_image_meta == []:
            self.CurrentStatusLabel.setText("*NOTHING TO TAG*")
            return
        split_names = self.curr_image_path.split('/')
        image_file_name = split_names[-1]
        if '.jpeg' in image_file_name :
            xml_file_name = image_file_name.replace('.jpeg','.xml')
        elif '.jpg' in image_file_name :
            xml_file_name = image_file_name.replace('.jpg','.xml')
        elif '.png' in image_file_name :
            xml_file_name = image_file_name.replace('.png','.xml')
        elif '.JPG' in image_file_name :
            xml_file_name = image_file_name.replace('.JPG','.xml')
        elif '.JPEG' in image_file_name :
            xml_file_name = image_file_name.replace('.JPEG','.xml')
        generated_string = self.FileGen.generate(self.Image_cv2.shape,self.curr_image_meta,self.ImageDirectory,image_file_name)
        with open(os.path.join(self.SaveAnnotationPath,xml_file_name),"wb") as xml_file:
            xml_file.write(generated_string)    
        self.CurrentStatusLabel.setText("*DONE!*")
        self.XML_GEN_DONE = True
    
    def handleReset(self):
        if self.XML_GEN_DONE :
            if '.jpeg' in self.curr_image_path :
                xml_file_name = self.curr_image_path.split('/')[-1].replace('.jpeg','.xml')
            elif '.jpg' in self.curr_image_path :
                xml_file_name = self.curr_image_path.split('/')[-1].replace('.jpg','.xml')
            elif '.png' in self.curr_image_path:
                xml_file_name = self.curr_image_path.split('/')[-1].replace('.png','.xml')
            elif '.JPG' in self.curr_image_path :
                xml_file_name = self.curr_image_path.split('/')[-1].replace('.JPG','.xml')        
            
            os.remove(os.path.join(self.SaveAnnotationPath,xml_file_name))
        self.curr_image_meta = []
        self.CurrentStatusLabel.setText("")
        self.loadScreen(True)

    def loadScreen(self,read):
        if read:
            self.Image_cv2 = cv2.imread(self.curr_image_path)
            self.ShapeActual = self.Image_cv2.shape
            self.Image_cv2 = cv2.resize(self.Image_cv2,(int(self.Image_cv2.shape[1]/2),int(self.Image_cv2.shape[0]/2)))
            
        self.dims = {'left': 50, 'right': 50,
                     'top': 10, 'width': (self.Image_cv2.shape[1])*1.2, 'height': (self.Image_cv2.shape[0])*1.5}
        self.GridCell = {
            'verticle': self.dims['height']/20, 'horizontal': self.dims['width']/20}
        self.setGeometry(self.dims['left'], self.dims['top'],
                         self.dims['width'], self.dims['height'])   
        self.NextButton.move(self.GridCell['horizontal']
                        * 1, self.GridCell['verticle']*1)
        self.CurrentStatusLabel.move(self.GridCell['horizontal']
                        * 7, self.GridCell['verticle']*1)                        
        self.GenerateButton.move(self.GridCell['horizontal']*1,
                    self.GridCell['verticle']*18)
        self.UndoButton.move(
            self.GridCell['horizontal']*15, self.GridCell['verticle']*18)                         
        self.pmi = gui.QImage(
            self.Image_cv2.data, self.Image_cv2.shape[1], self.Image_cv2.shape[0], self.Image_cv2.shape[1]*3, gui.QImage.Format_RGB888)
        self.PixMap = gui.QPixmap(self.pmi)
        
        # self.PixMap = self.PixMap.scaled(
        #     self.GridCell['horizontal']*18, self.GridCell['verticle']*13)
        self.Image.setPixmap(self.PixMap)
        self.Image.resize(
            self.Image_cv2.shape[1], self.Image_cv2.shape[0])
        self.Image.move(self.GridCell['horizontal']
                        * 1, self.GridCell['verticle']*3)
        
    #The UI Component
    def Home(self):
        self.setWindowTitle("Annotations")
        self.NextButton = widgets.QPushButton('Next',self)
        self.UndoButton = widgets.QPushButton ('Undo',self)
        self.GenerateButton = widgets.QPushButton('Gen XML', self)
        self.loadScreen(True)
        self.NextButton.clicked.connect(self.handleNext)
        self.GenerateButton.clicked.connect(self.handleGenerate)
        self.UndoButton.clicked.connect(self.handleReset)
    