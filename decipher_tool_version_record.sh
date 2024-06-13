#!/bin/sh

source /phe/tools/miniconda3/etc/profile.d/conda.sh

current_DateTime=$(date +'%d/%m/%Y  %R')

echo Date, $current_DateTime 
  
# echo BACTERIAL WGS RUN ID, $folder
echo Path to raw data,$dir

echo RUN ID,$folder

echo ' '

echo 'Pipeline: decipher v2.0.0'

echo ' '

echo TOOLS,TOOL_VERSION,DATABASES,DB_VERSION

##### phevir2 tools #####

conda activate phevir2

# FASTP
FASTP=$(conda list | grep "fastp" | awk '{print $1","$2}')
echo $FASTP

# KRAKEN
KRAKEN=$(conda list | grep "kraken2" | awk '{print $1","$2}')
KRAKEN_DB=$(basename /scratch/kraken/k2_pluspf_20220607/)
echo $KRAKEN,Kraken_k2_db,$KRAKEN_DB

# SEQTK
SEQTK=$(conda list | grep "seqtk" | awk '{print $1","$2}')
echo $SEQTK

# SAMTOOLS
SAMTOOLS=$(conda list | grep "samtools" | awk '{print $1","$2}')
echo $SAMTOOLS

# IVAR
IVAR=$(conda list | grep "ivar" | awk '{print $1","$2}')
echo $IVAR

##### metaphe tools #####
conda activate metaphe

# BOWTIE2
BOWTIE2=$(conda list | grep "bowtie2" | awk '{print $1","$2}')
echo $BOWTIE2

##### phesiqcal tools #####
conda activate phesiqcal

# SPADES
SPADES=$(conda list | grep "spades" | awk '{print $1","$2}')
echo $SPADES

# MINIMAP2
MINIMAP=$(conda list | grep "minimap2" | awk '{print $1","$2}')
echo $MINIMAP

# ABRICATE
ABRICATE=$(conda list | grep "abricate" | awk '{print $1","$2}')
HCVcore_dbupdate=$(stat -c %y /phe/tools/miniconda3/envs/phesiqcal/db/HCVcore/sequences | cut -d' ' -f 1)
echo $ABRICATE,HCVcore,$HCVcore_dbupdate

##### phevir tools #####
conda activate phevir

QUAST=$(conda list | grep "quast" | awk '{print $1","$2}')
echo $QUAST

##### covid-phylogeny tools #####
conda activate covid-phylogeny
BAMMIX=$(conda list | grep "bammix" | awk '{print $1","$2}')
echo $BAMMIX

##### shiver variants pipeline version dates #####

SHIVER=$(stat /phe/tools/decipher/HIV_scripts/shiver/ | grep "Modify" | cut -f 2 -d " ")
SHIVER_DB=$(stat /phe/tools/decipher/HIV_scripts/shiver/MyRefAlignment.fasta | grep "Modify" | cut -f 2 -d " ")
echo shiver,$SHIVER,shiver_reference_database,$SHIVER_DB

SHCVER=$(stat /phe/tools/decipher/HCV_scripts/shcver/ | grep "Modify" | cut -f 2 -d " ")
SHCVER_DB=$(stat /phe/tools/decipher/HCV_scripts/shcver/HCVRefAlignment_plusGT8.fasta | grep "Modify" | cut -f 2 -d " ")
echo shcver,$SHCVER,shcver_reference_database,$SHCVER_DB

SHBVER=$(stat /phe/tools/decipher/HBV_scripts/shbver/ | grep "Modify" | cut -f 2 -d " ")
SHBVER_DB=$(stat /phe/tools/decipher/HBV_scripts/shbver/HBVRefAlignment.fasta | grep "Modify" | cut -f 2 -d " ")
echo shbver,$SHBVER,shbver_reference_database,$SHBVER_DB

