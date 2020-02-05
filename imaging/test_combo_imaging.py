
'''
Test imaging two mosaics together.
Picking Brick 2 and Brick 3 Tile 1.
Former from 2017 w/ lower spectral resolution. Latter from
2019 w/ higher spectral resolution.

'''

import os
from tasks import tclean

brick2tile1_ms = "/mnt/bigdata/ekoch/M33/ALMA/ACA_Band6/2017.1.00901.S/Brick2-Tile1/2017.1.00901.S/science_goal.uid___A001_X1296_X6bf/group.uid___A001_X1296_X6c0/member.uid___A001_X1296_X6c1/calibrated/uid___A002_Xcfd24b_Xbf40.ms.split.cal"
brick3tile1_ms = "/mnt/bigdata/ekoch/M33/ALMA/ACA_Band6/2019.1.01182.S/2019.1.01182.S/science_goal.uid___A001_X1465_X164c/group.uid___A001_X1465_X164d/member.uid___A001_X1465_X164e/calibrated/working/uid___A002_Xe1baa0_X265a.ms"

myspw_num = '16'

tclean(vis=[brick2tile1_ms, brick3tile1_ms],
       field='M33', spw=[myspw_num],
       intent='OBSERVE_TARGET#ON_SOURCE',
       datacolumn='corrected',
       imagename='brick2_brick3_til5.M33_sci.spw{}.cube_speclim'.format(myspw_num),
       imsize=[1024, 1024],
       cell=['1arcsec'],
       phasecenter='J2000 01:33:33.70 +030.38.11.70',  # Half-way between the two mosaics
       stokes='I',
       specmode='cube',
       # nchan=500,
       nchan=105,
       start="-280km/s",
       # nchan=100,
       # start=800,
       # width=1,
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
       restoringbeam='common',
       pbcor=False,
       weighting='briggs',
       robust=0.5,
       niter=100000,
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


# single-scale to lower threshold

tclean(vis=[brick2tile1_ms, brick3tile1_ms],
       field='M33', spw=[myspw_num],
       intent='OBSERVE_TARGET#ON_SOURCE',
       datacolumn='corrected',
       imagename='brick2_brick3_til5.M33_sci.spw{}.cube_speclim'.format(myspw_num),
       imsize=[1024, 1024],
       cell=['1arcsec'],
       phasecenter='J2000 01:33:33.70 +030.38.11.70',  # Half-way between the two mosaics
       stokes='I',
       specmode='cube',
       # nchan=500,
       nchan=105,
       start="-280km/s",
       # nchan=100,
       # start=800,
       # width=1,
       width="2.0km/s",
       outframe='LSRK',
       gridder='mosaic',
       chanchunks=-1,
       usepointing=False,
       mosweight=True,
       pblimit=0.2,
       deconvolver='hogbom',
       restoration=True,
       restoringbeam='common',
       pbcor=False,
       weighting='briggs',
       robust=0.5,
       niter=100000,
       cycleniter=100,  # Force many major cycles
       nsigma=3.,
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
       calcres=False,
       calcpsf=False,
       smallscalebias=0.6
       )