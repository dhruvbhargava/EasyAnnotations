#Annotation Tool
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
import XMLGenerator as xmgen


class FolderSelectionUI(widget):
           
    def __init__(self):
        super(FolderSelectionUI, self).__init__()
        self.setWindowTitle("Folder Path")
        self.options = {'box_height':0,'box_width': 0}
        self.build_params = {'FOLDER PATH':'','ANNOTATION PATH':''}
        self.dims = {'left': 50, 'right': 50,
                     'top': 10, 'width': 500, 'height': 550}
        self.GridCell = {
            'verticle': self.dims['height']/20, 'horizontal': self.dims['width']/20}
        self.setGeometry(self.GridCell['horizontal']*5,self.GridCell['verticle']*16,self.GridCell['horizontal']*20,self.GridCell['verticle']*16)
        self.Fixed = False
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
                    self.cams = Main(self.build_params['FOLDER PATH'],self.build_params['ANNOTATION PATH'],self.BoundingBoxWidthField.text(),self.BoundingBoxHeightField.text(),self.FixedBoxChecked.isChecked())
                    self.cams.show()
                    self.close()                                   
                else:
                    os.mkdir(self.build_params['ANNOTATION PATH'])
                    return 
            else:
                self.InputLabel.setText("**FOLDER DOESN'T EXIST**")  
                return

    def Screen(self):
        GoButton = widgets.QPushButton('GO',self)
        SelectButton = widgets.QPushButton('Select',self)
        SelectButton2 = widgets.QPushButton('Select',self)
        self.FixedBoxChecked = widgets.QCheckBox('Fixed Size Bounding Box ',self)
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
        self.FixedBoxChecked.stateChanged.connect(self.fixedBoxCheckedHandler)
        SelectButton.clicked.connect(self.seletFolderInput)
        SelectButton2.clicked.connect(self.seletFolderAnnotation)
        GoButton.clicked.connect(self.Navigate)

    
        
class Main(widget):
    def __init__(self,Image_folder_path,Annotation_folder_path,bbox_width,bbox_height,fixed = False):
        super(Main, self).__init__()
        self.Fixed = fixed
        self.ImageDirectory = Image_folder_path
        self.bboxRatios = [bbox_width,bbox_height]
        self.CurrentStatusLabel = widgets.QLabel('',self)
        self.SaveAnnotationPath = Annotation_folder_path
        self.Image_List = []
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
        if self.Fixed:
            self.Image.mousePressEvent = self.getPixel
        self.currentTransform = ''
        self.setGeometry(self.dims['left'], self.dims['top'],
                         self.dims['width'], self.dims['height'])                 
        self.Home()                         

    def getPixel(self,event):
        center = {'x':event.pos().x(),'y':event.pos().y()}
        self.Image_cv2 ,topleft,bottomright= BB.DrawBox(self.Image_cv2,center,self.bboxRatios)
        self.curr_image_meta.append(obj("person",topleft,bottomright))#make this label
        self.Load_Screen(read = False)

    def check(self,pos):
        if(pos.x()<self.GridCell['horizontal']*1 or pos.x()>self.GridCell['horizontal']*1+self.Image_cv2.shape[1]):
            return 0
        if(pos.y()<self.GridCell['verticle']*3 or pos.y()>self.GridCell['verticle']*3+self.Image_cv2.shape[0]):
            return 0
        return 1
    
    def mousePressEvent(self, event):
        self.origin = event.pos()
        if(not self.check(self.origin) or self.Fixed):
            return
        self.rubberband.setGeometry(
            QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberband.show()
    

    def mouseMoveEvent(self, event):
        if self.rubberband.isVisible():
            curr = event.pos()
            if(not self.check(curr) or self.Fixed):
                return
            self.rubberband.setGeometry(
                QtCore.QRect(self.origin, curr).normalized())

    def mouseReleaseEvent(self, event):
        if(self.Fixed):
            return
        if self.rubberband.isVisible():
            self.rubberband.hide()
        coords = []
        coords.append(self.origin.x()-self.GridCell['horizontal'])
        coords.append(self.origin.y()-(self.GridCell['verticle']*3))
        coords.append(event.pos().x()-self.GridCell['horizontal'])
        coords.append(event.pos().y()-(self.GridCell['verticle']*3))
        self.Image_cv2 ,topleft,bottomright= BB.DrawBoxUnsized(self.Image_cv2,coords)
        self.curr_image_meta.append(obj("person",topleft,bottomright))
        self.Load_Screen(read = False)


    
    def HandleNext(self):
        self.XML_GEN_DONE = False
        self.CurrentStatusLabel.setText('')
        self.curr_image_meta = []
        self.Image_List.remove(self.curr_image_path.split('/')[-1])
        if len(self.Image_List) == 0:
            self.close()
            exit()
        self.curr_image_path = os.path.join(self.ImageDirectory,self.Image_List[0])
        self.Load_Screen(True)


    def HandleGenerate(self):
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
        generated_string = xmgen.write_file(self.Image_cv2.shape,self.curr_image_meta,self.ImageDirectory,image_file_name)
        with open(os.path.join(self.SaveAnnotationPath,xml_file_name),"wb") as xml_file:
            xml_file.write(generated_string)    
        self.CurrentStatusLabel.setText("*DONE!*")
        self.XML_GEN_DONE = True
    
    def HandleReset(self):
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
        self.Load_Screen(True)

    def Load_Screen(self,read):
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
        
        

   

    def Home(self):
        self.setWindowTitle("Annotations")
        self.NextButton = widgets.QPushButton('Next',self)
        self.UndoButton = widgets.QPushButton ('Undo',self)
        self.GenerateButton = widgets.QPushButton('Gen XML', self)
        self.Load_Screen(True)
        self.NextButton.clicked.connect(self.HandleNext)
        self.GenerateButton.clicked.connect(self.HandleGenerate)
        self.UndoButton.clicked.connect(self.HandleReset)
    


if __name__ == "__main__":
    App = app(sys.argv)
    w = FolderSelectionUI()
    w.show()
    sys.exit(App.exec_())