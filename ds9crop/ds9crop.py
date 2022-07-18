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
w = wcs.WCS(fitsFile[0].header, naxis = 2)
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
    print('Unable to fetch scale limits, using default  <-0.001, 0.01>  and linear scale')
    vMin = -0.001
    vMax = 0.01
else:
    d = pyds9.DS9()
    print('Connected to DS9 instance', str(d))
    scaleMode = d.get ('scale')
    if scaleMode != 'linear':
        print('Detected other scale mode that linear. Conversion is not supported so png will still be written in linear scale')
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
hdu.writeto(fitsFname, overwrite = True)


path, filename = os.path.split(fName)
print('Done. Check:', path + '/')
