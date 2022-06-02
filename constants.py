
'''
Useful numbers to have handy
'''

import astropy.units as u

distance = 840 * u.kpc


def ang_to_phys(ang_size, distance=distance):
    '''
    Convert from angular to physical scales
    '''
    return (ang_size.to(u.rad).value * distance).to(u.pc)


co21_freq = 230.538 * u.GHz
thirtco21_freq = 220.3986842 * u.GHz

line_dict = {"12co": co21_freq,
             "13co": thirtco21_freq}

co21_mass_conversion = 6.7 * (u.Msun / u.pc ** 2) / (u.K * u.km / u.s)
beam_eff_30m_druard = 56 / 92.


# Define the uid to BrickXTileY conversion. Also SB name.

brick_uid = {"Brick1Tile1": [{'proj': '2019.1.01182.S', 'name': 'M33_l_06_7M',
                              'memb_ous': 'A001_X1465_X1672',
                              'sci_ous': 'A001_X1465_X1670'}],
             "Brick1Tile2": [{'proj': '2019.1.01182.S', 'name': 'M33_k_06_7M',
                              'memb_ous': 'A001_X1465_X166e ',
                              'sci_ous': 'A001_X1465_X166c'}],
             "Brick1Tile3": [{'proj': '2019.1.01182.S', 'name': 'M33_j_06_7M',
                              'memb_ous': 'A001_X1465_X166a',
                              'sci_ous': 'A001_X1465_X1668'},
                             {'proj': '2017.1.00901.S', 'name': 'M33_m_06_7M',
                              'memb_ous': 'A001/X1296/X6cd ',
                              'sci_ous': 'A001_X1296_X6cb'}],
             "Brick1Tile4": [{'proj': '2019.1.01182.S', 'name': 'M33_i_06_7M',
                              'memb_ous': 'A001_X1465_X1666',
                              'sci_ous': 'A001_X1465_X1664'}],
             "Brick1Tile5": [{'proj': '2019.1.01182.S', 'name': 'M33_h_06_7M',
                              'memb_ous': 'A001_X1465_X1662',
                              'sci_ous': 'A001_X1465_X1660'}],
             "Brick2Tile1": [{'proj': '2017.1.00901.S', 'name': 'M33_j_06_7M',
                              'memb_ous': 'A001_X1296_X6c1 ',
                              'sci_ous': 'A001_X1296_X6bf'}],
             "Brick2Tile2": [{'proj': '2019.1.01182.S', 'name': 'M33_g_06_7M',
                              'memb_ous': 'A001_X1465_X165e',
                              'sci_ous': 'A001_X1465_X165c'}],
             "Brick2Tile3": [{'proj': '2019.1.01182.S', 'name': 'M33_f_06_7M',
                              'memb_ous': 'A001_X1465_X165a',
                              'sci_ous': 'A001_X1465_X1658'}],
             "Brick2Tile4": [{'proj': '2019.1.01182.S', 'name': 'M33_e_06_7M',
                              'memb_ous': 'A001_X1465_X1656',
                              'sci_ous': 'A001_X1465_X1654'}],
             "Brick2Tile5": [{'proj': '2019.1.01182.S', 'name': 'M33_d_06_7M',
                              'memb_ous': 'A001_X1465_X1652',
                              'sci_ous': 'A001_X1465_X1650'}],
             "Brick3Tile1": [{'proj': '2019.1.01182.S', 'name': 'M33_c_06_7M',
                              'memb_ous': 'A001_X1465_X164e',
                              'sci_ous': 'A001_X1465_X164c'}],
             "Brick3Tile2": [{'proj': '2019.1.01182.S', 'name': 'M33_b_06_7M',
                              'memb_ous': 'A001_X1465_X164a',
                              'sci_ous': 'A001_X1465_X1648'}],
             "Brick3Tile3": [{'proj': '2019.1.01182.S', 'name': 'M33_a_06_7M',
                              'memb_ous': 'A001_X1465_X1646',
                              'sci_ous': 'A001_X1465_X1644'}],
             "Brick3Tile4": [{'proj': '2017.1.00901.S', 'name': 'M33_b_06_7M',
                              'memb_ous': 'A001_X1296_X6a1',
                              'sci_ous': 'A001_X1296_X69f'}],
             "Brick3Tile5": [{'proj': '2017.1.00901.S', 'name': 'M33_a_06_7M',
                              'memb_ous': 'A001_X1296_X69d',
                              'sci_ous': 'A001_X1296_X69b'}]}

