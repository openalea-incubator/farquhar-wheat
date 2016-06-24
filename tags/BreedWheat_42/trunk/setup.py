# -*- coding: latin-1 -*-
"""

.. note::
    * use setup.py develop when tracking in-development code
    * when removing modules or data files from the project, run setup.py clean --all and delete any obsolete .pyc or .pyo.
    
"""

"""
    Information about this versioned file:
        $LastChangedBy$
        $LastChangedDate$
        $LastChangedRevision$
        $URL$
        $Id$
"""

import ez_setup
ez_setup.use_setuptools()

import sys
from setuptools import setup, find_packages

import farquharwheat

if sys.version_info < (2, 7):
    print('ERROR: Farquhar-Wheat requires at least Python 2.7 to run.')
    sys.exit(1)

if sys.version_info >= (3, 0):
    print('WARNING: Farquhar-Wheat has not been tested with Python 3.')

setup(
    name = "Farquhar-Wheat",
    version=farquharwheat.__version__,
    packages = find_packages(),
    
    install_requires = ['pandas>=0.14.0'],
    include_package_data = True,

    # metadata for upload to PyPI
    author = "C.Chambon, R.Barillot",
    author_email = "camille.chambon@grignon.inra.fr, romain.barillot@grignon.inra.fr",
    description = "Farqhuar model of wheat photosynthesis",
    long_description = "Modèle Farquhar de photosynthèse du blé",
    license = "", # TODO
    keywords = "", # TODO
    url = "https://sourcesup.renater.fr/projects/farquhar-wheat/",
    download_url = "", # TODO
)
