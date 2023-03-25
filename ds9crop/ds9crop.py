#!/usr/bin/env python

"""
A simple plugin for DS9. It allows to export a region as both FITS and png files
"""

import os
import re
import sys
import datetime
from pathlib import Path

import numpy as np
import pyregion
from astropy import coordinates, wcs
from astropy.io import fits
from astropy.nddata import Cutout2D
from imageio import imwrite
import pyds9


f_name = sys.stdin.readline().rstrip()
# discard any ds9 qualifiers, since we can't use them
f_name = re.sub(r'\[.*\]', '', f_name)
selected_reg = sys.stdin.readline().rstrip()
print('Filename is:', f_name)
print('Region is:', selected_reg)
f_namePart = f_name[:len(f_name) - 5]

if selected_reg == "":
    print("No region detected")
    sys.exit()

try:
    fits_file = fits.open(f_name)
except IOError as e:
    print(e)
    sys.exit()
image = np.squeeze(fits_file[0].data)
fits_header = fits_file[0].header
fits_file.close()
w = wcs.WCS(fits_header, naxis = 2)
try:
    BMAJ     = fits_header['BMAJ']
except:
    pass
try:
    BMIN     = fits_header['BMIN']
except:
    pass
try:
    BPA      = fits_header['BPA']
except:
    pass
try:
    BSCALE   = fits_header['BSCALE']
except:
    pass
try:
    BZERO    = fits_header['BZERO']
except:
    pass
try:
    BUNIT    = fits_header['BUNIT']
except:
    pass
try:
    BTYPE    = fits_header['BTYPE']
except:
    pass
try:
    DATE_MAP = fits_header['DATE-MAP']
except:
    pass
try:
    RESTFRQ  = fits_header['RESTFRQ']
except:
    pass
try:
    TELESCOP = fits_header['TELESCOP']
except:
    pass
try:
    OBSERVER = fits_header['OBSERVER']
except:
    pass
try:
    OBJECT   = fits_header['OBJECT']
except:
    pass
try:
    ORIGIN   = fits_header['ORIGIN']
except:
    pass
try:
    HISTORY  = fits_header['HISTORY']
except:
    pass

selected_reg = pyregion.parse(selected_reg)
selected_reg_coord_list = selected_reg[0].coord_list
if len(selected_reg) > 1:
    print('More than one region detected')
    sys.exit()
if (selected_reg[0].name != 'box') and (selected_reg[0].name != 'circle'):
    print('Only box or circle shaped regions are supported')
    sys.exit()
if (selected_reg[0].name == 'circle'):
    print('Circular region detected. Fitting a bounding box')
    selected_reg_coord_list = [selected_reg_coord_list[0], selected_reg_coord_list[1], 2*selected_reg_coord_list[2], 2*selected_reg_coord_list[2], 0] # center X, center Y, width, height, angle


center = coordinates.SkyCoord.from_pixel(selected_reg_coord_list[0], selected_reg_coord_list[1], wcs = w)
print('Center is:', center)
siz = [selected_reg_coord_list[3], selected_reg_coord_list[2]]
cutout = Cutout2D(image, center, siz, wcs = w)
del(image)

# fits
hdu = fits.PrimaryHDU(data = cutout.data, header = cutout.wcs.to_header())
fitsFname = f_namePart + "_cutout.fits"
cutout_hdr = hdu.header
try:
    cutout_hdr['BMAJ']     = BMAJ
except NameError:
    pass
try:
    cutout_hdr['BMIN']     = BMIN
except NameError:
    pass
try:
    cutout_hdr['BPA']      = BPA
except NameError:
    pass
try:
    cutout_hdr['BSCALE']   = BSCALE
except NameError:
    pass
try:
    cutout_hdr['BZERO']    = BZERO
except NameError:
    pass
try:
    cutout_hdr['BUNIT']    = BUNIT
except NameError:
    pass
try:
    cutout_hdr['BTYPE']    = BTYPE
except NameError:
    pass
try:
    cutout_hdr['DATE-MAP'] = DATE_MAP
