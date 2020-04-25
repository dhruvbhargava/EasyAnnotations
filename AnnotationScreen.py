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

class labelDialog(widgets.QDialog):
     def __init__(self, *args, **kwargs):
        super(labelDialog, self).__init__(*args, **kwargs)
        
        self.setWindowTitle("HELLO!")
        # QBtn = widgets.QDialogButtonBox.Ok | widgets.QDialogButtonBox.Cancel
        
        # self.buttonBox = widgets.QDialogButtonBox(QBtn)
        # self.buttonBox.accepted.connect(self.accept)
        # self.buttonBox.rejected.connect(self.reject)
        self.label = widgets.QLineEdit()
        self.layout = widgets.QVBoxLayout()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)


class AnnotaionScreen(widget):
    def __init__(self,Image_folder_path,Annotation_folder_path,bbox_width,bbox_height,Generator,fixed = False):
        super(AnnotaionScreen, self).__init__()
        self.Fixed = fixed
        self.currIndex = 0
        self.ImageDirectory = Image_folder_path
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
        self.DisplayBox = (400,600)
        self.factor = (self.DisplayBox[0]/self.ShapeActual[0],self.DisplayBox[1]/self.ShapeActual[1])
        self.bboxRatios = [int(bbox_width),int(bbox_height)]
        self.Image_cv2 = cv2.resize(self.Image_cv2,(int(600),int(400)))
        self.dims = {'left': 50, 'right': 50,
                     'top': 10, 'width': (self.Image_cv2.shape[1])*1.8, 'height': (self.Image_cv2.shape[0])*1.3}
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
        if not self.Fixed:
            return
        center = {'x':event.pos().x(),'y':event.pos().y()}
        self.rubberband.setGeometry(0,0,0,0)
        self.rubberband.hide()
        if not self.checkValidArea(event.pos()):
            return
        label = self.LabellingPopup(event.pos())
        self.Image_cv2 ,topleft,bottomright,dtp,dbr= BB.DrawBoxFixed(label,self.Image_cv2,center,self.bboxRatios,self.factor)
        tl = (max(center['x']-(int(self.bboxRatios[0])*self.factor[1]-self.GridCell['horizontal']),self.GridCell['horizontal']),max(center['y']-(int(self.bboxRatios[1])*self.factor[0]-3*self.GridCell['verticle']),3*self.GridCell['verticle']))
        br= (min(center['x']+(int(self.bboxRatios[0])*self.factor[1]+self.GridCell['horizontal']),600+self.GridCell['horizontal']),min(center['y']+(int(self.bboxRatios[1])*self.factor[0]+3*self.GridCell['verticle']),400+3*self.GridCell["verticle"]))
        self.curr_image_meta.append(obj(label,topleft,bottomright,tl,br))
        self.LabelsList.addItem("Object {}: {}".format(len(self.curr_image_meta),label))
        self.loadScreen(read = False)

    def checkValidArea(self,pos):
        if(pos.x()<self.GridCell['horizontal']*1 or pos.x()>self.GridCell['horizontal']+self.Image_cv2.shape[1]):
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
        curr = event.pos()
        if(not self.checkValidArea(curr) or self.Fixed or not self.checkValidArea(self.origin)):
                return
        if self.rubberband.isVisible():
        
            self.rubberband.setGeometry(
                QtCore.QRect(self.origin, curr).normalized())

    def renderVariableBox(self, event):
        if(self.Fixed):
            return
        if not self.checkValidArea(event.pos()) or not self.checkValidArea(self.origin) or abs(event.pos().x()-self.origin.x())<10 or abs(event.pos().y()-self.origin.y())<10:
            return
        post = event.pos()
        label = self.LabellingPopup(event.pos())
        if self.rubberband.isVisible():
            self.rubberband.hide()
        coords = []
        coords.append(self.origin.x()-self.GridCell['horizontal'])
        coords.append(self.origin.y()-(self.GridCell['verticle']*3))
        coords.append(post.x()-self.GridCell['horizontal'])
        coords.append(post.y()-(self.GridCell['verticle']*3))
        self.Image_cv2 ,topleft,bottomright,dtp,dbr= BB.DrawBoxVariable(label,self.Image_cv2,coords,self.factor)
        self.curr_image_meta.append(obj(label,topleft,bottomright,(int(self.origin.x()),int(self.origin.y())),(int(post.x()),int(post.y()))))
        self.LabelsList.addItem("Object {}: {}".format(len(self.curr_image_meta),label))
        self.loadScreen(read = False)
    
    def handleNext(self):
        self.XML_GEN_DONE = False
        self.CurrentStatusLabel.setText('')
        self.curr_image_meta = []
        self.currIndex+=1
        # self.Image_List.remove(self.curr_image_path.split('/')[-1])
        if len(self.Image_List) == self.currIndex:
            self.close()
            exit()
        self.curr_image_path = os.path.join(self.ImageDirectory,self.Image_List[self.currIndex])
        self.loadScreen(True)

    def handleGenerate(self):
        if self.curr_image_meta == []:
            self.CurrentStatusLabel.setText("*NOTHING TO TAG*")
            return
        if self.rubberband.isVisible():
            self.rubberband.hide()
        split_names = self.curr_image_path.split('/')
        image_file_name = split_names[-1]
        if '.jpeg' in image_file_name :
            xml_file_name = image_file_name.replace('.jpeg','.xml')#modularize
        elif '.jpg' in image_file_name :
            xml_file_name = image_file_name.replace('.jpg','.xml')#modularize
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
        self.LabelsList.clear()
        self.CurrentStatusLabel.setText("")
        self.loadScreen(True)

    def highlight(self,index):
        index = index.row()
        tpl = self.curr_image_meta[index].display_tl
        btm = self.curr_image_meta[index].display_br
        self.rubberband.setGeometry(tpl[0],tpl[1],btm[0]-tpl[0],btm[1]-tpl[1])
        self.rubberband.show()

    def loadScreen(self,read):
        if read:
            self.Image_cv2 = cv2.imread(self.curr_image_path)
            self.ShapeActual = self.Image_cv2.shape
            self.factor = (self.DisplayBox[0]/self.ShapeActual[0],self.DisplayBox[1]/self.ShapeActual[1])
            self.Image_cv2 = cv2.resize(self.Image_cv2,(int(600),int(400)))
            
        self.dims = {'left': 50, 'right': 50,
                     'top': 10, 'width': (self.Image_cv2.shape[1])*1.8, 'height': (self.Image_cv2.shape[0])*1.3}
        self.GridCell = {
            'verticle': self.dims['height']/20, 'horizontal': self.dims['width']/20}
        self.setGeometry(self.dims['left'], self.dims['top'],
                         self.dims['width'], self.dims['height'])   
        self.NextButton.move(self.GridCell['horizontal']
                        * 10.7, self.GridCell['verticle']*1)
        self.CurrentStatusLabel.move(self.GridCell['horizontal']
                        * 14, self.GridCell['verticle']*17.5)             
        self.CurrentStatusLabel.resize(self.GridCell['horizontal']
                        * 4, self.GridCell['verticle']*1)                                           
        self.GenerateButton.move(self.GridCell['horizontal']*17.5,
                    self.GridCell['verticle']*17.5)
        self.UndoButton.move(
            self.GridCell['horizontal']*1, self.GridCell['verticle']*1)                         
        self.LabelsList.resize(self.GridCell['horizontal']
                        * 6, self.GridCell['verticle']*14)
        self.LabelsList.move(self.GridCell['horizontal']*13,
                    self.GridCell['verticle']*3)
        self.pmi = gui.QImage(
            self.Image_cv2.data, self.Image_cv2.shape[1], self.Image_cv2.shape[0], self.Image_cv2.shape[1]*3, gui.QImage.Format_RGB888)
        self.PixMap = gui.QPixmap(self.pmi)
        self.LabelsList.clicked[QtCore.QModelIndex].connect(self.highlight)
        # self.PixMap = self.PixMap.scaled(
        #     self.GridCell['horizontal']*18, self.GridCell['verticle']*13)
        self.Image.setPixmap(self.PixMap)
        effect = widgets.QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(20.0)
        effect.setXOffset(20.0)
        effect.setYOffset(20.0)
        effect.setColor(gui.QColor(0,0,0,250))
        # self.Image.setGraphicsEffect(effect)
        self.LabelsLabel.move(self.GridCell['horizontal']*13,
                    self.GridCell['verticle']*1.5)
        self.Image.resize(
            self.Image_cv2.shape[1], self.Image_cv2.shape[0])
        self.Image.move(self.GridCell['horizontal']
                        * 1, self.GridCell['verticle']*3)


    def LabellingPopup(self,pos):
        labelpop = labelDialog(self) 
        labelpop.setWindowFlag(QtCore.Qt.CustomizeWindowHint,True)
        labelpop.setWindowFlag(QtCore.Qt.WindowCloseButtonHint,False)
        labelpop.move(pos.x(),pos.y())
        labelpop.setWindowTitle("Label:")
        # labelpop.setWindowModality(QtCore.Qt.ApplicationModal)
        labelpop.exec_()
        return labelpop.label.text()

    #The UI Component
    def Home(self):
        self.setWindowTitle("Annotations")
        self.NextButton = widgets.QPushButton('Next',self)
        self.UndoButton = widgets.QPushButton ('Undo',self)
        self.GenerateButton = widgets.QPushButton('Generate', self)
        self.LabelsList = widgets.QListWidget(self)
        self.LabelsLabel = widgets.QLabel('Object Labels',self)
        self.LabelsLabel.setFont(gui.QFont("Aerial",20,gui.QFont.Thin))
        self.loadScreen(True)
        self.NextButton.clicked.connect(self.handleNext)
        self.GenerateButton.clicked.connect(self.handleGenerate)
        self.UndoButton.clicked.connect(self.handleReset)
    