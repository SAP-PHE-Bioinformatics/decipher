##### NOTE: *Currently, the pipeline is specific to the pathogen genomics workflow at Public Health lab, SA Pathology. Under development for public use.*
# DECIPHER 

## Introduction
This pipeline designed to process HBV, HCV, and HIV probe-capture target enriched whole genome sequencing libraries prepared using the Agilent SureSelectXT system direct from clinical samples. It performs human read removal, initial automated QC assessments, accurate sample specific consensus construction, and downstream processing to support genotype and drug resistance analyses. Used by Pathogen genomics in Public Health and Epidemiology, South Australia. Automated using Snakemake and Slurm for processing on HPC cluster. It has a sub-workflow to process negative controls.

### Running the pipeline
Initiated by input of a Sample Sheet to a shell runner script as: <br>
`/path/to/decipher/bcl2deciPHEr_runner.sh /path/to/the/SampleSheet.csv/` , <br>

### Pipeline workflow
A snakemake workflow processes fastq files of HBV, HCV, and HIV to perform the following tasks:

1) read trimming (fastp),

2) human read removal (Bowtie2),

3) sequencing yield assessment (Seqtk packaged as 'fq' from the Nullabor pipeline),

4) species identification (Kraken2),

3) de novo assemblies (metaSPAdes) and their qc (Seqtk packaged as 'fa' from the Nullabor pipeline),

4) read mapping to a sample specific reference (using the shiver tool adapted for each virus),

6) consensus construction (iVar),

7) HCV genotyping (abricate using a custom HCVcore database),

8) coverage assessment (QUAST),

9) depth assessment (SAMtools),

10) HIV pol nucleotide variant analysis at drug resistant sites (bammix)

### Outputs

1) sequencing yeild summaries "*_seq_data.tab", 

2) species identification summaries "*_species_identification.tab",

3) whole genome and typing region consensus sequences "*_consensus/*_consensus.fa",

4) depth statistics summaries and histograms "depth_summary_*.tsv, *_depth_histograms/*_depth_*.tab",

5) coverage statistics summaries "summary_coverage_*.tsv"

6) HCV genotyping "HCV_genotype.tab"

7) HIV pol drug resistance site nucleotide variant files "bammix/*_DR_position_base_counts.csv"

#### Negative control (NEG) workflow
The pipeline includes the sub-workflow for negative controls determined by the sample ID given as "NEG*" in the sample sheet input. 
Only runs sequencing quality and kraken2 on NEGs to check for any potential contamination of HBV, HCV, and HIV viruses.


### Standard references and databases:
Human reference genome: GCA_000001405.29 <br>
Kraken2 database: k2pluspf (downloaded 20220607)

### For details on construction of custom references and databases:
For HBV whole genome reference database see: /path/to/decipher/HBV_scripts/shbver/hbv_decipher_reference_information.txt <br>

For HCV whole genome reference database see: /path/to/decipher/HCV_scripts/shcver/hcv_decipher_reference_information.txt <br>

For HIV whole genome reference database see: /path/to/decipher/HIV_scripts/shiver/hiv_decipher_reference_information.txt <br>

For HCVcore abricate database see the following settings: <br>

Downloaded from https://hcv.lanl.gov/components/sequence/HCV/search/searchi.html <br>
Genotype: Any Genotype <br>
	Subtype: Any Subtype <br>
	Include recombinants <br>
	Confirmed only <br>
	Genomic region: core <br>
	Exclude related <br>
	Format: Fasta <br>
	Gap handling: none <br>
	Sequence type: Nucleotides <br>
	Include genotype reference sequences <br>
	Include H77(NC_004102) reference sequence <br>
## Author
This pipeline was written by Rosa C. Coldbeck-Shackley.

## Citations
Acknowledgments to all the authors of tools used in the pipeline.
1. [fastp](https://github.com/OpenGene/fastp) <br>
   Chen S, Zhou Y, Chen Y, Gu J. fastp: an ultra-fast all-in-one FASTQ preprocessor. Bioinforma Oxf Engl. 2018 Sep 1;34(17):i884–90. 

2. [Bowtie2](https://github.com/tseemann/nullarbor) <br>
   Langmead B, Salzberg SL. Fast gapped-read alignment with Bowtie 2. Nat Methods. 2012 Mar 4;9(4):357–9.

3. [Nullarbor](https://github.com/tseemann/nullarbor) <br>
   Seemann T, Goncalves da Silva A, Bulach DM, Schultz MB, Kwong JC, Howden BP.

3. [kraken2](https://github.com/DerrickWood/kraken2) <br>
   Taxonomic sequence classifier that assigns taxonomic labels to DNA sequences Wood, D.E., Lu, J. & Langmead, B. Improved metagenomic analysis with Kraken 2 
   Genome Biol 20, 257 (2019)

4. [metaSPAdes](https://github.com/ablab/spades) <br>
   Nurk S, Meleshko D, Korobeynikov A, Pevzner PA. metaSPAdes: a new versatile metagenomic assembler. Genome Res. 2017 May;27(5):824–34.

5. [shiver](https://github.com/ChrisHIV/shiver) <br>
   Wymant C, Blanquart F, Golubchik T, Gall A, Bakker M, Bezemer D, et al. Easy and accurate reconstruction of whole HIV genomes from short-read sequence data with shiver. Virus Evol. 2018 Jan;4(1):vey007.

6. [ABRicate](https://github.com/tseemann/abricate) <br>
   Mass screening of contigs for antimicrobial resistance, virulence genes and plasmids. <br>
   Seemann T.
 
7. [iVar](https://github.com/andersen-lab/ivar) <br>
   Grubaugh ND, Gangavarapu K, Quick J, Matteson NL, De Jesus JG, Main BJ, et al. An amplicon-based sequencing framework for accurately measuring intrahost virus diversity using PrimalSeq and iVar. Genome Biol. 2019 Jan 8;20(1):8.

8. [QUAST](https://github.com/ablab/quast) <br>
   Gurevich A, Saveliev V, Vyahhi N, Tesler G. QUAST: quality assessment tool for genome assemblies. Bioinforma Oxf Engl. 2013 Apr 15;29(8):1072–5.

9. [SAMtools](https://github.com/samtools/samtools) <br>
   Li H, Handsaker B, Wysoker A, Fennell T, Ruan J, Homer N, et al. The Sequence Alignment/Map format and SAMtools. Bioinforma Oxf Engl. 2009 Aug 15;25(16):2078–9.

10. [bammix](https://github.com/chrisruis/bammix) <br>
    chrisruis.
    
12. [SNAKEMAKE](https://snakemake.github.io/) <br>
    Mölder, F., Jablonski, K.P., Letcher, B., Hall, M.B., Tomkins-Tinch, C.H., Sochat, V., Forster, J., Lee, S., Twardziok, S.O., Kanitz, A., Wilm, A., Holtgrewe, 
    M., Rahmann, S., Nahnsen, S., Köster, J., 2021. Sustainable data analysis with Snakemake. F1000Res 10, 33.

13. [SLURM](https://github.com/SchedMD/slurm) <br>
    Yoo, A.B., Jette, M.A., Grondona, M. (2003). SLURM: Simple Linux Utility for Resource Management. In: Feitelson, D., Rudolph, L., Schwiegelshohn, U. (eds) Job 
    Scheduling Strategies for Parallel Processing. JSSPP 2003. Lecture Notes in Computer Science, vol 2862. Springer, Berlin, Heidelberg. 
    https://doi.org/10.1007/10968987_3
