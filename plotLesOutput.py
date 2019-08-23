#!/usr/bin/python
import time
tic = time.clock()
import ModDataPros as mdp
import sys
from itertools import cycle
import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.colors as colors
import seaborn as sns
import os
import glob
from netCDF4 import Dataset
from PythonMethods import myRound
from PythonMethods import myRoundFloat
import PythonMethods as pm
import xarray as xr
import re
import matplotlib.ticker as ticker
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)


import pandas as pd
global piirra, tulostus, tightXAxis, saveFig, LEGEND, tag, kylla, emuloo, setupFileHandler, readFromFile, debug

####################################################
def setupFunction(question, condition = None):

    if readFromFile:
        returnableHelp = setupFileHandler.readline()[:-1]
        print("setupFunction", question, returnableHelp)
    else:
        returnableHelp = input( question )
        setupFileHandler.write( returnableHelp + '\n' )
        #print "setupFunction", question, returnableHelp


    if condition is None:
        returnable = returnableHelp
    else:
        returnable = returnableHelp in condition

    return returnable
##################################################


if __name__ == "__main__":
    print(" ")
    kylla = [ 'y', 'Y', 'yes', 'Yes', 'YES', 'True', 'true', '1' ]
    emuloo = ['e', 'E', 'emul', 'y', 'Y', 'yes']

    #sns.set()
    plt.style.use('seaborn-paper')
    sns.set_context("poster")
    mpl.rcParams['figure.figsize'] = [mpl.rcParams['figure.figsize'][0]*2.0, mpl.rcParams['figure.figsize'][1]*2.0]
    print('figure.figsize', mpl.rcParams['figure.figsize'])

    print('figure.dpi', mpl.rcParams['figure.dpi'])
    mpl.rcParams['savefig.dpi'] = 150.
    print('savefig.dpi', mpl.rcParams['savefig.dpi'])
    mpl.rcParams['legend.fontsize'] = 14
    print('legend.fontsize', mpl.rcParams['legend.fontsize'])
    mpl.rcParams['axes.titlesize'] = 42
    mpl.rcParams['axes.labelsize'] = 42
    mpl.rcParams['xtick.labelsize'] = 42 #22
    mpl.rcParams['ytick.labelsize'] = 42 #22
    mpl.rcParams['font.weight']= 'bold'
    print('axes.titlesize', mpl.rcParams['axes.titlesize'])
    print('axes.labelsize', mpl.rcParams['axes.labelsize'])
    print('xtick.labelsize', mpl.rcParams['xtick.labelsize'])
    print('ytick.labelsize', mpl.rcParams['ytick.labelsize'])

    mpl.rcParams['text.latex.unicode'] = False
    mpl.rcParams['text.usetex'] = False
    print("text.latex.unicode", mpl.rcParams['text.latex.unicode'])
    mpl.rcParams['text.latex.preamble']=[r'\usepackage{amsmath}']
    mpl.rc('text', usetex = True)
    readFromFile = input("Do you want to read setups from file (y/n): ") in kylla
    setupFile = "setup.txt"

    if os.path.isfile(setupFile):
        if readFromFile:
            mode = "r"
        else:
            mode = "w"
    else:
        mode = "w+"

    setupFileHandler = open(setupFile,mode)

    lvl = setupFunction( 'Level: ')

    EMUL             = False
    ICE              = False

    if lvl == '0':
        print("Level comparisons, WARNING make sure that the files are given in order of ice0, ice1, ice4")
    else:
        EMUL = setupFunction('Emulator/Regular pictures: e/r (y/n): ', emuloo)

        if EMUL:
            apuBool = setupFunction('Did you use emulatorPlotsAll -script (if no, generate emulator file list) : (y/n): ', kylla )
            generateEmulFilelist = not apuBool
        else:
            generateEmulFilelist = False
    tag      = setupFunction('give tag: ')
    LVLprint = setupFunction("Do you want to print LEVEL (yes/no): ", kylla)

    icevari = 'k'
    if len(tag) == 4 and tag[0:3]=='ice':
        if tag[-1] == '4':
            icevari = 'k'
        elif tag[-1] == '1':
            icevari = 'r'
    else:
        icevari = None

    if len(tag)>0:
        tag = tag + ' '
        saveTag = tag.replace(" ","_")
        if not LVLprint:
            saveTag=saveTag[:-1]
        saveTag = "_" + saveTag
    else:
        saveTag = ''

    ICE = (not EMUL )

    customLabels = setupFunction("Do you want to give custom labels for plots (yes/no): ", kylla )

    colorSetup   = setupFunction("Do you want to give specific colors for plots (yes/no): ", kylla )

    if EMUL:
        EMULCASESCUSTOM = setupFunction("Do you want to give custom emul cases (yes/no): ", kylla)



#######################
##### setting up    ###
##### DO NOT CHANGE ###
#######################
    ibrix = os.environ["IBRIXMOUNT"]
    global arguments
    global labelArray
    arguments = sys.argv

    labelArray      = []
    labelArraySets  = []
    emulCaseIndexes = []

    filenameNC = []
    filenamePS = []
    filenameTS = []




    if LVLprint:
        LVLprintFig  = ' ' + 'LVL' + lvl
        LVLprintSave = '_' + 'LVL' + lvl
    else:
        LVLprintFig  = ''
        LVLprintSave = ''

    kkk = 1
    uuu = 1
    applyForAll = False



    if generateEmulFilelist:
        emulatorSets = arguments[1:]
        apu2 = [ ss + "/emul???" for ss in emulatorSets ]

        apu3 = [ glob.glob(ss)  for ss in apu2 ]

        apu4 = [ len(ss)  for ss in apu3 ]

        lyhin = np.argmin( apu4 )

        emulatorSims = [ os.path.basename( ss ) for ss in apu3[ lyhin ] ] # valkkaa vahiten emulaattoriajoja sisaltava setti, muutoin vertailut eivat onnistu, voi kayttaa emulatorplotsall muutoin

        tiedostolista = []

        for ss in emulatorSets:
            for dd in emulatorSims:
                tiedostolista.append( ss + '/' + dd + '/' + dd )

        if customLabels:
            for ss in emulatorSets:
                teksti = "Give "+ str(kkk) +". label: (" + str(ss)+") : "
                labelArraySets.append( setupFunction(teksti) )
                kkk += 1
                for ggg in emulatorSims:
                    labelArray.append( labelArraySets[-1] + " " + ggg )

    else:
        tiedostolista = arguments[1:]

    print(" ")
    print("tiedostolista", tiedostolista)
    print(" ")
    for filebase in tiedostolista:


        filenameNC.append( filebase + '.nc'    )
        filenamePS.append( filebase + '.ps.nc' )
        filenameTS.append( filebase + '.ts.nc' )

        if customLabels and ( not generateEmulFilelist ):
            teksti = "Give "+ str(kkk) +". label: (" + str(filebase)+") : "
            labelArray.append( setupFunction(teksti) )
            kkk += 1
        elif ( (not customLabels) and (not EMUL) ):
            labelArray.append( filebase )

        if EMUL and EMULCASESCUSTOM :
                emulteksti = "Give "+ str(uuu) +". emul case (" + str(filebase)+") : "
                if not applyForAll:
                    emulcase = int(setupFunction(emulteksti))-1

                    applyteksti = "Do you want to apply this case " + str(emulcase+1) + " for all the rest? (yes/no): "
                    applyForAll = setupFunction(applyteksti, kylla)

                emulCaseIndexes.append( emulcase )
                uuu += 1



##############################
#### YOU CAN CHANGE THESE: ###
##############################

##############################
#
# drawing GLOBAL
#
# parameter settings
#
##############################

naytaPlotit = False

piirra = True

tulostus = False

tightXAxis = True

saveFig=True

debug = False

global jarjestys


if __name__ == "__main__":
    if saveFig:

        kuvavaliliite = setupFunction("Give custom picturefolder tag: ")
        if len(kuvavaliliite) > 0:
            kuvavaliliite = '_' + kuvavaliliite

        picturefolder='./pictures' + kuvavaliliite + '/'
        if not os.path.exists( picturefolder ):
            os.makedirs( picturefolder )

    cases    = len(tiedostolista)
    colorNRO = cases

    jarjestys = np.arange( 1, cases + 1 )

    if ( colorNRO > 6 ) :
        LEGEND = False
    else:
        LEGEND = True

    if colorNRO <= 18:
        useSnsColor = False
    else:
        useSnsColor = True

    if not colorSetup:
        colorList = mdp.initializeColors(colorNRO, useSnsColor = useSnsColor)
    elif colorSetup:
        colorList = []
        for simulaatioIND in range(len(tiedostolista)):
            teksti = "Give color for " + str(tiedostolista[simulaatioIND])+ ": "
            colorList.append( setupFunction(teksti) )

        #colorList =colorChoice = mdp.initializeColors( colorList = colorList )
            #namelist = os.path.dirname(os.path.realpath( simulaatio ))+"/NAMELIST"
            #if os.path.isfile(namelist):
            #    try:
            #        iceConc = mdp.read_NamelistValue( namelist ,var = 'fixINC' )
            #
            #    except TypeError:
            #        colorChoice = mdp.initializeColors(colorNRO)



        #colorChoice = mdp


    ajanhetket = 2*3600. #7200.

    for namelistInd in range(len(tiedostolista)):

        namelist = os.path.dirname(os.path.realpath(tiedostolista[namelistInd]))+"/NAMELIST"

        if os.path.isfile(namelist):
            print("NAMELIST", namelist)
            for spinupNamelistMuuttuja in "Tspinup", 'tspinup', 'lsauto%delay':
                try:
                    spinup = mdp.read_NamelistValue( namelist ,var = spinupNamelistMuuttuja )
                    break
                except TypeError:
                    spinup = 0.
            print('spinup', spinup)
            tmax   = mdp.read_NamelistValue( namelist ,var = 'timmax'  )

            slaissaaXY   = max( mdp.read_NamelistValue( namelist ,var = 'nxp'  ), mdp.read_NamelistValue( namelist ,var = 'nyp'  ))
            break
        else:
            continue

    try:
        ticksHours  = np.arange(0., tmax/3600. + 0.1, 0.5)
    except NameError:
        sys.exit("NAMELIST is not probably not read properly. Since tmax from NAMELIST doesn't have a value.")
    xLabelsHours = list(map(str, ticksHours ))

    xTicksSeconds = ticksHours*3600.


##########################
###                    ###
### GLOBAL SUBROUTINES ###
###                    ###
##########################

##############
def varibaari( variRefVektori, variKartta ):
    minRef = np.min( variRefVektori )
    maxRef = np.max( variRefVektori )
    step = 1
    Z = [[ 0,0 ],[ 0,0 ]]
    levels = list(range( int(minRef), int(maxRef) + step, step))
    CS3 = plt.contourf( Z, levels, cmap = variKartta )
    plt.close()
    return CS3



def shiftedColorMap(cmap, start=0, midpoint=0.5, stop=1.0, name='shiftedcmap'):
    '''
    Function to offset the "center" of a colormap. Useful for
    data with a negative min and positive max and you want the
    middle of the colormap's dynamic range to be at zero

    Input
    -----
      cmap : The matplotlib colormap to be altered
      start : Offset from lowest point in the colormap's range.
          Defaults to 0.0 (no lower ofset). Should be between
          0.0 and `midpoint`.
      midpoint : The new center of the colormap. Defaults to
          0.5 (no shift). Should be between 0.0 and 1.0. In
          general, this should be  1 - vmax/(vmax + abs(vmin))
          For example if your data range from -15.0 to +5.0 and
          you want the center of the colormap at 0.0, `midpoint`
          should be set to  1 - 5/(5 + 15)) or 0.75
      stop : Offset from highets point in the colormap's range.
          Defaults to 1.0 (no upper ofset). Should be between
          `midpoint` and 1.0.
    '''
    cdict = {
        'red': [],
        'green': [],
        'blue': [],
        'alpha': []
    }

    # regular index to compute the colors
    reg_index = np.linspace(start, stop, 257)

    # shifted index to match the data
    shift_index = np.hstack([
        np.linspace(0.0, midpoint, 128, endpoint=False),
        np.linspace(midpoint, 1.0, 129, endpoint=True)
    ])

    for ri, si in zip(reg_index, shift_index):
        r, g, b, a = cmap(ri)

        cdict['red'].append((si, r, r))
        cdict['green'].append((si, g, g))
        cdict['blue'].append((si, b, b))
        cdict['alpha'].append((si, a, a))

    newcmap = mpl.colors.LinearSegmentedColormap(name, cdict)
    plt.register_cmap(cmap=newcmap)

    return newcmap

##########################
def piirra_aikasarjasettii( muuttuja, muuttuja2 = None, muunnosKerroin2 = 1.0, variKartta = plt.cm.gist_rainbow, variRefVektori = jarjestys, colorBar = None, colorBarTickValues = [0,1], colorBarTickNames = ['0','1'], muunnosKerroin = 1.0, longName = 'titteli', xlabel = 'time [h]', ylabel='ylabel', extendBelowZero = True, asetaRajat = True, ymin = None, ymax = None, relative = False, savePrefix = None, omaVari = True, tit = '', nollaArvo = None, xlabels = None, ylabels = None, xticks = None, yticks = None, spinup = None, ylabelFont = None, askChangeOfVariable = False, piilotaOsaXlabel = False, legenda = True, profiili = False, piilotaOsaYlabel = False, piilotaOsaYlabelParam = 3, piilotaOsaXlabelParam =4, NCtiedosto= False, tallenna = False, loc = 3 ):
    origmuuttuja = muuttuja
    plottausOnnistuu = False
    maksimi = None
    minimi  = None
    maxRef = np.max( variRefVektori )
    maksInd = None
    minInd  = None
    #vastausKaikkiin = False
    nono = None

    if profiili:
        tiedostonimi = filenamePS
    elif NCtiedosto:
        tiedostonimi = filenameNC
    else:
        tiedostonimi = filenameTS

    nollatapaus = 0
    print(" ")

    time_dataLen = 0
    time_dataLongest = None
    updateDictTimeColumn = False

    for i in range(len(tiedostolista)):
        uusikuva = True if i == 0 else  False
        muuttuja = origmuuttuja
        if EMUL:
            if not EMULCASESCUSTOM:

                case_indeksi = int(tiedostonimi[i].split("/")[-2][4:])-1

            else:
                case_indeksi = emulCaseIndexes[i]
        else:
            case_indeksi = i

        if askChangeOfVariable:
            printti = "Case is "+ arguments[i+1] + ", the variable is currently: " + muuttuja + ' if you want to keep it press [Enter], otherwise give the name of the variable (e.g. prcp/rmH2Opr Nc_ic/CCN): '
            apumuuttuja = input(printti)

            if apumuuttuja != '':
                muuttuja = apumuuttuja

            if muuttuja == 'prcp':
                muunnosKerroin = 2.5e-06
            elif muuttuja == 'rmH2Opr':
                muunnosKerroin = 1.

            print('variable is', muuttuja, 'muunnosKerroin', muunnosKerroin)
            print(' ')



        time_data    = mdp.read_Data( tiedostonimi[i], 'time'  )
        if len(time_data) > time_dataLen:
            time_dataLen     = len(time_data)
            time_dataLongest = time_data
            updateDictTimeColumn = True



        try:
            muuttuja_Tdata  = mdp.read_Data( tiedostonimi[i], muuttuja )*muunnosKerroin
            plottausOnnistuu = True
        except KeyError:
            if debug: print("KeyError, variable " + muuttuja + " doesn't exist in " + tiedostonimi[i] )
            continue

        if muuttuja2 is not None:
            muuttuja_Tdata2  = mdp.read_Data( tiedostonimi[i], muuttuja2 )*muunnosKerroin2

        if muuttuja_Tdata[-1] < sys.float_info.epsilon:
            nollatapaus += 1
            print(muuttuja, 'nollatapaus', case_indeksi)
        #### relative
        if relative:


            if ((nollaArvo is None) and (nono is None)):

                nollaHetki = 0

                lahtoarvo = muuttuja_Tdata[nollaHetki]

                while lahtoarvo == -999.:
                    print('WARNING lahtoarvo = -999. lasketaan seuraavasta hetkesta: ' + str(nollaHetki) + " muuttuja: " + str(muuttuja))
                    nollaHetki += 1
                    lahtoarvo = muuttuja_Tdata[ nollaHetki ]

            elif ( isinstance( nollaArvo, np.ndarray) or isinstance(nollaArvo, list) ):
                lahtoarvo = nollaArvo[case_indeksi]
            elif nono is not None:
                lahtoarvo = muuttuja_Tdata[nono]
            if lahtoarvo == 0.:
                    print('VAROITUS: ei voida laskea relative koska lahtoarvo on nolla', muuttuja, 'case', i+1, 'nono', nono)
                    if nono is None:
                        NEXT = input('Haluatko etsia seuraavan ei-negatiivisen datasta kaikkiin kappyroihin: yes/no: ') in kylla

                        if NEXT:
                            nono = 0
                            while( muuttuja_Tdata[nono] == 0. ):
                                nono += 1
                            lahtoarvo = muuttuja_Tdata[nono]
                        else:
                            print("Let's skip this", muuttuja, i+1)
                            continue

                    else:
                        print("Let's skip this", muuttuja, i+1)
                        continue


            muuttuja_Tdata = np.where( muuttuja_Tdata > -999.,  muuttuja_Tdata / lahtoarvo, 0. )

            viimeinen = muuttuja_Tdata[-1]
            if viimeinen > 1.09:
                print("Variable:", muuttuja, "case", case_indeksi+1, "last value", viimeinen, "i", i)
        #### end relative





        colorMap = variKartta
        skal = variRefVektori[ case_indeksi ] / maxRef
        color = colorMap(skal)

        if omaVari:
            omavari = color
        else:
            omavari = omaVari

        if maksInd is not None:
            if np.max(muuttuja_Tdata) > maksimi: # maksimia ei ole viela tassa kohtaa paivitetty
                # maksimi indeksi muuttuu koska uusi maksimi on suurempi kuin vanha maksimi
                maksInd = np.argmax( muuttuja_Tdata)
        else:
            maksInd = np.argmax( muuttuja_Tdata)

        if minInd is not None:
            if np.min(muuttuja_Tdata) < minimi: # maksimia ei ole viela tassa kohtaa paivitetty
                # maksimi indeksi muuttuu koska uusi maksimi on suurempi kuin vanha maksimi
                minInd = np.argmin( muuttuja_Tdata)
        else:
            minInd = np.argmin( muuttuja_Tdata)



        if maksimi is not None:
            maksimi = max( maksimi,   np.max( muuttuja_Tdata ) )

        else:
            maksimi = np.max( muuttuja_Tdata )

        if minimi is not None:
            minimi = min( minimi,  np.min( muuttuja_Tdata) )
        else:
            minimi = np.min( muuttuja_Tdata )
        print("piirra_aikasarjasettii", muuttuja, "maksimi", maksimi)


        if EMUL:
            nimi = longName + ' ' + tag + LVLprintFig
            if customLabels:
                label = labelArray[i]
            else:
                label = str(case_indeksi+1)
        else:
            nimi = longName + ' ' + tag
            label = labelArray[i]

        if tallenna:
            muuttujaCSV = muuttuja
            if muuttujaCSV.endswith("_bar"):
                muuttujaCSV = muuttujaCSV[:-4].upper()

            if updateDictTimeColumn:
                timeIndDict = xlabel
                aikasarjaDict = dict(zip([timeIndDict], [time_dataLongest/3600.]))

            yarvot = pm.pad( list(muuttuja_Tdata), time_dataLen, padding=np.nan )
            aikasarjaDict.update(dict(zip([" ".join([label, muuttujaCSV, ylabel])], [yarvot])))

        if len(tiedostolista) <= 3:
            bboxmode = None
        else:
            bboxmode = "expand"

        fig, ax, legend = mdp.aikasarjaTulostus( muuttuja_Tdata, time_data,  tulostus = tulostus, piirra = piirra, uusikuva = uusikuva, nimi = nimi, xnimi = xlabel, ynimi = ylabel, tightXAxis=tightXAxis, LEGEND=legenda, omavari = colorList[i] , label = label, gridi = False, loc = loc, bboxmode = bboxmode )

        if muuttuja2 is not None:
            fig, ax, legend = mdp.aikasarjaTulostus( muuttuja_Tdata2, time_data,  tulostus = tulostus, piirra = piirra, uusikuva = False, nimi = nimi, xnimi = xlabel, ynimi = ylabel, tightXAxis=tightXAxis, LEGEND=legenda, omavari = colorList[i], label = label, changeColor = False, gridi = False, loc = loc, bboxmode = bboxmode )





        #######################
    if plottausOnnistuu:
        print(muuttuja, 'nollatapauksia yhteensa', nollatapaus)
        #print 'muuttuja', muuttuja, 'indeksi min', minInd, 'arvo min', minimi, 'indeksi max', maksInd, 'arvo max', maksimi

        xticksHours = np.arange(0., max(time_dataLongest)/3600. + 0.1, 0.5)

        xticks = xticksHours * 3600.

        if xlabels is None:
            xlabels = ['%i' % elem for elem in xticksHours ] #map( str, xticksHours)

        if yticks is not None:
            ax.set_yticks( yticks)


        if ylabels is not None:
            ax.set_yticklabels( ylabels )


        ax.set_xticks( xticks )
        ax.set_xticklabels( xlabels )

        if max(time_dataLongest)/3600 > 20:
            piilotaOsaXlabelParam = 8

        if piilotaOsaXlabel:
            k = 0
            for label in ax.xaxis.get_ticklabels():
                if np.mod(k,piilotaOsaXlabelParam) != 0:
                    label.set_visible(False)
                k+=1

        k = 0
        for line in ax.xaxis.get_ticklines():
            if np.mod(k,piilotaOsaXlabelParam) != 0:
                line.set_markersize(6)
                #line.set_markeredgewidth(3)
            k+=1



        if piilotaOsaYlabel:
            k = 0
            for label in ax.yaxis.get_ticklabels():
                if np.mod(k,piilotaOsaYlabelParam) != 0:
                    label.set_visible(False)
                k+=1

        if ((ylabelFont is not None) and (yticks is not None)):
            for takka in ( ax.xaxis.get_major_ticks() + ax.yaxis.get_major_ticks() ):
                takka.label.set_fontsize(ylabelFont)

        #if customYscale:
            #ax.set_yscale('symlog', basey=10, linthresy=[0,1])

        if spinup is not None:
            mdp.plot_vertical( spinup )

        if colorBar is not None and ( omaVari == True):
           cb = plt.colorbar( colorBar, shrink=.9, pad=.03, aspect=10, ticks = colorBarTickValues )#colorBar
           cb.ax.set_yticklabels(colorBarTickNames)
           cb.ax.set_ylabel( tit )

        # jos ymin ja ymax arvoja ei ole ennalta annettu, niin kaytetaan kuvan raja-arvoina laskettuja arvoja
        if ymin is None:
            ymin = minimi

        if ymax is None:
            ymax = maksimi

        if ( asetaRajat ):
            mdp.plot_setYlim( ymin, ymax, extendBelowZero = extendBelowZero)

        if savePrefix is None:
            savePrefix = muuttuja

        if saveFig:
            plt.savefig( picturefolder + savePrefix + saveTag + LVLprintSave + '.png', bbox_inches='tight', pad_inches=0.06)

            if legenda:
                legendfolder = picturefolder + "/" + "legends/"
                if not os.path.exists( legendfolder ):
                    os.makedirs( legendfolder )
                mdp.export_legend(legend, filename = legendfolder + muuttuja + "_"  + "legend" + str(loc) + ".png"   )

            if tallenna:
                df = pd.DataFrame(data=aikasarjaDict)
                df = df.set_index(timeIndDict)
                df.to_csv(picturefolder + savePrefix + saveTag + LVLprintSave + '.csv', sep=";")



