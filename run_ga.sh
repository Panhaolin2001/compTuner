replace_list=(
    'ispell'
    'jpeg-d'
    'lame'
    'rijndael'
    'tiff2gba'
    'tiffdither'
    'tiffmedian'
    'tiff2bw'
)

export SRC_PATH=/home/haolin/project/compilerautotuning/llvmdataset/10.0.0/cBench-v1
export SCRIPT_PATH=/home/haolin/project/compTuner/runGA.py

printf "%s\n" "${replace_list[@]}" | xargs -n 1 -P 8 -I {} python3 ${SCRIPT_PATH} --src-path ${SRC_PATH}/{}.ll
