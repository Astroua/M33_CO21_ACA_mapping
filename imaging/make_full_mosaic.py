
'''
Create linear mosaic of all fields.
'''

import sys
import os
from glob import glob
from spectral_cube import Projection
from astropy.io import fits

from casatasks import casalog

osjoin = os.path.join

repo_path = os.path.expanduser("~/ownCloud/project_code/M33_ALMA_2017.1.00901.S/")

constants_script = os.path.join(repo_path, "constants.py")
exec(compile(open(constants_script, "rb").read(), constants_script, 'exec'))
img_helper_script = os.path.join(repo_path, "calibration", "imaging_helpers.py")
exec(compile(open(img_helper_script, "rb").read(), img_helper_script, 'exec'))
mosaic_script = os.path.join(repo_path, "imaging", "mosaic_tools.py")
exec(compile(open(mosaic_script, "rb").read(), mosaic_script, 'exec'))
params_script = os.path.join(repo_path, "imaging/line_imaging_params.py")
exec(compile(open(params_script, "rb").read(), params_script, 'exec'))


data_path = os.path.expanduser("~/bigdata/ekoch/M33/ALMA/ACA_Band6/")

mosaic_path = osjoin(data_path, 'full_mosaic')

if not os.path.exists(mosaic_path):
    os.mkdir(mosaic_path)

# Get input params.

line_name = str(sys.argv[-6])
spec_width = str(sys.argv[-5])

convolve_to_round_beam = True if str(sys.argv[-4]) == "True" else False

# Excludes Brick 1 Tiles 3-5 which all have highly asymmetric beams.
exclude_asymm = True if str(sys.argv[-3]) == "True" else False

overwrite = True if str(sys.argv[-2]) == "True" else False

cleanup_temps = True if str(sys.argv[-1]) == "True" else False

print(f"Inputs: {line_name} {spec_width} "
      f"{convolve_to_round_beam} {exclude_asymm} {overwrite}")

# Make sure the line name is valid
if line_name not in spw_setup_2019.keys():
    raise ValueError("Line name is not found in list: {0}".format(spw_setup_2019.keys()))

if spec_width not in imaging_linedict[line_name].keys():
    raise ValueError("Spec setup not found in list defined in line_imaging_params.py: {0}".format(imaging_linedict.keys()))


mosaic_line_path = osjoin(mosaic_path, line_name)

if not os.path.exists(mosaic_line_path):
    os.mkdir(mosaic_line_path)

# Grab all pbcor images for that line and spectral width

per_mosaic_line_path = osjoin(data_path, 'per_mosaic_imaging', line_name)

images = glob(osjoin(per_mosaic_line_path,
                     "Brick*_{0}_{1}.image.pbcor".format(line_name, spec_width)))

pbs = glob(osjoin(per_mosaic_line_path,
                  "Brick*_{0}_{1}.pb".format(line_name, spec_width)))

# To estimate the noise, we'll also produce a list of non-pbcorr images
images_nopb = glob(osjoin(per_mosaic_line_path,
                          "Brick*_{0}_{1}.image".format(line_name, spec_width)))

# Should be 15
assert len(images) == 15
assert len(pbs) == 15
assert len(images_nopb) == 15

# Remove mosaics with asymmetric beams, if requested
# These are Tiles 3-5 in Brick 1
if exclude_asymm:
    output_suffix = "excludeasymmbeams"


    for tile in [3, 4, 5]:
        image_name = "Brick1Tile{0}_{1}_{2}".format(tile, line_name,
                                                    spec_width)

        images.remove("{0}/{1}.image.pbcor".format(per_mosaic_line_path, image_name))
        pbs.remove("{0}/{1}.pb".format(per_mosaic_line_path, image_name))
        images_nopb.remove("{0}/{1}.image".format(per_mosaic_line_path, image_name))

    # Should now have 12 images
    assert len(images) == 12
    assert len(pbs) == 12
    assert len(images_nopb) == 12

else:
    output_suffix = "fullmosaic"


# Convolve to a common beam. Write out into a temporary folder.
common_beam_outpath = osjoin(mosaic_line_path, "common_beam_mosaics")

if not os.path.exists(common_beam_outpath):
    os.mkdir(common_beam_outpath)


casalog.post("Convolving to a common beam.")

# Add whether the round beam is chosen to the output suffix
if convolve_to_round_beam:
    output_suffix += "_roundbeam"
    casalog.post("Will return a round beam.")
else:
    output_suffix += "_commonbeam"

comm_beam_imgs = \
    common_res_for_mosaic(images,
                          outfile_suffix=output_suffix,
                          out_path=common_beam_outpath,
                          overwrite=overwrite,
                          round_beam=convolve_to_round_beam,
                          # Requires the current dev version of radio-beam (02/04/20)
                          common_beam_kwargs={"auto_increase_epsilon": True,
                                              "max_epsilon": 5e-3,
                                              "max_iter": 20})

