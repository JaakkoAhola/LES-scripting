# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 15:54:25 2016

@author: aholaj
"""
##########################################
###                                    ###
### PURPOSE OF THE SCRIPT              ###
### plot profiles from sound_in files  ###
###                                    ###
##########################################

import numpy as np

import matplotlib.pyplot as plt

from FindCloudBase import calc_rh_profile

import ModDataPros as mdp

class Profiles:

    def __init__(self, file, subfolder, folder = '/home/aholaj/mounttauskansiot/voimahomemount/UCLALES-SALSA/' ):
        self.folder=folder
        self.file = file
        self.subfolder = subfolder
        #file = 'sound_in_DYCOMSIIRF02'
        #file = 'sound_in'
        filu = self.folder + "/" + self.subfolder + "/" + self.file
        f = open(filu, 'r')
    
        self.z = []
        self.t = []
        self.q = []
        self.u = []
        self.v = []
        
        
        
        
        for line in f:
            zA, tA, qA, uA, vA = line.split()
            self.z.append(float(zA))
            self.t.append(float(tA))
            self.q.append(float(qA))
            self.u.append(float(uA))
            self.v.append(float(vA))
        
            
        f.close()
        
        
        self.zu = np.column_stack(( self.z, self.u ))
        self.zv = np.column_stack(( self.z, self.v ))
        
        self.rh, self.ps = calc_rh_profile( self.t, np.multiply(np.asarray(self.q), 1.e-3),  self.z )
        self.p0 = self.z[0]
        self.z[0]=0.
    
    def getU(self):
        return self.u
    
    def getV(self):
        return self.v

    def getZU(self):
        return self.zu

    def getZV(self):
        return self.zv
    
    def getRH(self):
        return self.rh
    
    def getZ(self):
        return self.z
    
    def getQ(self):
        return self.q
    
    def getT(self):
        return self.t
    
    def getPS(self):
        return self.ps
    
    def getP0(self):
        return self.p0

    def returnWindAppr(self, height, wind):
        found = False
        i = 0
        indexUpper=0
        while ( i < len(self.z) and (not found) ) :
            if self.z[i] > height:
                found = True
                indexUpper = i
            i += 1
        
        found = False
        i = len(self.z)-1
        indexLower=0
        while ( i >= 0 and (not found) ) :
            if self.z[i] < height:
                found = True
                indexLower = i
            i -= 1
#        print 'indexLower ' + str(indexLower)
#        print 'indexUpper ' + str(indexUpper)
        if ( indexUpper - indexLower == 2):
            WindAppr = wind[indexLower+1]
        else:
            WindAppr = ( wind[indexUpper]-wind[indexLower] )/( self.z[indexUpper] - self.z[indexLower] )*( height-self.z[indexLower] ) + wind[indexLower]
#        print 'WindAppr' + str(WindAppr)
        return WindAppr
    
    def returnUAppr(self, height):
        if (height <= 3000.):
            u = self.returnWindAppr( height,self.u)
        else:
            u = 0. #10.*np.random.random()
        return u

    def returnVAppr(self, height):
        if (height <= 3000.):
            v = self.returnWindAppr( height,self.v)
        else:
            v = 0. # -10.*np.random.random()
        return v
                    
            

    def plot(self):
    
        
        mdp.plottaa( self.t, self.z, tit = 'Pot. temp.', xl = 'potential temperature [K]', yl = 'height [m]', markers=False, uusikuva = True, LEGEND = True )
        
        mdp.plottaa( self.q, self.z, tit = 'Total water mixing ratio', xl = 'mix. rat. [g/kg]', yl = 'height [m]', markers=False, uusikuva = True, LEGEND = True )
        
        mdp.plottaa( self.rh, self.z, tit = 'Relative humidity', xl = 'rel. humid. [%]', yl = 'height [m]', markers=False, uusikuva = True, LEGEND = True )
        
        mdp.plottaa( self.u, self.z, tit = 'Horizontal wind U', xl = 'wind [m/s]', yl = 'height [m]', markers=False, uusikuva = True, LEGEND = True )
        
        mdp.plottaa( self.v, self.z, tit = 'Horizontal wind U', xl = 'wind [m/s]', yl = 'height [m]', markers=False, uusikuva = True, LEGEND = True )
        
        
        mdp.plot_lopetus()

    # write to sound_in    
    
    def writeNewSoundIn(self, file, z, temp, wc, u, v):
        filu = self.folder + "/" + self.subfolder + "/" + file
        f = open(filu, 'w')
        
        for k in range(len(z)):
            
            row= ' {0:15f} {1:15.6f} {2:15.6f} {3:15.6f} {4:15.6f}\n'.format( \
                                            z[k],                             \
                                            temp[k],                          \
                                            wc[k],                            \
                                            u[k],                             \
                                            v[k]                              )
            f.write(row)                                        
        
        f.close()


#def giveU():
#    return
#
#
#if __name__ == "__main__":
#    main()
#print z