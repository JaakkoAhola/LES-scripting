#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 13:17:52 2020

@author: Jaakko Ahola, Finnish Meteorological Institute
@licence: MIT licence Copyright
"""
import matplotlib
import numpy
import os
import seaborn

from Data import Data
from Simulation import Simulation
from FileSystem import FileSystem

from decimal import Decimal


class Plot:
    
    def hideXLabels(ax, xLabelListShowBoolean, xLabelListMajorLineBoolean):
        k = 0
        for label in ax.xaxis.get_ticklabels():
            label.set_visible(xLabelListShowBoolean[k])
            k = k + 1
        
        k = 0
        for line in ax.xaxis.get_ticklines()[0::2]:
            if xLabelListMajorLineBoolean[k]:
                line.set_markersize(matplotlib.rcParams["xtick.major.size"])
            else:
                line.set_markersize(matplotlib.rcParams["xtick.minor.size"])
            k= k + 1

        return ax

    def hideYLabels(ax, param):
    
        k = 0
        for label in ax.yaxis.get_ticklabels():
            if numpy.mod(k,param) != 0:
                label.set_visible(False)
            k+=1
        
        return ax
        
    def hideColorbarXLabels(cbar, colorbarLabelListShowBoolean):
        k = 0
        for label in cbar.ax.xaxis.get_ticklabels():
            label.set_visible(colorbarLabelListShowBoolean[k])
            k = k + 1
        
        return cbar
    
    
    def hideColorbarYLabels(cbar, colorbarLabelListShowBoolean):
        k = 0
        for label in cbar.ax.yaxis.get_ticklabels():
            label.set_visible(colorbarLabelListShowBoolean[k])
            k = k + 1
    
    def setXTicksLabelsAsTime(ax, timeHvalues, tickInterval = 16, unit = "h", startPoint = 0,  xLabelListShow = None, xLabelListMajorLine = None, setXlabel = True):
        first = timeHvalues[0]
        last = timeHvalues[-1]
        xticks = numpy.arange(first,last+0.1, 0.5) 
        #xticks = xticks[::tickInterval]
        xticklabels = [ str(int(round(elem,1))) for elem in list(xticks) ]
        #print(xticks)
        ax.set_xticks( xticks )
        ax.set_xticklabels(xticklabels)
        
        timesize = numpy.shape(xticks)[0]
        #####################
        if xLabelListShow is None:
            xLabelListShowBoolean = [False]*timesize
            #timesize = numpy.shape(timeHvalues)[0]
            
            for i in range(timesize):
                if numpy.mod(i, tickInterval) == 0:
                    xLabelListShowBoolean[i] = True
        else:
            xLabelListShowBoolean = Data.getMaskedList( xticks, xLabelListShow)
        #############################
        if xLabelListMajorLine is None:
            xLabelListMajorLineBoolean = [False]*timesize
            
            for i in range(timesize):
                if numpy.mod(i, tickInterval) == 0:
                    xLabelListMajorLineBoolean[i] = True
        else:
            xLabelListMajorLineBoolean = Data.getMaskedList( xticks, xLabelListMajorLine)
        
            
        ax = Plot.hideXLabels(ax, xLabelListShowBoolean, xLabelListMajorLineBoolean)
        
        if setXlabel:
            ax.set_xlabel(r"$\mathbf{time (" + unit + ")}$") 
        else:
            ax.set_xlabel(None)
        ax.set_xlim( first ,last )
    
        return ax
    
    def getTicks(start, end, interval):
        return  [ int(elem) for elem in numpy.arange(start, end + interval*0.1, interval) ]
    
    def getLabels(ticks):
        return list(map(str,ticks))
    
    def getUnitLabel(label, unit, useBold = False):
        if useBold:
            boldingStart = "\mathbf{"
            boldingEnd  = "}"
        else:
            boldingStart = ""
            boldingEnd   = ""
        
        return r"$" +boldingStart +  "{" + label +  "}{\ } ( " + unit +      ")" + boldingEnd + "$"
        
    
    def getLogaritmicTicks(start, end, includeFives = False):
        tstart = -17
        tend = -9
        logaritmicTicks = numpy.arange(tstart, tend)
        if includeFives:
            fives = numpy.arange(tstart+numpy.log10(5), tend)
            logaritmicTicks = numpy.sort(numpy.concatenate((logaritmicTicks,fives)))
        
        return logaritmicTicks
        
    
    def getTimeseriesOfProfile(ax,
                         simulation : Simulation,
                         muuttuja,
                         useContours = True,
                         useColorBar = True,
                         showXaxisLabels = True,
                         showXLabel = True,
                         yticks = None,
                         levels = None,
                         timeStartH = 0., timeEndH = 48,
                         uusikuva = True, title = None, colors = None, plotSpinup = True):

        ps = simulation.getPSDataset()
        ts = simulation.getTSDataset()
        
        if ps is None:
            return "FileNotFound"
        
        timeStartInd = Data.getClosestIndex( ps.time.values, timeStartH*3600 )
        timeEndInd   = Data.getClosestIndex( ps.time.values, timeEndH*3600 )
        ps = ps.isel(time = slice(timeStartInd,timeEndInd))
        ts = ts.isel(time = slice(timeStartInd,timeEndInd))
        ps = ps.assign_coords(time = (ps.time / 3600))
        ts = ts.assign_coords(time = (ts.time / 3600))
        
        try:
            data = ps[muuttuja]
        except KeyError:
            return
        
        
        if levels is None:
            levels, rangePotenssi, minimiPotenssi, maksimiPotenssi = Data.getLogScale(data.values)
            
            levels = rangePotenssi#numpy.power(10,levels)
            print(levels, minimiPotenssi, maksimiPotenssi, rangePotenssi)
        
        xLabelListShow = numpy.arange(0, 48+1, 8)
        
        xLabelListMajorLine = numpy.arange(4, 48+1, 4)
        
        ax = Plot.setXTicksLabelsAsTime(ax, ps.time.values, xLabelListShow = xLabelListShow, xLabelListMajorLine = xLabelListMajorLine)
        if yticks is not None:
            ax.set_yticklabels( list(map(str, yticks)))
        data.values  = numpy.log10(data.values)
        im = data.plot.contourf("time","zt", ax = ax, levels=levels, add_colorbar = False, colors = colors) #
        
        if useContours:
            ps.P_RHi.plot.contour(x="time", y="zt",ax=ax, colors ="black", vmin = 100-1e-12, vmax = 100 + 1e-12)#e6194B
            ts.zb.where(ts.zb>0).plot(ax=ax, color="#f58231") 
        
        if useColorBar:
            cb = matplotlib.pyplot.colorbar(im, ticks = levels, orientation='horizontal', pad = 0.22) #, pad=0.21
            cb.ax.set_xticklabels([r"$10^{" + str(int(elem)) + "}$" for elem in levels]) 
            
            colorbarLabelListShowBoolean = Data.getIntegerExponentsAsBoolean( levels )
            cb = Plot.hideColorbarXLabels(cb, colorbarLabelListShowBoolean)
            cb.ax.tick_params(labelsize=36)
        
        ax.set_yticks( numpy.arange(0, 1001, 250))
       
        if not showXaxisLabels:
            ax.set_xticklabels([])
        
        if showXLabel:    
            matplotlib.pyplot.xlabel(r"$\mathbf{time (h)}$")
        else:
            matplotlib.pyplot.xlabel(None)
            
        matplotlib.pyplot.ylabel(r"$\mathbf{height (m)}$")
        matplotlib.pyplot.xlim( 0 ,data["time"].values[-1] )
        matplotlib.pyplot.ylim(0, 1000)
        if plotSpinup:
            matplotlib.pyplot.axvline(2, color = "black", linestyle = "--")
        if title is None:
            title = data.longname
        
           
        matplotlib.pyplot.title(title)
        
        #data.plot.contourf("time","zt")#, levels=levels, cbar_kwargs={"ticks": levels})
        
        return ax, im

    def getTimeseriesOfProportions(axes,
                                   simulation : Simulation,
                                   muuttuja,
                                   mode = "inCloud", cmap = "bright", limit = 1e-6, height = None, packing = None,
                                   timeStartH = 2.05, timeEndH = 48, analysis = False,
                                   fontsize = None, useLegend = True,
                                   figurePrefix = "",
                                   kuvakansio = "/home/aholaj/OneDrive/000_WORK/000_ARTIKKELIT/000-Manuscript-ICE/kuvat/bini/",
                                   kuvakansioPDF = "/home/aholaj/OneDrive/000_WORK/000_ARTIKKELIT/000-Manuscript-ICE/figures_pdf",
                                   filenamePDF = "figure6"):
        
        print(mode, end = " ")
        if height is not None:
            print(height)
        else:
            print()
        
        
        ps = simulation.getPSDataset()
        if ps is None:
            return "FileNotFound"
        
        ts = simulation.getTSDataset()
        if ts is None:
            return "FileNotFound"
        
        timeStartInd = Data.getClosestIndex( ps.time.values, timeStartH*3600 )
        timeEndInd   = Data.getClosestIndex( ps.time.values, timeEndH*3600 )
        ps = ps.isel(time = slice(timeStartInd,timeEndInd))
        
        
        try:
        
            if mode == "inCloud":
               # ps = ps.sel(zt = slice(665,745)).mean(dim = "zt")
                ps = ps.where( (ps.P_rl > limit) & (ps.P_ri > limit), drop = True).mean(dim = "zt", skipna = True) #ps.where(ps.zt > ts.zb).where(ps.zt < ts.zc).mean(dim = "zt")#
            elif mode == "belowCloud":
                #ps = ps.sel(zt = slice(5,410)).mean(dim = "zt")
                ps = ps.where(ps.P_rl < limit, drop = True).where(ps.zt < ts.zb, drop = True).mean(dim = "zt", skipna = True) #.where(ps.P_rl < 1e-6, drop = True)
            elif mode == "aboveCloud":
                ps = ps.where(ps.zt > ts.zc, drop = True).mean(dim = "zt", skipna = True) #.where(ps.P_rl < 1e-6, drop = True)
            elif mode == "height":
                ps = ps.sel(zt = height, method = 'nearest')        
        except KeyError:
            return
        
        ps = ps.assign_coords(time = (ps.time / 3600))
        
                
        try:
            aero  = ps["P_Nabb"]
            cloud = ps["P_Ncbb"]
            ice   = ps["P_Nibb"]
        except KeyError:
            return
        
        newname = "dryRadiusBinB"
        aero = aero.rename({"aeb":newname})
        cloud = cloud.rename({"clb":newname})
        ice   = ice.rename({"icb":newname})
        
        total = aero + cloud + ice
        
        if packing is not None:
            for daatta in aero, cloud, ice, total:
                daatta[:,packing] = numpy.sum(daatta[:,packing:], axis = 1)
        
        binNumber = min( numpy.shape(total.values)[1], packing +1 )
        
        
        matplotlib.rcParams['lines.linewidth'] = 6
        yTicks = [0, 0.5, 1]
        yTickLabels = map(str, yTicks)
            
        matplotlib.pyplot.subplots_adjust(hspace=0.05, wspace = 0.05)
            
        xLabelListShow = numpy.arange(8, 48+1, 8)
        xLabelListShow = numpy.insert(xLabelListShow, 0, 2)
        
        xLabelListMajorLine = numpy.arange(4, 48+1, 4)
        xLabelListMajorLine = numpy.insert(xLabelListMajorLine, 0, 2)
        
        for bini in range(binNumber):
            ax = axes[bini]
            aeroBin = aero[:,bini]
            cloudBin = cloud[:,bini]
            iceBin  = ice[:,bini]
            
            totalBin = total[:,bini]
            
            aeroFrac = aeroBin/totalBin
            cloudFrac = cloudBin/totalBin
            iceFrac = iceBin/totalBin
            
            totalBinRelative  = totalBin / totalBin.values[0]
            
            aeroFrac.plot(ax=ax, color = "#e6194B")
            cloudFrac.plot(ax=ax, color = "#000075")
            iceFrac.plot(ax=ax, color = "#42d4f4")
            totalBinRelative.plot(ax = ax, color = "black")
            
            ax.set_yticks( yTicks )
            ax.set_yticklabels( yTickLabels )
            ax.set_ylim( 0, 1.5)
            ax.set_title("")
            matplotlib.pyplot.setp(ax.get_yticklabels()[1], visible=False)
            
            if packing is not None and bini == (binNumber - 1):
                bininame = str(bini + 1 ) + " - 7"
            else:
                bininame = str(bini +1)
            
            if useLegend:
                legend_handles = [matplotlib.patches.Patch( facecolor = "black",
                            label = " ".join([ "Bin", bininame + ",", "Total", r"$N_0$",  str(int(totalBin.values[0])) + ",", "Min", r"$N$", str(int(numpy.min(totalBin))), "$(kg^{-1})$"  ]))]
                legend = ax.legend(handles = legend_handles, loc = "best", fontsize = fontsize)
                ax.add_artist(legend)
                
                if bini == 0:
                    header_handles = [matplotlib.patches.Patch(facecolor = "#e6194B", label="Aerosol"),
                                            matplotlib.patches.Patch(facecolor = "#000075", label="Cloud"),
                                            matplotlib.patches.Patch(facecolor = "#42d4f4", label="Ice")]
                                                  
                    header_legend = ax.legend(handles = header_handles, loc =(0.3,1.05), ncol = 3, frameon = True, framealpha = 1.0, fontsize = fontsize)
                    
                    ax.add_artist(header_legend)
            ########## END USELEGEND
            
            if bini in [2,3]:
                setXlabel= True
            else:
                setXlabel =False
            
            ax = Plot.setXTicksLabelsAsTime(ax, ps.time.values, xLabelListShow = xLabelListShow, xLabelListMajorLine = xLabelListMajorLine, setXlabel = setXlabel)
            
            if bini in [0,1]:
                ax.set_xticklabels([])
            
        axes[2].set_yticklabels([str(item) for item in yTicks])
        for tick in axes[2].get_yticklabels():
            print(tick)
            tick.set_visible(True)
        
        return axes
        
    def getTimeseriesOfBinMass(ax,
                              simulation : Simulation,
                              muuttuja,
                              height,
                              cmap = "OrRd", relative = True, limiter = 1e-3):
        
        ps = simulation.getPSDataset()
        
        if ps is None:
            return "FileNotFound"
        
        zt = ps.zt
        
        psSliced = ps.sel(zt = height, method = "nearest").isel(time = slice(61,1440))
        try:
            data = psSliced[muuttuja]
        except KeyError:
            return
        
        
        aerosolsUsed = False
        AerosolAbins = False
        AerosolBbins = False
        parallelAeroB = None
        parallelAeroA = None
        ################################
        if muuttuja == "P_Naba":
            aerosolsUsed = True
            
            if muuttuja == "P_Naba":
                AerosolAbins = True
            elif muuttuja == "P_Nabb":
                AerosolBbins = True
            
            
        if aerosolsUsed:
            parallelCloudA = psSliced["P_Ncba"]
            parallelCloudB = psSliced["P_Ncbb"]
        if AerosolAbins:
            parallelAeroB = psSliced["P_Nabb"]
            
        elif AerosolBbins:
            parallelAeroA = psSliced["P_Naba"]
            
        biniTieto = muuttuja[-1].upper()    
        ################################            
                
        dataAllBins = data
        dataAllBins = dataAllBins.assign_coords(time = (dataAllBins.time / 3600))
        size = numpy.shape(dataAllBins.values)[1]
        colorpalette = seaborn.color_palette(cmap, 10)
        skip = 0
        aero = None
        includeOtherAero = False
        includeParallelOthercloud = False
        includeParallelCloud = True
        
        label = biniTieto + " bin |" + r"$N_0\ (\#/kg)$"
        
        legend_elements = [matplotlib.patches.Patch(facecolor="white",label=label)]
        for bini in range(size):
            plottable = dataAllBins[:,bini]
            
            vertailuData = numpy.zeros( numpy.shape(plottable.values))
            
            if Data.isCloseToEpsilon(plottable, limiter):
                skip += 1
                continue
            
            if AerosolAbins:
                parallelBaeroBini  = bini - 3
                parallelAcloudBini = bini - 3
                parallelBcloudBini = bini - 3
    
            elif AerosolBbins:
                parallelAaeroBini = bini + 3
                parallelAcloudBini = bini
                parallelBcloudBini = bini
            
            
            if aerosolsUsed:# and (parallelbini >= 0):
                
                if includeOtherAero:
                    if AerosolAbins and parallelBaeroBini > 0:
                        aero = parallelAeroB[:, parallelBaeroBini]
                    elif AerosolBbins:
                        aero = parallelAeroA[:, parallelAaeroBini]
                    
                    vertailuData = vertailuData + aero.values
                
                if includeParallelOthercloud:
                    if AerosolAbins and parallelBcloudBini>0:
                        parallelOtherCloud = parallelCloudB[:, parallelBcloudBini ]
                    
                    elif AerosolBbins and parallelAcloudBini>0:
                        parallelOtherCloud = parallelCloudA[:, parallelAcloudBini ]
                    
                    vertailuData = vertailuData + parallelOtherCloud.values
                
                
                if includeParallelCloud:
                    if AerosolAbins:
                        parallelCloud = parallelCloudA[:, parallelAcloudBini]
                    elif AerosolBbins:
                        parallelCloud = parallelCloudB[:, parallelBcloudBini]
                    
                    vertailuData = vertailuData + parallelCloud.values
                
                
            denom = plottable.values + vertailuData
            plottable, lahtoarvo = Data.getRelativeChange(plottable, denominator=denom, limiter = limiter)
            
            
            color = Data.getColorBin(colorpalette, bini, plottable)
            plottable.plot(ax=ax, color = color)
            
            if lahtoarvo > 1000 or lahtoarvo < 0.1:
                label =  '{0:8d}{1:11.1E}'.format(bini + 1, Decimal(lahtoarvo))
            else:
                label =  '{0:8d}{1:11.1f}'.format(bini + 1, lahtoarvo)
            legend_elements.append(matplotlib.patches.Patch(facecolor=color,label=label))
    
        if skip == size:
            matplotlib.pyplot.close()
            return None
        
        #matplotlib.pyplot.axvline( 2, color = "k" , linestyle = "--" )
        
        #matplotlib.pyplot.legend()
        ax.legend(handles=legend_elements, loc='best', frameon = True, framealpha = 1.0 )
        
        heightTosi = str(int(zt.sel(zt = height, method = 'nearest' ).values))
        matplotlib.pyplot.title("zt =" + heightTosi + "(m)" )
    #    print(time.values)
        ax = Plot.setXTicksLabelsAsTime(ax, plottable["time"].values, startPoint=8)
    
        #matplotlib.pyplot.ylim(0, 5)
        ax.set_yscale('log')
        
        return ax
    
    def getSizeDistributionHeightTimeSpecified(ax,
                                               simulation : Simulation,
                                               muuttuja,
                                               label = None,
                                               color = "b",
                                               height =745, timeH = 2.5):
        
        ps = simulation.getPSDataset()

        
        if ps is None:
            return "FileNotFound"
        
        ps = ps.sel(zt=height).sel(time=timeH*3600, method = "nearest")
        
        try:
            dataarray = ps[muuttuja]
        except KeyError:
            return
        
        if label is None:
            label = dataarray.longname
        
        dataarray.plot.line(ax=ax, color = color , marker="o", label=label) #aero "#e6194B" cloud  "#000075" ice "#42d4f4"
        
        matplotlib.pyplot.legend()
        ax.set_yscale("log")
        ax.set_xscale("log")
        
        return ax


    ### getAnimation2D NEEDS REVISION ####
    def getAnimation2D(ax,
                       simulation : Simulation,
                       muuttuja = "S_Nc",
                       kuvakansio =  "/home/aholaj/OneDrive/000_WORK/000_ARTIKKELIT/000-Manuscript-ICE/kuvat/anim",
                       useAverage=False, ytValue = 0, useLog = False):
        
        nc = simulation.getNCDataset()

        if nc is None:
            return "FileNotFound"
    
        try:
            dataAnim = nc[muuttuja]#.sel(zt = slice(395, 850))    
        except KeyError:
            return
        
        dataAnim = dataAnim.assign_coords(time = (dataAnim.time / 3600))
        print(" ")
        print("animate", muuttuja)
        if useLog:
            dataAnim.values = numpy.ma.log10(dataAnim.values).filled(0)
        
        if useAverage:
            dataAnim = dataAnim.mean(dim="yt")
            
        else:
            dataAnim = dataAnim.sel(yt = ytValue, method="nearest")
        dataAnim= dataAnim.sel(time = slice(2.5,49))
        timeSpan = numpy.shape(dataAnim)[0]
        subkuvakansio = FileSystem.createSubfolder(kuvakansio, muuttuja)
        for i in range(timeSpan):
            
            fig, ax = plot_alustus()
            plottable = dataAnim.isel(time=i)
            plottable.plot(x = "xt", y = "zt",ax = ax, add_colorbar = False, cmap = "Blues_r") #, levels = levels
            ax.set_title("time = " +"{:5.1f} (h)".format(plottable.time.values) )
            ax.set_ylabel("height (m)")
            ax.set_xlabel("East-west displacement of cell centers (m)")
            saveFig(subkuvakansio, muuttuja + "_{:04d}".format(i))
        
        origDir = os.getcwd()    
        os.chdir(subkuvakansio)
        os.system("convert -delay 50 -loop 0 *.png animation.gif")
        os.chdir(origDir)    