comm_beam_imgs_nopb = \
    common_res_for_mosaic(images_nopb,
                          outfile_suffix=output_suffix,
                          out_path=common_beam_outpath,
                          overwrite=overwrite,
                          round_beam=convolve_to_round_beam,
                          # Requires the current dev version of radio-beam (02/04/20)
                          common_beam_kwargs={"auto_increase_epsilon": True,
                                              "max_epsilon": 5e-3,
                                              "max_iter": 20})

# Hard-code in M33's centre location in deg.
ra_ctr = 23.4607
dec_ctr = 30.6583

# Produce the header for the final mosaic.
out_header = build_common_header(comm_beam_imgs,
                                 ra_ctr=ra_ctr,
                                 dec_ctr=dec_ctr,
                                 delta_ra=None,
                                 delta_dec=None,
                                 allow_big_image=False,
                                 too_big_pix=1e4,)


common_beam_outpath = osjoin(mosaic_line_path, "common_beam_mosaics")

if not os.path.exists(common_beam_outpath):
    os.mkdir(common_beam_outpath)

comm_grid_imgs = \
    common_grid_for_mosaic(comm_beam_imgs,
                           outfile_suffix=output_suffix,
                           out_path=common_beam_outpath,
                           target_hdr=out_header,
                           template_file=None,
                           # could use **kwargs here if this gets much more complicated
                           ra_ctr=None,
                           dec_ctr=None,
                           delta_ra=None,
                           delta_dec=None,
                           allow_big_image=False,
                           too_big_pix=1e4,
                           asvelocity=True,
                           interpolation='cubic',
                           axes=[-1],
                           overwrite=overwrite)

# Do the same for the pb images.
comm_grid_pbs = \
    common_grid_for_mosaic(pbs,
                           outfile_suffix=output_suffix,
                           out_path=common_beam_outpath,
                           target_hdr=out_header,
                           template_file=None,
                           # could use **kwargs here if this gets much more complicated
                           ra_ctr=None,
                           dec_ctr=None,
                           delta_ra=None,
                           delta_dec=None,
                           allow_big_image=False,
                           too_big_pix=1e4,
                           asvelocity=True,
                           interpolation='cubic',
                           axes=[-1],
                           overwrite=overwrite)

# Now we need to produce weight maps. This requires estimating the
# noise in the cube.
# We will use the centroid velocities from the IRAM CO(2-1) map to define
# line-free channels to estimate the noise from.
# Uses estimate_noise from imaging_helpers.py

# Load in the 12CO 30-m moment 1 map to define line-free channels
co_iram_mom1_file = os.path.expanduser("~/bigdata/ekoch/M33/co21/m33.co21_iram.mom1.fits")
co_mom1_hdu = fits.open(co_iram_mom1_file)
co_mom1 = Projection.from_hdu(co_mom1_hdu)

# We'll also build the input dictionary for the final mosaicing

mosaic_dict = {}

for imagename in comm_beam_imgs_nopb:

    # Find line-free channels based on padding the
    # known 12CO(2-1) velocity extent from the IRAM map
    linefree_chans = \
        find_linefree_chan_cube(imagename, co_mom1,
                                vel_pad=40 * u.km / u.s,
                                debug_printing=False)

    # Estimate noise
    noise_value = estimate_noise(imagename, linefree_chans,
                                 noise_function=np.nanstd)

    # Use the basename to make sure we're grabbing the right
    # files.

    key_name = os.path.basename(imagename).split("_")[0]

    match_names = [img for img in comm_grid_imgs if key_name in img]
    assert len(match_names) == 1
    comm_grid_img = match_names[0]

    comm_grid_imgs.remove(comm_grid_img)

    match_names = [img for img in comm_grid_pbs if key_name in img]
    assert len(match_names) == 1
    comm_grid_pb = match_names[0]

    comm_grid_pbs.remove(comm_grid_pb)

    # Mosaicing dictionary has list entries that include
    # (1) common grid image, (2) common grid PB, (3) noise estimate
    # for each map
    mosaic_dict[key_name] = [comm_grid_img, comm_grid_pb, noise_value]

if exclude_asymm:
    assert len(mosaic_dict.keys()) == 12
else:
    assert len(mosaic_dict.keys()) == 15

# Finally, mosaic it all together
outfile = osjoin(mosaic_line_path,
                 "M33_ACA_{0}_{1}_{2}.image".format(line_name, spec_width, output_suffix))

mosaic_aligned_data(mosaic_dict,
                    outfile,
                    overwrite=overwrite,
                    is_pbcorr=True)

# Cleanup temporary files

# convolve maps, etc.
if cleanup_temps:
    os.system(f"rm -r {common_beam_outpath}/*")

    # Keep the weight file. Remove the rest.
    os.system(f"rm -r {outfile}.mask")
    os.system(f"rm -r {outfile}.sum")
    os.system(f"rm -r {outfile}.temp")
