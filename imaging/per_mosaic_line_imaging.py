
'''
Loop through imaging all 15 mosaics separately imaging
to setup linear mosaicing in the image plane.

Cmd line arguments set which brick + tile and line is to be imaged.

Creates:

1. Dirty cube
2. Stage 1 MS clean down to 4-sigma with automasking
3. Stage 2 singe-scale clean down to 1-sigma with automasking.

'''

import os
from glob import glob
import sys
import numpy as np

from tasks import tclean

osjoin = os.path.join

repo_path = os.path.expanduser("~/ownCloud/project_code/M33_ALMA_2017.1.00901.S/")

constants_script = os.path.join(repo_path, "constants.py")
exec(compile(open(constants_script, "rb").read(), constants_script, 'exec'))
helpers_script = os.path.join(repo_path, "calibration/imaging_helpers.py")
exec(compile(open(helpers_script, "rb").read(), helpers_script, 'exec'))
params_script = os.path.join(repo_path, "imaging/line_imaging_params.py")
exec(compile(open(params_script, "rb").read(), params_script, 'exec'))

orig_dir = os.getcwd()

data_path = os.path.expanduser("~/bigdata/ekoch/M33/ALMA/ACA_Band6/")

brick_num = int(sys.argv[-5])
tile_num = int(sys.argv[-4])
line_name = sys.argv[-3]
spec_width = sys.argv[-2]
redo_existing_imaging = True if sys.argv[-1] == "True" else False

print("Inputs : {}".format(sys.argv[-5:]))

if brick_num < 1 or brick_num > 3:
    raise ValueError("Brick number must be 1, 2, or 3.")

if tile_num < 1 or tile_num > 5:
    raise ValueError("Brick number must between 1 and 5.")

if line_name not in spw_setup_2019.keys():
    raise ValueError("Line name is not found in list: {0}".format(spw_setup_2019.keys()))

if spec_width not in imaging_linedict[line_name].keys():
    raise ValueError("Spec setup not found in list defined in line_imaging_params.py: {0}".format(imaging_linedict.keys()))

# Check whether a reduced MS exists for this mosaic.
prefix = "Brick{0}Tile{1}".format(brick_num, tile_num)

ms_names = glob("{0}/reduced/{1}/{2}*.ms.contsub".format(data_path, line_name, prefix))

if len(ms_names) == 0:
    print("No reduced MS found for {0}".format(prefix))
    sys.exit(0)

# Check output path exists
mosaic_path = os.path.join(data_path, '')

image_path = osjoin(data_path, 'per_mosaic_imaging')
if not os.path.exists(image_path):
    os.mkdir(image_path)

line_image_path = osjoin(image_path, line_name)
if not os.path.exists(line_image_path):
    os.mkdir(line_image_path)

imaging_params = imaging_linedict[line_name][spec_width]

# Find the pointing centre for the mosaic
ptg_centre = get_mosaic_centre(ms_names[0],
                               return_string=True,
                               field_name='M33')

pb_limit = 0.05

# Stage 0: Dirty cube

stage1_path = osjoin(line_image_path, 'stage1')
if not os.path.exists(stage1_path):
    os.mkdir(stage1_path)

dirtyimage_name = "{0}/dirty/{1}_{2}_{3}_dirty".format(line_image_path, prefix,
                                                       line_name, spec_width)

# Check if the residual exists. If so, remove it when needed. Otherwise, skip.
dirty_residual_name = "{}.residual".format(dirtyimage_name)

if os.path.exists(dirty_residual_name) and redo_existing_imaging:
    # Delete existing:
    for suff in ['image', 'model', 'mask', 'pb', 'psf',
                 'residual', 'weight', 'sumwt', "results_dict.npy"]:

        orig_image = "{0}.{1}".format(dirtyimage_name, suff)

        os.system("rm -r {}".format(orig_image))

if not os.path.exists(dirty_residual_name):

    dirty_tclean_dict = \
        tclean(vis=ms_names,
               field='M33',
               spw='0',
               intent='OBSERVE_TARGET#ON_SOURCE',
               datacolumn='corrected',
               imagename=dirtyimage_name,
               imsize=imaging_params['imsize'],
               cell=imaging_params['cellsize'],
               phasecenter=ptg_centre,
               nchan=imaging_params['nchan'],
               start=imaging_params['start'],
               width=imaging_params['width'],
               specmode='cube',
               outframe='LSRK',
               gridder='mosaic',
               chanchunks=-1,
               mosweight=True,
               pblimit=pb_limit,
               pbmask=pb_limit,
               restoration=False,
               pbcor=False,
               weighting='briggs',
               robust=0.5,
               niter=0,
               usemask='pb',
               interactive=0,
               savemodel='none',
               parallel=False,
               calcres=True,
               calcpsf=True,
               smallscalebias=0.6
               )

    # Save dictionary as numpy file
    np.save(dirtyimage_name + ".results_dict.npy", dirty_tclean_dict)

# Stage 1: MS clean down to ~4 sigma.
cleanimage_name = "{0}/{1}_{2}_{3}".format(line_image_path, prefix,
                                           line_name, spec_width)