def piirra_aikasarjavertailusettii( muuttuja, variKartta = plt.cm.gist_rainbow, variRefVektori = jarjestys, colorBar = None, colorBarTickValues = [0,1], colorBarTickNames = ['0','1'], muunnosKerroin = 1.0, longName = 'titteli', xlabel = 'time [h]', ylabel='ylabel', extendBelowZero = True, asetaRajat = True, ymin = None, ymax = None, relative = False, savePrefix = None, omaVari = True, tit = '', nollaArvo = None, xlabels = None, ylabels = None, xticks = None, yticks = None, spinup = None, ylabelFont = None, askChangeOfVariable = False, piilotaOsaXlabel = False, fontsizeCustom = False ):

    origmuuttuja = muuttuja
    maksimi = None
    minimi  = None
    maxRef = np.max( variRefVektori )
    maksInd = None
    minInd  = None
    #vastausKaikkiin = False
    nono = None

    time_data       = mdp.read_Data( filenameTS[0], 'time'  )

    for i in range(1,len(tiedostolista)):

        uusikuva = True
        case_indeksi = i


        if i == 1:
            longName = "ice1-ice0"
            stri = "ice1"
        elif i== 2:
            longName = "ice4-ice0"
            stri = "ice4"

        if muuttuja == "lwp":

            muuttuja_Tdata_ice0 = mdp.read_Data( filenameTS[0], 'lwp_bar' )*muunnosKerroin
            muuttuja_Tdata      = mdp.read_Data( filenameTS[i], 'lwp_bar' )*muunnosKerroin
            ylabel = r'$\Delta$LWP [$g/m^2$]'

            if i == 1:
                omavari = 'red'
            elif i == 2:
                omavari = 'darkviolet'



        elif muuttuja == "lwpiwp":

            muuttuja_Tdata_ice0 = ( mdp.read_Data( filenameTS[0], 'lwp_bar' )  ) *muunnosKerroin
            muuttuja_Tdata      = ( mdp.read_Data( filenameTS[i], 'lwp_bar' ) +  mdp.read_Data( filenameTS[i], 'iwp_bar' ) ) *muunnosKerroin
            ylabel = r'$\Delta$(LWP+IWP) [$g/m^2$]'

            if i == 1:
                omavari = 'blue'
            elif i == 2:
                omavari = 'darkblue'

        else:
            sys.exit("anna oikea muuttuja")

        muuttuja_Tdata = muuttuja_Tdata - muuttuja_Tdata_ice0



        maksimi = np.max( muuttuja_Tdata )

        minimi  = np.min( muuttuja_Tdata )





        nimi = longName + ' ' + tag


        fig, ax = mdp.aikasarjaTulostus( muuttuja_Tdata, time_data,  tulostus = tulostus, piirra = piirra, uusikuva = uusikuva, nimi = nimi, xnimi = xlabel, ynimi = ylabel, tightXAxis=tightXAxis, LEGEND=False, omavari = colorList[i])
        #######################
    #print 'muuttuja', muuttuja, 'indeksi min', minInd, 'arvo min', minimi, 'indeksi max', maksInd, 'arvo max', maksimi

        xticksHours = np.arange(0., max(time_data)/3600. + 0.1, 0.5)

        xticks = xticksHours * 3600.

        if xlabels is None:
            xlabels = list(map( str, xticksHours))

        if yticks is not None:
            ax.set_yticks( yticks)

        if ylabels is not None:
            ax.set_yticklabels( ylabels )


        ax.set_xticks( xticks )
        ax.set_xticklabels( xlabels )

        if piilotaOsaXlabel:
            k = 0
            for label in ax.xaxis.get_ticklabels():
                if np.mod(k,4) != 0:
                    label.set_visible(False)
                k+=1


        if fontsizeCustom:
            if ((ylabelFont is not None) and (yticks is not None)):
                for takka in ( ax.xaxis.get_major_ticks() + ax.yaxis.get_major_ticks() ):
                    takka.label.set_fontsize(ylabelFont)

        #if customYscale:
            #ax.set_yscale('symlog', basey=10, linthresy=[0,1])

        if spinup is not None:
            mdp.plot_vertical( spinup )

        mdp.plot_horizontal( 0. )

        if colorBar is not None and ( omaVari == True):
            cb = plt.colorbar( colorBar, shrink=.9, pad=.03, aspect=10, ticks = colorBarTickValues )#colorBar
            cb.ax.set_yticklabels(colorBarTickNames)
            cb.ax.set_ylabel( tit )



        if ( asetaRajat ):
            mdp.plot_setYlim( minimi, maksimi, extendBelowZero = extendBelowZero)




        if savePrefix is None:
            savePrefix = muuttuja+longName+stri
        else:
            savePrefix = savePrefix + stri

        if saveFig:
            plt.savefig( picturefolder + savePrefix + saveTag + LVLprintSave + '.png')


#########################
def piirra_profiilisettii( muuttuja, variKartta = plt.cm.gist_rainbow, variRefVektori = jarjestys, colorBar = None, colorBarTickValues = [0,1], colorBarTickNames = ['0','1'], muunnosKerroin = 1.0, longName = 'titteli', xlabel = 'xlabel', ylabel='ylabel', extendBelowZero = True, asetaRajat = True, ymin = None, ymax = None, xmin = None, xmax = None, relative = False, savePrefix = None, ajanhetket = None, tit = '', nollaArvo = None, rajaKerros = None, omaVari = True, fontsizeCustom = False ):

    maksimi = None
    minimi  = None
    maxRef = np.max( variRefVektori )
    maksimifracZ = None
    for i in range(len(tiedostolista)):
        uusikuva = True if i == 0 else  False

        muuttuja_data      = mdp.read_Data( filenamePS[i], muuttuja )*muunnosKerroin

        if EMUL:
            if not EMULCASESCUSTOM:
                case_indeksi = int(filenameNC[i].split("/")[-2][4:])-1
            else:
                case_indeksi = emulCaseIndexes[i]
        else:
            case_indeksi = i

        #### relative
        if relative:
            if ((nollaArvo is None) and (nono is None)):
                lahtoarvo = muuttuja_data[0]
                apu = lahtoarvo[0,:] == -999.
                if apu.all():
                    print('WARNING lahtoarvo = -999. lasketaan seuraavasta arvosta', muuttuja)
                    lahtoarvo = muuttuja_data[1]
            elif ( isinstance( nollaArvo, np.ndarray) or isinstance(nollaArvo, list) ):
                lahtoarvo = nollaArvo[case_indeksi]
            elif nono is not None:
                lahtoarvo = muuttuja_data[nono]

            if lahtoarvo == 0.:
                    print('VAROITUS: ei voida laskea relative koska lahtoarvo on nolla', muuttuja, 'case', i+1, 'nono', nono)
                    if nono is None:
                        NEXT = input('Haluatko etsia seuraavan ei-negatiivisen datasta kaikkiin kappyroihin: yes/no: ') in kylla

                        if NEXT:
                            nono = 0
                            while( muuttuja_data[nono] == 0. ):
                                nono += 1
                            lahtoarvo = muuttuja_data[nono]
                        else:
                            print("Let's skip this", muuttuja, i+1)
                            continue

                    else:
                        print("Let's skip this", muuttuja, i+1)
                        continue

            muuttuja_Tdata = muuttuja_data / lahtoarvo
        #### end relative

        time_data   = mdp.read_Data( filenameTS[i], 'time'    )

        height_data = mdp.read_Data( filenameNC[i], 'zt' )

        if ajanhetket is not None:
            aikaP = np.argmin( np.abs(ajanhetket - time_data) )

        if aikaP > np.shape(muuttuja_data)[0] -1:
            #print 'VAROITUS: indeksi liian iso, skipataan - ', 'aikaP indeksi:', aikaP, 'muuttuja_data viimeinen indeksi:',  np.shape(muuttuja_data)[0] -1, 'muuttuja', muuttuja
            if aikaP - (np.shape(muuttuja_data)[0] -1) > 1:
                print('VAROITUS: indeksi liian iso, skipataanko, koska ero viimeiseen indeksiin on >1 : ', aikaP - (np.shape(muuttuja_data)[0] -1) , 'aikaP indeksi:', aikaP, 'muuttuja_data viimeinen indeksi:',  np.shape(muuttuja_data)[0] -1, 'muuttuja', muuttuja)
                ippu = 'Do you want use the last index ' + str(aikaP) + ' (yes/no): '
                lastIND = input( ippu ) in kylla
                if not lastIND:
                    continue
            # asetetaan aikaP viimeiseksi indeksiksi
            aikaP = np.shape(muuttuja_data)[0] -1




        #### pbl height
        if rajaKerros is None:
            pbl_height = float(input('Anna rajakerroksen korkeus lahtotilanteessa (float): ') )
        elif ( isinstance(rajaKerros, np.ndarray) or isinstance(rajaKerros, list) ):
            pbl_height = rajaKerros[case_indeksi]
        #### end pbl height

        dens = 20

        fracZ   = np.zeros( dens*(len(height_data)-1) +1 )
        normZ   = np.zeros( len(fracZ) )

        pSpline = np.zeros( ( 2, len(fracZ) ) )


        for k in range(len(fracZ)-1):
            h_indeksi = int(np.floor(k/dens) )
            normZ[k] =  ( height_data[ h_indeksi ] + np.mod(k,dens)*(height_data[ h_indeksi + 1] - height_data[ h_indeksi ])/float(dens) )
            fracZ[k] =  normZ[k] / pbl_height

        normZ[-1] = height_data[-1]
        fracZ[-1] = normZ[-1] / pbl_height

        tck0 = interpolate.splrep( height_data, muuttuja_data[ 0,: ]     )
        tckT = interpolate.splrep(height_data, muuttuja_data[ aikaP,:]  )
        for k in range( np.shape(pSpline)[1] ):
            pSpline[ 0,k ]  = interpolate.splev( normZ[k], tck0 )
            pSpline[ 1,k ]  = interpolate.splev( normZ[k], tckT )

        p_difference = pSpline[ 1,:] / pSpline[ 0,:] -1


        if maksimifracZ is not None:
            maksimifracZ = max( maksimifracZ,  np.max(fracZ) )
        else:
            maksimifracZ = np.max(fracZ)

        if maksimi is not None:
            maksimi = max( maksimi,  np.max(p_difference) )
        else:
            maksimi = np.max(p_difference)

        if minimi is not None:
            minimi = min( minimi,  np.min(p_difference) )
        else:
            minimi = np.min(p_difference)

        colorMap = variKartta
        skal = variRefVektori[ case_indeksi ] / maxRef
        color = colorMap(skal)

        if omaVari:
            omavari = color
        else:
            omavari = omaVari

        if EMUL:
            nimi = longName + ' ' + tag + LVLprintFig
            if customLabels:
                label = labelArray[i]
            else:
                label = str(case_indeksi+1)
        else:
            nimi = longName + ' ' + tag
            label = labelArray[i]
        fig, ax = mdp.profiiliTulostus( p_difference, aikaPisteet = 0, korkeus = fracZ, tulostus = tulostus, piirra = piirra, uusikuva = uusikuva, nimi = nimi, xnimi = xlabel, ynimi = ylabel, tightXAxis=tightXAxis, LEGEND=LEGEND, omavari = colorList[i], label = label, loc = 3 )

        ####################
    if fontsizeCustom:
        # tikkien fonttikoko
        for takka in ( ax.xaxis.get_major_ticks() + ax.yaxis.get_major_ticks() ):
                    takka.label.set_fontsize(18)


        font = 26
        ax.xaxis.get_label().set_fontsize(font)
        ax.yaxis.get_label().set_fontsize(font)



    if colorBar is not None and ( omaVari == True):
       cb = plt.colorbar( colorBar, shrink=.9, pad=.03, aspect=10, ticks = colorBarTickValues )#colorBar
       cb.ax.set_yticklabels(colorBarTickNames)
       cb.ax.set_ylabel( tit )


        # jos ymin ja ymax arvoja ei ole ennalta annettu, niin kaytetaan kuvan raja-arvoina laskettuja arvoja
    if ymin is None:
        ymin = minimi

    if ymax is None:
        ymax = maksimi

    if ( asetaRajat ):
        mdp.plot_setYlim( ymin, ymax, extendBelowZero = extendBelowZero)

    if (xmin is not None) or (xmax is not None):
        plt.xlim( xmin, xmax)
    if savePrefix is None:
        savePrefix = muuttuja

    if saveFig:
        plt.savefig( picturefolder + savePrefix + saveTag + LVLprintSave + '.png')


def piirra_profiiliKehitys(  muuttuja, variKartta = plt.cm.gist_rainbow, colorBar = None, colorBarTickValues = [0,1], colorBarTickNames = ['0','1'], muunnosKerroin = 1.0, longName = 'titteli', xlabel = 'xlabel', ylabel='ylabel', extendBelowZero = True, asetaRajat = True, ymin = None, ymax = None, xmin = None, xmax = None,  savePrefix = None, aikaPisteet = None, tit = '', nollaArvo = None, rajaKerros = None, paksuus = None, xlabels = None, ylabels = None, xticks = None, yticks = None, tempConversion = False, askChangeOfVariable = False,fontsizeCustom = False, viivaTyyli = None, plottaaKaikkiSamaan = False, useSnsColor = False, xTikit = None, oikeatXtikit = None ):
    #import matplotlib.patches as mpatches
    from emulator_inputs import absT
    if aikaPisteet is None:
        sys.exit("You did not give any time points for profile evolution, exiting")

    time_data   = mdp.read_Data( filenameTS[0], 'time'    )
    maxRef = np.max( time_data )
    variRefVektori = time_data

    noErrors = True
    lastIND = None
    for i in reversed(range(len(tiedostolista))):
        if plottaaKaikkiSamaan:
            if i == 0:
                uusikuva = True
            elif i > 0:
                uusikuva = False

        maksimi = None
        minimi  = None
        maksimifracZ = None
        if EMUL:
            if not EMULCASESCUSTOM:
                case_indeksi = int(filenameNC[i].split("/")[-2][4:])-1
            else:
                case_indeksi = emulCaseIndexes[i]
        else:
            case_indeksi = i

        if askChangeOfVariable:
            printti = "Case is "+ arguments[i+1] + ", the variable is currently: " + muuttuja + ' if you want to keep it press [Enter], otherwise give the name of the variable (e.g. [prcp/rmH2Opr] [Nc_ic/CCN] [P_rl/l]): '
            apumuuttuja = input(printti)

            if apumuuttuja != '':
                muuttuja = apumuuttuja

            print('variable is', muuttuja)
            print(' ')


        heightMax = np.finfo(float).eps
        for t in range(len(aikaPisteet)):
            if not plottaaKaikkiSamaan:
	            uusikuva = True if t == 0 else  False

            try:
                muuttuja_data      = mdp.read_Data( filenamePS[i], muuttuja )*muunnosKerroin
            except KeyError:
                if debug: print("KeyError, variable " + muuttuja + " doesn't exist in " + filenamePS[i] )
                noErrors = False
                break
            except FileNotFoundError:
                if debug: print("FileNotFoundError", tiedostolista[i] + ".ps.nc" )
                noErrors = False
                break


            if tempConversion:
                paine_data    =  mdp.read_Data( filenamePS[i], 'p' )
                for aa in range( np.shape(paine_data)[0] ):
                    for bb in range( np.shape(paine_data)[1] ):
                        muuttuja_data[aa, bb] = absT( muuttuja_data[aa,bb], paine_data[aa,bb], 1.)

            height_data = mdp.read_Data( filenameNC[i], 'zt' )
            heightMax   = max(np.max(height_data), heightMax)
            base = mdp.read_Data( filenameTS[i], 'zb' )
            top  = mdp.read_Data( filenameTS[i], 'zc' )


            aikaP = np.argmin( np.abs(aikaPisteet[t] - time_data) )

            if aikaP > np.shape(muuttuja_data)[0] -1:
                #print 'VAROITUS: indeksi liian iso, skipataan - ', 'aikaP indeksi:', aikaP, 'muuttuja_data viimeinen indeksi:',  np.shape(muuttuja_data)[0] -1, 'muuttuja', muuttuja
                if aikaP - (np.shape(muuttuja_data)[0] -1) > 1:
                    if i == 0:
                        print(' ')
                    print('VAROITUS: indeksi liian iso, skipataanko, koska ero viimeiseen indeksiin on >1 : ', aikaP - (np.shape(muuttuja_data)[0] -1) , 'aikaP indeksi:', aikaP, 'muuttuja_data viimeinen indeksi:',  np.shape(muuttuja_data)[0] -1, 'muuttuja', muuttuja)
                    ippu = 'Do you want use the last index ' + str(aikaP) + ' (yes/no): '
                    if lastIND is None:
                        lastIND = input( ippu ) in kylla
                        if not lastIND:
                            continue
                # asetetaan aikaP viimeiseksi indeksiksi
                aikaP = np.shape(muuttuja_data)[0] -1



            ##### pbl height
            #if rajaKerros is None:
                #pbl_height = float(raw_input('Anna rajakerroksen korkeus lahtotilanteessa (float): ') )
            #elif ( isinstance(rajaKerros, np.ndarray) or isinstance(rajaKerros, list) ):
                #pbl_height = rajaKerros[case_indeksi]
            ##### end pbl height

            #dens = 20

            #fracZ   = np.zeros( dens*(len(height_data)-1) +1 )
            #normZ   = np.zeros( len(fracZ) )

            #pSpline = np.zeros( ( 2, len(fracZ) ) )


            #for k in xrange(len(fracZ)-1):
                #h_indeksi = int(np.floor(k/dens) )
                #normZ[k] =  ( height_data[ h_indeksi ] + np.mod(k,dens)*(height_data[ h_indeksi + 1] - height_data[ h_indeksi ])/float(dens) )
                #fracZ[k] =  normZ[k] / pbl_height

            #normZ[-1] = height_data[-1]
            #fracZ[-1] = normZ[-1] / pbl_height

            #tck0 = interpolate.splrep( height_data, muuttuja_data[ 0,: ]     )
            #tckT = interpolate.splrep(height_data, muuttuja_data[ aikaP,:]  )
            #for k in xrange( np.shape(pSpline)[1] ):
                #pSpline[ 0,k ]  = interpolate.splev( normZ[k], tck0 )
                #pSpline[ 1,k ]  = interpolate.splev( normZ[k], tckT )

            #p_difference = pSpline[ 1,:] / pSpline[ 0,:] -1


            #if maksimifracZ is not None:
                #maksimifracZ = max( maksimifracZ,  np.max(fracZ) )
            #else:
                #maksimifracZ = np.max(fracZ)

            if maksimi is not None:
                maksimi = max( maksimi,  np.max(muuttuja_data) )
            else:
                maksimi = np.max(muuttuja_data)

            if minimi is not None:
                minimi = min( minimi,  np.min(muuttuja_data) )
            else:
                minimi = np.min(muuttuja_data)
            ###########################
            if isinstance(variKartta, list):
                colorMap = variKartta[i]
            else:
                colorMap = variKartta
            ###########################
            if viivaTyyli is None:
                linestyle = '-'
            elif isinstance(viivaTyyli, list):
                linestyle = viivaTyyli[t]
            else:
                linestyle = viivaTyyli

            if not useSnsColor:
                skal = variRefVektori[ aikaP ] / maxRef
                color = colorMap(skal)
            else:
                color = colorMap[t]




            if EMUL and not customLabels:
                aputagi = str(case_indeksi+1)

            else:
                aputagi = labelArray[i]

            legend = str(myRoundFloat( time_data[aikaP]/3600.) ) + ' [h]'
            nimi = longName + ' ' + aputagi + ' ' + tag



            fig, ax = mdp.profiiliTulostus( muuttuja_data[aikaP,:], aikaPisteet = 0, korkeus = height_data, tulostus = tulostus, piirra = piirra, uusikuva = uusikuva, nimi = nimi, xnimi = xlabel, ynimi = ylabel, tightXAxis=False, tightYAxis = True, LEGEND=True, omavari = color, label = legend, loc = 2, linestyle = linestyle )

            if aikaP >0:
                plt.axhline( base[aikaP], color = color, linestyle= (0, (1, 5)) )
                plt.axhline(  top[aikaP], color = color, linestyle= (0, (1, 5)) )

            elif aikaP == 0 and EMUL:
                plt.axhline( rajaKerros[case_indeksi], color = color, linestyle= 'dashed' )
                plt.axhline( rajaKerros[case_indeksi] - paksuus[case_indeksi], color = color, linestyle= 'dashed' )


        ####################
        if noErrors and (not plottaaKaikkiSamaan):

            if fontsizeCustom:
                ## tikkien fonttikoko
                for takka in ( ax.xaxis.get_major_ticks() + ax.yaxis.get_major_ticks() ):
                    takka.label.set_fontsize(18)


                font = 26
                ax.xaxis.get_label().set_fontsize(font)
                ax.yaxis.get_label().set_fontsize(font)
                #### end tikkien fonttikoko

            korkeustikit = list(map( int, np.arange( 0, heightMax+101., 100.) ))
            #if yticks is not None:
            print("noErrors profKehitys", muuttuja, korkeustikit, filenameNC[i] )
            ax.set_yticks( korkeustikit )
            #if ylabes
            ax.set_yticklabels( list(map(str, korkeustikit)))

            if xTikit is not None:
                ax.set_xticks(xTikit)

            if (xTikit is not None) and (oikeatXtikit is None):
                ax.set_xticklabels(list(map(str, xTikit)))
            elif oikeatXtikit is not None:
                ax.set_xticklabels(oikeatXleimat)

            k = 0
            for label in ax.yaxis.get_ticklabels():
                if np.mod(k,2) != 0:
                    label.set_visible(False)
                k+=1

            #patch = mpatches.Patch(color=color, label=label)
            #plt.legend(handles=[patch])

            #if colorBar is not None:
                #cb = plt.colorbar( colorBar, shrink=.9, pad=.03, aspect=10, ticks = colorBarTickValues )#colorBar
                #cb.ax.set_yticklabels(colorBarTickNames)
                #cb.ax.set_ylabel( tit )


                # jos ymin ja ymax arvoja ei ole ennalta annettu, niin kaytetaan kuvan raja-arvoina laskettuja arvoja
            if ymin is None:
                ymin = minimi

            if ymax is None:
                ymax = maksimi

            if ( asetaRajat ):
                mdp.plot_setYlim( ymin, ymax, extendBelowZero = extendBelowZero)

            if (xmin is not None) or (xmax is not None):
                plt.xlim( xmin, xmax)
            if savePrefix is None:
                savePrefix = muuttuja

            if saveFig:
                valitagi = '_'
                if customLabels:
                    valitagi = labelArray[i]
                elif applyForAll and not customLabels:
                    valitagi = str(case_indeksi+1) + str(i)
                else:
                    valitagi = str(case_indeksi+1)

                subfolder = picturefolder + '/' + savePrefix + '/'
                if not os.path.exists( subfolder ):
                    os.makedirs( subfolder )

                plt.savefig( subfolder + savePrefix + '_' + valitagi + saveTag + LVLprintSave + '.png')

    if noErrors and plottaaKaikkiSamaan:
        print("taalla ei pitais olla")
        if fontsizeCustom:
            ## tikkien fonttikoko
            for takka in ( ax.xaxis.get_major_ticks() + ax.yaxis.get_major_ticks() ):
                takka.label.set_fontsize(18)


            font = 26
            ax.xaxis.get_label().set_fontsize(font)
            ax.yaxis.get_label().set_fontsize(font)
            #### end tikkien fonttikoko

        korkeustikit = list(map( int, np.arange( 0, heightMax+101., 100.) ))
        #if yticks is not None:
        ax.set_yticks( korkeustikit )
        #if ylabes
        ax.set_yticklabels( list(map(str, korkeustikit)))

        if xTikit is not None:
            ax.set_xticks(xTikit)

        if (xTikit is not None) and (oikeatXtikit is None):
            ax.set_xticklabels(list(map(str, xTikit)))
        elif oikeatXtikit is not None:
            ax.set_xticklabels(oikeatXleimat)

        k = 0
        for label in ax.yaxis.get_ticklabels():
            if np.mod(k,2) != 0:
                label.set_visible(False)
            k+=1

        #patch = mpatches.Patch(color=color, label=label)
        #plt.legend(handles=[patch])

        #if colorBar is not None:
            #cb = plt.colorbar( colorBar, shrink=.9, pad=.03, aspect=10, ticks = colorBarTickValues )#colorBar
            #cb.ax.set_yticklabels(colorBarTickNames)
            #cb.ax.set_ylabel( tit )


            # jos ymin ja ymax arvoja ei ole ennalta annettu, niin kaytetaan kuvan raja-arvoina laskettuja arvoja
        if ymin is None:
            ymin = minimi

        if ymax is None:
            ymax = maksimi

        if ( asetaRajat ):
            mdp.plot_setYlim( ymin, ymax, extendBelowZero = extendBelowZero)

        if (xmin is not None) or (xmax is not None):
            plt.xlim( xmin, xmax)
        if savePrefix is None:
            savePrefix = muuttuja

        if saveFig:
            valitagi = "_".join([ st for st in labelArray])
            plt.savefig( picturefolder + savePrefix + '_' + valitagi + saveTag + LVLprintSave + '.png')



