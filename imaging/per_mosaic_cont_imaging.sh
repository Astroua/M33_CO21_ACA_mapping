
# Run all mosaics for continuum

data_path="/mnt/bigdata/ekoch/M33/ALMA/ACA_Band6/"
code_path="/home/ekoch/ownCloud/project_code/M33_ALMA_2017.1.00901.S/imaging"
# casa_path="~/casa-release-5.4.1-32.el7/bin/casa"
casa_path="/home/ekoch/casa-pipeline-release-5.6.1-8.el7/bin/casa"

mkdir ${data_path}/per_mosaic_imaging/
mkdir ${data_path}/per_mosaic_imaging/logs/

cd ${data_path}/per_mosaic_imaging/logs/

# rerun_existing=True
rerun_existing=False


for brick_num in {1..3}; do
    # Run all 5 tiles at once.
    pids=
    for tile_num in {1..5}; do

        logfile_name="casa_M33_ACA_Brick${brick_num}Tile${tile_num}_Continuum_$(date "+%Y%m%d-%H%M%S").log"

        (${casa_path} --nologger --nogui --log2term --nocrashreport --logfile ${data_path}/per_mosaic_imaging/logs/${logfile_name} -c ${code_path}/per_mosaic_continuum_imaging.py ${brick_num} ${tile_num} ${rerun_existing}) &
        pids+=" $!"

        sleep 20
    done

    wait $pids || {echo "There was an error" >&2}

done

