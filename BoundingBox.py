import cv2 


class TaggedObject:
    def __init__(self,label,topleft,bottomright,tl,br):
        self.label = label  
        self.topleft = topleft
        self.bottomright = bottomright
        self.display_tl = tl
        self.display_br = br

def DrawBoxFixed(label,Image,center,box_ratios,factors):
    height = int(box_ratios[1])
    width = int(box_ratios[0])
    topleft_display =  (max(int(center['x'] - width*factors[1]),0),max(int(center['y'] -height*factors[0]),0))
    topleft_actual = (max(int(center['x']/factors[1] - width),0),max(int(center['y']/factors[0] - height),0))
    bottomright_display = (min(int(center['x'] + width*factors[1]),Image.shape[1]-1) ,min(int(center['y']+ height*factors[0]),Image.shape[0]-1))
    bottomright_actual = (min(int(center['x']/factors[1] + width),(Image.shape[1]-1)/factors[1]),min(int(center['y']/factors[0] + height),(Image.shape[0]-1)/factors[0]))
    top_x = topleft_display[0]
    top_y = topleft_display[1]
    bottom_x = bottomright_display[0]
    bottom_y = bottomright_display[1] 
    image = cv2.rectangle(Image,(int(top_x),int(top_y)),(int(bottom_x),int(bottom_y)),(100,100,100),3)
    if top_y<bottom_y:
        tx = top_x
        ty = top_y
    else:
        tx = bottom_x
        ty = bottom_y
    image = cv2.putText(image,label,(int(tx),int(ty)-15),cv2.FONT_HERSHEY_SIMPLEX ,.7, (100,100,100),2, cv2.LINE_AA)
    return image ,topleft_actual,bottomright_actual,topleft_display,bottomright_display

def DrawBoxVariable(label,Image,coords,factors):
    print(factors)
    topleft_actual = (max(coords[0]/factors[1],0),max(coords[1]/factors[0],0))
    bottomright_actual = (min(coords[2]/factors[1],(Image.shape[1]-1)/factors[1]),min(coords[3]/factors[0],(Image.shape[0]-1)/factors[0]))
    top_x = coords[0]
    top_y = coords[1]
    bottom_x = coords[2]
    bottom_y = coords[3]
    image = cv2.rectangle(Image,(int(top_x),int(top_y)),(int(bottom_x),int(bottom_y)),(100,100,100),3)
    if top_y<bottom_y:
        tx = top_x
        ty = top_y
    else:
        tx = bottom_x
        ty = bottom_y
    image = cv2.putText(image,label,(int(tx),int(ty)-15),cv2.FONT_HERSHEY_SIMPLEX ,.7, (100,100,100),2, cv2.LINE_AA)
    return image ,topleft_actual,bottomright_actual,(coords[0],coords[1]),(coords[2],coords[3])
        
