#!/usr/bin/env python

import os
import sys
from astropy.io import fits
from astropy.nddata import Cutout2D
from astropy import coordinates, wcs
from imageio import imwrite
import pyregion
import numpy as np
import re
import pyds9
from pathlib import Path
import subprocess


fName = sys.stdin.readline().rstrip()
# discard any ds9 qualifiers, since we can't use them
fName = re.sub(r'\[.*\]', '', fName)
selectedReg = sys.stdin.readline().rstrip()
print('Filename is:', fName)
print('Region is:', selectedReg)
fNamePart = fName[:len(fName) - 5]

if selectedReg == "":
    print("No region detected")
    sys.exit()

try:
    fitsFile = fits.open(fName)
except IOError as e:
    print(e)
    sys.exit()
image = np.squeeze(fitsFile[0].data)
fitsHeader = fitsFile[0].header
w = wcs.WCS(fitsHeader, naxis = 2)
BSCALE   = fitsHeader['BSCALE']
BZERO    = fitsHeader['BZERO']
BUNIT    = fitsHeader['BUNIT']
BTYPE    = fitsHeader['BTYPE']
TELESCOP = fitsHeader['TELESCOP']
OBSERVER = fitsHeader['OBSERVER']
OBJECT   = fitsHeader['OBJECT']
ORIGIN   = fitsHeader['ORIGIN']
HISTORY  = fitsHeader['HISTORY']
fitsFile.close()

selectedReg = pyregion.parse(selectedReg)
selectedRegCoordList = selectedReg[0].coord_list
if len(selectedReg) > 1:
    print('More than one region detected')
    sys.exit()
if (selectedReg[0].name != 'box') and (selectedReg[0].name != 'circle'):
    print('Only box or circle shaped regions are supported')
    sys.exit()
if (selectedReg[0].name == 'circle'):
    print('Circle shaped region detected. Fitting a bounding box')
    selectedRegCoordList = [selectedRegCoordList[0], selectedRegCoordList[1], 2*selectedRegCoordList[2], 2*selectedRegCoordList[2], 0] # center X, center Y, width, height, angle


center = coordinates.SkyCoord.from_pixel(selectedRegCoordList[0], selectedRegCoordList[1], wcs = w)
print('Center is:', center)
siz = [selectedRegCoordList[3], selectedRegCoordList[2]]
cutout = Cutout2D(image, center, siz, wcs = w)


# png
cutoutBitmap = cutout.data
pngFname = fNamePart + "_cutout.png"
if not (pyds9.ds9_targets()):
    print('Unable to fetch scale limits, using defaults:  <-0.001, 0.01>  and linear scale')
    vMin = -0.001
    vMax = 0.01
else:
    d = pyds9.DS9()
    print('Connected to DS9 instance', str(d))
    scaleMode = d.get ('scale')
    if scaleMode != 'linear':
        print('Detected other scale mode than linear. Conversion is not supported so png file will still be written in linear scale')
    scaleLimits = d.get ('scale limits')
    scaleLimits = scaleLimits.split(' ')
    vMin = scaleLimits[0]
    vMax = scaleLimits[1]
    vMin = float(re.sub(r'[^\x00-\x7F]+','-', vMin))
    vMax = float(re.sub(r'[^\x00-\x7F]+','-', vMax))
    print('Fetched scale limits:',  str(vMin) + ',', vMax)
cutoutBitmap[cutoutBitmap > vMax] = vMax
cutoutBitmap[cutoutBitmap < vMin] = vMin
cutoutBitmap = (cutoutBitmap - vMin)/(vMax - vMin)
cutoutBitmap = ((2**16-1)*cutoutBitmap).astype(np.uint16)
cutoutBitmap = cutoutBitmap[::-1, :]
imwrite(pngFname, cutoutBitmap, compression = 0)

# fits
hdu = fits.PrimaryHDU(data = cutout.data, header = cutout.wcs.to_header())
fitsFname = fNamePart + "_cutout.fits"
cutoutHdr = hdu.header
cutoutHdr['BSCALE']   = BSCALE
cutoutHdr['BZERO']    = BZERO
cutoutHdr['BUNIT']    = BUNIT
cutoutHdr['BTYPE']    = BTYPE
cutoutHdr['TELESCOP'] = TELESCOP
cutoutHdr['OBSERVER'] = OBSERVER
cutoutHdr['OBJECT']   = OBJECT
cutoutHdr['ORIGIN']   = ORIGIN
HISTORY = str(HISTORY)
HISTORY = re.sub(r'\n', '', HISTORY)
cutoutHdr['HISTORY']  = HISTORY
cutoutHdr['HISTORY']  = 'After that a cutout was made using ds9crop'
hdu.writeto(fitsFname, overwrite = True)


# verify
pathPng  = Path(pngFname)
pathFits = Path(fitsFname)
if ( pathPng.is_file() and pathFits.is_file() ):
    # path, filename = os.path.split(fName)
    # print('Done. Check:', path + '/')
    print('Done. Check input folder for cutouts.')
else:
    sys.exit('Something went wrong, unable to find one or both cutouts.')


# open cutouts
# fits
if ( pyds9.ds9_targets() ):
    args = ['ds9', '-scale', 'limits', scaleLimits[0], scaleLimits[1], pathFits]
    print(args)
    print('Using fetched scale limits in new ds9 window.')
else:
    args = ['ds9', pathFits]
    print('Using auto scale limits in new FITS ds9 window.')
subprocess.Popen(args)

# png
try:
   args = ['eog', pathPng]
   subprocess.Popen(args)
except:
   print('Unable to open PNG cutout in Eye of Gnome (default image viewer in Ubuntu).')
