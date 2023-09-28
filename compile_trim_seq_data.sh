#!/bin/sh

input=${@?Error:no input given}
awk 'BEGIN{ print "#Accession\tReads\tYield\tGeeCee\tMinLen\tAvgLen\tMaxLen\tAvgQual"}; {print $2}' $input | tr '\n' '\t' | sed $'s/trim/\\\n&/g' | sed 's/trim\///g;s/_T1.fastq.gz//g' | sed -e '$a\'

