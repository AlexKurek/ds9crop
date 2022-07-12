#!/usr/bin/env python

import sys
from astropy.io import fits
from imageio import imwrite
import pyregion
from astropy.nddata import Cutout2D
from astropy import wcs
import numpy as np

fName = sys.stdin.readline().rstrip()
# discard any ds9 qualifiers, since we can't use them
fName = re.sub(r'\[.*\]', '', fName)
selectedReg = sys.stdin.readline().rstrip()
print('Filename is', fName)
print('FG region is: ' + selectedReg)

if selectedReg == "":
    print("No region selected")
    sys.exit()

try:
    fitsFile = fits.open(fName)
except IOError as e:
    print(e)
    sys.exit()

print('Region should have a Box shape')
selectedReg = parse(selectedReg)

if len(selectedReg) != 1:
    print('More than one region detected')
    sys.exit()
if selectedReg[0].name != 'box':
    print('Region should have a Box shape; other shape detected')
    sys.exit()

selectedRegCoordList = selectedReg[0].coord_list
image = fitsFile[0].data
w = wcs.WCS(fitsFile[0].header, naxis = 2)
center = [selectedRegCoordList[0], selectedRegCoordList[1]]
siz = [selectedRegCoordList[2], selectedRegCoordList[3]]*u.deg
cutout = Cutout2D(image, center, siz, wcs=w)
fNamePart = fName[:len(fName) - 5]

# png
cutoutBitmap = cutout.data
pngFname = fNamePart + "_cutout.png"
vMin = -0.001
vMax = 0.01
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
