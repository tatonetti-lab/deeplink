import os
import sys

nevents = 10437
njobs = 30

neventsperjob = nevents/njobs

for i in range(0,nevents+1,neventsperjob):
    print "python src/correlated_but_not_slice.py %d:%d" % (i, i+neventsperjob)
