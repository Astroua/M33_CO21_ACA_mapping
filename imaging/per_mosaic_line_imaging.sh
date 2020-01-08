
# Run all mosaics for all lines for all spectral line widths.

data_path="/mnt/bigdata/ekoch/M33/ALMA/ACA_Band6/"
code_path="/home/ekoch/ownCloud/project_code/M33_ALMA_2017.1.00901.S/imaging"
# casa_path="~/casa-release-5.4.1-32.el7/bin/casa"
casa_path="/home/ekoch/casa-pipeline-release-5.6.1-8.el7/bin/casa"

mkdir ${data_path}/per_mosaic_imaging/
mkdir ${data_path}/per_mosaic_imaging/logs/

cd ${data_path}/per_mosaic_imaging/logs/

lines=( "12CO21" "13CO21" "C18O21" "H2CO_303_202" "H2CO_322_221" "H2CO_321_220" )
spec_widths=( "native" "0p7kms" "1p3kms" "2kms" "2p6kms" )

# rerun_existing=True
rerun_existing=False

for brick_num in {1..3}; do
    for tile_num in {1..5}; do
        for line in "${lines[@]}"; do
            for spec_width in "${spec_widths[@]}"; do

                logfile_name="casa_M33_ACA_Brick${brick_num}Tile${tile_num}_${line}_${spec_width}_$(date "+%Y%m%d-%H%M%S").log"

                ${casa_path} --logfile ${data_path}/${logfile_name} -c ${code_path}/per_mosaic_line_imaging.py ${brick_num} ${tile_num} ${line} ${spec_width} ${rerun_existing}

            done
        done
    done
done
