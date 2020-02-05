
'''
The 2017 SB has calibration issues. The 12CO is ok just noisy.
The 2019 SB was taken at a really low inclination, so the beam
is ridiculous (12x7'') and could make imaging the whole thing
a pain.

Exploring joint imaging here to see if the old data can round the
beam out.

Haven't bothered to continuum subtract or anything.
'''

# myspw_num = '16'
myspw_num = '20'

for myspw_num in ['22', '24', '26', '28']:

    tclean(vis=['uid___A002_Xd15514_X9009.asdm.sdm.ms_2017',
                'uid___A002_Xe29133_X249a.ms'],
           field='M33', spw=[myspw_num],
           intent='OBSERVE_TARGET#ON_SOURCE',
           datacolumn='corrected',
           imagename='custom_tclean.brick1tile3.M33_sci.spw{}.cube'.format(myspw_num),
           imsize=[512, 512],
           cell=['1arcsec'],
           phasecenter='J2000 01:34:08.20 +030.46.52.00',
           stokes='I',
           specmode='cube',
           nchan=80,
           start="-160km/s",
           width="-2km/s",
           outframe='LSRK',
           gridder='mosaic',
           chanchunks=-1,
           usepointing=False,
           mosweight=True,
           pblimit=0.2,
           deconvolver='multiscale',
           scales=[0, 7, 14],
           restoration=False,
           # restoringbeam='common',
           pbcor=False,
           weighting='briggs',
           robust=0.5,
           # niter=100000,
           niter=0,
           cycleniter=500,  # Force many major cycles
           nsigma=5.,
           usemask='auto-multithresh',
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
           parallel=False)



# How much does the beam change with uniform weighting?

tclean(vis=['uid___A002_Xd15514_X9009.asdm.sdm.ms_2017',
            'uid___A002_Xe29133_X249a.ms'],
       field='M33', spw=[myspw_num],
       intent='OBSERVE_TARGET#ON_SOURCE',
       datacolumn='corrected',
       imagename='custom_tclean.brick1tile3.M33_sci.spw{}.cube'.format(myspw_num),
       imsize=[512, 512],
       cell=['1arcsec'],
       phasecenter='J2000 01:34:08.20 +030.46.52.00',
       stokes='I',
       specmode='cube',
       nchan=80,
       start="-160km/s",
       width="-2km/s",
       outframe='LSRK',
       gridder='mosaic',
       chanchunks=-1,
       usepointing=False,
       mosweight=True,
       pblimit=0.2,
       deconvolver='multiscale',
       scales=[0, 7, 14],
       restoration=False,
       # restoringbeam='common',
       pbcor=False,
       weighting='briggs',
       robust=0.5,
       # niter=100000,
       niter=0,
       cycleniter=500,  # Force many major cycles
       nsigma=5.,
       usemask='auto-multithresh',
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
       parallel=False)