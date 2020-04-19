import cv2 

def DrawBox(Image,center,box_ratios):
    height = int(box_ratios[1])
    width = int(box_ratios[0])
    topleft_display =  (max(int(center['x'] - width/2),0),max(int(center['y'] -height/2),0))
    topleft_actual = (max(int(center['x']*2 - width),0),max(int(center['y']*2 - height),0))
    bottomright_display = (min(int(center['x'] + width/2),Image.shape[1]-1) ,min(int(center['y']+ height/2),Image.shape[0]-1))
    bottomright_actual = (min(int(center['x']*2 + width),(Image.shape[1]-1)*2),min(int(center['y']*2 + height),(Image.shape[0]-1)*2))
    top_x = topleft_display[0]
    top_y = topleft_display[1]
    bottom_x = bottomright_display[0]
    bottom_y = bottomright_display[1] 
    image = cv2.rectangle(Image,(int(top_x),int(top_y)),(int(bottom_x),int(bottom_y)),(0,0,255),3)
    return image ,topleft_actual,bottomright_actual

def DrawBoxUnsized(Image,coords):
    topleft_actual = (max(coords[0]*2,0),max(coords[1]*2,0))
    bottomright_actual = (min(coords[2]*2,(Image.shape[1]-1)*2),min(coords[3]*2,(Image.shape[0]-1)*2))
    top_x = coords[0]
    top_y = coords[1]
    bottom_x = coords[2]
    bottom_y = coords[3]
    image = cv2.rectangle(Image,(int(top_x),int(top_y)),(int(bottom_x),int(bottom_y)),(0,0,255),3)
    return image ,topleft_actual,bottomright_actual
        

class TaggedObject:
    def __init__(self,label,topleft,bottomright):
        self.label = "label"    
        self.topleft = topleft
        self.bottomright = bottomright
    