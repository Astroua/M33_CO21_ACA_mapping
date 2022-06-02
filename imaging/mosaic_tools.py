"""
Linear mosaicing routines. Adopted parts from the PHANGS-ALMA pipeline code:
(Leroy et al. 2021; https://github.com/akleroy/phangs_imaging_scripts).
"""

#region Imports and definitions

import os
import numpy as np
# import glob

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Analysis utilities
# import analysisUtils as au

# Other pipeline stuff
# import casaMaskingRoutines as cma

# Pipeline versionining
# from pipelineVersion import version as pipeVer

from casatasks import (imsmooth, imregrid, imsubimage, immath,
                       imhead, imval)
from casatools import image as iatool

#endregion

#region Routines to match resolution

def common_res_for_mosaic(infile_list,
                          outfile_suffix=None,
                          out_path=None,
                          overwrite=False,
                          round_beam=False,
                          add_pix_width=True,
                          common_beam_kwargs={}):
    """
    Convolve multi-part cubes to a common res for mosaicking.
    """

    from radio_beam import Beam, Beams
    from spectral_cube import SpectralCube
    from astropy.wcs.utils import proj_plane_pixel_scales
    from astropy import units as u

    # Figure out target resolution if it is not supplied

    beams_list = []
    pix_list = []

    for infile in infile_list:

        cube = SpectralCube.read(infile, format='casa_image')

        # Get pixel size
        pix_size = proj_plane_pixel_scales(cube.wcs)[0] * u.deg
        # Convert to arcsec.
        pix_size = pix_size.to(u.arcsec)

        pix_list.append(pix_size.value)

        try:
            beams = Beams.from_casa_image(infile)

            # Find common beam for this cube.
            if beams.size == 1:
                com_beam_permap = beams[0]
            else:
                com_beam_permap = beams.common_beam(**common_beam_kwargs)
        except KeyError:
            com_beam_permap = cube.beam
            # com_beam_permap = Beam.from_casa_image(infile)

        beams_list.append(com_beam_permap)


    all_beams = Beams(beams=beams_list)
    if round_beam:
        # Just grab largest BMAJ
        target_bmaj = all_beams.major.max().to(u.arcsec)
        target_beam = Beam(major=target_bmaj, minor=target_bmaj,
                           pa=0 * u.deg)

    else:
        target_beam = all_beams.common_beam(**common_beam_kwargs)

    if add_pix_width:
        pix_list = pix_list * u.arcsec
        max_pix = pix_list.max()
        # Add largest pixel in quadrature.
        # 2* b/c we want the kernel to be resolve by >1 diagonal pixel.
        # so that's (2**0.5 * max_pix)**2
        new_major = np.sqrt(target_beam.major.to(u.arcsec)**2 + 2 * max_pix**2)
        new_minor = np.sqrt(target_beam.minor.to(u.arcsec)**2 + 2 * max_pix**2)

        target_beam = Beam(major=new_major, minor=new_minor, pa=target_beam.pa)

    if outfile_suffix is None:
        outfile_suffix = "mosaic_commonbeam"

    output_files = []

    for ii, input_file in enumerate(infile_list):

        in_path, image_name = os.path.split(input_file)
        split_img = image_name.split(".")
        out_basename = "{0}_{1}".format(split_img[0], outfile_suffix)
        out_image_name = ".".join([out_basename, ".".join(split_img[1:])])

        if out_path is None:
            output_file = os.path.join(in_path, out_image_name)
        else:
            output_file = os.path.join(out_path, out_image_name)

        imsmooth(imagename=input_file,
                 outfile=output_file,
                 targetres=True,
                 major=str(target_beam.major.to(u.arcsec).value)+'arcsec',
                 minor=str(target_beam.minor.to(u.arcsec).value)+'arcsec',
                 pa='{}deg'.format(target_beam.pa.to(u.deg).value),
                 overwrite=overwrite,
                 )

        output_files.append(output_file)

    return output_files

#region Routines to match astrometry between parts of a mosaic