clean_residual_name = "{}.residual".format(cleanimage_name)

if os.path.exists(clean_residual_name) and redo_existing_imaging:
    # Delete existing:
    for suff in ['image', 'model', 'mask', 'pb', 'psf',
                 'residual', 'weight', 'sumwt', 'stage1.results_dict.npy',
                 'stage2.results_dict.npy']:

        orig_image = "{0}.{1}".format(dirtyimage_name, suff)

        os.system("rm -r {}".format(orig_image))

if not os.path.exists(clean_residual_name):

    stage1_tclean_dict = \
        tclean(vis=ms_names,
               field='M33',
               spw='0',
               intent='OBSERVE_TARGET#ON_SOURCE',
               datacolumn='corrected',
               imagename=cleanimage_name,
               imsize=imaging_params['imsize'],
               cell=imaging_params['cellsize'],
               phasecenter=ptg_centre,
               nchan=imaging_params['nchan'],
               start=imaging_params['start'],
               width=imaging_params['width'],
               specmode='cube',
               outframe='LSRK',
               gridder='mosaic',
               chanchunks=-1,
               mosweight=True,
               pblimit=pb_limit,
               pbmask=pb_limit,
               deconvolver='multiscale',
               scales=[0, 5, 10],
               restoration=True,
               pbcor=False,
               weighting='briggs',
               robust=0.5,
               niter=int(1e7),
               cycleniter=100,  # Force many major cycles
               nsigma=4.,
               usemask='auto-multithresh',
               sidelobethreshold=1.0,
               noisethreshold=3.0,
               lownoisethreshold=1.5,
               negativethreshold=0.0,
               minbeamfrac=0.1,
               growiterations=75,
               dogrowprune=True,
               minpercentchange=1.0,
               fastnoise=False,
               threshold='',
               interactive=0,
               savemodel='none',
               parallel=False,
               calcres=True,
               calcpsf=True,
               smallscalebias=0.6
               )

    np.save(cleanimage_name + ".stage1.results_dict.npy", stage1_tclean_dict)

    # Copy stage 1 into its own file

    stage1_path = osjoin(line_image_path, 'stage1')
    if not os.path.exists(stage1_path):
        os.mkdir(stage1_path)

    cleanimage_name_stage1 = "{0}/{1}/{2}_{3}_{4}.stage1".format(line_image_path,
                                                                 'stage1', prefix,
                                                                 line_name,
                                                                 spec_width)

    for suff in ['image', 'model', 'mask', 'pb', 'psf',
                 'residual', 'weight', 'sumwt',
                 'stage1.results_dict.npy']:

        orig_image = "{0}.{1}".format(cleanimage_name, suff)
        copy_image = "{0}.{1}".format(cleanimage_name_stage1, suff)

        if os.path.exists(copy_image):
            os.system("rm -r {}".format(copy_image))

        if ".npy" in suff:
            os.system('mv {0} {1}'.format(orig_image, stage1_path))
        else:
            os.system('cp -r {0} {1}'.format(orig_image, copy_image))

    # Finally we check whether any cleaning was actually done. If not,
    # we skip stage 2 (i.e., there's no clear signal, esp. given the
    # low masking requirements).

    if stage1_tclean_dict['iterdone'] == 0:
        # Empty auto-mask. Avoid stage 2.
        stage2_summary_name = cleanimage_name + ".stage2.results_dict.npy"
        np.save(stage2_summary_name, stage1_tclean_dict)


# Stage 2: Single-scale clean to 1-sigma.

# Skip if stage2 summary file is saved
stage2_summary_name = cleanimage_name + ".stage2.results_dict.npy"

if not os.path.exists(stage2_summary_name):

    stage2_tclean_dict = \
        tclean(vis=ms_names,
               field='M33',
               spw='0',
               intent='OBSERVE_TARGET#ON_SOURCE',
               datacolumn='corrected',
               imagename=cleanimage_name,
               imsize=imaging_params['imsize'],
               cell=imaging_params['cellsize'],
               phasecenter=ptg_centre,
               nchan=imaging_params['nchan'],
               start=imaging_params['start'],
               width=imaging_params['width'],
               specmode='cube',
               outframe='LSRK',
               gridder='mosaic',
               chanchunks=-1,
               mosweight=True,
               pblimit=pb_limit,
               pbmask=pb_limit,
               deconvolver='hogbom',
               restoration=True,
               pbcor=False,
               weighting='briggs',
               robust=0.5,
               niter=int(1e7),
               cycleniter=100,  # Force many major cycles
               nsigma=1.,
               # usemask='auto-multithresh',
               usemask='user',  # Use auto-mask from last step.
               sidelobethreshold=1.0,
               noisethreshold=3.0,
               lownoisethreshold=1.5,
               negativethreshold=0.0,
               minbeamfrac=0.1,
               growiterations=75,
               dogrowprune=True,
               minpercentchange=1.0,
               fastnoise=False,
               threshold='',
               interactive=0,
               savemodel='none',
               parallel=False,
               calcres=False,
               calcpsf=False,
               smallscalebias=0.6
               )

    np.save(stage2_summary_name, stage2_tclean_dict)
