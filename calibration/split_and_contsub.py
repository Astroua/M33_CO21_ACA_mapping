
'''
Split out different lines and continuum subtract from line-free channels.
'''

import os
from glob import glob
from spectral_cube import Projection
from astropy.io import fits
import astropy.units as u

from tasks import split, uvcontsub

repo_path = os.path.expanduser("~/ownCloud/project_code/M33_ALMA_2017.1.00901.S/")

constants_script = os.path.join(repo_path, "constants.py")
exec(compile(open(constants_script, "rb").read(), constants_script, 'exec'))
helpers_script = os.path.join(repo_path, "calibration/imaging_helpers.py")
exec(compile(open(helpers_script, "rb").read(), helpers_script, 'exec'))

orig_dir = os.getcwd()

data_path = os.path.expanduser("~/bigdata/ekoch/M33/ALMA/ACA_Band6/reduced/")

# Load in the 12CO 30-m moment 1 map to define line-free channels
co_iram_mom1_file = os.path.expanduser("~/bigdata/ekoch/M33/co21/m33.co21_iram.mom1.fits")
co_mom1_hdu = fits.open(co_iram_mom1_file)
co_mom1 = Projection.from_hdu(co_mom1_hdu)

# Loop through the mosaics
for brick_num in range(1, 4):
    for tile_num in range(1, 6):

        # Check whether a reduced MS exists for this mosaic.
        prefix = "Brick{0}Tile{1}".format(brick_num, tile_num)

        ms_names = glob("{0}/{1}*.ms".format(data_path, prefix))

        if len(ms_names) == 0:
            print("No reduced MS found for {0}".format(prefix))
            continue

        for ms_name in ms_names:

            if "2019" in ms_name:
                spw_setup = spw_setup_2019
            elif "2017" in ms_name:
                spw_setup = spw_setup_2017
            else:
                raise ValueError("Cannot find project code in the ms name"
                                 " {0}. You need to check this!"
                                 .format(ms_name))

            # Define line free channels based on the 30-m 12CO(2-1)
            linefree_chans = \
                find_linefree_freq(ms_name, co_mom1, spw_setup,
                                   field_name='M33',
                                   pb_size=27 * u.arcsec,
                                   debug_printing=False)

            # Loop through line SPWs

            for num, line_name in enumerate(spw_setup):

                # Not splitting out continuum.
                # Will run continuum from all line-free channels
                if "Continuum" in line_name:
                    continue

                line_path = os.path.join(data_path, line_name)
                if not os.path.exists(line_path):
                    os.mkdir(line_path)

                spw_num = spw_setup[line_name]['spw_num']

                # Split out full SPW:

                outputvis_name = "{0}/{1}/{2}_{3}.ms".format(data_path,
                                                             line_name,
                                                             os.path.split(ms_name)[1].rstrip(".ms"),
                                                             line_name)

                if os.path.exists(outputvis_name):
                    print("Found split MS for {0} {1}".format(prefix,
                                                              line_name))
                else:
                    split(vis=ms_name,
                          outputvis=outputvis_name,
                          spw=spw_num,
                          intent='OBSERVE_TARGET#ON_SOURCE',
                          datacolumn='CORRECTED',
                          keepflags=True)

                # Now continuum subtract with the line-free channels

                linefree_chan = linefree_chans[line_name]

                if len(linefree_chan) == 0:
                    print("No line free channels found for {0} {1}"
                          .format(prefix, line_name))

                linefree_str = ["{0}~{1}".format(*ch) for ch in linefree_chan]
                if len(linefree_chans) > 1:
                    linefree_str = ";".join(linefree_str)
                else:
                    linefree_str = linefree_str[0]

                # Add SPW 0 for the split MS
                linefree_str = "0:{0}".format(linefree_str)

                contsubvis_name = "{0}.contsub".format(outputvis_name)

                if os.path.exists(contsubvis_name):
                    print("Found contsub MS for {0} {1}"
                          .format(prefix, line_name))
                else:
                    uvcontsub(vis=outputvis_name,
                              fitspw=linefree_str,
                              fitorder=0)
