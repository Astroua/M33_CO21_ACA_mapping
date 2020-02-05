
'''
Try imaging all of brick 3 to see how severely beam changes affect
the mosaic.
'''

from glob import glob
import os

from tasks import tclean


data_path = os.path.expanduser("~/bigdata/ekoch/M33/ALMA/ACA_Band6/reduced/")
imaging_path = os.path.expanduser("~/bigdata/ekoch/M33/ALMA/ACA_Band6/brick3_mosaic/")

brick3_ms = glob("{0}/Brick3*.ms".format(data_path))

assert len(brick3_ms) == 5

myspw_num = '16'

tclean(vis=brick3_ms,
       field='M33', spw=[myspw_num],
       intent='OBSERVE_TARGET#ON_SOURCE',
       datacolumn='corrected',
       imagename=os.path.join(imaging_path, 'brick3.spw{}.12co_21.cube_2kms_dirty_2'.format(myspw_num)),
       imsize=[1200, 700],
       cell=['1arcsec'],
       phasecenter='J2000 01:33:52.20 +030.33.40.70',
       stokes='I',
       specmode='cube',
       nchan=70,
       start="-220km/s",
       width="2.0km/s",
       outframe='LSRK',
       gridder='mosaic',
       chanchunks=-1,
       usepointing=False,
       mosweight=True,
       pblimit=0.2,
       deconvolver='multiscale',
       # scales=[0, 7, 14],
       scales=[0, 5, 10],
       restoration=False,
       # restoringbeam='common',
       pbcor=False,
       weighting='briggs',
       robust=0.5,
       niter=0,
       cycleniter=100,  # Force many major cycles
       nsigma=5.,
       # usemask='auto-multithresh',
       usemask='pb',
       sidelobethreshold=1.25,
       noisethreshold=3.0,
       lownoisethreshold=1.5,
       negativethreshold=0.0,
       minbeamfrac=0.1,
       growiterations=75,
       dogrowprune=True,
       minpercentchange=1.0,
       threshold='0.0mJy',
       interactive=0,
       savemodel='none',
       parallel=False,
       calcres=True,
       calcpsf=True,
       smallscalebias=0.6
       )


out_dict_stage1 = \
    tclean(vis=brick3_ms,
           field='M33', spw=[myspw_num],
           intent='OBSERVE_TARGET#ON_SOURCE',
           datacolumn='corrected',
           imagename=os.path.join(imaging_path, 'brick3.spw{}.12co_21.cube_2kms_5sigmaclean_pbmask'.format(myspw_num)),
           imsize=[1200, 700],
           cell=['1arcsec'],
           phasecenter='J2000 01:33:52.20 +030.33.40.70',
           stokes='I',
           specmode='cube',
           nchan=70,
           start="-220km/s",
           width="2.0km/s",
           outframe='LSRK',
           gridder='mosaic',
           chanchunks=-1,
           usepointing=False,
           mosweight=True,
           pblimit=0.2,
           deconvolver='multiscale',
           # scales=[0, 7, 14],
           scales=[0, 5, 10],
           restoration=True,
           # restoringbeam='common',
           pbcor=False,
           weighting='briggs',
           robust=0.5,
           niter=100000,
           cycleniter=50,  # Force many major cycles
           nsigma=5.,
           # usemask='auto-multithresh',
           usemask='pb',
           pbmask=0.2,
           sidelobethreshold=1.25,
           noisethreshold=3.0,
           lownoisethreshold=1.5,
           negativethreshold=0.0,
           minbeamfrac=0.1,
           growiterations=75,
           dogrowprune=True,
           minpercentchange=1.0,
           threshold='0.0mJy',
           interactive=0,
           savemodel='none',
           parallel=False,
           calcres=True,
           calcpsf=True,
           smallscalebias=0.6
           )

# Good! try for a deeper clean but trigger automasking.

orig_image = os.path.join(imaging_path, 'brick3.spw{}.12co_21.cube_2kms_5sigmaclean_pbmask'.format(myspw_num))
new_image = os.path.join(imaging_path, 'brick3.spw{}.12co_21.cube_2kms_2sigmaclean_automask'.format(myspw_num))

suffixes = ['image', 'mask', 'model', 'pb', 'psf', 'residual', 'sumwt', 'weight']

for suffix in suffixes:
    if suffix == 'mask':
        print("Skipping mask.")
        continue

    old = "{0}.{1}".format(orig_image, suffix)
    new = "{0}.{1}".format(new_image, suffix)

    os.system("cp -r {0} {1}".format(old, new))


out_dict_stage2 = \
    tclean(vis=brick3_ms,
           field='M33', spw=[myspw_num],
           intent='OBSERVE_TARGET#ON_SOURCE',
           datacolumn='corrected',
           imagename=os.path.join(imaging_path, 'brick3.spw{}.12co_21.cube_2kms_2sigmaclean_automask'.format(myspw_num)),
           imsize=[1200, 700],
           cell=['1arcsec'],
           phasecenter='J2000 01:33:52.20 +030.33.40.70',
           stokes='I',
           specmode='cube',
           nchan=70,
           start="-220km/s",
           width="2.0km/s",
           outframe='LSRK',
           gridder='mosaic',
           chanchunks=-1,
           usepointing=False,
           mosweight=True,
           pblimit=0.2,
           deconvolver='multiscale',
           # scales=[0, 7, 14],
           scales=[0, 5, 10],
           restoration=True,
           # restoringbeam='common',
           pbcor=False,
           weighting='briggs',
           robust=0.5,
           niter=100000,
           cycleniter=50,  # Force many major cycles
           nsigma=2.5,
           usemask='auto-multithresh',
           pbmask=0.2,
           sidelobethreshold=0.25,
           noisethreshold=2.5,
           lownoisethreshold=1.5,
           negativethreshold=0.0,
           minbeamfrac=0.1,
           smoothfactor=2.0,
           growiterations=75,
           dogrowprune=True,
           minpercentchange=1.0,
           threshold='0.0mJy',
           interactive=0,
           savemodel='none',
           parallel=False,
           calcres=False,
           calcpsf=False,
           smallscalebias=0.6
           )
