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

mkdir -p /scratch/decipher/$folder

cd /scratch/decipher/$folder

### Creating config file
awk -F ',' 'BEGIN{ print "samples:"}; FNR > 21 {if($0 !~/NEG/ ) print "- " $2|"sort -u"}' $input > config.yaml
awk -F ',' 'BEGIN{ print "negative:"}; ( $0 ~/NEG/ ){print "- " $2 }' $input >> config.yaml

### Create input folder

mkdir -p /scratch/decipher/$folder/input

cd /scratch/decipher/$folder/input

### Pausing following jobs until bcl2fastq started properly

secs=$((30))
while [ $secs -gt 0 ]; do
   echo -ne "Waiting $secs\033[0K\r"
   sleep 1
   : $((secs--))
done

### COPY BaseCalls to input files (this is a requirement of shiver DON'T USE SYMLINKS)

for i in `ls $dir/BaseCalls/$folder/*.fastq.gz | cut -f 8 -d "/" | cut -f 1 -d "_" | sort -u`
do 
	cp $dir/BaseCalls/$folder/"$i"_*R1_001.fastq.gz /scratch/decipher/$folder/input/"$i"_R1.fastq.gz
        cp $dir/BaseCalls/$folder/"$i"_*R2_001.fastq.gz /scratch/decipher/$folder/input/"$i"_R2.fastq.gz
done

## Identify job_id of bcl2fastq on slurm

array=(${BCL// / })
JOBID_BCL=${array[3]}

### Load phevir2 module

source /phe/tools/miniconda3/etc/profile.d/conda.sh

conda activate phevir2

### Running deciPHEr_QC and deciPHErNEG on slurm
deciPHEr_QC=$(sbatch --dependency=afterok:${JOBID_BCL} --job-name deciPHEr_QC --mem 100G --ntasks 16 --time 960:00:00 -D /scratch/decipher/$folder --wrap "snakemake -j 16 --use-conda --configfile /scratch/decipher/$folder/config.yaml --snakefile /phe/tools/decipher/Snakefile_deciPHEr_QC_test_new_checkpoint " )
deciPHErNEG=$(sbatch --dependency=afterok:${JOBID_BCL} --job-name deciPHErNEG --mem 50G --ntasks 16 --time 960:00:00 -D /scratch/decipher/$folder --wrap "snakemake -j 16 --use-conda --configfile /scratch/decipher/$folder/config.yaml --snakefile /phe/tools/decipher/Snakefile_deciPHErNEG ")

## Identify job_id of deciPHEr_QC on slurm
array=(${deciPHEr_QC// / })
JOBID_deciPHEr_QC=${array[3]}

### Load phevir2 module

source /phe/tools/miniconda3/etc/profile.d/conda.sh

conda activate phevir2

### Running deciPHEr_HIV1 on slurm
deciPHEr_HIV1=$(sbatch --dependency=afterok:${JOBID_deciPHEr_QC} --job-name deciPHEr_HIV1 --mem 50G --ntasks 8 --time 960:00:00 -D /scratch/decipher/$folder --wrap "snakemake -j 8 --use-conda --configfile /scratch/decipher/$folder/QC_checkpoint_config.yaml --snakefile /phe/tools/decipher/HIV_scripts/Snakefile_deciPHEr_HIV1 " )

## Identify job_id of deciPHEr_HIV1 
array=(${deciPHEr_HIV1// / })
JOBID_deciPHEr_HIV1=${array[3]}

### Running deciPHEr_HIV2 on slurm
deciPHEr_HIV2=$(sbatch --dependency=afterok:${JOBID_deciPHEr_HIV1} --job-name deciPHEr_HIV2 --mem 50G --ntasks 8 --time 960:00:00 -D /scratch/decipher/$folder --wrap " snakemake -j 8 --use-conda --configfile /scratch/decipher/$folder/QC_checkpoint_config.yaml --snakefile /phe/tools/decipher/HIV_scripts/Snakefile_deciPHEr_HIV2 ")

## Identify job_id of deciPHEr_HIV2 
array=(${deciPHEr_HIV2// / })
JOBID_deciPHEr_HIV2=${array[3]}

### Load phevir2 module

source /phe/tools/miniconda3/etc/profile.d/conda.sh

conda activate phevir2

### Running deciPHEr_HCV1 on slurm
deciPHEr_HCV1=$(sbatch --dependency=afterok:${JOBID_deciPHEr_HIV2} --job-name deciPHEr_HCV1 --mem 50G --ntasks 8 --time 960:00:00 -D /scratch/decipher/$folder --wrap "snakemake -j 8 --use-conda --configfile /scratch/decipher/$folder/QC_checkpoint_config.yaml --snakefile /phe/tools/decipher/HCV_scripts/Snakefile_deciPHEr_HCV1 " )

## Identify job_id of deciPHEr_HCV1 
array=(${deciPHEr_HCV1// / })
JOBID_deciPHEr_HCV1=${array[3]}

### Running deciPHEr_HCV2 on slurm
deciPHEr_HCV2=$(sbatch --dependency=afterok:${JOBID_deciPHEr_HCV1} --job-name deciPHEr_HCV2 --mem 50G --ntasks 8 --time 960:00:00 -D /scratch/decipher/$folder --wrap " snakemake -j 8 --use-conda --configfile /scratch/decipher/$folder/QC_checkpoint_config.yaml --snakefile /phe/tools/decipher/HCV_scripts/Snakefile_deciPHEr_HCV2 ")