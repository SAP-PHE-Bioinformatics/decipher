#!/bin/sh

input=${@?Error:no input given}
awk 'BEGIN{ print "#Accession\tReads\tYield\tGeeCee\tMinLen\tAvgLen\tMaxLen\tAvgQual"}; {print $2}' $input | tr '\n' '\t' | sed $'s/filtered/\\\n&/g' | sed 's/filtered\///g;s/_R1.fastq.gz//g' | sed -e '$a\'