# casa versions to run pipeline for different projects.

casa_pipeline_versions = {'2017.1.00901.S': 'casa-release-5.4.0-68.el6',
                          '2019.1.01182.S': 'casa-pipeline-release-5.6.1-8.el7'}

# casa versions used for the imaging
# EWK: Don't want to use 5.4.1 but newer versions fail when too many files
# are open (regardless of `ulimit` setting)
casa_imaging_versions = {'2017.1.00901.S': "casa-release-5.4.1-32.el7",
                         '2019.1.01182.S': "casa-release-5.4.1-32.el7"}

# `vel_pad` is the padding used to define line-free regions
# This is more important for the 2017 setup with the narrow bandwidths

spw_setup_2019 = {'12CO21': {'spw_num': '16',
                             'bwidth': 0.5 * u.GHz,
                             'nchan': 2048,
                             'vel_pad': 25 * u.km / u.s,
                             'restfreq': 230.538 * u.GHz},
                  'Continuum_232': {'spw_num': '18',
                                    'bwidth': 2 * u.GHz,
                                    'nchan': 128,
                                    'vel_pad': 0 * u.km / u.s,
                                    'restfreq': 0 * u.GHz},
                  '13CO21': {'spw_num': '20',
                             'bwidth': 0.25 * u.GHz,
                             'nchan': 1024,
                             'vel_pad': 25 * u.km / u.s,
                             'restfreq': 220.398684 * u.GHz},
                  'C18O21': {'spw_num': '22',
                             'bwidth': 0.25 * u.GHz,
                             'nchan': 1024,
                             'vel_pad': 25 * u.km / u.s,
                             'restfreq': 219.56035 * u.GHz},
                  'H2CO_303_202': {'spw_num': '24',
                                   'bwidth': 0.25 * u.GHz,
                                   'nchan': 512,
                                   'vel_pad': 15 * u.km / u.s,
                                   'restfreq': 218.222192 * u.GHz},
                  'H2CO_322_221': {'spw_num': '26',
                                   'bwidth': 0.25 * u.GHz,
                                   'nchan': 512,
                                   'vel_pad': 15 * u.km / u.s,
                                   'restfreq': 218.475632 * u.GHz},
                  'H2CO_321_220': {'spw_num': '28',
                                   'bwidth': 0.25 * u.GHz,
                                   'nchan': 512,
                                   'vel_pad': 15 * u.km / u.s,
                                   'restfreq': 218.760066 * u.GHz}}

spw_setup_2017 = {'12CO21': {'spw_num': '16',
                             'bwidth': 0.125 * u.GHz,
                             'nchan': 256,
                             'vel_pad': 25 * u.km / u.s,
                             'restfreq': 230.538 * u.GHz},
                  'Continuum_232': {'spw_num': '18',
                                    'bwidth': 2 * u.GHz,
                                    'nchan': 128,
                                    'vel_pad': 0 * u.km / u.s,
                                    'restfreq': 0 * u.GHz},
                  '13CO21': {'spw_num': '20',
                             'bwidth': 0.125 * u.GHz,
                             'nchan': 256,
                             'vel_pad': 0 * u.km / u.s,
                             'restfreq': 220.398684 * u.GHz},
                  'C18O21': {'spw_num': '22',
                             'bwidth': 0.125 * u.GHz,
                             'nchan': 256,
                             'vel_pad': 0 * u.km / u.s,
                             'restfreq': 219.56035 * u.GHz},
                  'H2CO_303_202': {'spw_num': '24',
                                   'bwidth': 0.125 * u.GHz,
                                   'nchan': 256,
                                   'vel_pad': 0 * u.km / u.s,
                                   'restfreq': 218.222192 * u.GHz},
                  'H2CO_322_221': {'spw_num': '26',
                                   'bwidth': 0.125 * u.GHz,
                                   'nchan': 256,
                                   'vel_pad': 0 * u.km / u.s,
                                   'restfreq': 218.475632 * u.GHz},
                  'H2CO_321_220': {'spw_num': '28',
                                   'bwidth': 0.125 * u.GHz,
                                   'nchan': 256,
                                   'vel_pad': 0 * u.km / u.s,
                                   'restfreq': 218.760066 * u.GHz}}