def calculate_mosaic_extent(infile_list,
                            force_ra_ctr=None,
                            force_dec_ctr=None,
                            ):
    """
    Given a list of input files, calculate the center and extent of
    the mosaic needed to cover them all. Return the results as a
    dictionary.

    infile_list : list of input files to loop over.

    force_ra_ctr (default None) : if set then force the RA center of
    the mosaic to be this value, and the returned extent is the
    largest separation of any image corner from this value in RA.

    force_dec_ctr (default None) : as force_ra_ctr but for
    Declination.

    If the RA and Dec. centers are supplied, then they are assumed to
    be in decimal degrees.
    """

    # Initialize the list of corner RA and Dec positions.

    ra_list = []
    dec_list = []

    # TBD - right now we assume matched frequency/velocity axis
    freq_list = []

    # Loop over input files and calculate RA and Dec coordinates of
    # the corners.

    # myia = au.createCasaTool(casa.iatool)
    myia = iatool()

    for this_infile in infile_list:

        this_hdr = imhead(this_infile)

        if this_hdr['axisnames'][0] != 'Right Ascension':
            logger.error("Expected axis 0 to be Right Ascension. Returning.")
            return(None)
        if this_hdr['axisunits'][0] != 'rad':
            logger.error("Expected axis units to be radians. Returning.")
            return(None)
        if this_hdr['axisnames'][1] != 'Declination':
            logger.error("Expected axis 1 to be Declination. Returning.")
            return(None)
        if this_hdr['axisunits'][1] != 'rad':
            logger.error("Expected axis units to be radians. Returning.")
            return(None)

        this_shape = this_hdr['shape']
        xlo = 0
        xhi = this_shape[0]-1
        ylo = 0
        yhi = this_shape[1]-1

        pixbox = str(xlo)+','+str(ylo)+','+str(xlo)+','+str(ylo)
        blc = imval(this_infile, chans='0', stokes='I', box=pixbox)

        pixbox = str(xlo)+','+str(yhi)+','+str(xlo)+','+str(yhi)
        tlc = imval(this_infile, chans='0', stokes='I', box=pixbox)

        pixbox = str(xhi)+','+str(yhi)+','+str(xhi)+','+str(yhi)
        trc = imval(this_infile, chans='0', stokes='I', box=pixbox)

        pixbox = str(xhi)+','+str(ylo)+','+str(xhi)+','+str(ylo)
        brc = imval(this_infile, chans='0', stokes='I', box=pixbox)

        ra_list.append(blc['coords'][0][0])
        ra_list.append(tlc['coords'][0][0])
        ra_list.append(trc['coords'][0][0])
        ra_list.append(brc['coords'][0][0])

        dec_list.append(blc['coords'][0][1])
        dec_list.append(tlc['coords'][0][1])
        dec_list.append(trc['coords'][0][1])
        dec_list.append(brc['coords'][0][1])

    # Get the minimum and maximum RA and Declination.

    # TBD - this breaks straddling the meridian (RA = 0) or the poles
    # (Dec = 90). Add catch cases or at least error calls for
    # this. Meridian seems more likely to come up, so just that is
    # probably fine.

    min_ra = np.min(ra_list)
    max_ra = np.max(ra_list)
    min_dec = np.min(dec_list)
    max_dec = np.max(dec_list)

    # TBD - right now we assume matched frequency/velocity axis

    min_freq = None
    max_freq = None

    # If we do not force the center of the mosaic, then take it to be
    # the average of the min and max, so that the image will be a
    # square.

    if force_ra_ctr is None:
        ra_ctr = (max_ra+min_ra)*0.5
    else:
        ra_ctr = force_ra_ctr*np.pi/180.

    if force_dec_ctr is None:
        dec_ctr = (max_dec+min_dec)*0.5
    else:
        dec_ctr = force_dec_ctr*np.pi/180.

    # Now calculate the total extent of the mosaic given the center.

    delta_ra = 2.0*np.max([np.abs(max_ra-ra_ctr),np.abs(min_ra-ra_ctr)])
    delta_ra *= np.cos(dec_ctr)
    delta_dec = 2.0*np.max([np.abs(max_dec-dec_ctr),np.abs(min_dec-dec_ctr)])

    # Put the output into a dictionary.

    output = {'ra_ctr':[ra_ctr*180./np.pi,'degrees'],
             'dec_ctr':[dec_ctr*180./np.pi,'degrees'],
             'delta_ra':[delta_ra*180./np.pi*3600.,'arcsec'],
             'delta_dec':[delta_dec*180./np.pi*3600.,'arcsec'],
             }

    return output

