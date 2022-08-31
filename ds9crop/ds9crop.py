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
import datetime


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
try:
    BMAJ     = fitsHeader['BMAJ']
except:
    pass
try:
    BMIN     = fitsHeader['BMIN']
except:
    pass
try:
    BSCALE   = fitsHeader['BSCALE']
except:
    pass
try:
    BZERO    = fitsHeader['BZERO']
except:
    pass
try:
    BUNIT    = fitsHeader['BUNIT']
except:
    pass
try:
    BTYPE    = fitsHeader['BTYPE']
except:
    pass
try:
    TELESCOP = fitsHeader['TELESCOP']
except:
    pass
try:
    OBSERVER = fitsHeader['OBSERVER']
except:
    pass
try:
    OBJECT   = fitsHeader['OBJECT']
except:
    pass
try:
    ORIGIN   = fitsHeader['ORIGIN']
except:
    pass
try:
    HISTORY  = fitsHeader['HISTORY']
except:
    pass
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
    print('pyds9.ds9_targets() are:', pyds9.ds9_targets())
    vMin = -0.001
    vMax = 0.01
if len(pyds9.ds9_targets()) >= 1:
    print('More thanb one instance of DS9 is running. For full functionality only one instance is supported.')
    print('Unable to fetch scale limits, using defaults:  <-0.001, 0.01>  and linear scale')
    print('pyds9.ds9_targets() are:', pyds9.ds9_targets())
    vMin = -0.001
    vMax = 0.01
if len(pyds9.ds9_targets()) == 1:
    d = pyds9.DS9()
    print('Connected to DS9 instance', str(d))
    scaleMode = d.get ('scale')
    if scaleMode != 'linear':
        print('Detected other scale mode than linear. Conversion is not supported so .png file will still be written in linear scale')
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
try:
    cutoutHdr['BMAJ']     = BMAJ
except NameError:
    pass
try:
    cutoutHdr['BMIN']     = BMIN
except NameError:
    pass
try:
    cutoutHdr['BSCALE']   = BSCALE
except NameError:
    pass
try:
    cutoutHdr['BZERO']    = BZERO
except NameError:
    pass
try:
    cutoutHdr['BUNIT']    = BUNIT
except NameError:
    pass
try:
    cutoutHdr['BTYPE']    = BTYPE
except NameError:
    pass
try:
    cutoutHdr['TELESCOP'] = TELESCOP
except NameError:
    pass
try:
    cutoutHdr['OBSERVER'] = OBSERVER
except NameError:
    pass
try:
    cutoutHdr['OBJECT']   = OBJECT
except NameError:
    pass
try:
    cutoutHdr['ORIGIN']   = ORIGIN
except NameError:
    pass
try:
    HISTORY = str(HISTORY)
    HISTORY = re.sub(r'\n', '', HISTORY)
    cutoutHdr['HISTORY']  = HISTORY
except NameError:
    pass
now = datetime.datetime.now()
nowStr = now.strftime("%Y-%m-%d %H:%M:%S")
cutoutHdr['HISTORY']  = nowStr + ' a cutout was made using ds9crop'
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
