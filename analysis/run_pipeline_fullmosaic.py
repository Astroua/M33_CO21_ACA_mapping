
from astropy import log
from astropy.io import fits
from spectral_cube import SpectralCube
from radio_beam import Beam
import astropy.units as u
import os
import numpy as np

from cube_analysis import run_pipeline

osjoin = os.path.join

repo_path = os.path.expanduser("~/ownCloud/project_code/M33_ALMA_2017.1.00901.S/")

constants_script = os.path.join(repo_path, "constants.py")
exec(compile(open(constants_script, "rb").read(), constants_script, 'exec'))
img_helper_script = os.path.join(repo_path, "calibration", "imaging_helpers.py")
exec(compile(open(img_helper_script, "rb").read(), img_helper_script, 'exec'))
params_script = os.path.join(repo_path, "imaging/line_imaging_params.py")
exec(compile(open(params_script, "rb").read(), params_script, 'exec'))

data_path = os.path.expanduser("~/bigdata/ekoch/M33/ALMA/ACA_Band6/")

mosaic_path = osjoin(data_path, 'full_mosaic')

if not os.path.exists(mosaic_path):
    raise ValueError("Path to full mosaics does not exist.")

os.chdir(osjoin(mosaic_path, 'logs'))

# Load in the 12CO 30-m moment 1 map to define line-free channels
co_iram_mom1_file = os.path.expanduser("~/bigdata/ekoch/M33/co21/m33.co21_iram.mom1.fits")
co_mom1_hdu = fits.open(co_iram_mom1_file)
co_mom1 = Projection.from_hdu(co_mom1_hdu)


# min_mask_width = 5.0 * u.km / u.s

# Loop through line + spectral widths.
asymm_strs = {True: "excludeasymmbeams",
              False: "fullmosaic"}
beam_strs = {False: "roundbeam",
             True: "commonbeam"}

for line in imaging_linedict:
    # if "CO" not in line:
    #     continue
    for spec in imaging_linedict[line]:

        for excasymm in [True, False]:
            for rndbm in [True, False]:

                # See if that image exists.
                prefix = f"M33_ACA_{line}_{spec}_{asymm_strs[excasymm]}_{beam_strs[rndbm]}"

                image_name = f"{mosaic_path}/{line}/{prefix}.image_K.fits"

                if not os.path.exists(f"{image_name}"):
                    print(f"Did not find mosaic for {prefix} {line} {spec}")
                    continue

                fits_image = f"{image_name}.image.pbcor.fits"
                fits_image_K = f"{image_name}.image.pbcor_K.fits"

                # Load in the noise map
                noise_map_name = f"{mosaic_path}/{line}/{prefix}.image.noise_K.fits"

                noise_map = SpectralCube.read(noise_map_name).filled_data[:]

                # noise_map = Projection.from_hdu(fits.open(noise_map_name))
                # noise_map = noise_map.quantity

                cube = SpectralCube.read(image_name)
                cube = cube.with_spectral_unit(u.km / u.s)

                # Use a erosion element just a bit smaller than the true beam
                # kern_beam = Beam(beam.major * 0.7, beam.minor * 0.7, beam.pa)
                kern_beam = cube.beam
                # All square pixels
                pix_scale = np.abs(cube.header['CDELT2']) * u.deg
                kernel = kern_beam.as_tophat_kernel(pix_scale).array > 0

                spec_width = np.abs(np.diff(cube.spectral_axis)[0])
                del cube

                # min_chan = int(np.floor((min_mask_width / spec_width).value))
                min_chan = 3

                log.info(f"Masking and moments for {prefix}")

                fits_source_mask = f"{mosaic_path}/{line}/{prefix}.image_K_source_mask.fits"
                if os.path.exists(fits_source_mask):
                    print("Found existing signal mask for"
                          f"{image_name}. Skipping.")
                    continue

                # One beam over the minimum number of channels.
                min_pix = kernel.sum() * min_chan

                run_pipeline(image_name,
                             osjoin(mosaic_path, line),
                             masking_kwargs={"method": "ppv_dilation",
                                             "save_cube": True,
                                             "is_huge": False,
                                             "noise_map": noise_map,
                                             "min_sig": 3,
                                             "max_sig": 5,
                                             "min_pix": min_pix,
                                             "min_pix_high": int(0.85 * kernel.sum()),
                                             "min_chan": min_chan,
                                             "verbose": False,
                                             "roll_along_spec": True,
                                             "expand_spatial": True,
                                             },
                             moment_kwargs={"num_cores": 1,
                                            "verbose": True,
                                            "make_peakvels": False})
