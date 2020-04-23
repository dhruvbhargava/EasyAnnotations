import os
import json 

class Generator:
    def __init__(self):
        with open('Generators/SupportedFormats.json','r') as f:
            self.supportedFormats = json.load(f)
        self.selectedFormat = list(self.supportedFormats.keys())[0] #defaults to the first format in the json
        self.formatToImport = ''

    def getAllFormats(self):
        formats = []
        for format in self.supportedFormats.keys():
            formats.append(format)
        return formats

    def setFormat(self,selected):
        self.selectedFormat = selected

    def generate(self,Image_shape,Object_list,Image_directory_path,Image_file_name):
        self.formatToImport = self.supportedFormats[self.selectedFormat]
        gen = getattr(__import__('Generators', fromlist=[self.formatToImport]), self.formatToImport)
        return gen.write_file(Image_shape,Object_list,Image_directory_path,Image_file_name)