############################
def piirra_aikasarjaPathXYZ( muuttuja, muunnosKerroin = 1.0, longName = None, savePrefix = None, xaxislabel = 'time [h]', xlabels = None, ylabels = None, xticks = None, yticks = None, spinup = None, piilotaOsaXlabel = False, legenda = True ):


    if longName is None:
        longName = muuttuja
    for i in range(len(tiedostolista)):
        uusikuva = True if i == 0 else  False

        if EMUL:
            if not EMULCASESCUSTOM:
                case_indeksi = int(filenameNC[i].split("/")[-2][4:])-1
            else:
                case_indeksi = emulCaseIndexes[i]
        else:
            case_indeksi = i

        muuttuja_data = mdp.read_Data( filenameNC[i], muuttuja )*muunnosKerroin
        time_data     = mdp.read_Data( filenameNC[i], 'time'   )
        dn0_data      = mdp.read_Data( filenameNC[i], 'dn0'    )
        zt_data       = mdp.read_Data( filenameNC[i], 'zt'     )
        zm_data       = mdp.read_Data( filenameNC[i], 'zm'     )
        korkeus = ( zm_data - zt_data )*2.0


        if customLabels:
            aputagi = labelArray[i]
        else:
            aputagi = str(case_indeksi+1)

        nimi = longName + ' grid data'
        label = aputagi

        fig,ax = mdp.laske_path_aikasarjaXYZ( muuttuja_data, dn0_data, korkeus, time_data, muunnosKerroin = muunnosKerroin, tulostus = tulostus, piirra = piirra, uusikuva = uusikuva, nimi = nimi, xlabel = xaxislabel, tightXAxis=tightXAxis, label = label, LEGEND = legenda)


    ajat  =  np.round( mdp.read_Data( filenameNC[0], 'time' ), 0 )

    xticksHours = np.arange(0, max(ajat)/3600. + 0.1, 0.5)

    if xticks is None:
        xticks = xticksHours * 3600.

    if xlabels is None:
        xlabels = list(map( str, xticksHours))

    print('xticks', xticks)
    print('xlabels', xlabels)
    ax.set_xticks( xticks )
    ax.set_xticklabels( xlabels )

    if piilotaOsaXlabel:
        k = 0
        for label in ax.xaxis.get_ticklabels():
            if np.mod(k,4) != 0:
                label.set_visible(False)
            k+=1

    if spinup is not None:
        mdp.plot_vertical( spinup )

    if savePrefix is None:
        savePrefix = muuttuja
    if saveFig:
        plt.savefig( picturefolder + savePrefix + saveTag + LVLprintSave + '.png')


##########################
def piirra_maksimiKeissit( muuttuja, muunnosKerroin = 1.0, longName = 'pitka nimi', xlabel = 'case', ylabel = 'ylabel', savePrefix = None, askChangeOfVariable = False, ajanhetket = None, fontsizeCustom = False ):
    lista = np.zeros( cases )
    xTikit = np.zeros( cases )


    for i in range(len(tiedostolista)):
        if askChangeOfVariable:
            printti = "Case is "+ arguments[i+1] + ", the variable is currently: " + muuttuja + ' if you want to keep it press [Enter], otherwise give the name of the variable (e.g. [prcp/rmH2Opr] [Nc_ic/CCN] [P_rl/l]): '
            apumuuttuja = input(printti)

            if apumuuttuja != '':
                muuttuja = apumuuttuja

            if muuttuja == 'prcp':
                muunnosKerroin = 2.5e-06
            elif muuttuja == 'rmH2Opr':
                muunnosKerroin = 1.

            print('variable is', muuttuja, 'muunnosKerroin', muunnosKerroin)
            print(' ')

        muuttuja_Tdata  = mdp.read_Data( filenameTS[i], muuttuja )*muunnosKerroin
        time_data       = mdp.read_Data( filenameNC[i], 'time'   )

        if EMUL:
            if not EMULCASESCUSTOM:
                tikki = int(filenameNC[i].split("/")[-2][4:])
            else:
                tikki = emulCaseIndexes[i]+1
        else:

            tikki = int(i+1)

        xTikit[i] = tikki

        if ajanhetket is not None:
            aikaP = np.argmin( np.abs( ajanhetket - time_data) )
        else:
            aikaP = 0

        if aikaP > np.shape(muuttuja_Tdata)[0] -1:
            #print 'VAROITUS: indeksi liian iso, skipataan - ', 'aikaP indeksi:', aikaP, 'muuttuja_Tdata viimeinen indeksi:',  np.shape(muuttuja_Tdata)[0] -1, 'muuttuja', muuttuja
            if aikaP - (np.shape(muuttuja_Tdata)[0] -1) > 1:
                print('VAROITUS: indeksi liian iso, skipataanko, koska ero viimeiseen indeksiin on >1 : ', aikaP - (np.shape(muuttuja_Tdata)[0] -1) , 'aikaP indeksi:', aikaP, 'muuttuja_Tdata viimeinen indeksi:',  np.shape(muuttuja_Tdata)[0] -1, 'muuttuja', muuttuja)
                ippu = 'Do you want use the last index ' + str(aikaP) + ' (yes/no): '
                lastIND = input( ippu ) in kylla
                if not lastIND:
                    continue
            # asetetaan aikaP viimeiseksi indeksiksi
            aikaP = np.shape(muuttuja_Tdata)[0] -1



        #print 'np.shape(lista)', np.shape(lista), 'case_indeksi',i, 'aikaP', aikaP, 'np.shape(muuttuja_Tdata)[0]', np.shape(muuttuja_Tdata)[0], 'muuttuja', muuttuja

        lista[i] = np.max( muuttuja_Tdata[aikaP:] )

    fig, ax, leg = mdp.plottaa( jarjestys, lista, tit = longName+ ' ' + tag + LVLprintFig, xl = xlabel, yl = ylabel, changeColor = True, markers = True, uusikuva = True, gridi = False, tightXAxis = False, tightYAxis = True, LEGEND = False )

    mdp.plot_setYlim( 0., max(lista), extendBelowZero = False, A = 0.05 )
    #print map(str, xTikit)
    ax.set_xticks( list(map(int, jarjestys)) )
    if fontsizeCustom:
        for takka in ax.xaxis.get_major_ticks():
                    takka.label.set_fontsize(9)
    #ax.set_xticklabels( map(str, xTikit) , fontsize = 8 )

    if savePrefix is None:
                savePrefix = longName.replace( " ", "_" )
    if saveFig:
        plt.savefig( picturefolder + savePrefix+ saveTag + LVLprintSave + '.png')

##########################
def piirra_keissiVertailuEmul( muuttuja, muunnosKerroin = 1.0, tiedostopaate='ts', longNamePostfix = '', savePrefix = None, askChangeOfVariable = False, ajanhetket = 0., extendBelowZero = True, roundIt = False, myRoundInt = None, myRoundF = None ):
    lista = np.zeros( cases )
    xTikit = np.zeros( cases )

    if not EMUL or len(emulatorSets) != 2 :
        sys.exit("Tama toimii vain emulaattoriseteilla ja jos niita on kaksi")


    if len(tiedostopaate) > 0:
        tiedostopaate = "." + tiedostopaate + ".nc"
    else:
        tiedostopaate = ".nc"

    vertailuVektorit = np.zeros( ( len(emulatorSets), len(emulatorSims) ) )

    for i in range(len(emulatorSets)):
        for j in range(len(emulatorSims)):

            if askChangeOfVariable:
                printti = "Case is "+ emulatorSets[i] + "/" + emulatorSims[j] + ", the variable is currently: " + muuttuja + ' if you want to keep it press [Enter], otherwise give the name of the variable (e.g. [prcp/rmH2Opr] [Nc_ic/CCN] [P_rl/l]): '
                apumuuttuja = input(printti)

                if apumuuttuja != '':
                    muuttuja = apumuuttuja

                #if muuttuja == 'prcp':
                    #muunnosKerroin = 2.5e-06
                #elif muuttuja == 'rmH2Opr':
                    #muunnosKerroin = 1.

                print('variable is', muuttuja, 'muunnosKerroin', muunnosKerroin)
                print(' ')
            tiedosto = emulatorSets[i] + "/" + emulatorSims[j] + "/" + emulatorSims[j] + tiedostopaate
            datasetti  = xr.open_dataset( tiedosto  )

            aikaP = [ np.argmin( np.abs( datasetti["time"].values - tt*3600.)) for tt in ajanhetket ]
            aikalista = np.arange( min(aikaP), max(aikaP)+1 )
            vertailuVektorit[i,j] =  np.mean( datasetti[ muuttuja ].isel( time = aikalista ).values*muunnosKerroin )



    longName = datasetti[ muuttuja ].attrs['longname']

    if len(ajanhetket)==2:
        longName = longName + ' from ' + str(ajanhetket[0]) + ' h to ' + str(ajanhetket[1]) + ' h ' + longNamePostfix
    else:
        longName = longName + ' at ' + str(ajanhetket[0]) + 'h ' + longNamePostfix

    if customLabels and generateEmulFilelist:
        xlaabeli = labelArraySets[0]
        ylaabeli = labelArraySets[1]
    else:
        xlaabeli = emulatorSets[0]
        ylaabeli = emulatorSets[1]

    fig, ax = mdp.plottaa( vertailuVektorit[0], vertailuVektorit[1], tit = "Comparison of " + longName+ ' ' + tag + LVLprintFig, xl = xlaabeli, yl = ylaabeli, changeColor = False, scatter = True, uusikuva = True, gridi = False, tightXAxis = False, tightYAxis = True, LEGEND = False )
    mini = min( np.min( vertailuVektorit[0] ), np.min(vertailuVektorit[1] ))
    maxi = max( np.max( vertailuVektorit[0] ), np.max(vertailuVektorit[1] ))
    reinzi = np.linspace( mini, maxi, 4)

    if myRoundInt is not None:
        reinzi = [ myRound(kekke, myRoundInt) for kekke in reinzi ]
    elif myRoundF is not None:
        reinzi = [ myRoundFloat( kekke, prec = myRoundF[0], base = myRoundF[1] ) for kekke in reinzi ]

    mdp.plot_setXlim( mini, maxi, extendBelowZero = extendBelowZero, A = 0.05 )
    mdp.plot_setYlim( mini, maxi, extendBelowZero = extendBelowZero, A = 0.05 )

    lims = [
            np.min([ax.get_xlim(), ax.get_ylim()]),  # min of both axes
            np.max([ax.get_xlim(), ax.get_ylim()]),  # max of both axes
            ]

# now plot both limits against eachother
    ax.plot(lims, lims, 'k-', alpha=0.75, zorder=0)
    ax.set_aspect('equal')
    ax.set_xlim(lims)
    ax.set_ylim(lims)

    ax.xaxis.set_ticks( reinzi )
    ax.yaxis.set_ticks( reinzi )


    if roundIt:
        ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))

    #mdp.plot_setYlim( 0., max(lista), extendBelowZero = False, A = 0.05 )
    #print map(str, xTikit)
    #ax.set_xticks( map(int, jarjestys) )
    #for takka in ax.xaxis.get_major_ticks():
    #            takka.label.set_fontsize(9)
    #ax.set_xticklabels( map(str, xTikit) , fontsize = 8 )

    if savePrefix is None:
                savePrefix = muuttuja.replace( " ", "_" )
    if saveFig:
        plt.savefig( picturefolder + savePrefix+ saveTag + LVLprintSave + tiedostopaate + str(ajanhetket) + '.png')

######################################
def piirra_aikasarjaEmulVertailuSettii( muuttuja, tiedostopaate='ts', muunnosKerroin = 1.0, longName = 'titteli', longNamePostfix = '', xlabel = 'time [h]', ylabel='ylabel', extendBelowZero = True, asetaRajat = True, ymin = None, ymax = None, relative = False, savePrefix = None, omaVari = True, tit = '', nollaArvo = None, xlabels = None, ylabels = None, xticks = None, yticks = None, spinup = None, ylabelFont = None, askChangeOfVariable = False, piilotaOsaXlabel = False, legenda = True, profiili = False, piilotaOsaYlabel = False, piilotaOsaYlabelParam = 3, fontsizeCustom = False ):


    origmuuttuja = muuttuja
    maksimi = None
    minimi  = None
    maksInd = None
    minInd  = None
    #vastausKaikkiin = False
    nono = None

    if profiili:
        tiedostonimi = filenamePS
    else:
        tiedostonimi = filenameTS
##############################

    if len(tiedostopaate) > 0:
        tiedostopaate = "." + tiedostopaate + ".nc"
    else:
        tiedostopaate = ".nc"


    for j in range(len(emulatorSims)):
        uusikuva = True
        for i in range(len(emulatorSets)):

            if askChangeOfVariable:
                printti = "Case is "+ emulatorSets[i] + "/" + emulatorSims[j] + ", the variable is currently: " + muuttuja + ' if you want to keep it press [Enter], otherwise give the name of the variable (e.g. [prcp/rmH2Opr] [Nc_ic/CCN] [P_rl/l]): '
                apumuuttuja = input(printti)

                if apumuuttuja != '':
                    muuttuja = apumuuttuja

                if muuttuja == 'prcp':
                    muunnosKerroin = 2.5e-06
                elif muuttuja == 'rmH2Opr':
                    muunnosKerroin = 1.

                print('variable is', muuttuja, 'muunnosKerroin', muunnosKerroin)
                print(' ')

            tiedosto = emulatorSets[i] + "/" + emulatorSims[j] + "/" + emulatorSims[j] + tiedostopaate
            datasetti  = xr.open_dataset( tiedosto  )

            time_data =  datasetti["time"].values

            muuttuja_Tdata  =  datasetti[ muuttuja ].values*muunnosKerroin





            omavari = omaVari

            if maksInd is not None:
                if np.max(muuttuja_Tdata) > maksimi: # maksimia ei ole viela tassa kohtaa paivitetty
                    # maksimi indeksi muuttuu koska uusi maksimi on suurempi kuin vanha maksimi
                    maksInd = np.argmax( muuttuja_Tdata)
            else:
                maksInd = np.argmax( muuttuja_Tdata)

            if minInd is not None:
                if np.min(muuttuja_Tdata) < minimi: # maksimia ei ole viela tassa kohtaa paivitetty
                    # maksimi indeksi muuttuu koska uusi maksimi on suurempi kuin vanha maksimi
                    minInd = np.argmin( muuttuja_Tdata)
            else:
                minInd = np.argmin( muuttuja_Tdata)



            if maksimi is not None:
                maksimi = max( maksimi,   np.max( muuttuja_Tdata ) )

            else:
                maksimi = np.max( muuttuja_Tdata )

            if minimi is not None:
                minimi = min( minimi,  np.min( muuttuja_Tdata) )
            else:
                minimi = np.min( muuttuja_Tdata )




            longName = datasetti[ muuttuja ].attrs['longname'] + longNamePostfix
            nimi = longName + ' ' + tag + LVLprintFig

            if customLabels:
                label = labelArraySets[i]
            else:
                label = str(i+1)
            label = label + " " + emulatorSims[j]



            fig, ax = mdp.aikasarjaTulostus( muuttuja_Tdata, time_data,  tulostus = tulostus, piirra = piirra, uusikuva = uusikuva, nimi = nimi, xnimi = xlabel, ynimi = ylabel, tightXAxis=tightXAxis, LEGEND=legenda, omavari = colorList[i], label = label )
            uusikuva = False
            #######################
        #print 'muuttuja', muuttuja, 'indeksi min', minInd, 'arvo min', minimi, 'indeksi max', maksInd, 'arvo max', maksimi

            xticksHours = np.arange(0., max(time_data)/3600. + 0.1, 0.5)

            xticks = xticksHours * 3600.

            if xlabels is None:
                xlabels = ['%i' % elem for elem in xticksHours ] #map( str, xticksHours)

            if yticks is not None:
                ax.set_yticks( yticks)


            if ylabels is not None:
                ax.set_yticklabels( ylabels )


            ax.set_xticks( xticks )
            ax.set_xticklabels( xlabels )

            if piilotaOsaXlabel:
                k = 0
                for label in ax.xaxis.get_ticklabels():
                    if np.mod(k,4) != 0:
                        label.set_visible(False)
                    k+=1

            if piilotaOsaYlabel:
                k = 0
                for label in ax.yaxis.get_ticklabels():
                    if np.mod(k,piilotaOsaYlabelParam) != 0:
                        label.set_visible(False)
                    k+=1
            if fontsizeCustom:
                if ((ylabelFont is not None) and (yticks is not None)):
                    for takka in ( ax.xaxis.get_major_ticks() + ax.yaxis.get_major_ticks() ):
                        takka.label.set_fontsize(ylabelFont)

            #if customYscale:
                #ax.set_yscale('symlog', basey=10, linthresy=[0,1])

            if spinup is not None:
                mdp.plot_vertical( spinup )

            #if colorBar is not None and ( omaVari == True):
                #cb = plt.colorbar( colorBar, shrink=.9, pad=.03, aspect=10, ticks = colorBarTickValues )#colorBar
                #cb.ax.set_yticklabels(colorBarTickNames)
                #cb.ax.set_ylabel( tit )

            # jos ymin ja ymax arvoja ei ole ennalta annettu, niin kaytetaan kuvan raja-arvoina laskettuja arvoja
            if ymin is None:
                ymin = minimi

            if ymax is None:
                ymax = maksimi

            if ( asetaRajat ):
                mdp.plot_setYlim( ymin, ymax, extendBelowZero = extendBelowZero)

            if savePrefix is None:
                savePrefix = muuttuja

            if saveFig:
                plt.savefig( picturefolder + savePrefix + "_" + emulatorSims[j] + saveTag + LVLprintSave + '.png')




#######################
def piirra_binijakauma( muuttuja, muunnosKerroin = 1.0, longName = None, savePrefix = None ):

    if longName is None:
        longName = muuttuja

    #for bini in xrange( np.shape(S_Rwiba_data)[1] ):
        #mdp.laske_MeanDiameterInBin( S_Rwiba_data, bini, S_Nc_data, time_data, tulostus = True, piirra =piirra, nimi = 'Mean diameter of ice particles in liquid clouds in bin ' )


