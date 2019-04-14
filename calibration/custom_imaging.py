
'''
Re-run tclean on the line SPWs. Mostly Brick1-Tile3
'''

# Just for Brick1-Tile 3 right now

# for myspw_num in ['16', '20', '22', '24', '26', '28']:
for myspw_num in ['20', '22', '24', '26', '28']:

    tclean(vis=['uid___A002_Xd15514_X9009.asdm.sdm_target.ms'],
           field='M33', spw=[myspw_num],
           antenna=['0,1,2,3,4,5,6,7,8,9'],
           scan=['8,9,11,13,16,18,21,23,26,28,31,33,36'],
           intent='OBSERVE_TARGET#ON_SOURCE',
           datacolumn='corrected',
           imagename='custom_tclean.M33_sci.spw{}.cube'.format(myspw_num),
           imsize=[280, 486],
           cell=['1arcsec'],
           phasecenter='ICRS 01:34:08.6810 +030.46.38.818',
           stokes='I',
           specmode='cube',
           nchan=-1,
           start=1,
           width=1,
           outframe='LSRK',
           gridder='mosaic',
           chanchunks=-1,
           usepointing=False,
           mosweight=True,
           pblimit=0.2,
           deconvolver='multiscale',
           scales=[0, 7, 14],
           restoration=True,
           restoringbeam='common',
           pbcor=False,
           weighting='briggs',
           robust=0.5,
           niter=100000,
           cycleniter=2000,
           nsigma=3.,
           usemask='auto-multithresh',
           sidelobethreshold=1.,
           noisethreshold=3.0,
           lownoisethreshold=2.0,
           negativethreshold=0.0,
           minbeamfrac=0.1,
           growiterations=75,
           dogrowprune=True,
           minpercentchange=1.0,
           threshold='0.0mJy',
           interactive=0,
           savemodel='none',
           parallel=False)