def build_common_header(infile_list,
                        template_file=None,
                        ra_ctr=None,
                        dec_ctr=None,
                        delta_ra=None,
                        delta_dec=None,
                        allow_big_image=False,
                        too_big_pix=1e4,):
    """
    Build a target header to be used as a template by imregrid when
    setting up linear mosaicking operations.

    infile_list : the list of input files. Used to generate the
    center, extent, and pick a template file if these things aren't
    supplied by the user.

    template_file : the name of a file to use as the template. The
    coordinate axes and size are manipulated but other things like the
    pixel size and units remain the same. If this is not supplied the
    first file from the input file list is selected.

    ra_ctr : the center of the output file in right ascension. Assumed
    to be in decimal degrees. If None or not supplied, then this is
    calculated from the image stack.

    dec_ctr : as ra_ctr but for declination.

    delta_ra : the extent of the output image in arcseconds. If this
    is not supplied, it is calculated from the image stack.

    delta_dec : as delta_ra but for declination.

    allow_big_image (default False) : allow very big images? If False
    then the program throws an error if the image appears too
    big. This is often the sign of a bug.

    too_big_pix (default 1e4) : definition of pixel scale (in one
    dimension) that marks an image as too big.
    """

    # Check inputs

    if template_file is None:

        template_file = infile_list[0]
        logger.info("Using first input file as template - "+template_file)

    # If the RA and Dec center and extent are not full specified, then
    # calculate the extent based on the image stack.

    if (delta_ra is None) or (delta_dec is None) or \
            (ra_ctr is None) or (dec_ctr is None):

        logger.info("Extent not fully specified. Calculating it from image stack.")
        extent_dict = calculate_mosaic_extent(infile_list,
                                              force_ra_ctr=ra_ctr,
                                              force_dec_ctr=dec_ctr)

        if ra_ctr is None:
            ra_ctr = extent_dict['ra_ctr'][0]
        if dec_ctr is None:
            dec_ctr = extent_dict['dec_ctr'][0]
        if delta_ra is None:
            delta_ra = extent_dict['delta_ra'][0]
        if delta_dec is None:
            delta_dec = extent_dict['delta_dec'][0]

    # Get the header from the template file

    target_hdr = imregrid(template_file, template='get')

    # Get the pixel scale. This makes some assumptions. We could put a
    # lot of general logic here, but we are usually working in a
    # case where this works.

    if (target_hdr['csys']['direction0']['units'][0] != 'rad') or \
            (target_hdr['csys']['direction0']['units'][1] != 'rad'):
        logger.error("ERROR: Based on CASA experience. I expected pixel units of radians.")
        logger.error("I did not find this. Returning. Adjust code or investigate file "+infile_list[0])
        return(None)

    # Add our target center pixel values to the header after
    # converting to radians.

    ra_ctr_in_rad = ra_ctr * np.pi / 180.
    dec_ctr_in_rad = dec_ctr * np.pi / 180.

    target_hdr['csys']['direction0']['crval'][0] = ra_ctr_in_rad
    target_hdr['csys']['direction0']['crval'][1] = dec_ctr_in_rad

    # Calculate the size of the image in pixels and set the central
    # pixel coordinate for the RA and Dec axis.

    ra_pix_in_as = np.abs(target_hdr['csys']['direction0']['cdelt'][0]*180./np.pi*3600.)
    ra_axis_size = np.ceil(delta_ra / ra_pix_in_as)
    new_ra_ctr_pix = ra_axis_size / 2.0

    dec_pix_in_as = np.abs(target_hdr['csys']['direction0']['cdelt'][1]*180./np.pi*3600.)
    dec_axis_size = np.ceil(delta_dec / dec_pix_in_as)
    new_dec_ctr_pix = dec_axis_size / 2.0

    # Check that the axis size isn't too big. This is likely to be a
    # bug. If allowbigimage is True then bypass this, otherwise exit.

    if not allow_big_image:
        if ra_axis_size > too_big_pix or dec_axis_size > too_big_pix:
            logger.error("WARNING! This is a very big image you plan to create, "+str(ra_axis_size)+
                         " x "+str(dec_axis_size))
            logger.error(" To make an image this big set allowbigimage=True. Returning.")
            raise ValueError

    # Enter the new values into the header and return.

    target_hdr['csys']['direction0']['crpix'][0] = new_ra_ctr_pix
    target_hdr['csys']['direction0']['crpix'][1] = new_dec_ctr_pix

    target_hdr['shap'][0] = int(ra_axis_size)
    target_hdr['shap'][1] = int(dec_axis_size)

    return target_hdr