#######################
def piirra_domainProfiili( muuttuja, muunnosKerroin = 1.0, transpose = False, longName = None , savePrefix = None, useDN = False, useColorBar = True, colorBarOnly = False, colorBarTickTotalNumber = 10, colorBarTickValues = None, colorBarTickNames = None, colorBarTickValuesInteger = False,  xlabels = None, ylabels = None, xticks = None, yticks = None, variKartta = plt.cm.Blues, profiili = False, radCool = False, cloudBaseTop = False, spinup = None, testi = False, sliceXbeg = None, sliceXend = None, sliceYbeg = None, sliceYend = None, askChangeOfVariable = False, fontsizeCustom = False, legenda = True, hideColorBarLabels = None, showXlabel = True, showYlabel = True ):

    from mpl_toolkits.axes_grid1 import make_axes_locatable
    from matplotlib import colors

    if spinup is None:
        sys.exit("EXIT anna spinup @ piirra_domainProfiili")
    if profiili:
        tiedostonimi = filenamePS
    else:
        tiedostonimi = filenameNC




    norm = None

    maxi = None
    mini = None

    slices = ((sliceXbeg is not None) or (sliceXend is not None) or (sliceYbeg is not None) or (sliceYend is not None)) # slices

    if (sliceXbeg is not None) and (sliceXend is None):
        sliceXend = sliceXbeg
    if (sliceXbeg is None) and (sliceXend is not None):
        sliceXbeg = sliceXend
    if (sliceXbeg is not None) and (sliceXend is None):
        sliceXend = sliceXbeg
    if (sliceXbeg is None) and (sliceXend is not None):
        sliceXbeg = sliceXend

    for i in range(len(tiedostolista)):
        if askChangeOfVariable:
            printti = "Case is "+ arguments[i+1] + ", the variable is currently: " + muuttuja + ' if you want to keep it press [Enter], otherwise give the name of the variable (e.g. prcp/rmH2Opr Nc_ic/CCN): '
            apumuuttuja = input(printti)

            if apumuuttuja != '':
                muuttuja = apumuuttuja
            print('variable is', muuttuja)
            print(' ')

        if EMUL:
            if not EMULCASESCUSTOM:
                case_indeksi = int(filenameNC[i].split("/")[-2][4:])-1
            else:
                case_indeksi = emulCaseIndexes[i]
        else:
            case_indeksi = i
        # Make plot with vertical (default) colorbar
        asp = 20./32.

        #w, h = mpl.figure.figaspect( asp )
        #fig, ax = plt.subplots(figsize = (24,15)) #figsize=(w, h)
        fig, ax = mdp.plot_alustus()
        try:
            muuttuja_data  = np.multiply( mdp.read_Data( tiedostonimi[i], muuttuja ), muunnosKerroin)

            if (np.abs(np.min(muuttuja_data) - np.max(muuttuja_data)) < np.finfo(float).eps ):
                print("NOTE: All data is zero", muuttuja, tiedostonimi[i])
        except KeyError:
            if debug: print("KeyError, variable " + muuttuja + " doesn't exist in " + tiedostonimi[i] )
            continue
        except FileNotFoundError:
            if debug: print("FileNotFoundError", tiedostonimi[i])
            continue

        if useDN:
            dn0           = np.power( mdp.read_Data( filenamePS[i], 'dn0' ),-1)
            muuttuja_data = np.multiply( muuttuja_data, dn0 )

        if profiili:
            muuttuja_meanProfile = muuttuja_data
        elif not profiili:
            muuttuja_meanProfile = np.mean( np.mean( muuttuja_data, axis = 1), axis = 1)
        elif not profiili and slices:
            muuttuja_meanProfile = np.mean( muuttuja_data[:,sliceYbeg:sliceYend+1,sliceXbeg:sliceXend+1,:], axis = 1)


        if testi:
            muuttuja_meanProfile = np.where(mdp.read_Data( tiedostonimi[i], 'P_rl' )*1000. > 0.001, muuttuja_meanProfile, 0.)
            muuttuja_meanProfile = np.where(mdp.read_Data( tiedostonimi[i], 'P_RHi' ) > 1.05, muuttuja_meanProfile, 0.)
            #muuttuja_meanProfile = np.where(muuttuja_meanProfile < 1.05, muuttuja_meanProfile, 0.)

        if transpose:
            muuttuja_meanProfile = np.rot90(muuttuja_meanProfile)  #zip(*muuttuja_meanProfile[::-1])#muuttuja_meanProfile.T

        if maxi is not None:
            maxi = max( maxi,  np.max(muuttuja_meanProfile) )
        else:
            maxi = np.max(muuttuja_meanProfile)

        if mini is not None:
            mini = min( mini,  np.min(muuttuja_meanProfile) )
        else:
            mini = np.min(muuttuja_meanProfile)


        #print 'muuttuja', muuttuja, 'mini', mini, 'maxi', maxi
        if radCool:
            for pp in range(np.shape(muuttuja_meanProfile)[0]):
                for rr in range(1, np.shape(muuttuja_meanProfile)[1]):
                    muuttuja_meanProfile[pp,rr-1] = muuttuja_meanProfile[pp,rr] - muuttuja_meanProfile[pp,rr-1]
                muuttuja_meanProfile[pp,-1] = 0.

            mini = np.min(muuttuja_meanProfile)
            maxi = np.max(muuttuja_meanProfile)

            midpoint = np.abs( mini ) / np.abs( maxi-mini )
            print('midpoint', midpoint)

            apu = (1-midpoint) / midpoint
            start = 0.
            stop  = 1.
            if apu<1.:
                stop  = min( midpoint + apu*(1-midpoint), 1.)
            else:
                start = max( 0, midpoint - (1./apu*midpoint) )
            print('start', start, 'stop', stop)

            variKartta = shiftedColorMap( variKartta, start=start, stop=stop, midpoint = midpoint,   name='shrunk') #

        if colorBarTickValues is None:

            if colorBarTickValuesInteger:
                baseN = 5
                if ( mini < 0 and maxi > 0 ):
                    posi = np.arange( 0., min(10., maxi)+.5,  1. )
                    nega = np.arange( max(-10, mini), 0., 1. )
                    kokonaisluvut = list(map(int, np.arange( int(mini/baseN)*baseN, int(maxi/baseN)*baseN, baseN  )))
                    colorBarTickValues = list(map(int, np.concatenate((np.asarray([int(mini)]), nega, kokonaisluvut, posi, np.asarray([int(maxi)]) )) ))
                else:
                    colorBarTickValues =list(map(int, np.arange( int(mini/baseN)*baseN, int(maxi/baseN)*baseN+baseN, baseN  )))# map(int, np.arange( int(mini), int(maxi), 1  ))
            else:
                colorBarTickValues =[ round(elem, 2) for elem in np.linspace(mini,maxi, colorBarTickTotalNumber) ]

        colorBarWorking = ( len(colorBarTickValues) > 1 and useColorBar )


        #print 'colorbartickvalues', colorBarTickValues
        if isinstance( variKartta, list):
            variKartta[0] = "#FFFFFF"
            variKartta   = colors.ListedColormap(variKartta)
            bounds = colorBarTickValues
            norm   = colors.BoundaryNorm(bounds, variKartta.N)
        print("piirra_domainProfiili max value",muuttuja, np.max(muuttuja_meanProfile), "shape", np.shape(muuttuja_meanProfile))

        cax = ax.imshow( muuttuja_meanProfile, interpolation='nearest', cmap=variKartta, vmin= min(colorBarTickValues), vmax=max(colorBarTickValues), extent=[0, np.shape(muuttuja_meanProfile)[1], 0, np.shape(muuttuja_meanProfile)[0] ],  aspect='auto', norm = norm ) #




        if longName is None:
            longName = muuttuja


        ax.set_title(longName)


        if xticks is None:
            sys.exit("anna xticks")

        #if yticks is None:
            #yticks  = np.arange( np.shape(muuttuja_data)[-1])

        #if xlabels is None:
            #xlabels = map(str,  np.multiply( xticks,  1./3600. ) )
        #if ylabels is None:
            #ylabels = map(str, mdp.read_Data( filenameNC[0], 'zt' )  )

        lukuIndeksi = 0
        lukuSuccess = False
        while(lukuIndeksi < len(tiedostolista) and (not lukuSuccess)):
            try:
                ajat      =  np.round( mdp.read_Data( tiedostonimi[lukuIndeksi], 'time' ), 0 )
                korkeudet =  np.round( mdp.read_Data( filenameNC[lukuIndeksi], 'zt' ), 0 )
                lukuSuccess = True
            except FileNotFoundError:
                lukuIndeksi += 1
        if not lukuSuccess:
            sys.exit("Script was not able to read time or height values")



        oikeatXtikit = np.zeros( ( np.shape( xticks ) ))

        for tt in range(len(xticks)):
            oikeatXtikit[tt] = np.argmin( np.abs(ajat - 3600.*xticks[tt]) )
        oikeatXtikit = oikeatXtikit.astype(int)

        oikeatXleimat = ajat[oikeatXtikit]/3600.
        oikeatXleimat = oikeatXleimat.astype(int)

        ax.set_xticks( oikeatXtikit )
        ax.set_xticklabels( oikeatXleimat )

        k = 0
        for label in ax.xaxis.get_ticklabels():
            if np.mod(k,4) != 0:
                label.set_visible(False)
            k+=1





        if ICE:
            Ytikit = np.arange(0, 1500, 200 )  #np.zeros( ( np.shape( yticks ) ))
        elif EMUL:
            Ytikit = list(map( int, np.arange( 0, max(korkeudet)+101., 100.) ))

        #oikeatYtikit = np.zeros( np.shape(Ytikit))

        #yind = np.arange( np.shape( muuttuja_meanProfile)[0] )


        oikeatYleimat = list(map( str, np.flip(Ytikit)  ))
        #print Ytikit

        #for i in xrange(len(Ytikit)):
            #oikeatYtikit[i] = np.interp( Ytikit[i], korkeudet, yind)
        #print oikeatYtikit

        oikeatYtikit = np.arange( np.shape( muuttuja_meanProfile)[0], 0, -20  )
        ax.set_yticks( oikeatYtikit )
        ax.set_yticklabels( oikeatYleimat )

        #j = 0
        #for label in ax.yaxis.get_ticklabels():
            #if np.mod(j,4) != 0:
                #label.set_visible(False)
            #j+=1

        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixe  at 0.05 inch.
        #divider = make_axes_locatable(ax)
        #cax1 = divider.append_axes("right",  "5%", pad="3%")

        #Add colorbar, make sure to specify tick locations to match desired ticklabels
        #cbar = plt.colorbar(cax,fraction=0.046, pad=0.04, ticks = colorBarTickValues)
        #cbar = fig.colorbar(cax, ticks = colorBarTickValues) # , cax=cax1
        if colorBarWorking:
            print("colorBarTickValues",colorBarTickValues)
            cbar = fig.colorbar(cax, ax=ax, ticks = colorBarTickValues, norm = norm, orientation='horizontal', pad=0.21)#,fraction=0.046, pad=0.04 ###, shrink=.383, pad=.03, aspect=10,

            if colorBarTickNames is None:
                colorBarTickNames = list(map( str, colorBarTickValues))

            cbar.ax.set_yticklabels(colorBarTickNames)  # vertically oriented colorbar
            if fontsizeCustom:
                cbar.ax.tick_params(labelsize=36) #18
                ax.title.set_fontsize(35)

            j = 0
            if hideColorBarLabels is not None:
                for label in cbar.ax.xaxis.get_ticklabels():
                    if np.mod(j, hideColorBarLabels) != 0:
                        label.set_visible(False)
                    j +=1

        spinupIND = np.argmin( np.abs( ajat - spinup ) )
        mdp.plot_vertical( spinupIND )
        if showYlabel:
            plt.ylabel('height [m]')
        if showXlabel:
            plt.xlabel('time [h]')
        plt.tight_layout()


        if savePrefix is None:
            savePrefix = 'domainTimeseriesProfiili'
        if saveFig:
            valitagi = '_'
            if customLabels:
                valitagi = labelArray[i]
            elif applyForAll and not customLabels:
                valitagi = str(case_indeksi+1) + str(i)
            else:
                valitagi = str(case_indeksi+1)
            plt.plot(0,0, label = valitagi)

            if legenda:
                plt.legend(bbox_to_anchor=(0., 1.13, 1., .102), loc=3, ncol=6, fancybox = True, shadow = True , mode="expand" )

            if slices:
                kuvakansio = picturefolder + savePrefix + '_slices/'

                if not os.path.exists( picturefolder ):
                    os.makedirs( picturefolder )

                savePrefix = savePrefix + mdp.xstr(sliceXbeg) + mdp.xstr(sliceXend) + mdp.xstr(sliceYbeg) + mdp.xstr(sliceYend)
            elif EMUL:
                subfolder = picturefolder + '/' + savePrefix + '/'
                if not os.path.exists( subfolder ):
                    os.makedirs( subfolder )

                plt.savefig( subfolder + savePrefix + '_' + valitagi.replace(" ","_") + saveTag + LVLprintSave + '.png')

            else:
            	kuvakansio = picturefolder

            if not EMUL:
                if colorBarOnly:
                    ax.remove()
                plt.savefig( kuvakansio + savePrefix + '_' + muuttuja + '_' + valitagi.replace(" ","_") + saveTag + LVLprintSave + '.png', bbox_inches='tight', pad_inches=0.06)


        if cloudBaseTop:
            top  = mdp.read_Data( filenameTS[i], 'zc'   )
            base = mdp.read_Data( filenameTS[i], 'zb'   )
            aika = mdp.read_Data( filenameTS[i], 'time' )
            zt   = mdp.read_Data( filenamePS[i], 'zt'   )

            pilvi = np.zeros(np.shape(muuttuja_meanProfile))

            for mm in range(np.shape(top)[0]):
                indT = np.argmin( np.abs(  top[ mm ] - zt ))
                indB = np.argmin( np.abs( base[ mm ] - zt ))
                #print 'mm', mm,'base', base[mm], zt[indB], indB, 'top', top[mm], zt[indT], indT

                pilvi[-indT, mm] = 100.
                pilvi[-indB, mm] = 100.
            #asp = 25./45.
            #w, h = mpl.figure.figaspect( asp )
            #fig, ax = plt.subplots(figsize = (24,15)) #figsize=(w, h)
            plt.imshow( pilvi, cmap='Greys',  interpolation='none', alpha= 0.1 )
            #mdp.plottaa( aika, top, uusikuva = True  )
            #mdp.plottaa( aika, base )

###################################################################
def piirra_kokojakauma( muuttujaR = 'S_Rwiba', muuttujaN = 'S_Niba', typename = 'Ice', muunnosKerroinR = 2.e3, korkeusH = None, aikaT = None, xlabel = 'Diameter [mm]', ylabel=r'\#', asetaRajat = True, xmax = None, ymax = None, savePrefix = None, legenda = True, interplo = True, sekoita = True, xCustSize = None, yCustSize = None, askChangeOfVariable = False, fontsizeCustom = False):
    from scipy.interpolate import interp1d
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.ensemble import AdaBoostRegressor
    from random import shuffle
    from math import ceil

    if korkeusH is None:
        korkeusH = int(input("Anna z [m]: "))
    if aikaT is None:
        aikaT = int(input("Anna t [h]: "))



    LKM = len(tiedostolista)
    #fig , ax = mdp.plot_alustus(a=24,b=15*LKM, sub_i = 1, sub_j = LKM, )
    #uusifig = True
    figuuri = None
    for i in range(len(tiedostolista)):

        uusikuva = True

        if askChangeOfVariable:
            printti = "Case is "+ arguments[i+1] + ", the variable is currently: " + muuttujaR + ' if you want to keep it press [Enter], otherwise give the name of the variable (e.g. prcp/rmH2Opr Nc_ic/CCN): '
            apumuuttujaR = input(printti)

            if apumuuttujaR != '':
                muuttujaR = apumuuttujaR
            print('variable is', muuttujaR)
            print(' ')

            printti = "Case is "+ arguments[i+1] + ", the variable is currently: " + muuttujaN + ' if you want to keep it press [Enter], otherwise give the name of the variable (e.g. prcp/rmH2Opr Nc_ic/CCN): '
            apumuuttujaN = input(printti)

            if apumuuttujaN != '':
                muuttujaN = apumuuttujaN
            print('variable is', muuttujaN)
            print(' ')



        if EMUL:
            if not EMULCASESCUSTOM:
                case_indeksi = int(filenameNC[i].split("/")[-2][4:])-1
            else:
                case_indeksi = emulCaseIndexes[i]
        else:
            case_indeksi = i

        dn0_data     = mdp.read_Data( filenameNC[i], 'dn0'     )
        time_data    = mdp.read_Data( filenameNC[i], 'time'    )
        zt_data      = mdp.read_Data( filenameNC[i], 'zt'      )

        Radius_data = mdp.read_Data( filenameNC[i], muuttujaR )
        Number_data = mdp.read_Data( filenameNC[i], muuttujaN  )

        t =  np.argmin(np.abs(aikaT*3600-time_data))
        z =  np.argmin(np.abs(korkeusH-zt_data))


        maksimi = np.max( Number_data )

        ysize = np.shape(Radius_data)[2]
        xsize = np.shape(Radius_data)[3]

        Diameter_data = Radius_data[t,:,:,:,z]* muunnosKerroinR
        Number_data  = Number_data[t,:,:,:,z]* dn0_data[z]


        Diameter_data_flatten = Diameter_data.flatten()
        Number_data_flatten  = Number_data.flatten()

        jarj = np.argsort(Diameter_data_flatten)

        Diameter_data_flatten = np.reshape( np.sort(Diameter_data_flatten) , (-1,1) )
        koko =  np.shape(Number_data_flatten)
        apu = np.zeros(koko)

        for kkk in range(koko[0]):
            apu[kkk] = Number_data_flatten[ jarj[kkk] ]

        Number_data_flatten = np.reshape(apu, (-1,1))

        ### decision tree regression
        xnew = np.linspace(np.min(Diameter_data_flatten),np.max(Diameter_data_flatten), 1000, endpoint = True)[:,np.newaxis]

        rng = np.random.RandomState(1)
        regr_2 = AdaBoostRegressor(DecisionTreeRegressor(max_depth=4),n_estimators=500, random_state=rng)
        regr_2.fit(Diameter_data_flatten, Number_data_flatten)
        y_2 = regr_2.predict(xnew)
        ### end decision tree regression



        #if customLabels:
                #label = labelArray[i]
         #else:
                #label = str(case_indeksi+1)
        #else:

        label = labelArray[i]

        #tit = typename + ' size distribution, slize t = ' + str(round(time_data[t]/3600.,1)) + ' [h], h = ' + str(zt_data[z]) + ' [m] ' + label
        tit ='slize t = ' + str(round(time_data[t]/3600.,1)) + ' [h], h = ' + str(zt_data[z]) + ' [m] ' + label
        if xCustSize is None:
            xlist = list(range(xsize))
        else:
            a = xCustSize/2
            b = xCustSize - a
            xlist = list(map(int, np.arange( ceil(int(xsize/2)-a+.1), ceil(int(xsize/2)+b+.1),1)))

        if yCustSize is None:
            ylist = list(range(ysize))
        else:
            a = yCustSize/2
            b = yCustSize - a
            ylist = list(map(int, np.arange( ceil(int(ysize/2)-a+.1), ceil(int(ysize/2)+b+.1),1)))

        print('kokojakauma x ja y indeksit', xlist, ylist)
        mdp.initializeColors(len(xlist)*len(ylist), shuffling = sekoita)

        oikeatXtikit = np.arange( 0, xmax+0.01,  0.2)
        for x in xlist:
            for y in ylist:
                if figuuri is None:
                    uusifig = True
                else:
                    uusifig = False
                    ylabel = ' '

                fig, ax =  mdp.plottaa(Diameter_data[:,y,x], Number_data[:,y,x],xl=xlabel, yl=ylabel, tit = '', uusikuva = uusikuva, scatter = True, LEGEND = False, tightXAxis = True, tightYAxis = True, gridi = False, sub_i = 1, sub_j = LKM, sub_k = i+1, figuuri = None, uusisub = True, uusifig = uusifig )

                figuuri = fig
                ax.title.set_text(tit)
                if fontsizeCustom:
                    ax.title.set_fontsize(22)


                ax.set_xticklabels( list(map(str, oikeatXtikit )))
                ax.set_xticks( oikeatXtikit )

                j = 0
                for xxlabel in ax.xaxis.get_ticklabels():
                    if np.mod(j-1,4) != 0 or j == 0:
                    #if j==0:
                        xxlabel.set_visible(False)
                    j+=1
                xxlabel.set_visible(True)
                if i > 0:
                    for yylabel in ax.yaxis.get_ticklabels():
                        yylabel.set_visible(False)


        if interplo:
            mdp.plottaa(xnew, y_2,xl=xlabel, yl=ylabel, tit = '', uusikuva = uusikuva, omavari='k', LEGEND = False, sub_i = 1, sub_j = LKM, sub_k = i+1)

        figuuri.suptitle( typename + ' size distribution') #, fontsize=45


        # jos ymin ja ymax arvoja ei ole ennalta annettu, niin kaytetaan kuvan raja-arvoina laskettuja arvoja
        if ymax is None:
            ymax = maksimi

        if xmax is None:
            xmax = np.max(Diameter_data_flatten)

        if ( asetaRajat ):
            plt.ylim( 0., 1.1*ymax )
            plt.xlim( 0., xmax )










    if savePrefix is None:
        savePrefix = typename+ '_size_distribution'

    if saveFig:
        plt.savefig( picturefolder + savePrefix  + saveTag+ '_'+ str(round(time_data[t]/3600.,1)) + 'h_' + str(zt_data[z]) + 'm' + LVLprintSave + '.png')



###########################
#### NEEDS REVISION BIG TIME (INTERPOLATION)
######################
def piirra_hiukkausjakauma( tyyppi = 'ice', bini='a', ajanhetket = [0], korkeus = [0], useDN = True, color = 'b', savePrefix = None   ):
    from scipy.stats.mstats import gmean
    if tyyppi not in ['aerosol', 'cloud', 'precipitation', 'ice', 'snow' ]:
        sys.exit("wrong type")

    tyyppi1 = tyyppi[0:1]
    tyyppi2 = tyyppi[0:2]

    NumBin_name     = 'S_N'    + tyyppi1 + 'b' + bini
    RadBin_name     = 'S_Rw'   + tyyppi1 + 'b' + bini
    #SizBin_name =  tyyppi2 + bini



    for i in range(len(tiedostolista)):
        NumBin  = mdp.read_Data( filenameNC[i], NumBin_name)
        RadBin  = mdp.read_Data( filenameNC[i], RadBin_name)
        #SizBin = mdp.read_Data( filenameNC[i], SizBin_name)

        if useDN:
            dn0    = mdp.read_Data( filenameNC[i], 'dn0' )
            NumBin = np.multiply( NumBin, dn0 )

        ######### aika slaissaus
        time = mdp.read_Data( filenameNC[i], 'time')
        aikaindeksit = []
        for t in ajanhetket:
            aikaindeksit.append( np.argmin( np.abs(time - t*3600.) ))

        Tslize = tuple(( int, np.arange( min(aikaindeksit), max(aikaindeksit)+0.5 ) ))

        TslizeSTR = r'$t_0$' + ' = ' + str( time[ min(aikaindeksit) ]/3600. )
        if len(aikaindeksit)>0:
            TslizeSTR += ' ' + r'$t_1$' + ' = ' + str( time[ max(aikaindeksit) ]/3600. )
        print(TslizeSTR)
        ###############################

        ######### korkeus slaissaus
        zt = mdp.read_Data( filenameNC[i], 'zt')
        korkeusindeksit = []
        for h in korkeus:
            korkeusindeksit.append( np.argmin( np.abs(zt - h) ))

        Hslize = tuple(( int, np.arange( min(korkeusindeksit), max(korkeusindeksit)+0.5 ) ))

        HslizeSTR = r'$h_0$' + ' = ' + str( zt[ min(korkeusindeksit) ] )
        if len(korkeusindeksit)>0:
            HslizeSTR += + ' ' + r'$h_1$' + ' = ' + str( zt[ max(korkeusindeksit) ] )
        #print HslizeSTR
        #####################

        NumBinSlize  = NumBin[ Tslize, :, :, :, Hslize ]
        RadBinSlize  = RadBin[ Tslize, :, :, :, Hslize ]

        if len(Tslize)>1:
            print('Tslize pituus', len(Tslize))
            NumBinSlize = np.mean( NumBinSlize, axis = 0 )
            RadBinSlize = np.mean( RadBinSlize, axis = 0 )
        if len(Hslize)>1:
            print('Hslize pituus', len(Hslize))
            NumBinSlize = np.mean( NumBinSlize, axis = -1 )
            RadBinSlize = np.mean( RadBinSlize, axis = -1 )


        NumBinSlizeMean  = gmean( gmean(NumBinSlize, axis=1), axis=1) # #/L
        DiaBinSlizeMean  = gmean( gmean(RadBinSlize, axis=1), axis=1)*1000.*2. #  m -> mm, radius -> diameter


        tit = tyyppi + ' ' + TslizeSTR + ' ' + HslizeSTR

        mdp.plot_alustus()
        mdp.plottaa( SizBin, NumBinSlizeMean/DiaBinSlizeMean, tit , 'Diameter [mm]', r'$dN/dP(L^{-1}mm^{-1})$', log = True, changeColor=False, tightXAxis=True, markers=True, LEGEND=True, omavari = color, scatter=False )

    if savePrefix is None:
        savePrefix = 'Hiukkasjakauma'
    if saveFig:
        plt.savefig( picturefolder + savePrefix+ saveTag + LVLprintSave + '.png')

###########################
def piirra_MeanSize( tyyppi = 'ice', bini='a', ajanhetket = [0], korkeus = [0], useDN = True, color = 'b', savePrefix = None   ):
    from scipy.stats.mstats import gmean
    if tyyppi not in ['aerosol', 'cloud', 'precipitation', 'ice', 'snow' ]:
        sys.exit("wrong type")

    tyyppi1 = tyyppi[0:1]
    tyyppi2 = tyyppi[0:2]

    Rad_name = 'S_Rw'   + tyyppi1  + bini

    Num_name = 'S_N'   + tyyppi1

    print(tyyppi, Rad_name, Num_name)


    for i in range(len(tiedostolista)):
        Num  = np.multiply( mdp.read_Data( filenameNC[i], Num_name), 1./1000. )
        Rad  = mdp.read_Data( filenameNC[i], Rad_name)


        if useDN:
            dn0 = mdp.read_Data( filenameNC[i], 'dn0' )
            Num = np.multiply( Num, dn0 )

        ######### aika slaissaus
        time = mdp.read_Data( filenameNC[i], 'time')
        aikaindeksit = []
        for t in ajanhetket:
            aikaindeksit.append( np.argmin( np.abs(time - t*3600.) ))

        Tslize = tuple(( int, np.arange( min(aikaindeksit), max(aikaindeksit)+0.5 ) ))

        TslizeSTR = r'$t_0$' + ' = ' + str( time[ min(aikaindeksit) ]/3600. )
        if len(aikaindeksit)>0:
            TslizeSTR += ' ' + r'$t_1$' + ' = ' + str( time[ max(aikaindeksit) ]/3600. )
        print(TslizeSTR)
        ###############################

        ######### korkeus slaissaus
        zt = mdp.read_Data( filenameNC[i], 'zt')
        korkeusindeksit = []
        for h in korkeus:
            korkeusindeksit.append( np.argmin( np.abs(zt - h) ))

        Hslize = tuple(( int, np.arange( min(korkeusindeksit), max(korkeusindeksit)+0.5 ) ))

        HslizeSTR = r'$h_0$' + ' = ' + str( zt[ min(korkeusindeksit) ] )
        if len(korkeusindeksit)>0:
            HslizeSTR +=  ' ' + r'$h_1$' + ' = ' + str( zt[ max(korkeusindeksit) ] )
        print(HslizeSTR)
        #####################

        NumSlize  = Num[ Tslize,  :, :, Hslize ]
        RadSlize  = Rad[ Tslize,  :, :, Hslize ]

        if len(Tslize)>1:
            NumSlize = np.mean( NumSlize, axis = 0 )
            RadSlize = np.mean( RadSlize, axis = 0 )
        if len(Hslize)>1:
            NumSlize = np.mean( NumSlize, axis = -1 )
            RadSlize = np.mean( RadSlize, axis = -1 )


        #NumSlizeMean     = np.mean( np.mean(NumSlize, axis=1), axis=1) # #/L
        #DiaBinSlizeMean  = np.mean( np.mean(RadSlize, axis=1), axis=1)*1000.*2. #  m -> mm, radius -> diameter
        DiaBinSlize = RadSlize*1000.*2. #  m -> mm, radius -> diameter

        DwiAvg = np.mean( sum( DiaBinSlize * NumSlize ) / sum( NumSlize ) )
        NumAvg = np.mean( NumSlize )

        print('DwiAvg', DwiAvg, 'NumAvg/DwiAwg', NumAvg/DwiAvg)
        tit = tyyppi + ' ' + TslizeSTR + ' ' + HslizeSTR

        #mdp.plot_alustus()
        #mdp.plottaa( SizBin, NumSlizeMean/DiaBinSlizeMean, tit , 'Diameter [mm]', r'$dN/dP(L^{-1}mm^{-1})$', log = True, changeColor=False, tightXAxis=True, markers=True, LEGEND=True, omavari = color, scatter=False )
    #if savePrefix is None:
        #savePrefix = 'MeanSize'
    #if saveFig:
        #plt.savefig( picturefolder + savePrefix+ saveTag + LVLprintSave + '.png')