except NameError:
    pass
try:
    cutout_hdr['RESTFRQ']  = RESTFRQ
except NameError:
    pass
try:
    cutout_hdr['TELESCOP'] = TELESCOP
except NameError:
    pass
try:
    cutout_hdr['OBSERVER'] = OBSERVER
except NameError:
    pass
try:
    cutout_hdr['OBJECT']   = OBJECT
except NameError:
    pass
try:
    cutout_hdr['ORIGIN']   = ORIGIN
except NameError:
    pass
try:
    HISTORY = str(HISTORY)
    HISTORY = re.sub(r'\n', '', HISTORY)
    cutout_hdr['HISTORY']  = HISTORY
except NameError:
    pass
now = datetime.datetime.now()
now_str = now.strftime("%Y-%m-%d %H:%M:%S")
cutout_hdr['HISTORY']  = now_str + ' a cutout was made using ds9crop'
hdu.writeto(fitsFname, overwrite = True)

# png
cutout_bmp = cutout.data
png_f_name = f_namePart + "_cutout.png"
if not (pyds9.ds9_targets()):
    print('Unable to retrieve scale limits, using defaults:  <-0.001, 0.01>  and linear scale')
    print('pyds9.ds9_targets() are:', pyds9.ds9_targets())
    vMin = -0.001
    vMax = 0.01
if (pyds9.ds9_targets()) and (len(pyds9.ds9_targets())) >= 1:
    print('More than one instance of DS9 is running. Only one instance is supported for full functionality.')
    print('Unable to retrieve scale limits, using defaults:  <-0.001, 0.01>  and linear scale')
    print('pyds9.ds9_targets() are:', pyds9.ds9_targets())
    vMin = -0.001
    vMax = 0.01
if (pyds9.ds9_targets()) and (len(pyds9.ds9_targets())) == 1:
    d = pyds9.DS9()
    print('Connected to DS9 instance', str(d))
    scaleMode = d.get ('scale')
    if scaleMode != 'linear':
        print('Detected scale mode other than linear. Conversion is not supported so .png file will still be written in linear scale')
    scaleLimits = d.get ('scale limits')
    scaleLimits = scaleLimits.split(' ')
    vMin = scaleLimits[0]
    vMax = scaleLimits[1]
    vMin = float(re.sub(r'[^\x00-\x7F]+','-', vMin))
    vMax = float(re.sub(r'[^\x00-\x7F]+','-', vMax))
    print('Fetched scale limits:',  str(vMin) + ',', vMax)
cutout_bmp[cutout_bmp > vMax] = vMax
cutout_bmp[cutout_bmp < vMin] = vMin
cutout_bmp = (cutout_bmp - vMin)/(vMax - vMin)
cutout_bmp = ((2**16-1)*cutout_bmp).astype(np.uint16)
cutout_bmp = cutout_bmp[::-1, :]
imwrite(png_f_name, cutout_bmp, compression = 0)


# verify
path_png  = Path(png_f_name)
path_fits = Path(fitsFname)
if ( path_png.is_file() and path_fits.is_file() ):
    # path, filename = os.path.split(f_name)
    # print('Done. Check:', path + '/')
    print('Done. Check input folder for cutouts.')
else:
    sys.exit('Something went wrong, unable to find one or both cutouts.')


# open cutouts
# fits
try:
    if ( pyds9.ds9_targets() ):
        args = ['ds9', '-scale', 'limits', scaleLimits[0], scaleLimits[1], path_fits]
        print(args)
        print('Using fetched scale limits in popup windows.')
    else:
        args = ['ds9', '-scale', 'limits', str(vMin), str(vMax), path_fits]
        print('Using default scale limits <-0.001, 0.01> in popup windows.')
    subprocess.Popen(args)
except:
   print('Unable to open FITS cutout.')

# png
try:
   args = ['eog', path_png]
   subprocess.Popen(args)
except:
   print('Unable to open PNG cutout in Eye of Gnome (default image viewer in Ubuntu).')
