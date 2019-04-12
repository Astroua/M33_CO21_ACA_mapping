from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes

# Brick1-Tile3 has unusable continuum data. The lines are
# good, though, if a bit noisier than would be expected.
# This script excludes one poor antenna and lower the phase
# SNR so the continuum SPW is not relied on.

# Portions of the image still fail. Still not sure why.

__rethrow_casa_exceptions = True
context = h_init()
context.set_state('ProjectSummary', 'proposal_code', '2017.1.00901.S')
context.set_state('ProjectSummary', 'piname', 'unknown')
context.set_state('ProjectSummary', 'proposal_title', 'unknown')
# context.set_state('ProjectStructure', 'ous_part_id', 'X1905732538')
# context.set_state('ProjectStructure', 'ous_title', 'Undefined')
# context.set_state('ProjectStructure', 'ppr_file', '/home/dared/opt/dared.2018AUG/mnt/dataproc/2017.1.00901.S_2018_10_20T11_01_24.269/SOUS_uid___A001_X1296_X69b/GOUS_uid___A001_X1296_X69c/MOUS_uid___A001_X1296_X69d/working/PPR_uid___A001_X1296_X69e.xml')
# context.set_state('ProjectStructure', 'ps_entity_id', 'uid://A001/X1221/Xa7d')
# context.set_state('ProjectStructure', 'recipe_name', 'hifa_calimage')
# context.set_state('ProjectStructure', 'ous_entity_id', 'uid://A001/X1221/Xa79')
# context.set_state('ProjectStructure', 'ousstatus_entity_id', 'uid://A001/X1296/X69d')
try:
    # hifa_importdata(vis=['uid___A002_Xd15514_X9009.asdm.sdm'], dbservice=False, session=['session_1'])
    hifa_importdata(vis=['uid___A002_Xd15514_X9009.asdm.sdm'], session=['session_1'])
    fixsyscaltimes(vis = 'uid___A002_Xd15514_X9009.asdm.sdm.ms')# SACM/JAO - Fixes
    h_save() # SACM/JAO - Finish weblog after fixes
    h_init() # SACM/JAO - Restart weblog after fixes
    hifa_importdata(vis=['uid___A002_Xd15514_X9009.asdm.sdm'], session=['session_1'])

    hifa_flagdata(pipelinemode="automatic")
    hifa_fluxcalflag(pipelinemode="automatic")
    hif_rawflagchans(pipelinemode="automatic")
    hif_refant(pipelinemode="automatic", refantignore='CM10')
    h_tsyscal(pipelinemode="automatic")
    hifa_tsysflag(pipelinemode="automatic")
    hifa_antpos(pipelinemode="automatic")
    hifa_wvrgcalflag(pipelinemode="automatic")
    hif_lowgainflag(pipelinemode="automatic")
    hif_setmodels(pipelinemode="automatic")
    hifa_bandpassflag(pipelinemode="automatic")
    hifa_spwphaseup(pipelinemode="automatic", phasesnr=25.0)
    hifa_gfluxscaleflag(pipelinemode="automatic")
    hifa_gfluxscale(pipelinemode="automatic")
    hifa_timegaincal(pipelinemode="automatic")
    hif_applycal(pipelinemode="automatic")
    # hifa_imageprecheck(pipelinemode="automatic")

    # Cannot fit PSF in imageprecheck. Define params for the imaging
    myrobust = 0.0
    myspw = '16,20,22,24,26,28'
    myfields = 'M33'

    # This one worked.
    hif_makeimlist(intent='PHASE,BANDPASS,CHECK')
    hif_makeimages(pipelinemode="automatic")

    hif_checkproductsize(maxcubelimit=40.0, maxproductsize=400.0, maxcubesize=30.0)
    hifa_exportdata(pipelinemode="automatic")
    hif_mstransform(pipelinemode="automatic")
    hifa_flagtargets(pipelinemode="automatic")

    hif_makeimlist(specmode='mfs', spw=myspw, field=myfields, robust=myrobust,
                   hm_cell='1arcsec')
    hif_findcont(pipelinemode="automatic")
    hif_uvcontfit(pipelinemode="automatic")
    hif_uvcontsub(pipelinemode="automatic")
    hif_makeimages(pipelinemode="automatic")

    mynbins = '16:1,20:1,22:1,24:1,26:1,28:1'

    # hif_makeimlist(specmode='cont', spw=myspw, field=myfields, robust=myrobust)
    # hif_makeimages(pipelinemode="automatic")
    hif_makeimlist(pipelinemode="automatic", specmode='cube', spw=myspw, nbins=mynbins,
                   field=myfields, robust=myrobust, hm_cell='1arcsec')
    # Auto-masking is failing from (I think) large sidelobes.
    # Try some custom inputs.
    # Still fails.
    hif_makeimages(pipelinemode="automatic",
                   hm_masking='manual',
                   hm_sidelobethreshold=2.,
                   hm_noisethreshold=4.)

    mynbins = '16:4,20:4,22:4,24:4,26:4,28:4'

    hif_makeimlist(specmode='repBW', spw=myspw, nbins=mynbins, field=myfields,
                   robust=myrobust, hm_cell='1arcsec')
    hif_makeimages(pipelinemode="automatic")

finally:
    h_save()