#############################
def piirra_domainMeanProfiili( muuttuja, muuttujaPainotus =  'S_Niba', muuttujaPainotusPotenssi =  'S_Rwiba', nimi = None, muunnosKerroin = 1.0, ajanhetket = [0], useDN = True, profiili = False, binidata = False, xAxisL = '', color = 'k', savePrefix = None, akselit = False, xmax = None, askChangeOfVariable = False, fontsizeCustom = False   ):

    minimi  = None
    maksimi = None

    if nimi is None:
        nimi = muuttuja

    if profiili:
        tiedostonimi = filenamePS
    elif (not profiili)  or binidata:
        tiedostonimi = filenameNC

    for i in range(len(tiedostolista)):
        uusikuva = True if i == 0 else  False
        if askChangeOfVariable:
            printti = "Case is "+ arguments[i+1] + ", the variable is currently: " + muuttuja + ' if you want to keep it press [Enter], otherwise give the name of the variable (e.g. prcp/rmH2Opr Nc_ic/CCN): '
            apumuuttuja = input(printti)
            if apumuuttuja != '':
                muuttuja = apumuuttuja
            print('variable is', muuttuja)
            print(' ')

            printti = "Case is "+ arguments[i+1] + ", the muuttujaPainotus is currently: " + muuttujaPainotus + ' if you want to keep it press [Enter], otherwise give the name of the variable (e.g. prcp/rmH2Opr Nc_ic/CCN): '
            muuttujaPainotusApu = input(printti)
            if muuttujaPainotusApu != '':
                muuttujaPainotus = muuttujaPainotusApu
            print('muuttujaPainotus is', muuttujaPainotus)
            print(' ')

            printti = "Case is "+ arguments[i+1] + ", the muuttujaPainotus is currently: " + muuttujaPainotusPotenssi + ' if you want to keep it press [Enter], otherwise give the name of the variable (e.g. prcp/rmH2Opr Nc_ic/CCN): '
            muuttujaPainotusPotenssiApu = input(printti)
            if muuttujaPainotusPotenssiApu != '':
                muuttujaPainotusPotenssi = muuttujaPainotusPotenssiApu
            print('muuttujaPainotus is', muuttujaPainotusPotenssi)
            print(' ')

        data  = np.multiply( mdp.read_Data( tiedostonimi[i], muuttuja), muunnosKerroin )
        zt    = np.asmatrix( mdp.read_Data( tiedostonimi[i], 'zt') )

        dn0 = mdp.read_Data( tiedostonimi[i], 'dn0' )
        if useDN:
            data = np.multiply( data, dn0 )


        ######### aika slaissaus
        time = mdp.read_Data( filenameNC[i], 'time')
        aikaindeksit = []
        for t in ajanhetket:
            aikaindeksit.append( np.argmin( np.abs(time - t*3600.) ))

        Tslize = tuple(( int, np.arange( min(aikaindeksit), max(aikaindeksit)+0.5 ) ))

        TslizeSTR = r'$t_{0} = $' + str( round( time[ min(aikaindeksit) ]/3600.,1) ) + ' h'
        if len(aikaindeksit)>0:
            TslizeSTR += ' to ' + r'$t_{1} = $' + str( round( time[ max(aikaindeksit) ]/3600.,1) ) + ' h'

            TslizeSTR = 'from ' + TslizeSTR
        else:
            TslizeSTR = 'at ' + TslizeSTR
        #print TslizeSTR
        ###############################

        if profiili:
            dataSlize  = data[ Tslize,   : ]
        elif binidata:
            dataSlize  = data[ Tslize, :, :, :, : ]
        elif not profiili:
            dataSlize  = data[ Tslize, :, :, : ]

        if len(Tslize)>1:
            dataSlize = np.mean( dataSlize, axis = 0 )

        if profiili:
            dataSlizeMean = dataSlize
        elif binidata:
            from math import pi
            rho = 44.2*6./pi
            painotus =  np.multiply( mdp.read_Data( tiedostonimi[i], muuttujaPainotus), np.multiply( np.power(mdp.read_Data( tiedostonimi[i], muuttujaPainotusPotenssi ),3), dn0*44.2) )
            painotusSlize = painotus[ Tslize, :, :, :, : ]
            if len(Tslize)>1:
                painotusSlize = np.mean( painotusSlize, axis = 0 )

            nimittaja = np.sum( np.sum( np.sum(painotusSlize, axis = 0), axis= 0), axis=0 )
            nimittaja = np.where( nimittaja > 0.,  np.power(nimittaja, -1), 0.)

            osoittaja = np.sum( np.sum( np.sum(np.multiply(dataSlize, painotusSlize), axis = 0), axis= 0), axis=0 )

            dataSlizeMean = np.multiply( osoittaja, nimittaja)
        elif not profiili:
            dataSlizeMean = np.mean( np.mean( dataSlize, axis = 0), axis = 0)

        tit = nimi + ' ' + TslizeSTR

        if maksimi is not None:
            maksimi = max( maksimi,  np.max(dataSlizeMean) )
        else:
            maksimi = np.max(dataSlizeMean)

        if minimi is not None:
            minimi = min( minimi,  np.min(dataSlizeMean) )
        else:
            minimi = np.min(dataSlizeMean)

        dataSlizeMean = np.asmatrix(dataSlizeMean)

        if EMUL:
            if customLabels:
                label = labelArray[i]
            else:
                label = str(case_indeksi+1)
        else:
            label = labelArray[i]

        fig, ax = mdp.plottaa( dataSlizeMean.A1, zt.A1, tit , xl = xAxisL, yl='height [m]', changeColor=True, tightXAxis=True, tightYAxis = True, markers=False, LEGEND=True, label = label, omavari = color, scatter=False, uusikuva=uusikuva )
    if fontsizeCustom:
        ax.title.set_fontsize(35)
    mdp.plot_setXlim( minimi, maksimi, extendBelowZero = False, A = 0.05 )

    if akselit or (xmax is not None):
        if xmax is None:
            xmax = np.max(dataSlizeMean)

        oikeatXtikit = list(map(int, np.arange( 0, xmax+0.01,  50)))
        ax.set_xticklabels( list(map(str, oikeatXtikit )))
        ax.set_xticks( oikeatXtikit )

    if savePrefix is None:
        savePrefix = 'domainMeanProfiili'

    if saveFig:
        plt.savefig( picturefolder + savePrefix+ '_' + muuttuja + saveTag + LVLprintSave + '.png')

def piirra_domainMeanScatter( muuttujaX, muuttujaY, muuttujaYY = None, muunnosKerroinX = 1.0, muunnosKerroinY = 1.0, muunnosKerroinYY = 1.0, nimi = None, ajanhetket = [0], useDNX = False,useDNY = False, profiiliX = False, profiiliY = False, xaxislabel = None, yaxislabel = None, color = None, savePrefix = None, minimiX =  None, maksimiX = None, minimiY =  None, maksimiY = None, fontsizeCustom =False    ):

    minimi  = None
    maksimi = None

    if nimi is None:
        nimi = muuttujaX + muuttujaY + mdp.xstr(muuttujaYY)

    #if profiiliX:
        #tiedostonimiX = filenamePS
    #else:
        #tiedostonimiX = filenameNC

    #if profiiliY:
        #tiedostonimiY = filenamePS
    #else:
        #tiedostonimiY = filenameNC

    varit = cycle( ['b','r','k','g','c','m','y'][:(len(tiedostolista))] )

    if (len(tiedostolista))>7:
        changeColor = True
        color = False
    else:
        changeColor = False
        color = True

    for i in range(len(tiedostolista)):
        uusikuva = True if i == 0 else  False
        dataX  = np.multiply( mdp.read_Data( filenameTS[i], muuttujaX), muunnosKerroinX )
        dataY  = np.multiply( mdp.read_Data( filenameTS[i], muuttujaY), muunnosKerroinY )



        if muuttujaYY is not None:
            dataY = dataY + np.multiply( mdp.read_Data( filenameTS[i], muuttujaYY), muunnosKerroinYY )

        #zt    = np.asmatrix( mdp.read_Data( tiedostonimi[i], 'zt') )
        if useDNX:
            dn0  = mdp.read_Data( filenameTS[i], 'dn0' )
            dataX = np.multiply( dataX, dn0 )

        if useDNY:
            dn0   = mdp.read_Data( filenameTS[i], 'dn0' )
            dataY = np.multiply( dataY, dn0 )


        ######### aika slaissaus
        time = mdp.read_Data( filenameTS[i], 'time')
        aikaindeksit = []
        for t in ajanhetket:
            aikaindeksit.append( np.argmin( np.abs(time - t*3600.) ))

        Tslize = tuple(( int, np.arange( min(aikaindeksit), max(aikaindeksit)+0.5 ) ))

        TslizeSTR = r'$t_{0} = $' + str( round( time[ min(aikaindeksit) ]/3600.,1) ) + ' h'
        if len(aikaindeksit)>0:
            TslizeSTR += ' to ' + r'$t_{1} = $' + str( round( time[ max(aikaindeksit) ]/3600.,1) ) + ' h'

            TslizeSTR = 'from ' + TslizeSTR
        else:
            TslizeSTR = 'at ' + TslizeSTR
        print(' ')
        print(TslizeSTR)
        ###############################
        dataX = np.where( dataX > -999.,  dataX, 0. )
        dataY = np.where( dataY > -999.,  dataY, 0. )

        dataSlizeX  = dataX[ Tslize ]
        dataSlizeY  = dataY[ Tslize ]

        if len(Tslize)>1:
            dataSlizeMeanX = np.mean( dataSlizeX, axis = 0 )

        if len(Tslize)>1:
            dataSlizeMeanY = np.mean( dataSlizeY, axis = 0 )



        tit = nimi + ' ' + TslizeSTR

#        if maksimi is not None:
#            maksimi = max( maksimi,  np.max(dataSlizeMean) )
#        else:
#            maksimi = np.max(dataSlizeMean)
#
#       if minimi is not None:
#            minimi = min( minimi,  np.min(dataSlizeMean) )
#        else:
#            minimi = np.min(dataSlizeMean)
#
#        dataSlizeMean = np.asmatrix(dataSlizeMean)

#        if EMUL:
#            if customLabels:
#                label = labelArray[i]
#            else:
#                label = str(case_indeksi+1)
#        else:
#            label = labelArray[i]
        if color is not False:
            color = next(varit)

        print('case', filenameTS[i], 'muuttujaX', muuttujaX, 'dataSlizeMeanX', dataSlizeMeanX, 'dataSlizeMeanY', dataSlizeMeanY, 'color', color)

        fig, ax = mdp.plottaa( dataSlizeMeanX, dataSlizeMeanY, a = 20, b = 20, tit = tit , xl = xaxislabel, yl = yaxislabel, changeColor=changeColor, tightXAxis=True, tightYAxis = True, LEGEND=False, omavari = color, scatter=True, uusikuva=uusikuva, marker= '+', markersize = 90, fontsizeCustom = fontsizeCustom )

        if fontsizeCustom:
            ax.title.set_fontsize(35)

        if (minimiX is not None) and (maksimiX is not None):
            plt.xlim( minimiX, maksimiX )

        if (minimiY is not None) and (maksimiY is not None):
            plt.ylim( minimiY, maksimiY )

        if savePrefix is None:
            savePrefix = 'scatterSlize'

        if saveFig:
            plt.savefig( picturefolder + savePrefix+ '_' + muuttujaX + muuttujaY + saveTag + LVLprintSave + '.png')

def animoi_path(muuttuja, muunnosKerroin = 1.0, transpose = False, longName = None , savePrefix = None, useDN = False, colorBarTickValues = [0,1], colorBarTickNames = ['0','1'], xlabels = None, ylabels = None, xticks = None, yticks = None, variKartta = plt.cm.Blues, profiili = False, spinup = None ):

    import matplotlib.animation as animation
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    from matplotlib import colors
    from itertools import cycle

    if profiili:
        tiedostonimi = filenamePS
    else:
        tiedostonimi = filenameNC


    if isinstance( variKartta, list):
        variKartta   = colors.ListedColormap(variKartta)
        bounds = colorBarTickValues
        norm   = colors.BoundaryNorm(bounds, variKartta.N)
    else:
        norm = None


    # Make plot with vertical (default) colorbar
    asp = 1.
    w, h = mpl.figure.figaspect( asp )
    fig, ax = plt.subplots(figsize = (24,15)) #figsize=(w, h)

    def onClick(event):
        global pause
        pause ^= True

    #for i in xrange(len(tiedostolista)):
    global muuttuja_meanDomain
    if (len(tiedostolista))>1:
        sys.exit("animation doesn't work at the moment with multiple arguments")


    muuttuja_data  = np.multiply( mdp.read_Data( tiedostonimi[0], muuttuja ), muunnosKerroin)
    dn0_data = mdp.read_Data( filenameNC[0], 'dn0'    )
    zt_data       = mdp.read_Data( filenameNC[0], 'zt'     )
    zm_data       = mdp.read_Data( filenameNC[0], 'zm'     )
    korkeus = ( zm_data - zt_data )*2.0

    dn0Kork  = dn0_data * korkeus

    muuttuja_meanDomain = np.sum( muuttuja_data * dn0Kork, axis = -1 )

    print('muoto txyz', np.shape(muuttuja_data))
    print('muoto txy', np.shape(muuttuja_meanDomain))



    if transpose:
        muuttuja_meanDomain = np.rot90(muuttuja_meanDomain)  #zip(*muuttuja_meanDomain[::-1])#muuttuja_meanDomain.T

    data = muuttuja_meanDomain[0,:,:]




    def simData():
        ajat  =  np.round( mdp.read_Data( filenameNC[0], 'time' ), 0 )
        indeksijoukko = cycle( np.arange(np.shape(muuttuja_meanDomain)[0]) )
        t_max = ajat[-1]
        dt = ajat[2]-ajat[1]
        t = 0.0

        while t < t_max:
            if not pause:
                k = next(indeksijoukko)
                data = muuttuja_meanDomain[k,:,:]
                t = t + dt

            yield data, t

    def simPoints(simData):
        data, t = simData[0], simData[1]
        time_text.set_text(time_template%(t))
        cax.set_array( data )
        return cax, time_text

    global pause
    pause = False

    cax = ax.imshow( [[],[]] , interpolation='nearest', cmap=variKartta, aspect=asp, norm = norm, animated=True )

    if longName is None:
        longName = muuttuja

    ax.set_title(longName)

    xt = mdp.read_Data( filenameNC[0], 'xt'     )
    oikeatXtikit = np.arange( np.shape( data)[1], 0, -20  )
    ax.set_yticks( oikeatXtikit  )
    ax.set_xticklabels( list(map(str, xt)) )

    h = 0
    for label in ax.xaxis.get_ticklabels():
        if np.mod(h,20) != 0:
            label.set_visible(False)
        h+=1


    yt = mdp.read_Data( filenameNC[0], 'yt'     )

    oikeatYtikit = np.arange( np.shape(data)[0], 0, -20  )
    ax.set_yticks( oikeatYtikit  )
    ax.set_yticklabels( list(map(str, yt)) )

    j = 0
    for label in ax.yaxis.get_ticklabels():
        if np.mod(j,6) != 0:
            label.set_visible(False)
        j+=1


    # Add colorbar, make sure to specify tick locations to match desired ticklabels
    cbar = fig.colorbar(cax, ax=ax, shrink=.45, pad=.03, aspect=10, ticks = colorBarTickValues, norm = norm)
    cbar.ax.set_yticklabels(colorBarTickNames)

    time_template = 'Time = %.1f s'
    time_text = ax.text(-1.00, 0.9, '', transform=ax.transAxes )
    fig.canvas.mpl_connect('button_press_event', onClick)
    ani = animation.FuncAnimation(fig, simPoints, simData, blit=False, interval=10, repeat=True)


##############################
#
# drawing STYLES
#
# parameter settings
#
##############################
if __name__ == "__main__":

    aika_color      = mdp.truncate_colormap(  plt.cm.Blues, minval = 0.3)
    aikaPisteet     = xTicksSeconds
    aikaBAR         = varibaari( aikaPisteet,  aika_color)
    aikaTIT         = 'time [h]'
    cbvalT          =  xTicksSeconds
    cbvalTStr       = list(map(str, ticksHours))
    fontsizeCustom  = False
