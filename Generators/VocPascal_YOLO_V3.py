import os
import xml.etree.cElementTree as ET
from BoundingBox import TaggedObject as Object

def write_file(Image_shape,Object_list,Image_directory_path,Image_file_name):
    annotation = ET.Element('annotation')
    ET.SubElement(annotation, 'folder').text = Image_directory_path
    ET.SubElement(annotation, 'filename').text = Image_file_name
    size = ET.SubElement(annotation, 'size')
    ET.SubElement(size, 'width').text = str(Image_shape[1]*2)#since this is display image width
    ET.SubElement(size, 'height').text = str(Image_shape[0]*2)#since this is display image height
    ET.SubElement(size, 'depth').text = str(Image_shape[2])
    for obj in Object_list :
        ob = ET.SubElement(annotation, 'object')
        ET.SubElement(ob, 'name').text = obj.label
        ET.SubElement(ob, 'pose').text = 'Unspecified'
        ET.SubElement(ob, 'truncated').text = '0'
        ET.SubElement(ob, 'difficult').text = '0'
        bbox = ET.SubElement(ob, 'bndbox')
        ET.SubElement(bbox, 'xmin').text = str(int(obj.topleft[0]))
        ET.SubElement(bbox, 'ymin').text = str(int(obj.topleft[1]))
        ET.SubElement(bbox, 'xmax').text = str(int(obj.bottomright[0]))
        ET.SubElement(bbox, 'ymax').text = str(int(obj.bottomright[1]))
    xml_str = ET.tostring(annotation)
    return xml_str