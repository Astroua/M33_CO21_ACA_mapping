
'''
Copy calibrated MSs to a new directory and label with the brick + tile name.
'''

import os
from glob import glob

repo_path = os.path.expanduser("~/ownCloud/project_code/M33_ALMA_2017.1.00901.S/")

constants_script = os.path.join(repo_path, "constants.py")
exec(compile(open(constants_script, "rb").read(), constants_script, 'exec'))
helpers_script = os.path.join(repo_path, "calibration/helper_funcs.py")
exec(compile(open(helpers_script, "rb").read(), helpers_script, 'exec'))

orig_dir = os.getcwd()

data_path = os.path.expanduser("~/bigdata/ekoch/M33/ALMA/ACA_Band6/")
out_path = os.path.join(data_path, 'reduced')

if not os.path.exists(out_path):
    os.mkdir(out_path)

# Loop through the maps, copy the reduced MS to a common folder
# and rename the MS to include the brick + tile #

for key in brick_uid:

    maps_info = brick_uid[key]

    # Loop through observations of each mapping region
    for uid_dict in maps_info:

        proj_name = uid_dict['proj']
        sci_ous = uid_dict['sci_ous']

        if sci_ous == 'NODELIVERY':
            print(f"No data yet for {key}")
            continue

        # Get the data directory.

        parent_dir = os.path.join(data_path, proj_name, proj_name,
                                  f"science_goal.uid___{sci_ous}")

        full_path = return_sci_ous_dir(parent_dir)

        # Check if the calibrated folder already exists.
        has_calibrated = os.path.exists(f"{full_path}/calibrated")

        if not has_calibrated:
            print(f"{key} {sci_ous} does not have reduced data. Run pipeline"
                  " first.")
            continue

        # Find the MS
        ms_name = glob(f"{full_path}/calibrated/working/*.ms")

        if not len(ms_name) == 1:
            print(f"Something wrong in the reduction for {key} {proj_name} {sci_ous}")
            continue

        ms_name = ms_name[0]

        # Give new name
        new_ms_name = f"{key}_{proj_name}_{os.path.basename(ms_name)}"

        out_full = os.path.join(out_path, new_ms_name)

        if os.path.exists(out_full):
            print("MS has already been copied over.")
            continue

        os.system(f"cp -r {ms_name} {out_full}")
