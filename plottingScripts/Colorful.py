#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 13:33:54 2020

@author: Jaakko Ahola, Finnish Meteorological Institute
@licence: MIT licence Copyright
"""
import matplotlib
import numpy
import os
import pathlib
import seaborn

class Colorful:
    # if snsColorPalette and matplotlibColorMap are None and colorNumber < 21 use distinctColorlist
    
    def __init__(self, colorNumber = None, colorList = None,
                 shuffling = False,
                 blindnessLevel = 4, useWhite = False, useBlack = True, useBeige = False, useLavender = False, useGrey = False,
                 snsColorPalette = None, 
                 matplotlibColorMap = None, # e.g. matplotlib.pyplot.cm.gist_ncar
                 matplotlibLimiter = 0.95
                 ):
        
        self.colorList = Colorful.getIndyColorList(colorNumber, colorList,
                                                   shuffling,
                                                   blindnessLevel, useWhite, useBlack, useBeige, useLavender, useGrey,
                                                   snsColorPalette, 
                                                   matplotlibColorMap, # e.g. matplotlib.pyplot.cm.gist_ncar
                                                   matplotlibLimiter)
        
    
    def getColorList(self):
        return self.colorList
    
    def stringToFloatTuple(string):
        return tuple(map(float, string.replace("(", "").replace(")","").split(",")))
    
    def getIndyColorList( colorNumber = None, colorList = None,
                 shuffling = False,
                 blindnessLevel = 4, useWhite = False, useBlack = True, useBeige = False, useLavender = False, useGrey = False,
                 snsColorPalette = None, 
                 matplotlibColorMap = None, # e.g. matplotlib.pyplot.cm.gist_ncar
                 matplotlibLimiter = 0.95
                 ):
        
        if colorList is not None:
            colorList = colorList
        
        nmax = 22 - int(not useWhite) - int( not useBlack) - int( not useBeige) - int( not useLavender) - int( not useGrey)

        if snsColorPalette is None and matplotlibColorMap is None and colorNumber < nmax:
            colorList = Colorful.getDistinctColorList(colorNumber, blindnessLevel = blindnessLevel,
                                                            useWhite = useWhite, useBlack = useBlack,
                                                            useBeige = useBeige, useLavender = useLavender,
                                                            useGrey = useGrey)
        elif snsColorPalette is None and matplotlibColorMap is None and colorNumber > nmax:
            colorList = seaborn.color_palette( snsColorPalette, colorNumber )
        elif snsColorPalette is not None:
            colorList = seaborn.color_palette( snsColorPalette, colorNumber )
        elif matplotlibColorMap is not None:
            colorList = [ matplotlibColorMap(i) for i in numpy.linspace(0, matplotlibLimiter, colorNumber) ]
            

        if shuffling:
            colorList = numpy.random.shuffle(colorList)
        
        for ind, value in enumerate(colorList):
            colorList[ind] = matplotlib.colors.to_hex(value)
            
        return colorList
    
    
    def getScientificColormap(cmap_name, scm_base_dir = os.environ["SCRIPT"] + "/" + "ScientificColourMaps5/", reverse = False):

        cmap_file = pathlib.Path(scm_base_dir) / cmap_name / (cmap_name+'.txt')

        cmap_data = numpy.loadtxt(cmap_file)

        if reverse:
            cmap_data = numpy.flip(cmap_data)
    
        return matplotlib.colors.LinearSegmentedColormap.from_list(cmap_name, cmap_data)    
    
    def getDistinctColorList(elements, blindnessLevel = 4, useBlack = True, useWhite = False, useLavender = False, useBeige = False, useGrey = False):
        
        # list of all the colors
        distinctColorsMother = { "red":  "#e6194B", "green" : "#3cb44b",
                          "yellow" : "#ffe119", "blue" :"#4363d8",
                          "orange" : "#f58231", "purple": "#911eb4",
                          "cyan" :"#42d4f4", "magenta" : "#f032e6",
                          "lime" :"#bfef45", "pink" :"#fabebe", 
                          "teal" : "#469990", "lavender" : "#e6beff",
                          "brown" : "#9A6324", "beige" : "#fffac8", 
                          "maroon" : "#800000", "mint" : "#aaffc3", 
                          "olive" : "#808000", "apricot" : "#ffd8b1", 
                          "navy" : "#000075", "grey" : "#a9a9a9", 
                          "white" : "#ffffff", "black" : "#000000"}
                          
        if isinstance(elements, str):
            distinctColors = distinctColorsMother[elements.lower()]
        elif isinstance(elements, list):
            distinctColors = {}
            for key in elements:
                key = key.lower()
                if key in distinctColorsMother:
                    distinctColors[key] = distinctColorsMother[key]
            
            distinctColors = list(distinctColors.values())
        elif isinstance(elements, int):
                          
            distinctColors = distinctColorsMother
            # choose indexes of colors, based on blindnessLevel parameter (values 1,2,3,4 allowed, default 4)
            
            if blindnessLevel == 1: # 95% of population can tell the difference
                pass # 22 colors including black & white
        
            elif blindnessLevel == 2: # 99% of population can tell the difference
                del distinctColors["purple"]
                del distinctColors["lime"]
                del distinctColors["olive"]
                del distinctColors["apricot"]
        
            elif blindnessLevel == 3: # 99,99% of population can tell the difference
                keys = ["yellow", "blue", "orange", "pink", "lavender", "maroon", "navy", "grey", "white", "black"]
                
                distinctColors = { key : distinctColorsMother[key] for key in keys}
                
            elif blindnessLevel == 4:  # ~100% of population can tell the difference
        
                keys = ["yellow", "blue", "grey", "white", "black"]
                
                distinctColors = { key : distinctColorsMother[key] for key in keys}
            else:
                raise Exception("Wrong blindnessLevel used")
        
        
        
            # if white is not needed, remove it from the listOfIndexes
            # useWhite default set is False since usually colors are painted using white background
            if not useWhite:
                try:
                    del distinctColors["white"]
                except KeyError:
                    pass # value already removed
        
            # if you don't want to use black color
            if not useBlack:
                try:
                    del distinctColors["white"]
                except KeyError:
                    pass # value already removed
        
            # if you don't want to use lavender color
            if not useLavender:
                try:
                    del distinctColors["lavender"]
                except KeyError:
                    pass # value already removed
        
            # if you don't want to use beige color
            if not useBeige:
                try:
                    del distinctColors["beige"]
                except KeyError:
                    pass # value already removed
        
            # if you don't want to use grey color
            if not useGrey:
                try:
                    del distinctColors["grey"]
                except KeyError:
                    pass # value already removed
        
    
    
            # if the number of colors needed is larger than within the blindnessLevel, use recursion and decrease blindnessLevel
            if elements > len(distinctColors) and (blindnessLevel > 1):
                return Colorful.getDistinctColorList( elements, blindnessLevel - 1, useBlack = useBlack, useWhite = useWhite, useLavender = useLavender, useBeige = useBeige, useGrey = useGrey )
        
            # if the number of colors needed is larger than possible colors and blindnessLevel can't be decreased, return False value
            elif elements > len(distinctColors) and (blindnessLevel == 1):
                raise Exception("list of colors not possible to generate with the given number")
            else:
                distinctColors = list(distinctColors.values())[:elements] # give list of distinctColors with given number, blindnessLevel and choice of using white & black
        
        return distinctColors