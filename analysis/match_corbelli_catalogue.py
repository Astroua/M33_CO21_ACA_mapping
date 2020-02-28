
'''
Map from the ACA catalogue to the IRAM catalogue from Corbelli+2017

We'll also determine which clouds have 13CO detected and
their evolutionary phase
'''

from astropy.table import Table
from astropy.io import fits
import os
import astropy.units as u
from astropy.coordinates import SkyCoord
from spectral_cube import SpectralCube
import numpy as np


# data_path = os.path.expanduser("~/storage/M33/")
data_path = os.path.expanduser("~/bigdata/ekoch/M33/")

aca_path = f"{data_path}/ALMA/ACA_Band6/"

corbelli_table = Table.read(f"{data_path}/Corbelli_17_catalogues/J_A+A_601_A146_table5.dat.fits")

aca_table = Table.read(f"{aca_path}/cprops_12CO21/M33_ACA_12CO21_0p7kms_fullmosaic_roundbeam.image_K_M33_co21_m33_props.fits")


# The beam is ~12 arcsec. We're going to require matched clouds be within
# 1.5 beams
max_sep = 12 * u.arcsec * 1.5

iram_cloud_coords = SkyCoord(corbelli_table['RAdeg'],
                             corbelli_table['DEdeg'],
                             frame='icrs')

dist_matrix = np.zeros((len(aca_table), len(corbelli_table))) * u.deg

for idx in range(len(aca_table)):

    cloud_coord = SkyCoord(aca_table['XCTR_DEG'][idx] * u.deg,
                           aca_table['YCTR_DEG'][idx] * u.deg,
                           frame='icrs')

    dist_matrix[idx] = cloud_coord.separation(iram_cloud_coords)



# Match the clouds. Assume that each ACA cloud is associated with 0 or 1
# IRAM clouds
mapping_dict = {}

iram_cloud_index = np.arange(len(corbelli_table))

for idx in range(len(aca_table)):

    mapping_dict[idx] = []

    matches = np.where(dist_matrix[idx] < max_sep)[0]

    if len(matches) == 0:
        continue

    match_dists = dist_matrix[idx][matches]

    # Otherwise, match the minimum, if it's closest.
    for idx2 in np.argsort(match_dists):

        match_idx = matches[idx2]

        match_dist = match_dists[idx2]

        # If this is the smallest distance from the IRAM cloud,
        # include the mapping and ignore the rest.
        if match_dist == dist_matrix[:, match_idx].min():
            mapping_dict[idx].append(match_idx)

        # Otherwise, we don't map those clouds.

# Need to save this in some format.
# Convert to an array. Pad empty spots

max_match = 0
for match in mapping_dict:
    nmatch = len(mapping_dict[match])
    if max_match < nmatch:
        max_match = nmatch

out_array = np.zeros((len(aca_table), max_match + 1), dtype=int)

for match in mapping_dict:

    nmatch = len(mapping_dict[match])

    out_array[match, 0] = match
    out_array[match, 1:nmatch + 1] = mapping_dict[match]
    if nmatch < max_match:
        out_array[match, nmatch + 1:] = (2 - nmatch) * [-1]

columns = ['ACA_IDX'] + [f'IRAM_IDX_{i +1 }' for i in range(max_match)]

match_table = Table(data=out_array, names=columns)

match_table.write(f"{aca_path}/cprops_12CO21/M33_ACA_12CO21_0p7kms_fullmosaic_roundbeam.image_K_M33_co21.GMCcat_mapto_IRAM.fits",
                  overwrite=True)
