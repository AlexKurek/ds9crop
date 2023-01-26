## Install
Install using pip:
```
sudo pip install git+https://github.com/AlexKurek/ds9crop
```
or manually:
```
git clone https://github.com/AlexKurek/ds9crop.git
cd ds9crop/
sudo python setup.py install
```
and add it to DS9 as any other analysis commands (http://ds9.si.edu/doc/ref/analysis.html).

## Usage
Launch DS9 e.g. like this:
```
ds9 /patchToFITSfile/file.fits -xpa unix -regions shape box -scale limits -0.001 0.01 &
```
Create a box- or circle shaped region and simply press 'x' to save it as both FITS and 16-bit png files. ds9crop will try to connect via [XPA server](https://fossies.org/linux/ds9/xpa/doc/server.html) to DS9 instance to fetch curent scale limits. If this won't work, <-0.001, 0.01> will be set in saved png file and both popup windows.

![Zrzut ekranu 2023-01-26 100555](https://user-images.githubusercontent.com/45330694/214797743-707c3ca4-13bf-462d-b3e6-68c7c681858b.png)
