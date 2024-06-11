replace_list=(
    "ispell"
    "jpeg-d"
    "lame"
    "rijndael"
    "tiff2rgba"
    "tiffdither"
    "tiffmedian"
    "tiff2bw"
    "sha"
    "adpcm"
    "bitcount"
    "blowfish"
    "bzip2"
    "crc32"
    "dijkstra"
    "gsm"
    "patricia"
    "qsort"
    "stringsearch2"
    "stringsearch"
    "susan"
    "jpeg-c"
    "ghostscript"
    )

export SRC_PATH=/home/haolin/project/compilerautotuning/llvmdataset/10.0.0/cBench-v1
export SCRIPT_PATH_COMTUNER=/home/haolin/project/compTuner/runCompTuner.py

printf "%s\n" "${replace_list[@]}" | xargs -n 1 -P 22 -I {} python3 ${SCRIPT_PATH_COMTUNER} --src-path ${SRC_PATH}/{}.ll
