#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 13:22:16 2020

@author: Jaakko Ahola, Finnish Meteorological Institute
@licence: MIT licence Copyright
"""
import os
import pathlib
import yaml

class FileSystem:
    def createSubfolder(rootfolderName, subfolderName):
        subfolder = os.path.join( rootfolderName, subfolderName)
        if not os.path.exists( subfolder ):
            os.makedirs( subfolder )
        
        return subfolder
    
    def readYAML(absoluteFilePath):
        with open(absoluteFilePath, "r") as stream:
            try:
                output = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        return output
    
    def getAbsoluteFilename(folder, file):
        return pathlib.Path(folder) / file