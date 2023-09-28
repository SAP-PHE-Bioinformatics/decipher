#!/bin/sh

input=${1?Error:no SampleSheet.csv given}

dir=$( dirname $input)

### Load module

source /phe/tools/miniconda3/etc/profile.d/conda.sh

conda activate phesiqcal

### Running bcl2fastq
BCL=$(sbatch --job-name bcl2fastq --mem 100G --ntasks 16 --time 960:00:00 --wrap "bcl2fastq --sample-sheet $input --runfolder-dir $dir --mask-short-adapter-reads 0 --use-bases-mask Y150,I8,N10,Y150 --no-lane-splitting --ignore-missing-bcls --ignore-missing-filter --ignore-missing-positions --output-dir $dir/BaseCalls")

### Create folder
folder=$(awk -F ',' 'FNR == 4 {print $2}' $input)

mkdir -p /scratch/shcvPHEr/$folder

cd /scratch/shcvPHEr/$folder

### Creating config file
awk -F ',' 'BEGIN{ print "samples:"}; FNR > 21 {if($0 !~/NEG/ ) print "- " $2|"sort -u"}' $input > config.yaml
awk -F ',' 'BEGIN{ print "negative:"}; ( $0 ~/NEG/ ){print "- " $2 }' $input >> config.yaml

### Create input folder

mkdir -p /scratch/shcvPHEr/$folder/input

cd /scratch/shcvPHEr/$folder/input

### Pausing following jobs until bcl2fastq started properly

secs=$((30))
while [ $secs -gt 0 ]; do
   echo -ne "Waiting $secs\033[0K\r"
   sleep 1
   : $((secs--))
done

### COPY BaseCalls to input files (this is a requirement of shcver DON'T USE SYMLINKS)

for i in `ls $dir/BaseCalls/$folder/*.fastq.gz | cut -f 8 -d "/" | cut -f 1 -d "_" | sort -u`
do 
	cp $dir/BaseCalls/$folder/"$i"_*R1_001.fastq.gz /scratch/shcvPHEr/$folder/input/"$i"_R1.fastq.gz
        cp $dir/BaseCalls/$folder/"$i"_*R2_001.fastq.gz /scratch/shcvPHEr/$folder/input/"$i"_R2.fastq.gz
done

## Identify job_id of bcl2fastq on slurm

array=(${BCL// / })
JOBID_BCL=${array[3]}

### Load phevir2 module

source /phe/tools/miniconda3/etc/profile.d/conda.sh

conda activate phevir2

### Running shcver1 and shcverNEG on slurm
shcvER1=$(sbatch --dependency=afterok:${JOBID_BCL} --job-name shcver1 --mem 250G --ntasks 16 --time 960:00:00 -D /scratch/shcvPHEr/$folder --wrap "snakemake -j 16 --use-conda --configfile /scratch/shcvPHEr/$folder/config.yaml --snakefile /phe/tools/decipher/HCV_scripts/Snakefile_shcvPHEr1 " )
shcvERNEG=$(sbatch --dependency=afterok:${JOBID_BCL} --job-name shcverNEG --mem 50G --ntasks 16 --time 960:00:00 -D /scratch/shcvPHEr/$folder --wrap "snakemake -j 16 --use-conda --configfile /scratch/shcvPHEr/$folder/config.yaml --snakefile /phe/tools/decipher/HCV_scripts/Snakefile_shcvPHErNEG ")

## Identify job_id of shcver1 on slurm
array=(${shcvER1// / })
JOBID_shcvER1=${array[3]}

### Load phevir2 module

source /phe/tools/miniconda3/etc/profile.d/conda.sh

conda activate phevir2

### Running shcver2 on slurm
shcvER2=$(sbatch --dependency=afterok:${JOBID_shcvER1} --job-name shcver2 --mem 50G --ntasks 8 --time 960:00:00 -D /scratch/shcvPHEr/$folder --wrap "snakemake -j 8 --use-conda --configfile /scratch/shcvPHEr/$folder/config.yaml --snakefile /phe/tools/decipher/HCV_scripts/Snakefile_shcvPHEr2 " )

## Identify job_id of shcver2 on slurm
array=(${shcvER2// / })
JOBID_shcvER2=${array[3]}

### Load phevir2 module

#source /phe/tools/miniconda3/etc/profile.d/conda.sh

#conda activate phevir2

### Running shcver3 on slurm
#shcvER3=$(sbatch --dependency=afterok:${JOBID_shcvER2} --job-name shcver3 --mem 50G --ntasks 8 --time 960:00:00 -D /scratch/shcvPHEr/$folder --wrap " snakemake -j 8 --use-conda --configfile /scratch/shcvPHEr/$folder/QC_checkpoint_config.yaml --snakefile /phe/tools/decipher/HCV_scripts/Snakefile_shcvPHEr3 ")
