
# Make all final mosaic cubes.


data_path="/mnt/bigdata/ekoch/M33/ALMA/ACA_Band6/"
code_path="/home/ekoch/ownCloud/project_code/M33_ALMA_2017.1.00901.S/imaging"

# This needs CASA 6 to use radio-beam properly
conda activate casa_py36

mkdir ${data_path}/full_mosaic/
mkdir ${data_path}/full_mosaic/logs/

cd ${data_path}/full_mosaic/logs/

# rerun_existing=True
overwrite=False

cleanup_temps=True

# Make versions with the smallest round beam
# and the smallest elliptical beam
round_beam_convolution=( "True" "False" )

# Make versions with and without the mosaics that have
# highly asymmetric beams
exclude_asymms=( "True" "False" )

# CO imaging
lines=( "12CO21" "13CO21" "C18O21")
# lines=( "12CO21")
spec_widths=( "2p6kms" "2kms" "1p3kms" "0p7kms" )

for round_convolve in "${round_beam_convolution[@]}"; do
    for exclude_asymm in "${exclude_asymms[@]}"; do
        for spec_width in "${spec_widths[@]}"; do
            pids=
            for line in "${lines[@]}"; do

                (python ${code_path}/make_full_mosaic.py ${line} ${spec_width} ${round_convolve} ${exclude_asymm} ${overwrite} ${cleanup_temps}) &
                pids+=" $!"

                sleep 20
            done
            wait $pids || {echo "There was an error" >&2}
        done
    done
done

# H2CO imaging
lines=( "H2CO_303_202" "H2CO_322_221" "H2CO_321_220" )
spec_widths=( "1p3kms" )

for round_convolve in "${round_beam_convolution[@]}"; do
    for exclude_asymm in "${exclude_asymms[@]}"; do
        for spec_width in "${spec_widths[@]}"; do
            pids=
            for line in "${lines[@]}"; do

                (python ${code_path}/make_full_mosaic.py ${line} ${spec_width} ${round_convolve} ${exclude_asymm} ${overwrite} ${cleanup_temps}) &

                pids+=" $!"

                sleep 20
            done
            wait $pids || {echo "There was an error" >&2}
        done
    done
done

# Add running the continuum mosaic when ready.