def common_grid_for_mosaic(infile_list,
                           outfile_suffix=None,
                           out_path=None,
                           target_hdr=None,
                           template_file=None,
                           ra_ctr=None,
                           dec_ctr=None,
                           delta_ra=None,
                           delta_dec=None,
                           allow_big_image=False,
                           too_big_pix=1e4,
                           asvelocity=True,
                           interpolation='cubic',
                           axes=[-1],
                           overwrite=False,):
    """
    Build a common astrometry for a mosaic and align all input image
    files to that astrometry. If the common astrometry isn't supplied
    as a header, the program calls other routines to create it based
    on the supplied parameters and stack of input images. Returns the
    common header.

    infile_list : list of input files.

    outfile_list : a list of output files that will get the convolved
    data. Can be a dictionary or a list. If it's a list then matching
    is by order, so that firs infile goes to first outfile, etc. If
    it's a dictionary, it looks for the infile name as a key.

    target_hdr : the CASA-format header used to align the images,
    needs the same format returned by a call to imregrid with
    template='get'.

    ra_ctr, dec_ctr, delta_ra, delta_dec, allow_big_image, too_big_pix
    : keywords passed to the header creation routine. See
    documentation for "build_common_header" to explain these.

    asvelocity, interpolation, axes : keywords passed to the CASA imregrid
    call. See documentation there.

    overwrite (default False) : Delete existing files. You probably
    want to set this to True but it's a user decision.
    """

    # Get the common header if one is not supplied

    if target_hdr is None:

        logger.info('Generating target header.')

        target_hdr = build_common_header(infile_list,
                                         template_file=None,
                                         ra_ctr=None,
                                         dec_ctr=None,
                                         delta_ra=None,
                                         delta_dec=None,
                                         allow_big_image=False,
                                         too_big_pix=1e4,)

    # Align the input files to the new astrometry. This will also loop
    # over and align any "weight" files.

    logger.info('Aligning image files.')

    if outfile_suffix is None:
        outfile_suffix = "mosaic_commongrid"

    output_files = []

    for input_file in infile_list:

        in_path, image_name = os.path.split(input_file)
        split_img = image_name.split(".")
        out_basename = "{0}_{1}".format(split_img[0], outfile_suffix)
        out_image_name = ".".join([out_basename, ".".join(split_img[1:])])

        if out_path is None:
            output_file = os.path.join(in_path, out_image_name)
        else:
            output_file = os.path.join(out_path, out_image_name)


        imregrid(imagename=input_file,
                 template=target_hdr,
                 output=output_file,
                 asvelocity=asvelocity,
                 axes=axes,
                 interpolation=interpolation,
                 overwrite=overwrite)

        output_files.append(output_file)

    return output_files

#endregion

#region Routines to carry out the mosaicking

