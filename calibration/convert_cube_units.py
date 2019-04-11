
'''
Convert to K and m/s from pipeline cubes.
'''


from astropy import log
from spectral_cube import SpectralCube
import astropy.units as u
import os
import numpy as np

from paths import (alma_aca_path, alma_aca_tiles)
from constants import line_dict

osjoin = os.path.join

# Eventually run on all tiles
# for tilename in alma_aca_tiles:
for tilename in ['Brick2-Tile1']:

    # Loop through 12CO, 13CO
    for line in ['12co', '13co']:

        log.info("On {0} {1}".format(tilename, line))

        data_path = alma_aca_path(osjoin(tilename, line), no_check=True)

        file_prefix = "{0}-{1}.cube".format(tilename.lower(), line)

        cube = SpectralCube.read(osjoin(data_path, "{}.pbcor.fits".format(file_prefix)))

        # Convert to velocity

        cube = cube.with_spectral_unit(u.m / u.s,
                                       rest_value=line_dict[line],
                                       velocity_convention='radio')

        # And convert to K from Jy/beam

        cube = cube.to(u.K)

        cube.write(osjoin(data_path, "{}.pbcor.fits".format(file_prefix)),
                   overwrite=True)
