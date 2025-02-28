#!/bin/sh

# run this script to cleanup decipher temp files and slurm logs after sample QC has been confirmed
### the input file is the full path to the run's QC config file
### to run the script: /path/to/decipher/decipher_cleanup.sh /path/to/QC_checkpoint_config.yaml

input=${1?Error:no QC_checkpoint_config.yaml given}
dir=$( dirname $input )

cd $dir

### remove temp files, and intermediate processing sh*ver read files
for i in `grep "-" QC_checkpoint_config.yaml | cut -f 2 -d " " | cut -f 2 -d "'"` ;
do 
rm "$i"/sh*ver/sh*ver_output/temp_* 
rm -r "$i"/sh*ver/sh*ver_input/
rm "$i"/sh*ver/sh*ver_output/"$i"_convert_*.fastq
done

### remove slurm files and intermediate processing trim read files
rm -r ./trim
rm ./slurm*
