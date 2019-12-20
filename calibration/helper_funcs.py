import os
from glob import glob
from copy import copy


def casa_full_path(casa_version):
    return f"~/{casa_version}/bin/casa --nologger --log2term --pipeline"


def return_sci_ous_dir(parent_dir):
    '''
    Keep going until we reach the actual data.
    '''

    new_dir = copy(parent_dir)

    while True:

        glob_dir = glob("{}/*".format(new_dir))

        if len(glob_dir) == 1:
            new_dir = glob_dir[0]
            continue
        elif len(glob_dir) > 1:
            has_product = any(["script" in path for path in glob_dir])
            if has_product:
                break
            else:
                raise ValueError("Unsure of folder structure")
        else:
            raise ValueError("Unsure of folder structure")

    return new_dir