if EMUL:
    CFRAC = True
    CLOUD = True
    PRCP  = True
    LWP   = True
    SHF   = False
    LHF   = False
    QDIFF = True
    TDIFF = True
    CDNC  = True
    WMAX  = False
    W2    = False
    RAD   = False
    RH    = False
    refColorbarSwitch = True
    askChangeOfVariable = False


    #CFRAC = False
    #CLOUD = True
    #PRCP  = False
    #LWP   = False
    #SHF   = False
    #LHF   = False
    #QDIFF = False
    #TDIFF = False
    #CDNC  = False
    #WMAX  = False
    #W2    = False
    #RAD   = False
    #RH    = False

    PROFKEHITYS = False

    NCFwrite = False
    emulatorname = False
    if generateEmulFilelist:
        emulatorname = emulatorSets[0]
    else:
        emulatorname = os.getcwd().split("/")[-1]

    print(" ")
    #print 'emulatorname', emulatorname
    vers = emulatorname[21:27]
    DesignBool = bool(re.match('v[0-9].[0-9].[0-9]',vers))
    if DesignBool:
        design_input = 'Do you want to give an other design version other than: ' + vers + ' (yes/no)? '
        designLogical = not setupFunction( design_input, kylla)
    else:
        designLogical = False

    if not designLogical:
        vers= str( setupFunction( 'Give a design (esim: v1.5.1 ): '))

    if int(lvl) < 4:
        CDNC = False
        prcp = 'prcp'
        sadekerroin = 2.5e-06
        liqW='l'
    else:
        prcp = 'rmH2Opr'
        sadekerroin = 1. # latent heat of vaporization J/kg
        liqW = 'P_rl'



    maksimisateet   = np.zeros(cases)

    maksimiLatent   = np.zeros(cases)

    maksimiSensible = np.zeros(cases)

    maksimiLWPlist  = np.zeros(cases)

    designroot = ibrix + '/DESIGN/'

    cwd = os.getcwd()

    os.chdir(designroot)


    thickness_color = plt.cm.gist_rainbow #Paired Blues
    pblh_color      = plt.cm.cool
    num_pbl_color   = plt.cm.Wistia


    for file in glob.glob("*.csv"):
        designbasename=file

    filu = designroot + designbasename
    os.chdir(cwd)



    #####################
    ncfolder = ibrix+'/DESIGNnetcdf/'
    print("DESIGN VERSION", vers)
    ncfilename = ncfolder + 'design_'+vers + '.nc'
    print('ncfilename', ncfilename)
    try:
        ncfile = Dataset( ncfilename, 'r+' )
    except FileNotFoundError:
        try:
            ncfolder = ibrix+'/DESIGNnetcdf/' + vers + "/"
            ncfilename = ncfolder + 'design_'+vers + '.nc'
            ncfile = Dataset( ncfilename, 'r+' )
        except FileNotFoundError:
            sys.exit("Design netCDF-file was not found, exiting")



    q_inv_design     = ncfile.variables['q_inv'][:]
    tpot_inv_design  = ncfile.variables['tpot_inv'][:]
    clw_max_design   = ncfile.variables['clw_max'][:]
    tpot_pbl_design  = ncfile.variables['tpot_pbl'][:]
    pblh_design      = ncfile.variables['pblh'][:]
    q_pbl_design     = ncfile.variables['q_pbl'][:]
    cloudbase_design = ncfile.variables['cloudbase'][:]
    thickness_design = ncfile.variables['thickness'][:]

    try:
        num_pbl_design   = ncfile.variables['num_pbl'][:]

    except KeyError:
        try:
            print("Explicit aerosol")
            num_ks_design   = ncfile.variables['num_as'][:]
            num_as_design   = ncfile.variables['num_ks'][:]
            num_cs_design   = ncfile.variables['num_cs'][:]

            num_pbl_design  = num_ks_design + num_as_design + num_cs_design
            print(num_pbl_design)
        except KeyError:
            sys.exit("No aerosol/cdnc values available in the netcdf")




    ##########
    thickBAR = varibaari( thickness_design, thickness_color )
    pblhBAR  = varibaari( pblh_design,      pblh_color      )
    cdncBAR  = varibaari( num_pbl_design,    num_pbl_color   )

    thickTIT = 'cloud thickness'
    pblhTIT  = 'PBL height'
    cdncTIT  = r'CDNC \#/mg'



    cbvalThick =  list(map( int, np.arange( myRound(min(thickness_design), 100),  myRound(max(thickness_design), 100), 100.) ))  #map( int, np.arange( 0, myRound( max(thickness_design), 200 ), 200.) )
    cbvalThickStr = list(map( str, cbvalThick ))

    cbvalPblh = list(map( int, np.arange( myRound(min(pblh_design), 100),  myRound(max(pblh_design), 100), 200.) ))
    cbvalPblhStr = list(map( str, cbvalPblh ))

    cbvalQ = list(map(int, np.arange( 0, max(num_pbl_design), 50.) ))
    cbvalQStr = list(map( str, cbvalQ ))




    zcTicks = np.arange(0.8, 2.45, 0.2)
    zcTicksStr = list(map( str, zcTicks))


    ##########

    #mdp.plot_alustus()

    # thickness histogram
    #plt.hist(thickness_design, 20, normed=1, facecolor='green', alpha=0.75)
    # thickBAR
    if int(lvl) > 0:
        if CFRAC:
            piirra_aikasarjasettii( muuttuja = 'cfrac',  variRefVektori = thickness_design, colorBar =  thickBAR, colorBarTickValues = cbvalThick, colorBarTickNames = cbvalThickStr, longName= 'Cloud fraction',               ylabel = 'Cloud fraction',      variKartta = thickness_color, ymin = 0.0, ymax = 1.0, tit = thickTIT, spinup = spinup, xlabels = xLabelsHours, xticks = xTicksSeconds, omaVari = refColorbarSwitch, legenda = LEGEND, tallenna = False )

            mdp.plot_suljetus( not naytaPlotit)

        if CLOUD:
            piirra_aikasarjasettii( muuttuja = 'zc',     variRefVektori = thickness_design, colorBar =  thickBAR, colorBarTickValues = cbvalThick, colorBarTickNames = cbvalThickStr, longName= 'Relative change of cloud top', ylabel = 'relative change',     variKartta = thickness_color, relative = True, savePrefix = 'cloud_top_rel_change', tit = thickTIT, spinup = spinup, xlabels = xLabelsHours, xticks = xTicksSeconds, yticks = zcTicks, omaVari = refColorbarSwitch, legenda = LEGEND  )

            mdp.plot_suljetus( not naytaPlotit)

            if PROFKEHITYS:
                piirra_profiiliKehitys( liqW, muunnosKerroin = 1000.0, variKartta = aika_color, colorBar = aikaBAR, colorBarTickValues = cbvalT, colorBarTickNames = cbvalTStr, longName =  'Cloud ' + r'$H_2{O}$' + ' mix. rat. evolution', xlabel = 'q_cloud [g/kg]', ylabel = 'z [m]', savePrefix = 'q_cloud_evol', aikaPisteet = aikaPisteet, tit = aikaTIT, rajaKerros = pblh_design, asetaRajat = False, paksuus = thickness_design, askChangeOfVariable = askChangeOfVariable )

                mdp.plot_suljetus( not naytaPlotit)

        if PRCP:
            piirra_aikasarjasettii( muuttuja = prcp,     muunnosKerroin = sadekerroin, variRefVektori = thickness_design, colorBar =  thickBAR, colorBarTickValues = cbvalThick, colorBarTickNames = cbvalThickStr, longName = 'Surface precipitation [' + r'$kg/m^2/s$' + ']',       ylabel = 'Precipitation [' + r'$kg/m^2/s$' + ']', variKartta = thickness_color, ymin = 0.0, savePrefix = 'prcp', tit = thickTIT, spinup = spinup, xlabels = xLabelsHours, xticks = xTicksSeconds, omaVari = refColorbarSwitch, askChangeOfVariable = askChangeOfVariable, legenda = LEGEND )

            mdp.plot_suljetus( not naytaPlotit)

            piirra_maksimiKeissit( muuttuja = prcp, muunnosKerroin = sadekerroin, longName = 'Maximum precipitation after '+str(int(ajanhetket/3600.))+'h [' + r'$kg/m^2/s$' + ']', ylabel = 'precipitation kg/m^2/s',      savePrefix = 'prcp_max', askChangeOfVariable = askChangeOfVariable, ajanhetket = ajanhetket )

            mdp.plot_suljetus( not naytaPlotit)

        if SHF:
            piirra_aikasarjasettii( muuttuja = 'shf_bar', variRefVektori = thickness_design, colorBar =  thickBAR, colorBarTickValues = cbvalThick, colorBarTickNames = cbvalThickStr, longName = 'Sensible heat flux',        ylabel = 'Sensible heat flux W/m^2', variKartta = thickness_color, savePrefix = 'heat_flux_sensible', tit = thickTIT, spinup = spinup, xlabels = xLabelsHours, xticks = xTicksSeconds, omaVari = refColorbarSwitch, legenda = LEGEND )

            mdp.plot_suljetus( not naytaPlotit)

            piirra_maksimiKeissit( maksimiSensible, longName = "Maximum sensible heat",                                       ylabel = 'Sensible heat flux W/m^2', savePrefix = 'heat_flx_sensible_max', ajanhetket = ajanhetket )

            mdp.plot_suljetus( not naytaPlotit)

        if LHF:
            piirra_aikasarjasettii( muuttuja = 'lhf_bar', variRefVektori = thickness_design, colorBar =  thickBAR, colorBarTickValues = cbvalThick, colorBarTickNames = cbvalThickStr, longName = 'Latent heat flux',        ylabel = 'Latent heat flux W/m^2', variKartta = thickness_color, savePrefix = 'heat_flux_latent', tit = thickTIT, spinup = spinup, xlabels = xLabelsHours, xticks = xTicksSeconds, omaVari = refColorbarSwitch, legenda = LEGEND )

            mdp.plot_suljetus( not naytaPlotit)

            piirra_maksimiKeissit( maksimiLatent,   longName = "Maximum latent heat",                                         ylabel = 'Latent heat flux W/m^2',   savePrefix = 'heat_flx_latent_max', ajanhetket = ajanhetket )

            mdp.plot_suljetus( not naytaPlotit)

        if LWP:
            piirra_aikasarjasettii( muuttuja = 'lwp_bar', muunnosKerroin = 1000.0, variKartta = thickness_color,  variRefVektori = thickness_design, colorBar =  thickBAR, colorBarTickValues = cbvalThick, colorBarTickNames = cbvalThickStr, longName = 'LWP', ylabel = 'LWP g/m^2', ymin = 0.0,  savePrefix = 'lwp', tit = thickTIT, spinup = spinup, xlabels = xLabelsHours, xticks = xTicksSeconds, omaVari = refColorbarSwitch, legenda = LEGEND, tallenna = False )

            mdp.plot_suljetus( not naytaPlotit)

        if CDNC:
            piirra_aikasarjasettii( muuttuja = 'Nc_ic', variKartta = num_pbl_color, variRefVektori = num_pbl_design, colorBar = cdncBAR, colorBarTickValues = cbvalQ, colorBarTickNames = cbvalQStr, longName = 'Relative change of in-cloud CDNC', ylabel = 'Relative change of In-cloud CDNC', tit = cdncTIT, relative = True, nollaArvo = None,  spinup = spinup, xlabels = xLabelsHours, xticks = xTicksSeconds, omaVari = refColorbarSwitch, askChangeOfVariable = askChangeOfVariable, legenda = LEGEND) #

            mdp.plot_suljetus( not naytaPlotit)

        if QDIFF:
            #piirra_profiilisettii( 'q', variKartta = pblh_color, variRefVektori = pblh_design, colorBar = pblhBAR, colorBarTickValues = cbvalPblh, colorBarTickNames = cbvalPblhStr, longName =  'Tot. ' + r'$H_2{O}$' + ' mix. rat. ' + ' relative change ' +'0h - '+str((ajanhetket/3600.)) + 'h', xlabel = r'$\frac{q_{t=2h}}{q_{t=0h}}-1$', ylabel = 'z/pblh', ymin = 0.0, ymax = 1.01, xmin = -0.35, xmax = 0.025, savePrefix = 'q_diff', ajanhetket = ajanhetket, tit = pblhTIT, rajaKerros = pblh_design, relative = True, nollaArvo = q_pbl_design, omaVari = refColorbarSwitch )

            #mdp.plot_suljetus( not naytaPlotit)

            if PROFKEHITYS:
                piirra_profiiliKehitys( 'q', muunnosKerroin = 1000.0, variKartta = aika_color, colorBar = aikaBAR, colorBarTickValues = cbvalT, colorBarTickNames = cbvalTStr, longName =  'Tot. ' + r'$H_2{O}$' + ' mix. rat. evolution', xlabel = 'q [g/kg]', ylabel = 'z [m]', savePrefix = 'q_evol', aikaPisteet = aikaPisteet, tit = aikaTIT, rajaKerros = pblh_design, asetaRajat = False, paksuus = thickness_design )

                mdp.plot_suljetus( not naytaPlotit)

        if TDIFF:

            ########################################################
            #for temp in 'theta', 't':
                #try:
                    #piirra_profiilisettii( temp, variKartta = pblh_color, variRefVektori = pblh_design, colorBar = pblhBAR, colorBarTickValues = cbvalPblh, colorBarTickNames = cbvalPblhStr, longName =  r'$\theta$' + ' relative change 0h - '+str((ajanhetket/3600.)) + 'h', xlabel = r'$\frac{\theta_{t=2h}}{\theta_{t=0h}}-1$', ylabel = 'z/pblh', ymin = 0.0, ymax = 1.01, xmin = -0.05, xmax = 0.025, savePrefix = 't_diff', ajanhetket = ajanhetket, tit = pblhTIT, rajaKerros = pblh_design, relative = True, nollaArvo = tpot_pbl_design, omaVari = refColorbarSwitch )

                    #mdp.plot_suljetus( not naytaPlotit)
                    #break

                #except KeyError:
                    #print("TDIFF calculation failed with ", temp)
            ########################################################
            for temp in 'theta', 't':
                if PROFKEHITYS:
                    piirra_profiiliKehitys( temp,  variKartta = aika_color, colorBar = aikaBAR, colorBarTickValues = cbvalT, colorBarTickNames = cbvalTStr, longName =  'Potential temperature', xlabel = r'$\theta$' + ' [K]', ylabel = 'z [m]', savePrefix = 'theta_evol', aikaPisteet = aikaPisteet, tit = aikaTIT, rajaKerros = pblh_design, asetaRajat = False, paksuus = thickness_design )

                    mdp.plot_suljetus( not naytaPlotit)
                    break

            ########################################################
            #for temp in 'theta', 't':
                #try:
                    #if PROFKEHITYS:
                        #piirra_profiiliKehitys( temp,  variKartta = aika_color, colorBar = aikaBAR, colorBarTickValues = cbvalT, colorBarTickNames = cbvalTStr, longName =  'Absolute temperature', xlabel = 'theta' + ' [K]', ylabel = 'z [m]', savePrefix = 'temp_evol', aikaPisteet = aikaPisteet, tit = aikaTIT, rajaKerros = pblh_design, asetaRajat = False, paksuus = thickness_design, tempConversion = True )

                        #mdp.plot_suljetus( not naytaPlotit)
                        #break

                #except KeyError:
                    #print("TDIFF calculation failed with ", temp)
            ########################################################

        if WMAX:
            piirra_aikasarjasettii( muuttuja = 'wmax', variRefVektori = thickness_design, colorBar =  thickBAR, colorBarTickValues = cbvalThick, colorBarTickNames = cbvalThickStr, longName = 'Maximum vertical velocity',        ylabel = 'Maximum vertical velocity m/s', variKartta = thickness_color, savePrefix = 'w_max', tit = thickTIT, spinup = spinup, xlabels = xLabelsHours, xticks = xTicksSeconds, omaVari = refColorbarSwitch, legenda = LEGEND )

            mdp.plot_suljetus( not naytaPlotit)

        if W2:
            if PROFKEHITYS:
                piirra_profiiliKehitys( 'w_2', variKartta = aika_color, colorBar = aikaBAR, colorBarTickValues = cbvalT, colorBarTickNames = cbvalTStr, longName =  "Vertical velocity squared evolution", xlabel = r'$m^{2}/s^{2}$', ylabel = 'z [m]', savePrefix = 'w_2_evol', aikaPisteet = aikaPisteet, tit = aikaTIT, rajaKerros = pblh_design, asetaRajat = False, paksuus = thickness_design, askChangeOfVariable = askChangeOfVariable )

                mdp.plot_suljetus( not naytaPlotit)

            cbvalW2 = np.arange(0, 0.81, 0.1)
            cbvalICEStr = ['%.1f' % elem for elem in cbvalW2 ]
            piirra_domainProfiili( 'w_2', longName = "vertical velocity squared " + r'$m^{2}/s^{2}$', useDN = False, transpose = True, colorBarTickValues = cbvalW2, colorBarTickNames = cbvalICEStr, xlabels = xLabelsHours, xticks = ticksHours, variKartta = plt.cm.RdPu, profiili = True, spinup = spinup, savePrefix = 'w_2_evol_prof' )

            mdp.plot_suljetus( not naytaPlotit)

        if RH:
            cbvalRH = np.arange(50, 130, 10)
            cbvalICEStr = ['%.1f' % elem for elem in cbvalRH ]

            piirra_domainProfiili( 'P_RH', longName = 'Relative humidity', useDN = False, transpose = True, colorBarTickValues = cbvalRH, colorBarTickNames = cbvalICEStr, xlabels = xLabelsHours, xticks = ticksHours, variKartta = plt.cm.gist_rainbow, profiili = True, spinup = spinup, savePrefix = 'rh_evol_prof' )

            mdp.plot_suljetus( not naytaPlotit)


    elif int(lvl) == -10: # emulaattorivertailu, scatterplot
        for tt in [[0.25], [0.5], [2.0], [2.5], [3.5], [2.5, 3.5]]:

            piirra_keissiVertailuEmul( 'rmH2Opr', muunnosKerroin = 1.e6, tiedostopaate='ts', longNamePostfix = r'$[10^{-3}g/m^{2}/s]$', savePrefix = None, askChangeOfVariable = False, ajanhetket = tt, extendBelowZero = True, myRoundF = [1, 0.5] )

            piirra_keissiVertailuEmul( 'prcp_bc', muunnosKerroin = 2.5e-06*1.e6, tiedostopaate='ts', longNamePostfix = r'$[10^{-3}g/m^{2}/s]$', savePrefix = None, askChangeOfVariable = False, ajanhetket = tt, extendBelowZero = True, myRoundF = [1, 0.5] )

            piirra_keissiVertailuEmul( 'Nc_ic', muunnosKerroin = 1.e-6, tiedostopaate='ts', longNamePostfix = r'$[\#/mg]$', savePrefix = None, askChangeOfVariable = False, ajanhetket = tt, extendBelowZero = True, myRoundF = [1, 0.5] )

            piirra_keissiVertailuEmul( 'lwp_bar', muunnosKerroin = 1000., tiedostopaate='ts', longNamePostfix = r'$[g/m^2]$', savePrefix = None, askChangeOfVariable = False, ajanhetket = tt, myRoundInt = 5 )

            piirra_keissiVertailuEmul( 'rwp_bar', muunnosKerroin = 1000., tiedostopaate='ts', longNamePostfix = r'$[g/m^2]$', savePrefix = None, askChangeOfVariable = False, ajanhetket = tt, myRoundInt = 5 )

            piirra_keissiVertailuEmul( 'wmax', muunnosKerroin = 1., tiedostopaate='ts', longNamePostfix = r'$[g/m^2]$', savePrefix = None, askChangeOfVariable = False, ajanhetket = tt, myRoundF = [1, 0.5] )

            piirra_keissiVertailuEmul( 'cfrac', muunnosKerroin = 1., tiedostopaate='ts', longNamePostfix = '', savePrefix = None, askChangeOfVariable = False, ajanhetket = tt, myRoundF = [1, 0.1] )

            piirra_keissiVertailuEmul( 'vtke', muunnosKerroin = 1.0, tiedostopaate='ts', longNamePostfix = r'$[kg/s]$', savePrefix = None, askChangeOfVariable = False, ajanhetket = tt, myRoundInt = 5 )

            piirra_keissiVertailuEmul( 'zb', muunnosKerroin = 1.0, tiedostopaate='ts', longNamePostfix = r'$[m]$', savePrefix = None, askChangeOfVariable = False, ajanhetket = tt, myRoundInt = 5 )
            piirra_keissiVertailuEmul( 'zc', muunnosKerroin = 1.0, tiedostopaate='ts', longNamePostfix = r'$[m]$', savePrefix = None, askChangeOfVariable = False, ajanhetket = tt, myRoundInt = 5 )

    #if RAD:
    elif int(lvl) == -11:
        piirra_aikasarjaEmulVertailuSettii( muuttuja = 'Nc_ic', muunnosKerroin = 1.e-6, spinup = spinup, ylabel = r'CDNC [\#/mg]', xlabels = xLabelsHours, xticks = xTicksSeconds, askChangeOfVariable = askChangeOfVariable, legenda = True, omaVari = False)


    if NCFwrite:
        maksimiLWPlist_ncf    = ncfile.createVariable( 'lwp_max',     np.dtype('float32').char, ('case') )
        maksimiLWPlist_ncf[:] = maksimiLWPlist
        print('eniten lwp:ta keissi', np.argmax(maksimiLWPlist))
    ncfile.close()
################

