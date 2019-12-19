
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
                              'sci_ous': 'NODELIVERY'}],
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
             "Brick2Tile2": [{'proj': '2019.1.01182.S', 'name': 'M33_i_06_7M',
                              'memb_ous': 'A001_X1465_X165e',
                              'sci_ous': 'NODELIVERY'}],
             "Brick2Tile3": [{'proj': '2019.1.01182.S', 'name': 'M33_f_06_7M',
                              'memb_ous': 'A001_X1465_X165a',
                              'sci_ous': 'NODELIVERY'}],
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
                              'sci_ous': 'NODELIVERY'}],
             "Brick3Tile4": [{'proj': '2017.1.00901.S', 'name': 'M33_b_06_7M',
                              'memb_ous': 'A001_X1296_X6a1',
                              'sci_ous': 'A001_X1296_X69f'}],
             "Brick3Tile5": [{'proj': '2017.1.00901.S', 'name': 'M33_a_06_7M',
                              'memb_ous': 'A001_X1296_X69d',
                              'sci_ous': 'A001_X1296_X69b'}]}

# casa versions to run pipeline for different projects.

casa_pipeline_versions = {'2017.1.00901.S': 'casa-release-5.4.0-68.el6',
                          '2019.1.01182.S': 'casa-pipeline-release-5.6.1-8.el7'}
