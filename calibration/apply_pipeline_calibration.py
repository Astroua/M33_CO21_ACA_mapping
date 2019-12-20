
'''
Run the pipeline on all of the scheduling blocks
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

        parent_dir = os.path.join(data_path, proj_name, proj_name, f"science_goal.uid___{sci_ous}")

        full_path = return_sci_ous_dir(parent_dir)

        # Check if the calibrated folder already exists.
        has_calibrated = os.path.exists(f"{full_path}/calibrated")

        if has_calibrated:
            # Sometimes that folder is made but is empty.
            contents = glob(f"{full_path}/calibrated/*")
            if len(contents) > 0:
                print(f"Already calibrated {key} {sci_ous}")
                continue
            else:
                path_name = f"{full_path}/calibrated"
                os.system(f'rmdir {path_name}')

        # Change to the script directory.
        os.chdir(os.path.join(full_path, 'script'))

        # Run the PI script from this directory
        script_name = glob("*.scriptForPI.py")
        assert len(script_name) == 1
        script_name = script_name[0]

        casa_path = casa_full_path(casa_pipeline_versions[proj_name])

        out = os.system(f"{casa_path} -c {script_name}")

        os.chdir(orig_dir)
