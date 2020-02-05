
# Run all mosaics for all lines for all spectral line widths.

data_path="/mnt/bigdata/ekoch/M33/ALMA/ACA_Band6/"
code_path="/home/ekoch/ownCloud/project_code/M33_ALMA_2017.1.00901.S/imaging"
# casa_path="~/casa-release-5.4.1-32.el7/bin/casa"
casa_path="/home/ekoch/casa-pipeline-release-5.6.1-8.el7/bin/casa"

mkdir ${data_path}/per_mosaic_imaging/
mkdir ${data_path}/per_mosaic_imaging/logs/

cd ${data_path}/per_mosaic_imaging/logs/

# rerun_existing=True
rerun_existing=False

# CO imaging
lines=( "12CO21" "13CO21" "C18O21")
spec_widths=( "1p3kms" "2kms" "2p6kms" "0p7kms")
# spec_widths=( "0p7kms" "1p3kms" "2kms" "2p6kms" "native")


for spec_width in "${spec_widths[@]}"; do
    for line in "${lines[@]}"; do
        for brick_num in {1..3}; do
            # Run all 5 tiles at once.
            pids=
            for tile_num in {1..5}; do

                logfile_name="casa_M33_ACA_Brick${brick_num}Tile${tile_num}_${line}_${spec_width}_$(date "+%Y%m%d-%H%M%S").log"

                (${casa_path} --nologger --nogui --log2term --nocrashreport --logfile ${data_path}/per_mosaic_imaging/logs/${logfile_name} -c ${code_path}/per_mosaic_line_imaging.py ${brick_num} ${tile_num} ${line} ${spec_width} ${rerun_existing}) &
                pids+=" $!"

                sleep 20
            done

        #     wait $pids || {echo "There was an error" >&2}

        done
    done
done
# wait $pids || {echo "There was an error" >&2}

# H2CO will only be detected via stacking.
# Only run an intermediate spectral resolution for now.

lines=( "H2CO_303_202" "H2CO_322_221" "H2CO_321_220" )
spec_widths=( "1p3kms" )

for spec_width in "${spec_widths[@]}"; do
    for line in "${lines[@]}"; do
        for brick_num in {1..3}; do
            # Run all 5 tiles at once.
            pids=
            for tile_num in {1..5}; do

                logfile_name="casa_M33_ACA_Brick${brick_num}Tile${tile_num}_${line}_${spec_width}_$(date "+%Y%m%d-%H%M%S").log"

                (${casa_path} --nologger --nogui --log2term --nocrashreport --logfile ${data_path}/per_mosaic_imaging/logs/${logfile_name} -c ${code_path}/per_mosaic_line_imaging.py ${brick_num} ${tile_num} ${line} ${spec_width} ${rerun_existing}) &
                pids+=" $!"

                sleep 20
            done
        done
    done
done

# Old code to run one mosaic at a time

# for spec_width in "${spec_widths[@]}"; do
#     for line in "${lines[@]}"; do
#         for brick_num in {1..3}; do
#             for tile_num in {1..5}; do

#                 logfile_name="casa_M33_ACA_Brick${brick_num}Tile${tile_num}_${line}_${spec_width}_$(date "+%Y%m%d-%H%M%S").log"

#                 ${casa_path} --logfile ${data_path}/${logfile_name} -c ${code_path}/per_mosaic_line_imaging.py ${brick_num} ${tile_num} ${line} ${spec_width} ${rerun_existing}

#             done
#         done
#     done
# done

# Run a dirty-only uniform imaging of 12CO. Just to see
# how much smaller the beam is.

# line="12CO21"
# spec_width="1p3kms"


# # Only run 3 at a time (b/c other runs are still going at the moment)
# for tile_num in {1..5}; do
#     pids=
#     for brick_num in {1..3}; do

#         logfile_name="casa_M33_ACA_Brick${brick_num}Tile${tile_num}_${line}_${spec_width}_$(date "+%Y%m%d-%H%M%S").log"

#         (${casa_path} --nologger --nogui --log2term --nocrashreport --logfile ${data_path}/per_mosaic_imaging/logs/${logfile_name} -c ${code_path}/per_mosaic_line_imaging_uniform.py ${brick_num} ${tile_num} ${line} ${spec_width} ${rerun_existing}) &
#         pids+=" $!"

#         sleep 20
#     done

#     wait $pids || {echo "There was an error" >&2}

# done
