#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 27 16:50:23 2018

@author: aholaj
"""

from PythonMethods import zenith
import numpy as np
a = []
b = []
for d in np.arange(260,280, 0.00001):
    a.append( zenith(0., d) )
    b.append( d )

a = np.asarray(a)
b = np.asarray(b)

M = np.column_stack((a,b))

ykkos = np.ones(np.shape(a))

mini = np.argmin( np.abs(a-ykkos))

print("mini", mini)