#!/usr/bin/env python

from setuptools import setup
from setuptools.command.install import install

class post_install(install):
    def run(self):
        # Call parent 
        install.run(self)
        # Execute commands
        import os
        codepath = os.path.join(self.install_libbase, 'ds9crop')
        ds9path = os.path.join(self.install_data, 'ds9', 'ds9crop.ds9')
        print('Path to .ds9 file is', ds9path)
        os.system('sed -i -e s!REPLACE!' + codepath + '! ' + ds9path)
        os.system('chmod +x ' + codepath + '/*.py')

setup(name='ds9crop',
      author = 'Aleksander Kurek',
      description = 'Exporting regions as FITS and png',
      download_url = '',
      version = '0.1',
      packages = ['ds9crop'],
      install_requires = ['astropy', 'imageio', 'numpy', 'pyregion'],
      data_files = [('ds9', ['ds9crop.ds9'])],
      cmdclass = {"install": post_install}
      )