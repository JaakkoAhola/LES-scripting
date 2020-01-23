# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 16:28:50 2017

@author: aholaj
"""
import sys
import os
import datetime

class Logger(object): # allows output to stdout and log file, by default to ${HOME}/logger.txt file
    def __init__(self, file = os.environ["HOME"] + "logger.txt" ):
        self.terminal = sys.stdout
        self.log = open(file, "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass

class TooLongError(ValueError):
    pass


def Muunnos(aika):
   AIKA=float(aika)
   DAY=(24*60*60)
   HOUR=(60*60)
   MINUTE=60

   PAIVA=AIKA//DAY
   TUNTI=(AIKA%DAY)//HOUR
   MINUUTTI=((AIKA%DAY)%HOUR)//MINUTE
   SEKUNTI=(((AIKA%DAY)%HOUR)%MINUTE)

   PAIVA    = str(int(PAIVA))
   TUNTI    = str(int(TUNTI))
   MINUUTTI = str(int(MINUUTTI))
   SEKUNTI  = str(int(SEKUNTI))


  ###
  ### Muuta seuraavan rivin print komentoa, mikali kaytat python 2 -versiota
   return PAIVA + "d" + " " + TUNTI + "h" + " " + MINUUTTI + "m"+ " " + SEKUNTI + "s"

def date(format="%Y-%m-%d"):
    return datetime.datetime.utcnow().strftime(format)

def pad(seq, target_length, padding=None):
    """Extend the sequence seq with padding (default: None) so as to make
    its length up to target_length. Return seq. If seq is already
    longer than target_length, raise TooLongError.

    >>> pad([], 5, 1)
    [1, 1, 1, 1, 1]
    >>> pad([1, 2, 3], 7)
    [1, 2, 3, None, None, None, None]
    >>> pad([1, 2, 3], 2)
    ... # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
      ...
    TooLongError: sequence too long (3) for target length 2

    """
    length = len(seq)
    if length > target_length:
        raise TooLongError("sequence too long ({}) for target length {}"
                           .format(length, target_length))
    seq.extend([padding] * (target_length - length))
    return seq

def stringToBoolean(s, precise = False):
    r = False
    string = str(s)

    if precise:
        if string == 'True':
            r = True
    else:
        if string.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'kylla', 'k']:
            r = True

    return r


def waterBallMassToDiam(m):
    from math import pi
    from numpy import power
    diam = power( 6*m/(pi*1000.), (1./3.))*1e6

    return diam # um

def waterBallVolumeToDiam(V):
    from math import pi
    from numpy import power
    diam = power( 6*V/pi, (1./3.) )*1e6

    return diam # um

def myRound(x, base = 5):
    return int(base*round(float(x)/base))

def myRoundFloat(x, prec=2, base=.5):
  return round(base * round(float(x)/base),prec)

def giveValue( z,  z1, z2, V1, V2  ):
    return ( (z -z1)*(V2-V1) + (z2-z1)*V1 ) / (z2-z1)

def degToDecim(deg,mins,secs, printing = False):
    decim = deg + mins/60. + secs/3600.
    if printing: print(decim)
    return decim

def decimToDeg(decim, printing = False):
    deg  = int(decim)
    mins = int((decim-deg)*60.)
    secs = ((decim - deg)*60. - mins)*60.
    if printing: print(str(deg) + '\u00B0' + ' ' + str(mins) + "'" + ' ' + str(round(secs,2)) + '"')
    return deg, mins, secs

def antiPodeInDecim( lat, lon ):
    latR = -lat
    if ( lon < 180. and lon > 0.):
        lonR = lon-180.
    elif ( lon <0. and lon >= -180. ):
        lonR = 180-lon
    print(latR, lonR)
    return latR, lonR
