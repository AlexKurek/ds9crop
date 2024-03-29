## Installation
<!--- ds9crop.ds9 is not copied --->
`pip install git+https://github.com/AlexKurek/ds9crop` in not working!

### Global Install
Install using pip:
```
git clone https://github.com/AlexKurek/ds9crop.git
cd ds9crop/
sudo pip install .
```
or manually ([deprecated](https://blog.ganssle.io/articles/2021/10/setup-py-deprecated.html#summary) but working):
```
git clone https://github.com/AlexKurek/ds9crop.git
cd ds9crop/
sudo python setup.py install
```
and add it to DS9 like any other analysis commands (http://ds9.si.edu/doc/ref/analysis.html).
### Single user install
```
git clone https://github.com/AlexKurek/ds9crop.git
cd ds9crop/
pip install .
```
Note that the .ds9 file is copied to `~/.local/ds9/` instead of `/usr/local/ds9/`.
## Usage
Start DS9 e.g. like this:
```
ds9 /patchToFITSfile/file.fits -xpa unix -regions shape box -scale limits -0.001 0.01 &
```
Create a box- or circle shaped region and simply press 'x' to save it as both FITS and 16-bit png files. ds9crop will try to connect to the DS9 instance via the [XPA server](https://fossies.org/linux/ds9/xpa/doc/server.html) to get the current scale limits. If this doesn't work, <-0.001, 0.01> will be set in the saved png file and in both popup windows.
<p align="center">
  <img alt="Eagle Nebula from Hubble Space Telescope, 656 nm filter, source: https://noirlab.edu/public/products/education/edu008/" src="https://user-images.githubusercontent.com/45330694/214798789-aa419afd-2102-4370-994a-f758edfeee9a.jpg" />
</p>