def mosaic_aligned_data(infile_dict,
                        outfile,
                        overwrite=False,
                        is_pbcorr=True,
                        output_noise_map=True):
    """
    Combine a list of previously aligned data into a single image
    using linear mosaicking. Weight each file using a corresponding
    weight file and also create sum and integrated weight files.

    infile_dict : dict
        Dictionary with keys corresponding to the chunks to be mosaiced
        together. Each dictionary entry should be a list with 3 components:
        the image, the PB file, and the noise std of the image. The images
        should already be on the same grid as the final mosaic.

    outfile : str
        The name of the output mosaic image. Will create
        associated files with ".sum" and ".weight" appended to this file
        name.

    overwrite (default False) : Delete existing files. You probably
    want to set this to True but it's a user decision.

    """

    # Define some extra outputs and then check file existence

    sum_file = outfile + '.sum'
    weight_file = outfile + '.weight'
    mask_file = outfile + '.mask'
    temp_file = outfile + '.temp'

    if output_noise_map:
        sum_noise_file = outfile + ".sum_noise"
        temp_noise_file = outfile + '.temp_noise'
        outfile_noise = outfile + ".noise"

    for this_file in [outfile, sum_file, weight_file, temp_file, mask_file]:
        if os.path.isdir(this_file):
            if not overwrite:
                logger.error(f"Output file present and overwrite off - {this_file}")
                return(None)
            os.system(f'rm -rf {this_file}')

    # Check the weightfile dictionary/list and get it set.

    # Define LEL expressions to be fed to immath. These just sum up
    # weight*image and weight. Those produce the .sum and .weight
    # output file.

    full_imlist = []

    lel_exp_sum = ''
    lel_exp_weight = ''

    if output_noise_map:
        lel_exp_sum_noise = ''

    counter = 0

    for ii, key in enumerate(infile_dict):

        # Build out to a list that goes image1, pb1, image2, pb2...

        full_imlist.append(infile_dict[key][0])
        full_imlist.append(infile_dict[key][1])

        sigma = infile_dict[key][2]

        # Make LEL string expressions that refer to these two images
        # and then increment the counter by 2. So IM0 is the first
        # image, IM1 the first weight, IM2 the second image, IM3 the
        # second weight, and so on.

        # EWK: include the sigma values in these expressions.

        this_im = 'IM'+str(counter)
        this_pb = 'IM'+str(counter+1)
        counter += 2

        # LEL expressions that refer to the weighted sum and the
        # weight for this image pair.

        if is_pbcorr:
            # If pbcor, numerator is (PB**2 / sigma**2) * Image
            this_lel_sum = "({0}*{1}^2/{2})".format(this_im, this_pb, sigma**2)
            if output_noise_map:
                # A_p^2 / sig_p^2 * sig_p^2 / A_p = A_p / sig_p
                this_lel_sum_noise = "({0}/{1})".format(this_pb, sigma)

        else:
            # Otherwise PB is not squared.
            this_lel_sum = "({0}*{1}/{2})".format(this_im, this_pb, sigma**2)

        # In all cases, the denominator is PB^2 / sigma^2
        this_lel_weight = "({0}^2/{1})".format(this_pb, sigma**2)

        # Chain these together into a full string that adds all of the
        # images together.

        if ii == 0:
            lel_exp_sum += this_lel_sum
            lel_exp_weight += this_lel_weight

            if output_noise_map:
                lel_exp_sum_noise = this_lel_sum_noise
        else:
            lel_exp_sum += '+' + this_lel_sum
            lel_exp_weight += '+' + this_lel_weight

            if output_noise_map:
                lel_exp_sum_noise += '+' + this_lel_sum_noise

    # Feed our two LEL strings into immath to make the sum and weight
    # images.

    immath(imagename=full_imlist, mode='evalexpr',
           expr=lel_exp_sum, outfile=sum_file,
           imagemd=full_imlist[0])

    immath(imagename=full_imlist, mode='evalexpr',
           expr=lel_exp_weight, outfile=weight_file,
           imagemd=full_imlist[0])

    if output_noise_map:
        immath(imagename=full_imlist, mode='evalexpr',
               expr=lel_exp_sum_noise, outfile=sum_noise_file,
               imagemd=full_imlist[0])

    # Just to be safe, reset the masks on the two images.

    # myia = au.createCasaTool(casa.iatool)
    myia = iatool()
    myia.open(sum_file)
    myia.set(pixelmask=1)
    myia.close()

    myia.open(weight_file)
    myia.set(pixelmask=1)
    myia.close()

    if output_noise_map:
        myia.open(sum_noise_file)
        myia.set(pixelmask=1)
        myia.close()

    # Now divide the sum*weight image by the weight image.

    immath(imagename=[sum_file, weight_file], mode='evalexpr',
           expr='iif(IM1 > 0.0, IM0/IM1, 0.0)', outfile=temp_file,
           imagemd=sum_file)

    if output_noise_map:
        immath(imagename=[sum_noise_file, weight_file],
               mode='evalexpr',
               expr='iif(IM1 > 0.0, IM0/IM1, 0.0)',
               outfile=temp_noise_file,
               imagemd=sum_noise_file)

    # The mask for the final output is where we have any weight. This
    # may not be exactly what's desired in all cases, but it's not
    # clear to me what else to do except for some weight threshold
    # (does not have to be zero, though, I guess).

    immath(imagename=weight_file, mode='evalexpr',
           expr='iif(IM0 > 0.0, 1.0, 0.0)',
           outfile=mask_file)

    # Strip out any degenerate axes and create the final output file.

    imsubimage(imagename=temp_file,
               outfile=outfile,
               mask='"' + mask_file + '"',
               dropdeg=True)

    if output_noise_map:
        imsubimage(imagename=temp_noise_file,
                   outfile=outfile_noise,
                   mask='"' + mask_file + '"',
                   dropdeg=True)

#endregion