if ICE:


    naytaPlotit = False
    korkeustikit =np.arange(0, 1201, 50)
    ylabels    = list(map(str, korkeustikit ))

    profiiliVariLIQ = [ '#000099', '#00ccff', '#00e600', '#f9f906', '#ff9900', '#ff0000' ]
    profiiliVariICE = [ '#000099', '#000099', '#00ccff', '#29a385', '#00e600', '#00e673','#ffff66', '#f9f906', '#c8e600', '#ff9900', '#ff6600', '#ff0000' ] # , '#990000', '#660000'

    distinctColors = [ "#000075", #navy
"#4363d8", #Blue
"#42d4f4", #Cyan
"#3cb44b", #Green
"#bfef45", #Lime
"#ffe119", #Yellow
"#f58231", #Orange
"#e6194B", #Red
"#800000" #Maroon
]

    cbvalLIQ    = np.arange(0, 0.241, 0.04)
    cbvalLIQStr = list(map(str, cbvalLIQ))

    if tag[:-1] == 'ice1':
        cbvalICE    = np.arange( 0, 0.41, 0.05) # np.arange(0, 1.4, 0.1)
        nicLKM = 1.41
    else:
        cbvalICE    =  np.arange(0, 1.41, 0.1)
        nicLKM = 4.41

    cbvalICEStr = ['%.1f' % elem for elem in cbvalICE ]

    cbvalLIQPATH = np.arange(0, 61, 5)
    cbvalLIQPATHStr = list(map(str, cbvalLIQPATH))

    piilotaOsaXlabel = True

    cbvalDiam = np.arange(0,600, 75)
    cbvalDiamStr = list(map(str,cbvalDiam))

    diamVari = profiiliVariICE #[plt.cm.tab20(3),plt.cm.tab20(2),plt.cm.tab20c(1), plt.cm.tab20c(0),plt.cm.tab20c(7),plt.cm.tab20c(6),plt.cm.tab20c(5),plt.cm.tab20c(4),plt.cm.tab20c(11),plt.cm.tab20c(10),plt.cm.tab20c(9),plt.cm.tab20c(8) ]
    #askChangeOfVariable = setupFunction( "Snow stuff included? (yes/no) Then will ask askChangeOfVariable ", kylla )
    askChangeOfVariable = False
    if len(tiedostolista)>1:
        icevari = False


    if int(lvl)>=4:

        #piirra_aikasarjaPathXYZ( 'l', longName = 'Liquid Water Path', savePrefix = 'lwp', xaxislabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel )
        #mdp.plot_vertical( spinup )
        #plt.xticks( ticksHours, xLabelsHours )

        piirra_aikasarjasettii( muuttuja = 'lwp_bar', muunnosKerroin = 1000.0, longName = 'Liquid water path', ylabel = 'path ' + r'[$g/m^2$]', ymin = 0.0,  savePrefix = 'lwpTS', omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel, legenda = True  )

        mdp.plot_suljetus( not naytaPlotit)

        #mdp.plot_vertical( spinup )
        #plt.xticks( ticksHours, xLabelsHours )

        #piirra_aikasarjasettii( muuttuja = 'shf_bar',  longName = 'Sensible heat flux', ylabel = 'W/m^2', ymin = 0.0,  savePrefix = 'heat_flux_sensible', omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel  )

        #piirra_aikasarjasettii( muuttuja = 'lhf_bar',  longName = 'Latent heat flux', ylabel = 'W/m^2', ymin = 0.0,  savePrefix = 'heat_flux_latent', omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel  )



        #piirra_domainProfiili( 'l', muunnosKerroin = 1000., longName = "Liquid water mixing ratio  " + r'$g/kg^{-1}$', useDN = False, transpose = True, colorBarTickValues = cbvalLIQ, colorBarTickNames = cbvalLIQStr, xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit,  variKartta = profiiliVariLIQ, spinup = spinup )

        piirra_domainProfiili( 'P_rl', muunnosKerroin = 1000., longName = "Liquid water mixing ratio  " + r'$g/kg^{-1}$', useDN = False, transpose = True, colorBarTickValues = cbvalLIQ, colorBarTickNames = cbvalLIQStr, xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit,  variKartta = profiiliVariLIQ, spinup = spinup, profiili = True ) # variKartta = profiiliVariLIQ

        mdp.plot_suljetus( not naytaPlotit)


        #animoi_path( 'l', muunnosKerroin = 1000., longName = "Liquid water path  " + r'$g/kg^{-1}$', useDN = False, transpose = True, colorBarTickValues = cbvalLIQPATH, colorBarTickNames = cbvalLIQPATHStr, xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit,  variKartta = plt.cm.Reds, spinup = spinup )

        #piirra_MeanSize(tyyppi = 'cloud', ajanhetket = [6], korkeus = [700], color = 'r')




        #piirra_domainMeanProfiili( 'S_Nc',nimi = 'Cloud number concentration averaged',  muunnosKerroin=1.e-6, ajanhetket = [6,8], useDN = True, profiili = False, xAxisL = r'$N [L^{-1}]$', color = icevari )

        piirra_domainMeanProfiili( 'P_Nca',nimi = 'Cloud number concentration averaged',  muunnosKerroin=1.e-6, ajanhetket = [6,8], useDN = True, profiili = True, xAxisL = r'[#$/cm^{3}$]', color = icevari )

        mdp.plot_suljetus( not naytaPlotit)



        piirra_domainProfiili( 'w_2', longName = "vertical velocity squared " + r'$m^{2}/s^{2}$', useDN = False, transpose = True, colorBarTickValues = cbvalICE, colorBarTickNames = cbvalICEStr, xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit,  variKartta = plt.cm.RdPu, profiili = True, spinup = spinup )

        #piirra_domainProfiili( 'rflx', longName = "Radiative cooling " + r'$W/m^{2}$', useDN = False, transpose = True, profiili = True, xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit,  variKartta = plt.cm.bwr, spinup = spinup, radCool = True, cloudBaseTop = True )

        piirra_profiiliKehitys( 'theta',  variKartta = aika_color, colorBar = aikaBAR, colorBarTickValues = cbvalT, colorBarTickNames = cbvalTStr, longName =  'Potential temperature', xlabel = r'$\theta$' + ' [K]', ylabel = 'z [m]', savePrefix = 'theta_evol', aikaPisteet = aikaPisteet, tit = aikaTIT, asetaRajat = False )

        #piirra_aikasarjasettii( muuttuja = 'rmH2Opr',     muunnosKerroin = 1.,  longName = "Removal of water by sedimentation of rain",       ylabel = 'flux ' + r'[$kg/m^2/s$]', ymin = 0.0,  savePrefix = 'depRain', omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel, legenda = True  )

        piirra_aikasarjasettii( muuttuja = 'Nc_ic', muunnosKerroin = 1.e-6, longName = 'in-cloud CDNC', ylabel = r'[\#/mg]', ymin = 0.0,  savePrefix = 'cdncTS', omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel, legenda = True  )

        mdp.plot_suljetus( not naytaPlotit)

        #piirra_domainProfiili( 'theta', longName = 'Potential temperature', useDN = False, transpose = True,  xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit, variKartta = plt.cm.Reds, spinup = spinup, profiili = True  )

        #piirra_domainProfiili( 'thl', longName = 'Liquid water potential temperature', useDN = False, transpose = True,  xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit, variKartta = plt.cm.Reds, spinup = spinup, profiili = True  )

        #piirra_aikasarjasettii( muuttuja = 'vtke', muunnosKerroin = 1.0, longName = 'Vertical integral of total TKE', ylabel = '[kg/s]', ymin = 0.0,  savePrefix = 'vtkeTS', omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel, legenda = True  )

        mdp.plot_suljetus( not naytaPlotit)

        piirra_domainProfiili( 'w_2', longName = "vertical velocity squared " + r'$m^{2}/s^{2}$', useDN = False, transpose = True, colorBarTickValues = cbvalICE, colorBarTickNames = cbvalICEStr, xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit,  variKartta = plt.cm.RdPu, profiili = True, spinup = spinup )

    if int(lvl)== 5:
        #piirra_aikasarjaPathXYZ( 'i', longName = 'Ice Water Path', savePrefix = 'iwp', xaxislabel = 'time [h]',xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel )
        #mdp.plot_vertical( spinup )
        #plt.xticks( ticksHours, xLabelsHours )

        piirra_aikasarjasettii( muuttuja = 'iwp_bar', muunnosKerroin = 1000.0, longName = 'Ice water path', ylabel = 'path ' + r'[$g/m^2$]', ymin = 0.0,  savePrefix = 'iwpTS', omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel, legenda = True, askChangeOfVariable = askChangeOfVariable  )

        mdp.plot_suljetus( not naytaPlotit)

        #piirra_aikasarjasettii( muuttuja = 'swp_bar', muunnosKerroin = 1000.0, longName = 'Ice water path', ylabel = 'path ' + r'[$g/m^2$]', ymin = 0.0,  savePrefix = 'swpTS', omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel, legenda = True  )

        #piirra_domainProfiili( 'i', muunnosKerroin = 1000.*np.power(10.,2), longName = 'Ice mixing ratio ' + r'$10^{2}g/kg^{-1}$', useDN = False, transpose = True, colorBarTickValues = cbvalICE, colorBarTickNames = cbvalICEStr, xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit, variKartta = profiiliVariICE, spinup = spinup  )

        piirra_domainProfiili( 'P_ri', muunnosKerroin = 1000.*np.power(10.,2), longName = 'Ice mixing ratio ' + r'$10^{2}g/kg^{-1}$', useDN = False, transpose = True, colorBarTickValues = cbvalICE, colorBarTickNames = cbvalICEStr, xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit, variKartta = profiiliVariICE, spinup = spinup, profiili = True, askChangeOfVariable = askChangeOfVariable  ) #variKartta = profiiliVariICE, colorBarTickValues = cbvalICE plt.cm.Blues

        mdp.plot_suljetus( not naytaPlotit)

        #piirra_domainProfiili( 'P_ri', muunnosKerroin = 1000.*np.power(10.,4), longName = 'Ice mixing ratio ' + r'$10^{4}g/kg^{-1}$', useDN = False, transpose = True, xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit, variKartta = plt.cm.Blues, spinup = spinup, profiili = True  ) #variKartta = profiiliVariICE, colorBarTickValues = cbvalICE plt.cm.Blues

        nic = np.arange(0, nicLKM, 0.2)
        piirra_domainProfiili( 'P_Nia', muunnosKerroin = 1.e-3, longName = 'Ice number concentration ', useDN = False, transpose = True, colorBarTickValues = nic, colorBarTickNames = ['%.1f' % elem for elem in nic ], xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit, variKartta = profiiliVariICE, spinup = spinup, profiili = True, askChangeOfVariable = askChangeOfVariable  ) #variKartta = profiiliVariICE, colorBarTickValues = cbvalICE

        mdp.plot_suljetus( not naytaPlotit)
        #piirra_domainProfiili( 'P_ri', muunnosKerroin = 1000.*np.power(10.,2), longName = 'Ice mixing ratio ' + r'$10^{2}g/kg^{-1}$', useDN = False, transpose = True,  xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit, variKartta = plt.cm.Blues, spinup = spinup, profiili = True  )

        #animoi_path( 'f', muunnosKerroin = 1000., longName = tag + "Ice water path  " + r'$g/kg^{-1}$', useDN = False, transpose = True, colorBarTickValues = cbvalLIQPATH, colorBarTickNames = cbvalLIQPATHStr, xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit,  variKartta = plt.cm.Blues, spinup = spinup )
        ## muuttuja, muunnosKerroin = 1.0, transpose = False, longName = None , savePrefix = None, useDN = False, colorBarTickValues = [0,1], colorBarTickNames = ['0','1'], xlabels = None, ylabels = None, xticks = None, yticks = None

        #piirra_MeanSize(tyyppi = 'ice', ajanhetket = [6], korkeus = [700] )
        #piirra_MeanSize(tyyppi = 'ice', ajanhetket = [6], korkeus = [400] )
        #piirra_MeanSize(tyyppi = 'ice', ajanhetket = [6], korkeus = [200] )
        #piirra_domainMeanProfiili( 'S_Ni',   nimi = 'Ice number concentration averaged',   muunnosKerroin=1./1000., ajanhetket = [6,8], useDN = True, profiili = False, xAxisL = r'$N [L^{-1}]$', color = icevari )
        ##piirra_domainMeanProfiili( 'S_Ni',   nimi = 'Ice number concentration averaged',   muunnosKerroin=1./1000., ajanhetket = [3,6], useDN = True, profiili = False, xAxisL = r'$N [L^{-1}]$', color = icevari )
        #piirra_domainMeanProfiili( 'S_Rwia', nimi = 'Ice particle mean diameter averaged', muunnosKerroin=2.e6  ,   ajanhetket = [6,8], useDN = True, profiili = False, xAxisL = r'$D [{\mu}m]$', color = icevari )

        piirra_domainMeanProfiili( 'P_Nia',  nimi = 'Ice number concentration averaged',   muunnosKerroin=1./1000., ajanhetket = [6,8], useDN = True, profiili = True, xAxisL = r'[#$/L$]', color = icevari, askChangeOfVariable = askChangeOfVariable )

        mdp.plot_suljetus( not naytaPlotit)

        piirra_domainMeanProfiili( 'P_Rwia', nimi = 'Ice particle mean diameter averaged', muunnosKerroin=2.e6  ,   ajanhetket = [6,8], useDN = False, profiili = True, xAxisL = r'[${\mu}m$]', color = icevari, askChangeOfVariable = askChangeOfVariable )

        mdp.plot_suljetus( not naytaPlotit)

        piirra_domainMeanProfiili( 'S_Rwiba', nimi = 'Ice particle mass mean diameter averaged testi', muunnosKerroin=2.e6  ,   ajanhetket = [6,8], useDN = False, binidata = True, xAxisL = r'[${\mu}m$]', color = icevari, savePrefix = 'domainMassMeanProfiili_salsa', askChangeOfVariable = askChangeOfVariable )

        mdp.plot_suljetus( not naytaPlotit)
        #piirra_domainMeanProfiili( 'S_Rwiba', nimi = 'Ice particle mean diameter averaged testi', muunnosKerroin=2.e6  ,   ajanhetket = [6,8], useDN = False, binidata = True, xAxisL = r'[${\mu}m$]', color = icevari, savePrefix = 'domainMeanProfiili_salsa' )

        piirra_domainMeanProfiili( 'P_ri',  nimi = 'Ice mixing ratio averaged',   muunnosKerroin=1000., ajanhetket = [6,8], useDN = False, profiili = True, xAxisL = r'[g/kg]', color = icevari, askChangeOfVariable = askChangeOfVariable )

        mdp.plot_suljetus( not naytaPlotit)

        piirra_domainProfiili( 'P_Rwia', muunnosKerroin = 2.e6, longName = 'Ice particle mean diameter '+r'[${\mu}m$]', useDN = False, transpose = True,  xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit, spinup = spinup, profiili = True, colorBarTickValues = cbvalDiam, colorBarTickNames = cbvalDiamStr, variKartta = diamVari, askChangeOfVariable = askChangeOfVariable  )

        mdp.plot_suljetus( not naytaPlotit)

        #piirra_domainProfiili( 'thil', longName = 'Ice-Liquid water potential temperature', useDN = False, transpose = True,  xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit, variKartta = plt.cm.Reds, spinup = spinup, profiili = True  )

        piirra_aikasarjasettii( muuttuja = 'rmH2Oic',     muunnosKerroin = 1.,  longName = 'Removal of water by sedimentation of ice',       ylabel = 'flux ' + r'[$kg/m^2/s$]', ymin = 0.0,  savePrefix = 'depIce', omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel, askChangeOfVariable = askChangeOfVariable  )

        mdp.plot_suljetus( not naytaPlotit)

    if int(lvl)== 6:  # plain snow stuff
        print('plain snow stuff')
        #piirra_aikasarjaPathXYZ( 'i', longName = 'Ice Water Path', savePrefix = 'iwp', xaxislabel = 'time [h]',xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel )
        #mdp.plot_vertical( spinup )
        #plt.xticks( ticksHours, xLabelsHours )

        piirra_aikasarjasettii( muuttuja = 'swp_bar', muunnosKerroin = 1000.0, longName = 'Ice water path (snow)', ylabel = 'path ' + r'[$g/m^2$]', ymin = 0.0,  savePrefix = 'swpTS', omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel, legenda = True, askChangeOfVariable = askChangeOfVariable  )

        mdp.plot_suljetus( not naytaPlotit)

        #piirra_aikasarjasettii( muuttuja = 'swp_bar', muunnosKerroin = 1000.0, longName = 'Ice water path', ylabel = 'path ' + r'[$g/m^2$]', ymin = 0.0,  savePrefix = 'swpTS', omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel, legenda = True  )

        #piirra_domainProfiili( 'i', muunnosKerroin = 1000.*np.power(10.,2), longName = 'Ice mixing ratio ' + r'$10^{2}g/kg^{-1}$', useDN = False, transpose = True, colorBarTickValues = cbvalICE, colorBarTickNames = cbvalICEStr, xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit, variKartta = profiiliVariICE, spinup = spinup  )

        piirra_domainProfiili( 'P_rs', muunnosKerroin = 1000.*np.power(10.,2), longName = 'Ice mixing ratio ' + r'$10^{2}g/kg^{-1}$', useDN = False, transpose = True, colorBarTickValues = cbvalICE, colorBarTickNames = cbvalICEStr, xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit, variKartta = profiiliVariICE, spinup = spinup, profiili = True, askChangeOfVariable = askChangeOfVariable  ) #variKartta = profiiliVariICE, colorBarTickValues = cbvalICE plt.cm.Blues

        mdp.plot_suljetus( not naytaPlotit)

        #piirra_domainProfiili( 'P_ri', muunnosKerroin = 1000.*np.power(10.,4), longName = 'Ice mixing ratio ' + r'$10^{4}g/kg^{-1}$', useDN = False, transpose = True, xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit, variKartta = plt.cm.Blues, spinup = spinup, profiili = True  ) #variKartta = profiiliVariICE, colorBarTickValues = cbvalICE plt.cm.Blues

        nic = np.arange(0, nicLKM, 0.2)
        piirra_domainProfiili( 'P_Ns', muunnosKerroin = 1.e-3, longName = 'Ice number concentration ', useDN = False, transpose = True, colorBarTickValues = nic, colorBarTickNames = list(map(str,nic)), xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit, variKartta = profiiliVariICE, spinup = spinup, profiili = True, askChangeOfVariable = askChangeOfVariable  ) #variKartta = profiiliVariICE, colorBarTickValues = cbvalICE

        mdp.plot_suljetus( not naytaPlotit)
        #piirra_domainProfiili( 'P_ri', muunnosKerroin = 1000.*np.power(10.,2), longName = 'Ice mixing ratio ' + r'$10^{2}g/kg^{-1}$', useDN = False, transpose = True,  xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit, variKartta = plt.cm.Blues, spinup = spinup, profiili = True  )

        #animoi_path( 'f', muunnosKerroin = 1000., longName = tag + "Ice water path  " + r'$g/kg^{-1}$', useDN = False, transpose = True, colorBarTickValues = cbvalLIQPATH, colorBarTickNames = cbvalLIQPATHStr, xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit,  variKartta = plt.cm.Blues, spinup = spinup )
        ## muuttuja, muunnosKerroin = 1.0, transpose = False, longName = None , savePrefix = None, useDN = False, colorBarTickValues = [0,1], colorBarTickNames = ['0','1'], xlabels = None, ylabels = None, xticks = None, yticks = None

        #piirra_MeanSize(tyyppi = 'ice', ajanhetket = [6], korkeus = [700] )
        #piirra_MeanSize(tyyppi = 'ice', ajanhetket = [6], korkeus = [400] )
        #piirra_MeanSize(tyyppi = 'ice', ajanhetket = [6], korkeus = [200] )
        #piirra_domainMeanProfiili( 'S_Ni',   nimi = 'Ice number concentration averaged',   muunnosKerroin=1./1000., ajanhetket = [6,8], useDN = True, profiili = False, xAxisL = r'$N [L^{-1}]$', color = icevari )
        ##piirra_domainMeanProfiili( 'S_Ni',   nimi = 'Ice number concentration averaged',   muunnosKerroin=1./1000., ajanhetket = [3,6], useDN = True, profiili = False, xAxisL = r'$N [L^{-1}]$', color = icevari )
        #piirra_domainMeanProfiili( 'S_Rwia', nimi = 'Ice particle mean diameter averaged', muunnosKerroin=2.e6  ,   ajanhetket = [6,8], useDN = True, profiili = False, xAxisL = r'$D [{\mu}m]$', color = icevari )

        piirra_domainMeanProfiili( 'P_Ns',  nimi = 'Ice number concentration averaged',   muunnosKerroin=1./1000., ajanhetket = [6,8], useDN = True, profiili = True, xAxisL = r'[#$/L$]', color = icevari, askChangeOfVariable = askChangeOfVariable )

        mdp.plot_suljetus( not naytaPlotit)

        piirra_domainMeanProfiili( 'P_Rws', nimi = 'Ice particle mean diameter averaged', muunnosKerroin=2.e6  ,   ajanhetket = [6,8], useDN = False, profiili = True, xAxisL = r'[${\mu}m$]', color = icevari, askChangeOfVariable = askChangeOfVariable )

        mdp.plot_suljetus( not naytaPlotit)

        piirra_domainMeanProfiili( 'S_Rwsba', muuttujaPainotus = 'S_Nsba', muuttujaPainotusPotenssi =  'S_Rwsba',  nimi = 'Ice particle mass mean diameter averaged testi', muunnosKerroin=2.e6  ,   ajanhetket = [6,8], useDN = False, binidata = True, xAxisL = r'[${\mu}m$]', color = icevari, savePrefix = 'domainMassMeanProfiili_salsa', askChangeOfVariable = askChangeOfVariable )

        mdp.plot_suljetus( not naytaPlotit)
        #piirra_domainMeanProfiili( 'S_Rwiba', nimi = 'Ice particle mean diameter averaged testi', muunnosKerroin=2.e6  ,   ajanhetket = [6,8], useDN = False, binidata = True, xAxisL = r'[${\mu}m$]', color = icevari, savePrefix = 'domainMeanProfiili_salsa' )

        piirra_domainMeanProfiili( 'P_rs',  nimi = 'Ice mixing ratio averaged',   muunnosKerroin=1000., ajanhetket = [6,8], useDN = False, profiili = True, xAxisL = r'[g/kg]', color = icevari, askChangeOfVariable = askChangeOfVariable )

        mdp.plot_suljetus( not naytaPlotit)

        piirra_domainProfiili( 'P_Rws', muunnosKerroin = 2.e6, longName = 'Ice particle mean diameter '+r'[${\mu}m$]', useDN = False, transpose = True,  xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit, spinup = spinup, profiili = True, colorBarTickValues = cbvalDiam, colorBarTickNames = cbvalDiamStr, variKartta = diamVari, askChangeOfVariable = askChangeOfVariable  )

        mdp.plot_suljetus( not naytaPlotit)

        #piirra_domainProfiili( 'thil', longName = 'Ice-Liquid water potential temperature', useDN = False, transpose = True,  xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit, variKartta = plt.cm.Reds, spinup = spinup, profiili = True  )

        piirra_aikasarjasettii( muuttuja = 'rmH2Osn',     muunnosKerroin = 1.,  longName = 'Removal of water by sedimentation of ice',       ylabel = 'flux ' + r'[$kg/m^2/s$]', ymin = 0.0,  savePrefix = 'depIce', omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel, askChangeOfVariable = askChangeOfVariable  )

        mdp.plot_suljetus( not naytaPlotit)

    if int(lvl) == 0:
        piirra_aikasarjavertailusettii( muuttuja = 'lwp',    muunnosKerroin = 1000.0,  savePrefix = 'changeLWP',    omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel  )
        piirra_aikasarjavertailusettii( muuttuja = 'lwpiwp', muunnosKerroin = 1000.0,  savePrefix = 'changeLWPIWP', omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel  )

        piirra_domainMeanScatter(muuttujaX = 'lwp_bar', muuttujaY = 'zc', muuttujaYY = 'zb', muunnosKerroinX = 1000., muunnosKerroinY = 1.0, muunnosKerroinYY = -1.0, nimi = None, ajanhetket = [6,8], xaxislabel = r'LWP [$g/m^2$]', yaxislabel = 'CLD depth [m]', savePrefix = None, minimiX =  0, maksimiX = 70, minimiY  = 0., maksimiY = 500 )

        piirra_domainMeanScatter(muuttujaX = 'zb', muuttujaY = 'zc', muuttujaYY = 'zb', muunnosKerroinX = 1., muunnosKerroinY = 1.0, muunnosKerroinYY = -1.0, nimi = None, ajanhetket = [6,8], xaxislabel = r'Z cld base [m]', yaxislabel = 'CLD depth [m]', savePrefix = None, minimiX =  400, maksimiX = 750, minimiY  = 0., maksimiY = 500 )

        piirra_domainMeanScatter(muuttujaX = 'zc', muuttujaY = 'zc', muuttujaYY = 'zb', muunnosKerroinX = 1., muunnosKerroinY = 1.0, muunnosKerroinYY = -1.0, nimi = None, ajanhetket = [6,8], xaxislabel = r'Z cld top [m]', yaxislabel = 'CLD depth [m]', savePrefix = None, minimiX =  700, maksimiX = 900, minimiY  = 0., maksimiY = 500 )

    if int(lvl) == -1:
        nic = np.arange(0, 1.41, 0.2)

        piirra_domainProfiili( 'P_Nia', muunnosKerroin = 1.e-3, longName = 'Ice number concentration ', useDN = True, transpose = True, colorBarTickValues = nic, colorBarTickNames = list(map(str,nic)), xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit, variKartta = profiiliVariICE, spinup = spinup, profiili = True  ) #variKartta = profiiliVariICE, colorBarTickValues = cbvalICE


        nyp = mdp.read_NamelistValue( namelist ,var = 'nyp'  )-4

        for slaissi in range(0,nyp):
            piirra_domainProfiili( 'S_Ni', muunnosKerroin = 1.e-3, longName = 'Ice number concentration ', useDN = True, transpose = True, colorBarTickValues = nic, colorBarTickNames = list(map(str,nic)), xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit, variKartta = profiiliVariICE, spinup = spinup, profiili = False, sliceYbeg = slaissi, sliceXend = slaissi+1, savePrefix = 'NicSlices'  )

    if int(lvl) == -2:

        piirra_kokojakauma( muuttujaR = 'S_Rwiba', muuttujaN = 'S_Niba', typename = 'Ice', korkeusH = 700, aikaT = 6, ymax = 11000, xmax = 1.6, yCustSize = 2, xCustSize = 2, sekoita = False, interplo = False, askChangeOfVariable = askChangeOfVariable ) # , xCustSize = 2
        piirra_kokojakauma( muuttujaR = 'S_Rwiba', muuttujaN = 'S_Niba', typename = 'Ice', korkeusH = 400, aikaT = 6, ymax = 11000, xmax = 1.6, yCustSize = 2, xCustSize = 2, sekoita = False, interplo = False, askChangeOfVariable = askChangeOfVariable ) # , xCustSize = 2
        piirra_kokojakauma( muuttujaR = 'S_Rwiba', muuttujaN = 'S_Niba', typename = 'Ice', korkeusH = 200, aikaT = 6, ymax = 11000, xmax = 1.6, yCustSize = 2, xCustSize = 2, sekoita = False, interplo = False, askChangeOfVariable = askChangeOfVariable ) # , xCustSize = 2

    if int(lvl) == -3:
        piirra_domainMeanProfiili( 'P_Rwia', nimi = 'Ice particle mean diameter averaged', muunnosKerroin=2.e6  ,   ajanhetket = [6,8], useDN = False, profiili = True, xAxisL = r'[${\mu}m$]', color = icevari, xmax=450 )
        piirra_domainMeanProfiili( 'S_Rwiba', nimi = 'Ice particle mass mean diameter averaged testi', muunnosKerroin=2.e6  ,   ajanhetket = [6,8], useDN = False, binidata = True, xAxisL = r'[${\mu}m$]', color = icevari, savePrefix = 'domainMassMeanProfiili_salsa' )

    if int(lvl) == -4:

        piirra_kokojakauma( muuttujaR = 'S_Rwsba', muuttujaN = 'S_Nsba', typename = 'Snow', korkeusH = 700, aikaT = 6, ymax = 11000, xmax = 1.6, yCustSize = 2, sekoita = False, interplo = False, askChangeOfVariable = askChangeOfVariable ) # , yCustSize = 2
        piirra_kokojakauma( muuttujaR = 'S_Rwsba', muuttujaN = 'S_Nsba', typename = 'Snow', korkeusH = 400, aikaT = 6, ymax = 11000, xmax = 1.6, yCustSize = 2, sekoita = False, interplo = False, askChangeOfVariable = askChangeOfVariable ) # , yCustSize = 2
        piirra_kokojakauma( muuttujaR = 'S_Rwsba', muuttujaN = 'S_Nsba', typename = 'Snow', korkeusH = 200, aikaT = 6, ymax = 11000, xmax = 1.6, yCustSize = 2, sekoita = False, interplo = False, askChangeOfVariable = askChangeOfVariable ) # , yCustSize = 2
    if int(lvl) == -5:

        piirra_kokojakauma( muuttujaR = 'S_Rwaba', muuttujaN = 'S_Naba', typename = 'Aero', korkeusH = 1100, aikaT = 6,  yCustSize = 2, sekoita = False, interplo = False ) # , yCustSize = 2
        #piirra_kokojakauma( muuttujaR = 'S_Rwiba', muuttujaN = 'S_Niba', typename = 'Aero', korkeusH = 400, aikaT = 6, ymax = 11000, xmax = 1.6, yCustSize = 2, sekoita = False, interplo = False ) # , yCustSize = 2
        #piirra_kokojakauma( muuttujaR = 'S_Rwiba', muuttujaN = 'S_Niba', typename = 'Aero', korkeusH = 200, aikaT = 6, ymax = 11000, xmax = 1.6, yCustSize = 2, sekoita = False, interplo = False ) # , yCustSize = 2
    if int(lvl) == -6:
        piirra_aikasarjasettii( muuttuja = 'iwp_bar', muunnosKerroin = 1000.0, longName = 'Ice water path', ylabel = 'path ' + r'[$g/m^2$]', ymin = 0.0,  savePrefix = 'iwpTS', omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel, legenda = True  )

    if int(lvl) == -7:
        piirra_domainMeanProfiili( 'S_Rwiba', nimi = 'Ice particle mass mean diameter averaged testi', muunnosKerroin=2.e6  ,   ajanhetket = [6,8], useDN = False, binidata = True, xAxisL = r'[${\mu}m$]', color = icevari, savePrefix = 'domainMassMeanProfiili_salsa', askChangeOfVariable = askChangeOfVariable )

    if int(lvl) == -8: # Ovchinnikov style isdac plots

        domainP = True
        RajausFlag = True
        try:
            if len(tag[-1]) > 0:
                tagii = "_" + tag[-1]
        except IndexError:
            tagii = "_"
        legendaPaper= False
        kehitys = True
        tallennaCSV = True

        for lwpmax in [50,60,100]:
            WPticks =  list(map(int, np.arange(0, lwpmax + .1 ,2)))
            WPlabels = list(map(str, WPticks))
            if lwpmax > 60:
                legendalwp = True
                loclwp = 2
            else:
                legendalwp = False
                loclwp = 3
            piirra_aikasarjasettii( muuttuja = 'lwp_bar', muunnosKerroin = 1000.0, longName = '', ylabel ="LWP " + r'$\mathbf{[ 10^{-3} {kg} / {m}^2 ]}$', ymin = 0.0, ymax=max(WPticks), extendBelowZero = False,  savePrefix = 'lwp' + tagii + str(lwpmax) + '_uclales-salsa', omaVari = False, xlabel = 'time [h]', yticks = WPticks, ylabels = WPlabels, spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel, piilotaOsaYlabel = True, piilotaOsaYlabelParam = 5, legenda = legendalwp, loc = loclwp, tallenna = tallennaCSV  )

            mdp.plot_suljetus( not naytaPlotit)

        for iwpmax in [20,21]:

            WPticks = list(map(int, np.arange(0,iwpmax + .1,1)))
            WPlabels = list(map(str, WPticks))

            piirra_aikasarjasettii( muuttuja = 'iwp_bar', muunnosKerroin = 1000.0, longName = '', ylabel ="IWP " + r'$\mathbf{[ 10^{-3} {kg} / {m}^2]}$', ymin = 0.0, ymax=max(WPticks), extendBelowZero = False,  savePrefix = 'iwp' + tagii + str(iwpmax) + '_uclales-salsa', omaVari = False, xlabel = 'time [h]', yticks = WPticks, ylabels = WPlabels, spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel, piilotaOsaYlabel = True, piilotaOsaYlabelParam = 3, legenda = legendaPaper, tallenna = tallennaCSV  )

            mdp.plot_suljetus( not naytaPlotit)


        piirra_aikasarjasettii( muuttuja = 'zc', muuttuja2 = 'zb',     longName= '', ylabel = 'height [m]', asetaRajat = RajausFlag, ymin = 0.0, extendBelowZero = False,  savePrefix = 'cloud_top_base' + tagii + '_uclales-salsa', omaVari = False, xlabel = 'time [h]', yticks = korkeustikit, ylabels = ylabels, spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel,  legenda = legendaPaper, piilotaOsaYlabel = True, piilotaOsaYlabelParam = 3, tallenna = tallennaCSV) #piilotaOsaYlabel = True, piilotaOsaYlabelParam = 3,

        mdp.plot_suljetus( not naytaPlotit)

        piirra_aikasarjasettii( muuttuja = 'Nc_ic', muunnosKerroin = 1.e-6, longName = 'in-cloud CDNC', ylabel = r'$\mathbf{[ \#/10^{-6} \ {kg}]}$', asetaRajat = RajausFlag, ymin = 0.0, extendBelowZero = False,  savePrefix = 'cdnc' + tagii + '_uclales-salsa' , omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel, legenda = legendaPaper, tallenna = tallennaCSV  )

        mdp.plot_suljetus( not naytaPlotit)

        # Ice number concentration
        piirra_aikasarjasettii( muuttuja = 'Ni_ii', muunnosKerroin = 1.e-3, longName = '', ylabel = r'$\mathbf{N_i\ [ \#/10^{-3} {kg}]}$', asetaRajat = RajausFlag, extendBelowZero = False, ymin = 0.0,  savePrefix = 'Ni' + tagii + '_uclales-salsa' , omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel, legenda = legendaPaper, tallenna = tallennaCSV  )

        mdp.plot_suljetus( not naytaPlotit)

        piirra_aikasarjasettii( muuttuja = 'wmax', longName = '', ylabel = '[m/s]', asetaRajat = RajausFlag, ymin = 0.0, extendBelowZero = False, savePrefix = 'w_max' + tagii + '_uclales-salsa' , omaVari = False, spinup = spinup, xlabel = 'time [h]', piilotaOsaXlabel = piilotaOsaXlabel, legenda = True, tallenna = tallennaCSV, loc = 3 )

        piirra_aikasarjasettii( muuttuja = 'wmax', longName = 'Maximum vertical velocity', ylabel = '[m/s]', asetaRajat = RajausFlag, ymin = 0.0, extendBelowZero = False, savePrefix = 'w_max' + tagii + '_uclales-salsa' , omaVari = False, spinup = spinup, xlabel = 'time [h]', piilotaOsaXlabel = piilotaOsaXlabel, legenda = True, tallenna = tallennaCSV, loc = 2 )

        mdp.plot_suljetus( not naytaPlotit)

        #cbvalDiam = np.arange(0,601, 50)
        #cbvalDiamStr = list(map(str,cbvalDiam))

        #piirra_domainProfiili( 'P_Rwia', muunnosKerroin = 2.e6, longName = 'Ice particle mean diameter '+r'[${\mu}m$]', useDN = False, transpose = True,  xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit, spinup = spinup, profiili = True, colorBarTickValues = cbvalDiam, colorBarTickNames = cbvalDiamStr, variKartta = diamVari, askChangeOfVariable = askChangeOfVariable  )

        #mdp.plot_suljetus( not naytaPlotit)

        WPticks = np.arange(0,6.1,1)
        WPlabels = list(map(str, WPticks))
        piirra_aikasarjasettii( muuttuja = 'rmH2Oic',     muunnosKerroin = 1.e6,  longName = '', ylabel = r'$\mathbf{{Prec}_{{srf}}\ [10^{-6} {kg} {m}^{-2} {s}^{-1}]}$', asetaRajat = RajausFlag, ymin = 0.0, ymax=WPticks[-1], extendBelowZero = False,  savePrefix = 'depIce', omaVari = False, xlabel = 'time [h]', yticks = WPticks, ylabels = WPlabels, spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel, piilotaOsaYlabel = False, piilotaOsaYlabelParam = 5, askChangeOfVariable = askChangeOfVariable, legenda = legendaPaper, tallenna = tallennaCSV )

        mdp.plot_suljetus( not naytaPlotit)

        for muuttujaTemp, nameTemp, unitTemp, muunnosTemp in [["rmDUdr","Deposition of dust with aerosols", r'$kg m^{-2} s^{-1}$', 1.e6],
        ["rmDUic", "Deposition of DU with ice", r'$kg m^{-2} s^{-1}$', 1.e12],
        ["rmDUcl", "Deposition of dust with of clouds", r'$kg m^{-2} s^{-1}$', 1.e6],
        ["DU_ii", "Dust mass mixing ratio in ice", "kg/kg", 1.e12], ["DU_ic", "Cloud droplet DU mass mixing ratio", "kg/kg", 1.e12], ["DU_int", "DU mass mixing ratio in interstitial aerosols", "kg/kg", 1.e12 ]]:
            piirra_aikasarjasettii( muuttujaTemp, longName =nameTemp, ylabel = r'[$10^{' + str(-int(np.log10(muunnosTemp)))+'}$'+ unitTemp+ ']', muunnosKerroin = muunnosTemp, asetaRajat = RajausFlag, extendBelowZero = False, ymin = 0.0,  savePrefix = muuttujaTemp + tagii + '_uclales-salsa' , omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel, legenda = legendaPaper, tallenna = tallennaCSV  )

            mdp.plot_suljetus( not naytaPlotit)

        for muuttujaTemp, nameTemp, unitTemp in [["vtke","Vertical integral of total TKE", "\mathbf{kg/s}" ]]:
            piirra_aikasarjasettii( muuttujaTemp, longName ='', ylabel = r'$['+ unitTemp+ ']$', muunnosKerroin = 1., asetaRajat = RajausFlag, ymin = 0.0, extendBelowZero = False,  savePrefix = muuttujaTemp + tagii + '_uclales-salsa' , omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel, legenda = legendaPaper, tallenna = tallennaCSV  )

            mdp.plot_suljetus( not naytaPlotit)

        #cbvalICE    =  np.arange(0, 3.1, 0.5)
        #cbvalICEStr = ['%.1f' % elem for elem in cbvalICE ]
        #cmap = plt.cm.jet
        #diamVari = [cmap(i) for i in range(cmap.N)]
        #piirra_domainProfiili( 'P_ri', muunnosKerroin = 1000.*np.power(10.,2), longName = 'Ice mixing ratio ' + r'$10^{2}g/kg^{-1}$', useDN = False, transpose = True, colorBarTickValues = cbvalICE, colorBarTickNames = cbvalICEStr, xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit, variKartta = diamVari, spinup = spinup, profiili = True, askChangeOfVariable = askChangeOfVariable  )

        #mdp.plot_suljetus( not naytaPlotit)

        #piirra_domainProfiili( 'P_rl', muunnosKerroin = 1000., longName = "Liquid water mixing ratio  " + r'$g/kg^{-1}$', useDN = False, transpose = True, colorBarTickValues = cbvalLIQ, colorBarTickNames = cbvalLIQStr, xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit,  variKartta = plt.cm.Reds, spinup = spinup, profiili = True ) # variKartta = profiiliVariLIQ

        #mdp.plot_suljetus( not naytaPlotit)

        if kehitys:
            origFig = mpl.rcParams['figure.figsize']
            mpl.rcParams['figure.figsize'] = [mpl.rcParams['figure.figsize'][0]*1.4, mpl.rcParams['figure.figsize'][1]*1.4]
            print(" ")
            print("mpl.rcParams['figure.figsize']",mpl.rcParams['figure.figsize'])

            listOfLineStyles = [ (0, ()), (0, (5, 1)), (0, (3, 1, 1, 1)), (0, (3, 1, 1, 1, 1, 1)), (0, (1, 1)) ] #,  (0, (1, 5))

            interTime = np.argmin( np.abs( xTicksSeconds - xTicksSeconds[-1]/(len(listOfLineStyles)-1)))
            aikaPisteet      = xTicksSeconds[::interTime] # even hours

            print("aikaPisteet kehitys", aikaPisteet)
            kehitysvarit = [ "Greens_r", "Blues_r", "Reds_r"]

            while len(kehitysvarit) < len(tiedostolista):
                kehitysvarit.insert(0, "Greens_r")


            aika_color       = [ sns.color_palette(kartta, len(aikaPisteet)-1) for kartta in kehitysvarit]
            for ac in aika_color:
                ac.insert(0, (0,0,0))


            #aikaBAR         = varibaari( aikaPisteet,  aika_color)
            #aikaTIT         = 'time [h]'
            #cbvalTStr       = list(map(str, xTicksSeconds))
            for temp in 'thl', 't':
                try:
                    piirra_profiiliKehitys( temp,  variKartta = aika_color, longName =  'Potential temperature', xlabel = r'$\theta$' + ' [K]', ylabel = 'z [m]', savePrefix = 'evol01_theta', aikaPisteet = aikaPisteet, asetaRajat = False, useSnsColor = True, xTikit = range(263, 273), xmin = 263., xmax = 273.5, viivaTyyli = listOfLineStyles )
                    mdp.plot_suljetus( not naytaPlotit)
                except KeyError:
                    print("piirra_profiiliKehitys did not succeed with", temp)
            muunnosTemp = 1e6
            unitTemp = "\mathbf{kg/kg}"
            piirra_profiiliKehitys( 'P_cH2Oi', muunnosKerroin = muunnosTemp, variKartta = aika_color, longName =  'SALSA total mass mixing ratio of H2O in ice', xlabel = r'$[10^{' + str(-int(np.log10(muunnosTemp)))+'}'+ unitTemp+ ']$', ylabel = 'z [m]', savePrefix = 'evol02_cH2Oi', aikaPisteet = aikaPisteet, asetaRajat = False, useSnsColor = True,  viivaTyyli = listOfLineStyles )
            mdp.plot_suljetus( not naytaPlotit)


            piirra_profiiliKehitys( 'P_ri', muunnosKerroin = muunnosTemp,  variKartta = aika_color, longName =  'Ice water mixing ratio', xlabel = r'$[10^{' + str(-int(np.log10(muunnosTemp)))+'}'+ unitTemp+ ']$', ylabel = 'z [m]', savePrefix = 'evol03_P_ri', aikaPisteet = aikaPisteet, asetaRajat = False, useSnsColor = True,  viivaTyyli = listOfLineStyles )
            mdp.plot_suljetus( not naytaPlotit)

            piirra_profiiliKehitys( 'P_rl', muunnosKerroin = muunnosTemp,  variKartta = aika_color, longName =  'Cloud water mixing ratio', xlabel = r'$[10^{' + str(-int(np.log10(muunnosTemp)))+'}'+ unitTemp+ ']$', ylabel = 'z [m]', savePrefix = 'evol04_P_rl', aikaPisteet = aikaPisteet, asetaRajat = False, useSnsColor = True,  viivaTyyli = listOfLineStyles )
            mdp.plot_suljetus( not naytaPlotit)


            piirra_profiiliKehitys( 'P_Nia',  variKartta = aika_color, longName =  'SALSA ice number concentration in regime A', xlabel = r'$[\#/kg]$', ylabel = 'z [m]', savePrefix = 'evol05_P_Nia', aikaPisteet = aikaPisteet, asetaRajat = False, useSnsColor = True,  viivaTyyli = listOfLineStyles )
            mdp.plot_suljetus( not naytaPlotit)

            piirra_profiiliKehitys( 'P_Nib',  variKartta = aika_color, longName =  'SALSA ice number concentration in regime B', xlabel = r'$[\#/kg]$', ylabel = 'z [m]', savePrefix = 'evol06_P_Nib', aikaPisteet = aikaPisteet, asetaRajat = False, useSnsColor = True,  viivaTyyli = listOfLineStyles )
            mdp.plot_suljetus( not naytaPlotit)

            muunnosTemp = 1e6
            unitTemp = "\mathbf{m}"
            piirra_profiiliKehitys( 'P_Rwia', muunnosKerroin = muunnosTemp,  variKartta = aika_color, longName =  'SALSA mean ice radius, regime A', xlabel = r'$[10^{' + str(-int(np.log10(muunnosTemp)))+'}'+ unitTemp+ ']$', ylabel = 'z [m]', savePrefix = 'evol07_P_Rwia', aikaPisteet = aikaPisteet, asetaRajat = False, useSnsColor = True,  viivaTyyli = listOfLineStyles )
            mdp.plot_suljetus( not naytaPlotit)

            piirra_profiiliKehitys( 'P_Rwib', muunnosKerroin = muunnosTemp,  variKartta = aika_color, longName =  'SALSA mean ice radius, regime B', xlabel = r'$[10^{' + str(-int(np.log10(muunnosTemp)))+'}'+ unitTemp+ ']$', ylabel = 'z [m]', savePrefix = 'evol08_P_Rwib', aikaPisteet = aikaPisteet, asetaRajat = False, useSnsColor = True,  viivaTyyli = listOfLineStyles )
            mdp.plot_suljetus( not naytaPlotit)

            mpl.rcParams['figure.figsize'] = origFig
            print(" ")

        cbvalICE    =  np.arange(0, 0.41, 0.1)
        cbvalICEStr = ['%.1f' % elem for elem in cbvalICE ]
        if domainP:

            piirra_domainProfiili( 'w_2', longName = "Vertical velocity squared " + r'$\mathbf{[ {m}^{2} / {s}^{2}]}$', useDN = False, transpose = True, colorBarTickValues = cbvalICE, colorBarTickNames = cbvalICEStr, xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit,  variKartta = mdp.scientific_colormaps("turku", reverse = True), profiili = True, spinup = spinup )

            mdp.plot_suljetus( not naytaPlotit)

