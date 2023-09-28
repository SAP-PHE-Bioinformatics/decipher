#!/bin/sh

input=${@?Error:no input given}
awk 'BEGIN{ print "#Accession\tReads\tYield\tGeeCee\tMinLen\tAvgLen\tMaxLen\tAvgQual"}; {print $2}' $input | tr '\n' '\t' | sed $'s/input/\\\n&/g' | sed 's/input\///g;s/_R1.fastq.gz//g' | sed -e '$a\'

