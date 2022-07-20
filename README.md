## Install
Install from pip or manually:
```
git clone https://github.com/AlexKurek/ds9crop.git
cd ds9crop/
sudo python setup.py install
```
and add it to DS9 as any other analysis commands (http://ds9.si.edu/doc/ref/analysis.html).

## Usage
Launch DS9 e.g. like this:
```
ds9 /patchToFITSfile/file.fits -xpa unix -regions shape box
```
Create a box- or circle shaped region and simply press 'x' to save it as both FITS and 16-bit png files. ds9crop will try to connect via [XPA server](https://fossies.org/linux/ds9/xpa/doc/server.html) to DS9 instance to fetch curent scale limits. If this won't work, <-0.001, 0.01> will be set in png.