# ["P_DUib", "Mass mixing ratio of dust in ice", "kg/kg"],
# ["P_Naba", "Aerosol number concentration in size bins A", "#/kg"],
# ["P_Nabb", "Aerosol number concentration in size bins B", "#/kg"],
# ["P_DUab", "Mass mixing ratio of dust in aerosol bins B","kg/kg"],
            colorBarTickTotalNumber = 13
            for muuttujaTemp, nameTemp, unitTemp in [["P_cDUi", "Total mass mixing ratio of dust in ice","kg/kg"],
            ["P_cDUa", "Total mass mixing ratio of dust in aerosols","kg/kg"], ["P_cDUc", "Total mass mixing ratio of dust in cloud droplets","kg/kg"]]:
                if muuttujaTemp == "P_cDUa":
                    useColorBar = True
                    colorBarOnly = True
                    showXlabel = False

                elif muuttujaTemp == "P_cDUc":
                    useColorBar = False
                    colorBarOnly = False
                    showXlabel = True

                elif muuttujaTemp == "P_cDUi":
                    useColorBar = False
                    colorBarOnly = False
                    showXlabel = True

                piirra_domainProfiili( muuttujaTemp, longName="", muunnosKerroin = 1.e12,  useDN = False, transpose = True, xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit,  variKartta = sns.color_palette("Reds", colorBarTickTotalNumber), profiili = True, spinup = spinup, colorBarTickValues = range(0,13+1), useColorBar = useColorBar, legenda = legendaPaper, hideColorBarLabels = 2, showXlabel = showXlabel, colorBarOnly = colorBarOnly ) #longName =nameTemp + " " + r'$[10^{-12}$' + unitTemp +"]"

                mdp.plot_suljetus( not naytaPlotit)


            for nicMax, nicInterval in [[2.5, 0.5], [9.0, 1.0]]:
                print("nicMax, nicInterval",nicMax, nicInterval)
                nic = np.arange(0, nicMax + 0.01, nicInterval)
                print("nic",nic)
                print("varikartta pituus", len(nic))
                for k in range(len(nic)):
                    nic[k] = round(nic[k],2)
                colorClasses = np.shape(nic)[0]-1
                snsColorMap = sns.color_palette("Blues", colorClasses)
                print("varikartta pituus", colorClasses)
                for P_ice_concentration in 'P_Nia', 'P_Nib':

                    piirra_domainProfiili( P_ice_concentration, muunnosKerroin = 1.e-3, longName = 'Ice number concentration ' + r'$\mathbf{[\# / 10^{-3} {kg}]}$', useDN = False, transpose = True, colorBarTickValues = nic, savePrefix = "P_ice_concentration_" + str(P_ice_concentration) + "_" + str(nicMax), colorBarTickNames = list(map(str,nic)), xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit, variKartta = snsColorMap, spinup = spinup, profiili = True  )

                    mdp.plot_suljetus( not naytaPlotit)



    if int(lvl) == -9:

        piirra_aikasarjasettii( muuttuja = 'lwp_bar', muunnosKerroin = 1000.0, longName = 'Liquid water path', ylabel = r'[$g/m^2$]', ymin = 0.0,  extendBelowZero = False,  savePrefix = 'lwpTS', omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel, legenda = False  )

        mdp.plot_suljetus( not naytaPlotit)

        piirra_aikasarjasettii( muuttuja = 'iwp_bar', muunnosKerroin = 1000.0, longName = 'Ice water path', ylabel = r'[$g/m^2$]', ymin = 0.0,  extendBelowZero = False,  savePrefix = 'iwpTS', omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel, legenda = False  )

        mdp.plot_suljetus( not naytaPlotit)

        piirra_aikasarjasettii( muuttuja = 'Nc_ic', muunnosKerroin = 1.e-6, longName = 'in-cloud CDNC', ylabel = r'[\#/mg]', ymin = 0.0,  savePrefix = 'cdncTS', omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel, legenda = False  )

        mdp.plot_suljetus( not naytaPlotit)

        piirra_aikasarjasettii( muuttuja = 'wmax', longName = 'Maximum vertical velocity', ylabel = '[m/s]', ymin = 0.0, savePrefix = 'w_max', omaVari = False, spinup = spinup, xlabel = 'time [h]', piilotaOsaXlabel = piilotaOsaXlabel, legenda = False )

        mdp.plot_suljetus( not naytaPlotit)

        piirra_aikasarjasettii( muuttuja = 'rmH2Oic',     muunnosKerroin = 1000.,  longName = '', ylabel = r'[$g m^{-2} s^{-1}$]', ymin = 0.0, extendBelowZero = False,  savePrefix = 'depIce', omaVari = False, xlabel = 'time [h]', spinup = spinup, piilotaOsaXlabel = piilotaOsaXlabel, askChangeOfVariable = askChangeOfVariable, legenda = False )

        mdp.plot_suljetus( not naytaPlotit)



    if int(lvl) == -11:
        piirra_domainProfiili( 'w', longName = "vertical velocity ", useDN = False, transpose = True, xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit,  variKartta = plt.cm.RdPu, profiili = True, spinup = spinup )
        piirra_domainProfiili( 'u', longName = "u velocity ", useDN = False, transpose = True, xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit,  variKartta = plt.cm.RdPu, profiili = True, spinup = spinup )
        piirra_domainProfiili( 'v', longName = "v velocity ", useDN = False, transpose = True, xlabels = xLabelsHours, ylabels = ylabels, xticks = ticksHours, yticks = korkeustikit,  variKartta = plt.cm.RdPu, profiili = True, spinup = spinup )

    if int(lvl) == -12: # zenithAngle LVL 3
        zenith_color      = mdp.truncate_colormap(  plt.cm.Reds, minval = 0.3)
        zenithPisteet     = [0.,10.,20.,30.,40.,50.,60.]
        zenithBAR         = varibaari( zenithPisteet,  zenith_color)
        zenithTIT         = 'zenith angle'
        zenithPisteetStr  = list(map(str, zenithPisteet))
        #colorBar = zenithBAR, colorBarTickValues = zenithPisteet, colorBarTickNames = zenithPisteetStr, tit = zenithTIT
        LEGEND = True
        refColorbarSwitch = True
        zcTicks = [ 0, 0.5, 0.8, 0.85, 0.9, 0.95, 1, 1.05, 1.1, 1.15, 1.20, 1.25, 1.3, 1.35, 1.4]
        prcp = 'prcp'
        sadekerroin = 2.5e-06

        piirra_aikasarjasettii( muuttuja = 'cfrac', variRefVektori = zenithPisteet, longName= 'Cloud fraction', ylabel = 'Cloud fraction', variKartta = zenith_color, ymin = 0.0, ymax = 1.0, spinup = spinup, xlabels = xLabelsHours, xticks = xTicksSeconds, omaVari = refColorbarSwitch, legenda = LEGEND )

        mdp.plot_suljetus( not naytaPlotit)

        piirra_aikasarjasettii( muuttuja = 'zc', variRefVektori = zenithPisteet, longName= 'Relative change of cloud top', ylabel = 'relative change',     variKartta = zenith_color, relative = True, savePrefix = 'cloud_top_rel_change', spinup = spinup, xlabels = xLabelsHours, xticks = xTicksSeconds, yticks = zcTicks, ylabelFont = 18, omaVari = refColorbarSwitch, legenda = LEGEND, fontsizeCustom = fontsizeCustom  )

        mdp.plot_suljetus( not naytaPlotit)

        piirra_aikasarjasettii( muuttuja = prcp, variRefVektori = zenithPisteet,     muunnosKerroin = sadekerroin, longName = 'Surface precipitation [' + r'$kg/m^2/s$' + ']',       ylabel = 'Precipitation [' + r'$kg/m^2/s$' + ']', variKartta = zenith_color, ymin = 0.0, savePrefix = 'prcp', spinup = spinup, xlabels = xLabelsHours, xticks = xTicksSeconds, omaVari = refColorbarSwitch, askChangeOfVariable = askChangeOfVariable, legenda = LEGEND )

        mdp.plot_suljetus( not naytaPlotit)

        piirra_aikasarjasettii( muuttuja = 'lwp_bar', variRefVektori = zenithPisteet, muunnosKerroin = 1000.0, variKartta = zenith_color, longName = 'LWP', ylabel = 'LWP g/m^2', ymin = 0.0,  savePrefix = 'lwp', spinup = spinup, xlabels = xLabelsHours, xticks = xTicksSeconds, omaVari = refColorbarSwitch, legenda = LEGEND )

        mdp.plot_suljetus( not naytaPlotit)

        piirra_maksimiKeissit( muuttuja = prcp, muunnosKerroin = sadekerroin, longName = 'Maximum precipitation after '+str(int(ajanhetket/3600.))+'h [' + r'$kg/m^2/s$' + ']', ylabel = 'precipitation kg/m^2/s',      savePrefix = 'prcp_max', askChangeOfVariable = askChangeOfVariable, ajanhetket = ajanhetket )

        mdp.plot_suljetus( not naytaPlotit)

        piirra_aikasarjasettii( muuttuja = 'wmax', variRefVektori = zenithPisteet, longName = 'Maximum vertical velocity',        ylabel = 'Maximum vertical velocity m/s', variKartta = zenith_color, savePrefix = 'w_max', spinup = spinup, xlabels = xLabelsHours, xticks = xTicksSeconds, omaVari = refColorbarSwitch, legenda = LEGEND )

        mdp.plot_suljetus( not naytaPlotit)

        piirra_aikasarjaPathXYZ( muuttuja = 'q', muunnosKerroin = 1000.0, longName = "Total water path", savePrefix = "tot_water", xaxislabel = 'time [h]', xlabels = xLabelsHours, xticks = xTicksSeconds, spinup = spinup, legenda = LEGEND)

        mdp.plot_suljetus( not naytaPlotit)

        aika_color      = mdp.truncate_colormap(  plt.cm.Blues, minval = 0.3)
        aikaPisteet     = xTicksSeconds
        aikaBAR         = varibaari( aikaPisteet,  aika_color)
        aikaTIT         = 'time [h]'
        cbvalTStr       = list(map(str, xTicksSeconds))
        for temp in 'theta', 't':
                try:
                    piirra_profiiliKehitys( temp,  variKartta = aika_color, colorBar = aikaBAR, colorBarTickValues = xTicksSeconds, colorBarTickNames = cbvalTStr, longName =  'Potential temperature', xlabel = r'$\theta$' + ' [K]', ylabel = 'z [m]', savePrefix = 'theta_evol', aikaPisteet = aikaPisteet, tit = aikaTIT, asetaRajat = False )

                    mdp.plot_suljetus( not naytaPlotit)
                    break

                except KeyError:
                    print("TDIFF calculation failed with ", temp)


toc = time.clock()
print(round(toc - tic, 2), "seconds of execution")
########################
### finishing up     ###
### DO NOT CHANGE    ###
########################
if __name__ == "__main__":
    if piirra and naytaPlotit:
        mdp.plot_lopetus()
