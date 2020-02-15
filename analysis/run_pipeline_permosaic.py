
from astropy import log
from spectral_cube import SpectralCube
from radio_beam import Beam
import astropy.units as u
import os
import numpy as np

from cube_analysis import run_pipeline
from cube_analysis.masking import common_beam_convolve

from casatasks import exportfits

osjoin = os.path.join

repo_path = os.path.expanduser("~/ownCloud/project_code/M33_ALMA_2017.1.00901.S/")

constants_script = os.path.join(repo_path, "constants.py")
exec(compile(open(constants_script, "rb").read(), constants_script, 'exec'))
img_helper_script = os.path.join(repo_path, "calibration", "imaging_helpers.py")
exec(compile(open(img_helper_script, "rb").read(), img_helper_script, 'exec'))
mosaic_script = os.path.join(repo_path, "imaging", "mosaic_tools.py")
params_script = os.path.join(repo_path, "imaging/line_imaging_params.py")
exec(compile(open(params_script, "rb").read(), params_script, 'exec'))

data_path = os.path.expanduser("~/bigdata/ekoch/M33/ALMA/ACA_Band6/")

permosaic_path = osjoin(data_path, 'per_mosaic_imaging')

# Load in the 12CO 30-m moment 1 map to define line-free channels
co_iram_mom1_file = os.path.expanduser("~/bigdata/ekoch/M33/co21/m33.co21_iram.mom1.fits")
co_mom1_hdu = fits.open(co_iram_mom1_file)
co_mom1 = Projection.from_hdu(co_mom1_hdu)


min_mask_width = 5.0 * u.km / u.s

# Loop through line + spectral widths.

for line in imaging_linedict:
    # if "CO" not in line:
    #     continue
    for spec in imaging_linedict[line]:

        for brick in range(1, 4):
            for tile in range(1, 6):

                # See if that image exists.
                prefix = "Brick{0}Tile{1}".format(brick, tile)

                image_name = f"{permosaic_path}/{line}/{prefix}_{line}_{spec}"

                if not os.path.exists(f"{image_name}.image.pbcor"):
                    print(f"Did not find image for {prefix} {line} {spec}")
                    continue

                fits_image = f"{image_name}.image.pbcor.fits"
                fits_image_K = f"{image_name}.image.pbcor_K.fits"

                need_export = not os.path.exists(fits_image_K)
                if need_export:
                    exportfits(imagename=f"{image_name}.image.pbcor",
                               fitsimage=fits_image,
                               velocity=True,
                               optical=False,
                               dropdeg=True,
                               history=False,
                               overwrite=True)

                    cube = SpectralCube.read(fits_image)
                    cube.allow_huge_operations = True
                    cube = cube.to(u.K)
                    # Also convolve to a common beam.
                    com_beam = cube.beams.common_beam(auto_increase_epsilon=True,
                                                      max_epsilon=5e-3,
                                                      max_iter=20)
                    cube = cube.convolve_to(com_beam)
                    cube.write(fits_image_K, overwrite=True)

                    # Remove the Jy/beam fits cube.
                    # We're not using it for anything after this.
                    os.system(f"rm {fits_image}")

                # Same for the PB cube
                fits_imagepb = f"{image_name}.pb.fits"

                need_export = not os.path.exists(fits_imagepb)
                if need_export:
                    exportfits(imagename=f"{image_name}.pb",
                               fitsimage=fits_imagepb,
                               velocity=True,
                               optical=False,
                               dropdeg=True,
                               history=False,
                               overwrite=True)

                # Estimate noise level

                linefree_chans = \
                    find_linefree_chan_cube(f"{image_name}.image", co_mom1,
                                            vel_pad=spw_setup_2017[line]['vel_pad'],
                                            debug_printing=False)

                # Estimate noise
                noise_value = estimate_noise(f"{image_name}.image",
                                             linefree_chans,
                                             noise_function=np.nanstd)

                cube = SpectralCube.read(fits_image_K)
                cube = cube.with_spectral_unit(u.km / u.s)

                # Convert noise to K.
                if hasattr(cube, "beams"):
                    beam = cube.beams.common_beam()
                    jytok_factor = beam.jtok(spw_setup_2019[line]['restfreq'])
                else:
                    beam = cube.beam
                    jytok_factor = cube.beam.jtok(spw_setup_2019[line]['restfreq'])

                noise_value = noise_value * jytok_factor

                if np.isnan(noise_value):
                    raise ValueError("Found noise to be nan")

                # Make a noise map by dividing out the pb
                # 2017 data has nan channels. Continue through
                # cube until finite values are found
                pb_cube = fits.open(fits_imagepb)[0]
                for i in range(pb_cube.shape[0]):
                    pb_plane = pb_cube.data[i]
                    if np.isfinite(pb_plane).any():
                        break

                noise_map = noise_value / pb_plane

                # Use a erosion element just a bit smaller than the true beam
                # kern_beam = Beam(beam.major * 0.7, beam.minor * 0.7, beam.pa)
                kern_beam = beam
                # All square pixels
                pix_scale = np.abs(cube.header['CDELT2']) * u.deg
                kernel = kern_beam.as_tophat_kernel(pix_scale).array > 0

                spec_width = np.abs(np.diff(cube.spectral_axis)[0])
                del cube

                min_chan = int(np.floor((min_mask_width / spec_width).value))

                log.info(f"Masking and moments for {tile} {line} cube")

                fits_source_mask = f"{image_name}.image.pbcor_K_source_mask.fits"
                if os.path.exists(fits_source_mask):
                    print("Found existing signal mask for"
                          f"{image_name}. Skipping.")
                    continue

                run_pipeline(fits_image_K,
                             osjoin(permosaic_path, line),
                             masking_kwargs={"method": "ppv_dilation",
                                             "save_cube": True,
                                             "is_huge": False,
                                             "noise_map": noise_map,
                                             "min_sig": 3,
                                             "max_sig": 5,
                                             "min_pix": kernel.sum(),
                                             "min_pix_high": int(0.85 * kernel.sum()),
                                             "min_chan": min_chan,
                                             "verbose": False,
                                             "roll_along_spec": True,
                                             },
                             moment_kwargs={"num_cores": 1,
                                            "verbose": True,
                                            "make_peakvels": False})
