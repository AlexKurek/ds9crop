#!/usr/bin/env python

from setuptools import setup
from setuptools.command.install import install
import os.path

DESCRIPTION = 'Export regions of FITS files as both FITS and png files'
def get_long_description():
    if os.path.exists('README.md'):
        with open('README.md') as f:
            return f.read()
    return DESCRIPTION



class PostInstall(install):
    def run(self):
        # Call parent 
        install.run(self)
        # Execute commands
        import os
        codepath = os.path.join(self.install_libbase, 'ds9crop')
        ds9path = os.path.join(self.install_data, 'ds9', 'ds9crop.ds9')
        # This will print with python setup.py install, but won't show with pip:
        # https://github.com/pypa/pip/blob/main/src/pip/_internal/utils/subprocess.py#L73
        # https://stackoverflow.com/questions/44616823/how-to-print-warnings-and-errors-when-using-setuptools-pip
        # https://stackoverflow.com/questions/59965769/print-a-message-from-setup-py-through-pip
        print('Path to .ds9 file is:', ds9path)
        os.system('sed -i -e s!REPLACE!' + codepath + '! ' + ds9path)
        os.system('chmod +x ' + codepath + '/*.py')

setup(
      name = 'ds9crop',
      author = 'Aleksander Kurek',
      description = DESCRIPTION,
      long_description = get_long_description(),
      long_description_content_type = 'text/markdown',
      url = 'https://github.com/AlexKurek/ds9crop',
      version = '0.1',
      packages = ['ds9crop'],
      platforms = 'any',
      install_requires=[
          'astropy',
          'imageio',
          'numpy',
          'pyregion',
          'pyds9',
      ],
      classifiers = [
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.8',
                 'Programming Language :: Python :: 3.9',
                 'Programming Language :: Python :: 3.10',
                 'Programming Language :: Python :: 3.11',
                 'Development Status :: 5 - Production/Stable',
                 'Environment :: Plugins',
                 'Natural Language :: English',
                 'Intended Audience :: Science/Research',
                 'Operating System :: POSIX :: Linux',
                 'Topic :: Scientific/Engineering :: Astronomy'
                 ],
      data_files = [('ds9', ['ds9crop.ds9'])],
      cmdclass = {"install": PostInstall}
      )
