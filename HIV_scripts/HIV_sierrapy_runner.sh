#!/bin/sh

### this runner script executes Snakefile_HIV_sierrapy if the HIV reporting config file exists.

### Load phevir2 module

source /phe/tools/miniconda3/etc/profile.d/conda.sh

conda activate phevir2

### creating a variable for the HIV reporting config file 
path_to_config_file="$1"  
config_file=$path_to_config_file"/QC_HIV_reporting_config.yaml"  

if [[ ! -f "$config_file" ]]; then
    echo "ERROR: The HIV reporting config file '$config_file' does not exist. Snakefile_HIV_sierrapy will not be run."
    exit 1
else
    echo "The HIV reporting config file '$config_file' exists. Now running Snakefile_HIV_sierrapy."
    snakemake -j 8 --printshellcmds --use-conda --configfile $config_file --snakefile /phe/tools/decipher/HIV_scripts/Snakefile_HIV_sierrapy
fi