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
import pathlib
import seaborn

from Data import Data
from FileSystem import FileSystem
from PlotTweak import PlotTweak
from Simulation import Simulation


from decimal import Decimal

class Plot:
    
    def getVerticalLine(ax, x, color = 'k', linestyle = '--' ):
        ax.axvline( x, color = color , linestyle = linestyle )


    def getHorizontalLine(ax, y, color = 'k', linestyle = '--' ):
        ax.axhline( y, color = color , linestyle = linestyle )
    
    
    def getTimeseries(ax,
                      simulation : Simulation,
                      muuttuja,
                      conversionFactor = 1.0):
        if isinstance(simulation, list):
            for simulationInstance in simulation:
                ax = Plot.getTimeseries(ax, simulationInstance, muuttuja, conversionFactor)
            return ax
        
        ts = simulation.getTSDataset()
        try:
            dataset = ts[muuttuja]
        except KeyError:
            print("KeyError")
            return None
        
        # conversion
        dataset = dataset*conversionFactor
        
        dataset.plot(ax = ax,
                     color = simulation.getColor(),
                     label =  simulation.getLabel(),
                     linewidth = simulation.getLineWidth())
        
        return ax
    
    #REVISEu
    def getTimeseriesOfProfile(ax,
                         simulation : Simulation,
                         muuttuja,
                         levels = None,
                         useLogaritmic = False,
                         useColorBar = False,
                         colors = None):

        ps = simulation.getPSDataset()
        
        try:
            data = ps[muuttuja]
        except KeyError:
            print("KeyError", simulation, muuttuja, "Plot.getTimeseriesOfProfile")            
            return
        
        if useLogaritmic:
            if levels is None:
                levels, rangePotenssi, minimiPotenssi, maksimiPotenssi = Data.getLogScale(data.values)
                levels = rangePotenssi
            
            data.values  = numpy.log10(data.values)
            
        im = data.plot.contourf("time","zt", ax = ax, levels=levels, add_colorbar = useColorBar, colors = colors) #
        
        return ax, im, levels
    
    def getContourLine(ax,
                       simulation : Simulation,
                       muuttuja,
                       value,
                       color = "black",
                       epsilon = 1e-12):
        ps = simulation.getPSDataset()
        try:
            data = ps[muuttuja]
        except KeyError:
            print("KeyError", simulation, muuttuja, "Plot.getContourLine")
            return
        
        data.plot.contour(x="time", y="zt",ax=ax, colors = color, vmin = value - epsilon , vmax = value + epsilon)
        
        return ax
    
    def getColorBar(im, ax, levels = None):
        cb = matplotlib.pyplot.colorbar(im, cax = ax, ticks = levels, orientation='horizontal') #, pad=0.21
        if levels is not None:
            cb.ax.set_xticklabels([r"$10^{" + str(int(elem)) + "}$" for elem in levels]) 
            
            colorbarLabelListShowBoolean = Data.getIntegerExponentsAsBoolean( levels )
            cb = PlotTweak.hideColorbarXLabels(cb, colorbarLabelListShowBoolean)
            cb.ax.tick_params(labelsize=36)
    
    # REVISE
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
            
            ax = PlotTweak.setXTicksLabelsAsTime(ax, ps.time.values, xLabelListShow = xLabelListShow, xLabelListMajorLine = xLabelListMajorLine, setXlabel = setXlabel)
            
            if bini in [0,1]:
                ax.set_xticklabels([])
            
        axes[2].set_yticklabels([str(item) for item in yTicks])
        for tick in axes[2].get_yticklabels():
            print(tick)
            tick.set_visible(True)
        
        return axes
    
    # REVISE
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
        ax = PlotTweak.setXTicksLabelsAsTime(ax, plottable["time"].values, startPoint=8)
    
        #matplotlib.pyplot.ylim(0, 5)
        ax.set_yscale('log')
        
        return ax
    
    # REVISE
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
