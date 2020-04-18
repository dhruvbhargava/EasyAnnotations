import os

images = os.listdir("./haar_cascade")
xmls = os.listdir("./Annotations")

for xml in xmls:
    corres_image = xml.split(".")[0]+".jpg"
    if corres_image in images:
        images.remove(corres_image)

for image in images:
    os.remove("./haar_cascade/"+image)
    