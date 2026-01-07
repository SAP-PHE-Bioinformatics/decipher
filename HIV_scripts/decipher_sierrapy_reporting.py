#!/usr/bin/env python

# run this script to generate an excel formatted report from Stanford HIV DB sierrapy .json output

# load packages
import sys
import pandas as pd
import numpy as np
import json
import openpyxl
import re
import argparse
import os

## defining ANSI escape sequences for colors for print messages
class bcolors:
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    OKYELLOW = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

################################ UPDATE THE VERSION INFORMATION IF THE SCRIPT IS MODIFIED #################################
VERSION = "1.0.0"
parser = argparse.ArgumentParser(prog="decipher_sierrapy_reporting.py",
                                 description="This script converts the sierrapy Stanford HIVDB output into a report."
)
parser.add_argument("-v", 
                    "--version", 
                    action="version", 
                    version="%(prog)s v" + VERSION
)
## define inputs, outputs and comment reference files based on command-line flags
parser.add_argument(
    '--input', 
    required=True,  
    help=f"Path to raw .json data from sierrapy", 
    )
parser.add_argument(
    '--intermediate', 
    required=True,  
    help=f"Path to preliminary sierrapy report", 
    )
parser.add_argument(
    '--output', 
    required=True, 
    help="Name of final report file")
parser.add_argument(
    '--ref_PR', 
    required=True, 
    help="Path to the PR drug comments reference file",
    )
parser.add_argument(
    '--ref_NRTI', 
    required=True, 
    help="Path to the NRTI drug comments reference file",
    )
parser.add_argument(
    '--ref_NNRTI', 
    required=True, 
    help="Path to the NNRTI drug comments reference file",
    )
parser.add_argument(
    '--ref_IN', 
    required=True, 
    help="Path to the IN drug comments reference file",
    )

args = parser.parse_args()
print(args)

## Access the value/path of arguments being passed to the script
### preliminary report file path
input_json = os.path.abspath(args.input)
print(f"{bcolors.OKYELLOW} Using raw .json file: {input_json} {bcolors.ENDC}")

### preliminary report file path
prelim_report = os.path.abspath(args.intermediate)
print(f"{bcolors.OKYELLOW} Creating preliminary report file: {prelim_report} {bcolors.ENDC}")

### final report files path
output_final_report = os.path.abspath(args.output)
print(f"{bcolors.OKYELLOW} Creating final report file: {output_final_report} {bcolors.ENDC}")

### PR comments reference file path
in_ref_PR = os.path.abspath(args.ref_PR)
print(f"{bcolors.OKYELLOW} Using the PR comments reference file: {in_ref_PR} {bcolors.ENDC}")

### NRTI comments reference file path
in_ref_NRTI = os.path.abspath(args.ref_NRTI)
print(f"{bcolors.OKYELLOW} Using the NRTI comments reference file: {in_ref_NRTI} {bcolors.ENDC}")

### NRTI comments reference file path
in_ref_NNRTI = os.path.abspath(args.ref_NNRTI)
print(f"{bcolors.OKYELLOW} Using the NNRTI comments reference file: {in_ref_NNRTI} {bcolors.ENDC}")

### IN comments reference file path
in_ref_IN = os.path.abspath(args.ref_IN)
print(f"{bcolors.OKYELLOW} Using the IN comments reference file: {in_ref_IN} {bcolors.ENDC}")

## Open and read the JSON file
with open(input_json, 'r') as f:
    json_data = json.load(f)
json_df = pd.DataFrame(json_data)

## pull basic information about sequence (consensus id and subtype), rename the column headers, transpose and drop unneccesary columns
basic_data = pd.json_normalize(data=json_data[0], record_path=['inputSequence'], meta=[['inputSequence','header'],['subtypeText']], errors='ignore').drop([0],axis=1).reindex()
basic_data_rename = basic_data.rename(columns={"inputSequence.header": "Consensus ID","subtypeText":"Subtype"})
basic_data_transposed = basic_data_rename.transpose().drop([1],axis=1)
basic_data_transposed_rename = basic_data_transposed.reset_index().rename(columns={0:"Sequence_Information","index":"Basic_Info"})

## pull the version information, rename the column headers, transpose and drop unneccesary columns
version = pd.json_normalize(data=json_data, record_path=['drugResistance']).drop(['drugScores','gene.name'],axis=1).drop_duplicates(keep="first", inplace=False).reindex()
version_rename = version.rename(columns={"version.text": "Database Version","version.publishDate":"Published Date"})
version_transpose = version_rename.transpose()
version_transposed_rename = version_transpose.reset_index().rename(columns={0:"Database_Information","index":"Database_Info"})

## create a dataframe pulling specific drug resistance mutations
# create an empty report dataframe including all possible mutationTypes that we report
col_header = pd.DataFrame(columns=['alignedGeneSequences.gene.name','primaryType','text'])
mut_types = pd.DataFrame({'mutationTypes': ['NRTI Mutations','NNRTI Mutations', 'RT Other Mutations', 'INSTI Major Mutations', 'INSTI Accessory Mutations', 'IN Other Mutations', 'PI Major Mutations', 'PI Accessory Mutations', 'PR Other Mutations']})
mutations_report_empty = pd.concat([col_header, mut_types], ignore_index=True)
# pull the mutations: flattern .json data to the nested 'alignedGeneSequences','mutations' record path to enable extraction of mutations (one-line per mutation type)
mutations = pd.json_normalize(data=json_data, record_path=['alignedGeneSequences','mutations'], meta=[['alignedGeneSequences','gene','name'], ['alignedGeneSequences', 'gene', 'length'], ['subtypeText']], errors='ignore')
# condense data into a comma separated list of all mutations for each gene and each primaryType 
mutations_list = mutations.groupby(['alignedGeneSequences.gene.name','primaryType']).agg({'text': ','.join}).reset_index()
# add a 'mutationType' column to the data based on each gene and its primaryType to match the empty report template column
conditions = [
    (mutations_list['alignedGeneSequences.gene.name'].str.contains('RT')) & (mutations_list['primaryType']=='NRTI'),
    (mutations_list['alignedGeneSequences.gene.name'].str.contains('RT')) & (mutations_list['primaryType']=='NNRTI'),
    (mutations_list['alignedGeneSequences.gene.name'].str.contains('RT')) & (mutations_list['primaryType'].str.contains('Other')),
    (mutations_list['alignedGeneSequences.gene.name'].str.contains('IN')) & (mutations_list['primaryType'].str.contains('Major')),
    (mutations_list['alignedGeneSequences.gene.name'].str.contains('IN')) & (mutations_list['primaryType'].str.contains('Accessory')),
    (mutations_list['alignedGeneSequences.gene.name'].str.contains('IN')) & (mutations_list['primaryType'].str.contains('Other')),
    (mutations_list['alignedGeneSequences.gene.name'].str.contains('PR')) & (mutations_list['primaryType'].str.contains('Major')),
    (mutations_list['alignedGeneSequences.gene.name'].str.contains('PR')) & (mutations_list['primaryType'].str.contains('Accessory')),
    (mutations_list['alignedGeneSequences.gene.name'].str.contains('PR')) & (mutations_list['primaryType'].str.contains('Other')),
]
choices = [
    'NRTI Mutations',
    'NNRTI Mutations',
    'RT Other Mutations',
    'INSTI Major Mutations',
    'INSTI Accessory Mutations',
    'IN Other Mutations', 
    'PI Major Mutations', 
    'PI Accessory Mutations', 
    'PR Other Mutations'
]
mutations_list['mutationTypes'] = np.select(conditions, choices, 'None')
# fill in sample data using the empty report as a template for all possible mutationTypes
mutations_report_full1 = mutations_report_empty.merge(mutations_list, how = 'left', on = ['mutationTypes'])
# drop unused columns (generated during the left join) from merge, and replace NaN with "None"
mutations_report_full2 = mutations_report_full1.drop(['alignedGeneSequences.gene.name_x', 'primaryType_x', 'text_x', 'alignedGeneSequences.gene.name_y', 'primaryType_y'], axis = 1).replace(np.nan,"None")
# split data by mutationTypes (one dataframe for each drug resistance gene), rename column headers
PR_resistances = ['PI Major Mutations','PI Accessory Mutations','PR Other Mutations']
mutations_report_PR = mutations_report_full2[mutations_report_full2.mutationTypes.isin(PR_resistances)]
mutations_report_PR_rename = mutations_report_PR.rename(columns={"mutationTypes": "PR_Mutation_Types","text_y":"Mutations"})
RT_resistances = ['NRTI Mutations','NNRTI Mutations','RT Other Mutations']
mutations_report_RT = mutations_report_full2[mutations_report_full2.mutationTypes.isin(RT_resistances)]
mutations_report_RT_rename = mutations_report_RT.rename(columns={"mutationTypes": "RT_Mutation_Types","text_y":"Mutations"})
IN_resistances = ['INSTI Major Mutations','INSTI Accessory Mutations','IN Other Mutations']
mutations_report_IN = mutations_report_full2[mutations_report_full2.mutationTypes.isin(IN_resistances)]
mutations_report_IN_rename = mutations_report_IN.rename(columns={"mutationTypes": "IN_Mutation_Types","text_y":"Mutations"})

## create dataframes that show resistance interpretations for each drug class
# flatten .json to the drugResistance drugScores data
resistance = pd.json_normalize(data=json_data[0]['drugResistance'], record_path=['drugScores'], meta=[['version','text']])
# drop unused columns and change column order
resistance_slim = resistance.drop(['partialScores','score','level','drug.displayAbbr','version.text'], axis=1).reindex(columns=['drug.name','drugClass.name','text'])
# split data by drug class, rename the header appropriately and remove drugClass.name column when finished
grouped2 = resistance_slim.groupby(resistance_slim['drugClass.name'])

PR_resistance_data = grouped2.get_group("PI")
PR_resistance_data_rename = PR_resistance_data.rename(columns={"drug.name": "PR_Inhibitors","text":"Resistance_Level"})
PR_resistance_data_fin = PR_resistance_data_rename.drop(['drugClass.name'], axis=1).reindex()

NRTI_resistance_data = grouped2.get_group("NRTI")
NRTI_resistance_data_rename = NRTI_resistance_data.rename(columns={"drug.name": "NRTI_Inhibitors","text":"Resistance_Level"})
NRTI_resistance_data_fin = NRTI_resistance_data_rename.drop(['drugClass.name'], axis=1).reindex()

NNRTI_resistance_data = grouped2.get_group("NNRTI")
NNRTI_resistance_data_rename = NNRTI_resistance_data.rename(columns={"drug.name": "NNRTI_Inhibitors","text":"Resistance_Level"})
NNRTI_resistance_data_fin = NNRTI_resistance_data_rename.drop(['drugClass.name'], axis=1).reindex()

IN_resistance_data = grouped2.get_group("INSTI")
IN_resistance_data_rename = IN_resistance_data.rename(columns={"drug.name": "IN_Inhibitors","text":"Resistance_Level"})
IN_resistance_data_fin = IN_resistance_data_rename.drop(['drugClass.name'], axis=1).reindex()

# print all parts of the intermediate file
print("printing all the parts of the intermediate report file")
print(basic_data_transposed_rename)
print(version_transposed_rename)
print(PR_resistance_data_fin)
print(mutations_report_PR_rename)
print(NRTI_resistance_data_fin)
print(NNRTI_resistance_data_fin)
print(mutations_report_RT_rename)
print(IN_resistance_data_fin)
print(mutations_report_IN_rename) 

# calculate dataframe lengths to determine their positioning on the pre-liminary report
basic_rows = basic_data_transposed_rename.shape[0]
version_rows = version_transposed_rename.shape[0]
PR_res_rows = PR_resistance_data_fin.shape[0]
mutation_PR_rows = mutations_report_PR_rename.shape[0]
NRTI_res_rows = NRTI_resistance_data_fin.shape[0]
NNRTI_res_rows = NNRTI_resistance_data_fin.shape[0]
mutation_RT_rows = mutations_report_RT_rename.shape[0]
IN_res_rows = IN_resistance_data_fin.shape[0]
mutation_IN_rows = mutations_report_IN_rename.shape[0]

basic_startrow = 1
version_startrow = basic_startrow + basic_rows + 2
PR_res_startrow = version_startrow + version_rows + 2
mut_PR_startrow = PR_res_startrow + PR_res_rows + 1
NRTI_res_startrow = mut_PR_startrow + mutation_PR_rows + 2
NNRTI_res_startrow = NRTI_res_startrow + NRTI_res_rows + 1
mut_RT_startrow = NNRTI_res_startrow + NNRTI_res_rows + 1
IN_res_startrow = mut_RT_startrow + mutation_RT_rows + 2
mut_IN_startrow = IN_res_startrow + IN_res_rows + 1

## add all dataframes to excel format creating a preliminary report (comments will be appended later for the final report)
print("Now creating the intermediate report file")
with pd.ExcelWriter(prelim_report, engine="openpyxl") as writer:
    basic_data_transposed_rename.to_excel(writer, sheet_name="Sheet_1", startcol=1, startrow=basic_startrow, header=True, index=False)
    version_transposed_rename.to_excel(writer, sheet_name="Sheet_1", startcol=1, startrow=version_startrow, header=True, index=False)
    PR_resistance_data_fin.to_excel(writer, sheet_name="Sheet_1", startcol=1, startrow=PR_res_startrow, header=True, index=False)
    mutations_report_PR_rename.to_excel(writer, sheet_name="Sheet_1", startcol=1, startrow=mut_PR_startrow, header=True, index=False)
    NRTI_resistance_data_fin.to_excel(writer, sheet_name="Sheet_1", startcol=1, startrow=NRTI_res_startrow, header=True, index=False)
    NNRTI_resistance_data_fin.to_excel(writer, sheet_name="Sheet_1", startcol=1, startrow=NNRTI_res_startrow, header=True, index=False)
    mutations_report_RT_rename.to_excel(writer, sheet_name="Sheet_1", startcol=1, startrow=mut_RT_startrow, header=True, index=False)
    IN_resistance_data_fin.to_excel(writer, sheet_name="Sheet_1", startcol=1, startrow=IN_res_startrow, header=True, index=False)
    mutations_report_IN_rename.to_excel(writer, sheet_name="Sheet_1", startcol=1, startrow=mut_IN_startrow, header=True, index=False)

## confirm that the intermediate file was successfully created, and read this file for the next parts of the script
print("Checking if the intermediate report file was generated successfully")
if os.path.exists(prelim_report):
    print(f"The '{prelim_report}' exists. Reading this file to scan for 'Other' and 'Dosage' comments to be appended (happens later on).")
    report_df = pd.read_excel(f"{prelim_report}", header=None)
    print("Here is what the file looks like:")
    print(report_df)
else:
    print(f"The path '{prelim_report}' does not exist.")

####### This section of the script pulls all comments from the original .json file (main comments only), and adds extra comments when needed (conditional comments based on reference data)
## now collect all the main comments from the .json file in a comments dictionary (these include PI Major, PI Accessory, NRTI, NNRTI, INSTI Major and INSTI Accessory mutation comments)
## if any 'Other' or 'Dosage' comments are pulled from the .json, these will be removed (less critical comments are added later by reference file mapping)
print("Now looking for all the comments from the .json file (these include PI Major, PI Accessory, NRTI, NNRTI, INSTI Major and INSTI Accessory mutation comments)")
comments = dict()
for drug_resistance in json_data[0]["drugResistance"]:
    for drug_score in drug_resistance["drugScores"]:
        drug_class_name = drug_score["drugClass"]["name"]
        for partial_score in drug_score["partialScores"]:
            for mutation in partial_score["mutations"]:
                for comment in mutation["comments"]:
                    if drug_class_name not in comments:
                        comments[drug_class_name] = set()
                    comments[drug_class_name].add((comment["type"],comment["text"]))


# create placeholder comment dictionary if there are no comments at all
if len(comments) == 0:
    print("No comments were found in the .json file, creating an empty comments dictionary as a placeholder.")
    comments = {'empty': {('comment type', 'empty comment')}}
else:
    print("Some comments were found in the .json file, moving on to formatting these comments.")

# convert the comments dictionary into a dataframe (creates: value='None' to make array's the same size for each dictionary key)
comments_df = pd.DataFrame.from_dict(comments, orient='index')
comments_df = comments_df.reset_index()

# convert to long format based on the first column (has the header 'index' after performing reset_index), drop the first 'variable' column (these are just the old indexes i.e. 0,1,2,3...)
comments_df_long = pd.melt(comments_df, id_vars='index').drop(columns=['variable'])

# remove value='None' rows, in a new copy 
comments_df_long_noNA = comments_df_long.dropna(subset=['value']).copy()

# split the comment tuple inside the 'value' column into two separate columns 'type' and 'comment'
comments_df_long_noNA['type'] = comments_df_long_noNA['value'].str[0]
comments_df_long_noNA['comment'] = comments_df_long_noNA['value'].str[1]

#### remove 'Other' and 'Dosage' types if these exist becuase these are added later by secondary reference script (DO YOU NEED TO DO THIS HERE OR CAN YOU DE-DUPLICATE AT THE END 09/12/2025 - to test) #####
print("Dropping 'Other' and 'Dosage' comment types becuase these are added later using a reference database.")
comments_df_long_noNA = comments_df_long_noNA[comments_df_long_noNA['type'].str.contains("Other") == False]
comments_df_long_noNA = comments_df_long_noNA[comments_df_long_noNA['type'].str.contains("Dosage") == False]

# create a new column joining 'index' (i.e. 'PI','INSTI','NRTI','NNRTI') to 'type' (i.e. 'Major','Accessory','NRTI','NNRTI'), unless these values are the same (in case on NRTI and NNRTI)
def create_comment_type(row):
    if row['index'] != row['type']:
        return row['index'] + ' ' + row['type']
    else:
        return row['index']
comments_df_long_noNA['Comment/Mutation Type'] = comments_df_long_noNA.apply(create_comment_type, axis=1)

# drop unnecessary columns, rename, and re-order columns
comments_df_long_noNA_slim = comments_df_long_noNA.drop(columns=['index', 'value','type'], axis=1)
comments_df_long_noNA_slim.rename(columns={'comment':'Comment'}, inplace=True)

main_comments_fin = comments_df_long_noNA_slim[['Comment/Mutation Type','Comment']]

print("Now displaying the formatted main comments from the .json file.")
###
print(main_comments_fin)
###

####### this section of the script finds all 'Other'/'Dosage' comments that apply by searching the preliminary report against mutations/conditions stipulated in reference files and adds these to the main comments 
print("Now adding all other comments like 'Other' and 'Dosage' that apply by searching the preliminary report against mutations/conditions stipulated in reference files.")

# reference comment dataframes
## Load comment reference dataframes
print("Loading comment reference dataframes...")
ref_comment_df_PR = pd.read_csv(in_ref_PR)
ref_comment_df_NRTI = pd.read_csv(in_ref_NRTI)
ref_comment_df_NNRTI = pd.read_csv(in_ref_NNRTI)
ref_comment_df_IN = pd.read_csv(in_ref_IN)

## set-up short hand for comment type variables (these are used throughout the script)
PI_Maj = "PI Major"
PI_Acc = "PI Accessory"
NRTI_ = "NRTI"
NNRTI_ = "NNRTI"
INSTI_Maj = "INSTI Major"
INSTI_Acc = "INSTI Accessory"
PR_Oth = "PR Other"
PR_Dos = "PR Dosage"
RT_Oth = "RT Other"
RT_Dos = "RT Dosage"
IN_Oth = "IN Other"
IN_Dos = "IN Dosage"

# join NRTI and NNRTI reference comment dataframes into single RT dataframe
ref_comment_df_RT = pd.concat([ref_comment_df_NRTI,ref_comment_df_NNRTI], ignore_index=True)

# add column to reference comment dataframes that indicates the gene associated with comments
ref_comment_df_PR['Gene'] = "PR"
ref_comment_df_RT['Gene'] = "RT"
ref_comment_df_IN['Gene'] = "IN"

# join gene annotated reference comment dataframes these into a single dataframe
ref_comment_df = pd.concat([ref_comment_df_PR,ref_comment_df_RT,ref_comment_df_IN])
print("Making sure reference dataframe headers are all consistent formats")
for col in ref_comment_df.columns:
    if '\n' in col or '\r' in col:
        print(f"Column header '{col}' contains a newline character. The newline will be removed")
        ref_comment_df.columns = ref_comment_df.columns.str.replace('\n', '')
    else:
        print (f"Column header '{col}' does not contain a newline character.")
 

# Modify numerical resistance levels to their corresponding strings
ref_comment_df['Condition'] = ref_comment_df['Condition'].str.replace('/r', '')
ref_comment_df['Condition'] = ref_comment_df['Condition'].str.replace('=1', '="Susceptible"')
ref_comment_df['Condition'] = ref_comment_df['Condition'].str.replace('=2', '="Potential Low-Level Resistance"')
ref_comment_df['Condition'] = ref_comment_df['Condition'].str.replace('=3', '="Low-Level Resistance"')
ref_comment_df['Condition'] = ref_comment_df['Condition'].str.replace('=4', '="Intermediate Resistance"')
ref_comment_df['Condition'] = ref_comment_df['Condition'].str.replace('=5', '="High-Level Resistance"')

print("Here is the reference dataframe:")
###
print(ref_comment_df)
###
print("Defining rules to check for the mutation types in the reference database.")
# Define insertion conditions in comment dataframe (these can sometimes be in lists separated by 'OR' i.e. "33i OR 34i OR 35i")
def check_insertion_mutation_PR(condition_str, report_df):
    inserts = [insert.strip() for insert in re.split(r'\bOR\b', condition_str, flags=re.IGNORECASE)]
    for insert in inserts:
        m = re.match(r'(\d+)i$', insert)
        if not m:
            continue
        pos = m.group(1) 
        ## Pattern of an insertion in the report dataframe is one capital letter, then the position number, then one capital letter, then an underscore, then one or more letters, then a word boundary (i.e. L33_M*)
        pattern = rf'\b[A-Z]{pos}[A-Z]_[A-Z]+\b' 
        if report_df[2].str.contains(pattern, regex=True, case=True).any():
            return True
    return False

# Define deletion conditions in comment dataframe (these can sometimes be in lists separated by 'OR' i.e. "33d OR 34d")
def check_deletion_mutation(condition_str, report_df):
    deles = [dele.strip() for dele in re.split(r'\bOR\b', condition_str, flags=re.IGNORECASE)]
    for dele in deles:
        d = re.match(r'(\d+)d$', dele)
        if not d:
            continue
        pos = d.group(1)
        ## Pattern of a delection in the report dataframe is one capital letter before position number and "del" after position number, with word boundaries (i.e. L33del)
        del_pattern = rf'\b[A-Z]{pos}del\b'
        if report_df[2].str.contains(del_pattern, regex=True, case=True).any():
            return True
    return False

# Define and expand compound mutation conditions like "10IV" to ["10I", "10V"] or define simple mutations like "138D" in comment dataframe
def expand_compound_mutation(mutation):
    ## regex pattern for a compound mutation condition is a digit followed by 2 or more capital letters
    ## (SHOULD THIS BE m = re.match(r'(\d+)([A-Z]{1,})$', mutation)???? to capture individual mutants (i.e. 1 or more capital letters) - these are already captured with the current regex, but the logic is less clear 09/12/2025 - to test this)
    m = re.match(r'(\d+)([A-Z]{2,})$', mutation)
    ## if a compound mutation is found split it into its parts:
    if m:
        pos = m.group(1)
        aas = m.group(2)
        ## Pattern of mutation in the report dataframe is the nucleotide position {pos} (i.e. 10) and the amino acid(s) {aas} (i.e. I or V) i.e. ["10I", "10V"]
        return [f"{pos}{aa}" for aa in aas]
    ## otherwise return the simple mutation pattern
    else:
        return [mutation]

# Define complex multi-drug conditions with AND (i.e. DRV/r=5 AND TPV/r=1)
def check_complex_condition(condition_str, report_df):
    ## define individual conditions separated by "AND"
    parts = [part.strip() for part in re.split(r'\bAND\b', condition_str, flags=re.IGNORECASE)]
    for part in parts:
        ## match the pattern in the dataframe for individual conditions
        match = re.match(r'(\w+)\s*=\s*"(.*)"', part)
        if not match:
            return False
        key, val = match.groups()
        if not ((report_df[1] == key) & (report_df[2] == val)).any():
            return False
    ## if all conditions joined by AND are met:
    return True

# Define single drug resistance conditions 
def check_drug_resistance(condition_str, report_df):
    ## match the pattern in the dataframe for individual conditions
    match = re.match(r'(\w+)\s*=\s*"(.*)"', condition_str)
    if not match:
        return False
    drug, resistance = match.groups()
    ## if condition is met return TRUE
    return ((report_df[1] == drug) & (report_df[2] == resistance)).any()

# Find row indexes for start and stop of report sections relevant to each gene
idx_PR_start = report_df.index[report_df[1] == 'PR_Inhibitors'].tolist()
idx_PR_stop = report_df.index[report_df[1] == 'PR Other Mutations'].tolist()
idx_RT_start = report_df.index[report_df[1] == 'NRTI_Inhibitors'].tolist()
idx_RT_stop = report_df.index[report_df[1] == 'RT Other Mutations'].tolist()
idx_IN_start = report_df.index[report_df[1] == 'IN_Inhibitors'].tolist()
idx_IN_stop = report_df.index[report_df[1] == 'IN Other Mutations'].tolist()

# Extract the indexes as an integers and increase the stop position by one to include the last line in the range
idx_PR_R1 = idx_PR_start[0]
idx_PR_R2 = idx_PR_stop[0]+1
idx_RT_R1 = idx_RT_start[0]
idx_RT_R2 = idx_RT_stop[0]+1
idx_IN_R1 = idx_IN_start[0]
idx_IN_R2 = idx_IN_stop[0]+1

# Define the ranges of the report that relate to each gene
gene_section_ranges = {
    "PR": range(idx_PR_R1, idx_PR_R2),   
    "RT": range(idx_RT_R1, idx_RT_R2),   
    "IN": range(idx_IN_R1, idx_IN_R2),   
}

# Main loop to add comments when the conditions are met (by scanning the report by relevant gene sections) 
print("Adding comments when the conditions are met for mutation types")
all_comments_df = main_comments_fin.copy()

for _, row in ref_comment_df.iterrows():
    mutation = row['Condition']
    comment = row['Comment']
    comment_type = row['Comment/Mutation Type']
    gene = row['Gene']

    if pd.isna(comment_type) or str(comment_type).strip() == "":
        comment_type = "Dosage"

    ## Select the relevant part of the report for each gene
    gene_rows = gene_section_ranges.get(gene)
    if gene_rows is None:
        continue  ## Skip if no range defined

    gene_df = report_df.loc[gene_rows]

    ## Check if defined conditions/patterns are met but only within the gene-specific region of the report 
    ## If the condition is met in the report, if it is add the associated comment to the bottom of the comments section   
    if 'AND' in mutation:
        if check_complex_condition(mutation, gene_df):
            all_comments_df = pd.concat([all_comments_df, pd.DataFrame([{'Comment/Mutation Type': comment_type, 'Comment': comment, 'Gene': gene}])], ignore_index=True)
    elif '=' in mutation:
        if check_drug_resistance(mutation, gene_df):
            all_comments_df = pd.concat([all_comments_df, pd.DataFrame([{'Comment/Mutation Type': comment_type, 'Comment': comment, 'Gene': gene}])], ignore_index=True)
    else:
        if check_insertion_mutation_PR(mutation, gene_df):
            all_comments_df = pd.concat([all_comments_df, pd.DataFrame([{'Comment/Mutation Type': comment_type, 'Comment': comment, 'Gene': gene}])], ignore_index=True)
        elif check_deletion_mutation(mutation, gene_df):
            all_comments_df = pd.concat([all_comments_df, pd.DataFrame([{'Comment/Mutation Type': comment_type, 'Comment': comment, 'Gene': gene}])], ignore_index=True)
        else:
            expanded_mutations = expand_compound_mutation(mutation)
            matched = False
            ## Define pattern for each expanded mutation condition i.e. position (digit) followed by amino acid (capital letter) (i.e. ["10V", "10I"])
            for em in expanded_mutations:
                m = re.match(r'(\d+)([A-Z])$', em)
                ## Define the parts of each expanded mutation (position and amino acid(s))
                if not m:
                    continue
                pos, aa = m.groups()
                ## Define the pattern of these mutations in the report dataframe (i.e. the mutation of interest might be hidden amongst other amino acids "L10AIL")
                pattern = rf'\b[A-Z]{pos}[A-Z]*{aa}[A-Z]*\b'
                if gene_df[2].str.contains(pattern, regex=True).any():
                    all_comments_df = pd.concat([all_comments_df, pd.DataFrame([{'Comment/Mutation Type': comment_type, 'Comment': comment, 'Gene': gene}])], ignore_index=True)
                    matched = True
                    break
            ## If nothing matches that pattern, just check the exact wording of expanded mutation against report dataframe, incase it appears just as a simple mutation like "10V" in the report
            if not matched:
                for em in expanded_mutations:
                    if gene_df[2].str.contains(rf'\b{re.escape(em)}\b', regex=True).any():
                        all_comments_df = pd.concat([all_comments_df, pd.DataFrame([{'Comment/Mutation Type': comment_type, 'Comment': comment, 'Gene': gene}])], ignore_index=True)
                        break
# remove duplicated comments (these may exist for the main mutations pulled from the .json file) 
all_comments_df.drop_duplicates(subset=['Comment'],inplace=True)
print("Here is a dataframe containing all de-duplicated comments that relate to this sample (these still need further formatting):")
##
print(all_comments_df)
##

# identify 'Other' and 'Dosage' Comment_Types with their correct gene (if these exist).
if all_comments_df['Comment/Mutation Type'].isin(['Other']).any():
    all_comments_df.loc[all_comments_df['Comment/Mutation Type'].str.contains('Other'), 'Comment/Mutation Type'] = all_comments_df['Gene'] + " " + all_comments_df['Comment/Mutation Type']
if all_comments_df['Comment/Mutation Type'].isin(['Dosage']).any():   
    all_comments_df.loc[all_comments_df['Comment/Mutation Type'].str.contains('Dosage'), 'Comment/Mutation Type'] = all_comments_df['Gene'] + " " + all_comments_df['Comment/Mutation Type']

# determine if any 'Comment_Type's are missing from this dataframe and add a comment saying 'No comment was found' for any that are missing
print("Identifying any comment types that are missing.")
all_comments_incl_missing = all_comments_df.copy()

# set up labels and descriptions (these comment labels are variables for actual text set up earlier in the script)
comment_labels = [
    (PI_Maj, "PI Major mutation"),
    (PI_Acc, "PI Accessory mutation"),
    (PR_Oth, "PR Other mutation"),
    (PR_Dos, "PR Dosage"),
    (NRTI_, "NRTI mutation"),
    (NNRTI_, "NNRTI mutation"),
    (RT_Oth, "RT Other mutation"),
    (RT_Dos, "RT Dosage"),
    (INSTI_Maj, "INSTI Major mutation"),
    (INSTI_Acc, "INSTI Accessory mutation"),
    (IN_Oth, "IN Other mutation"),
    (IN_Dos, "IN Dosage")
]
  
for clab, desc in comment_labels:
    #changed this to do exact match to string as str.contains was causing issues with NRTI (NNRTI contains NRTI) 22/09/2025
    #if not all_comments_incl_missing['Comment/Mutation Type'].str.contains(clab, case=False, na=False).any():
    if not all_comments_incl_missing['Comment/Mutation Type'].isin([clab]).any():
        new_row = {'Comment/Mutation Type': clab, 'Comment': f"No {desc} comments were found."}
        all_comments_incl_missing = pd.concat([all_comments_incl_missing, pd.DataFrame([new_row])], ignore_index=True)
    else:
        new_row = pd.DataFrame()
        all_comments_incl_missing = pd.concat([all_comments_incl_missing, new_row], ignore_index=True)
     
# for the main comments and "No ... comments were found rows", add appropriate gene in 'Gene' column, and remove empty placeholder
mapping_dict = {
    PI_Maj: 'PR',
    PI_Acc: 'PR',
    PR_Oth: 'PR',
    PR_Dos: 'PR',
    NRTI_: 'RT',
    NNRTI_: 'RT',
    RT_Oth: 'RT',
    RT_Dos: 'RT',
    INSTI_Maj: 'IN',
    INSTI_Acc: 'IN',
    IN_Oth: 'IN',
    IN_Dos: 'IN',
    'empty comment type': 'empty comment to be removed'
}

print("Making sure the 'Gene' column has been correctly populated.")
# create a new column 'Fill_Gene', by mapping the comment type to the gene assigned in the mapping dictionary
all_comments_incl_missing['Fill_Gene'] = all_comments_incl_missing['Comment/Mutation Type'].map(mapping_dict)
if 'Gene' not in all_comments_incl_missing.columns:
    # fill in old 'Gene' column in NaN if there was nothing there to begin with
    all_comments_incl_missing['Gene'] = np.nan
# Where 'Gene' is NaN, replace these with the 'Fill_Gene' mapped data, and drop the extra column
all_comments_incl_missing['Gene'] = all_comments_incl_missing['Gene'].fillna(all_comments_incl_missing['Fill_Gene'])
all_comments_incl_missing = all_comments_incl_missing.drop(columns=['Fill_Gene'])
# remove placeholder empty comment from when the main comments were pulled from the .json file
all_comments_incl_missing = all_comments_incl_missing[all_comments_incl_missing['Gene'] != 'empty comment to be removed']

# Sort comments in order 
print("Sorting comments in order.")
print("Displaying all the final formatted comments for this sample.")
comments_order = [PI_Maj, PI_Acc, PR_Oth, PR_Dos, NRTI_, NNRTI_, RT_Oth, RT_Dos,  INSTI_Maj, INSTI_Acc, IN_Oth, IN_Dos, ]
all_comments_incl_missing['Comment/Mutation Type'] = pd.Categorical(all_comments_incl_missing['Comment/Mutation Type'], categories=comments_order, ordered=True)
all_comments_fin = all_comments_incl_missing.sort_values('Comment/Mutation Type')
print(all_comments_fin)

# separate all comments dataframe into one for each resistance gene
print("Splitting comments up by 'Gene', so they can be put in the right section of the report.")
PR_all_comments_fin =  all_comments_fin[all_comments_fin['Gene'].str.contains("PR")].copy()
RT_all_comments_fin =  all_comments_fin[all_comments_fin['Gene'].str.contains("RT")].copy()
IN_all_comments_fin =  all_comments_fin[all_comments_fin['Gene'].str.contains("IN")].copy()

# drop gene column 
PR_all_comments_fin.drop(columns=['Gene'], axis=1, inplace = True)
RT_all_comments_fin.drop(columns=['Gene'], axis=1, inplace = True)
IN_all_comments_fin.drop(columns=['Gene'], axis=1, inplace = True)

# calculate dataframe lengths to determine their positioning on the final report
PR_comments_rows = PR_all_comments_fin.shape[0]
RT_comments_rows = RT_all_comments_fin.shape[0]
IN_comments_rows = IN_all_comments_fin.shape[0]

basic_startrow = 1
version_startrow = basic_startrow + basic_rows + 2
PR_res_startrow = version_startrow + version_rows + 2
mut_PR_startrow = PR_res_startrow + PR_res_rows + 1
PR_comments_startrow = mut_PR_startrow + mutation_PR_rows +1
NRTI_res_startrow = PR_comments_startrow + PR_comments_rows + 2
NNRTI_res_startrow = NRTI_res_startrow + NRTI_res_rows + 1
mut_RT_startrow = NNRTI_res_startrow + NNRTI_res_rows + 1
RT_comments_startrow = mut_RT_startrow + mutation_RT_rows +1
IN_res_startrow = RT_comments_startrow + RT_comments_rows + 2
mut_IN_startrow = IN_res_startrow + IN_res_rows + 1
IN_comments_startrow = mut_IN_startrow + mutation_IN_rows +1

print("Displaying all the parts of the final report file.")
print(basic_data_transposed_rename)
print(version_transposed_rename)
print(PR_resistance_data_fin)
print(mutations_report_PR_rename)
print(PR_all_comments_fin)
print(NRTI_resistance_data_fin)
print(NNRTI_resistance_data_fin)
print(mutations_report_RT_rename)
print(RT_all_comments_fin)
print(IN_resistance_data_fin)
print(mutations_report_IN_rename)
print(IN_all_comments_fin)

## add all dataframes to excel format creating a final report including all relevant comments
print("Now creating the final report file.")
with pd.ExcelWriter(output_final_report, engine="openpyxl") as writer:
    basic_data_transposed_rename.to_excel(writer, sheet_name="Sheet_1", startcol=1, startrow=basic_startrow, header=True, index=False)
    version_transposed_rename.to_excel(writer, sheet_name="Sheet_1", startcol=1, startrow=version_startrow, header=True, index=False)
    PR_resistance_data_fin.to_excel(writer, sheet_name="Sheet_1", startcol=1, startrow=PR_res_startrow, header=True, index=False)
    mutations_report_PR_rename.to_excel(writer, sheet_name="Sheet_1", startcol=1, startrow=mut_PR_startrow, header=True, index=False)
    PR_all_comments_fin.to_excel(writer, sheet_name="Sheet_1", startcol=1, startrow=PR_comments_startrow, header=True, index=False)
    NRTI_resistance_data_fin.to_excel(writer, sheet_name="Sheet_1", startcol=1, startrow=NRTI_res_startrow, header=True, index=False)
    NNRTI_resistance_data_fin.to_excel(writer, sheet_name="Sheet_1", startcol=1, startrow=NNRTI_res_startrow, header=True, index=False)
    mutations_report_RT_rename.to_excel(writer, sheet_name="Sheet_1", startcol=1, startrow=mut_RT_startrow, header=True, index=False)
    RT_all_comments_fin.to_excel(writer, sheet_name="Sheet_1", startcol=1, startrow=RT_comments_startrow, header=True, index=False)
    IN_resistance_data_fin.to_excel(writer, sheet_name="Sheet_1", startcol=1, startrow=IN_res_startrow, header=True, index=False)
    mutations_report_IN_rename.to_excel(writer, sheet_name="Sheet_1", startcol=1, startrow=mut_IN_startrow, header=True, index=False)
    IN_all_comments_fin.to_excel(writer, sheet_name="Sheet_1", startcol=1, startrow=IN_comments_startrow, header=True, index=False)

## confirming the final report was successfully generated and printing this to the log
print("Checking if the final report file was generated successfully")
if os.path.exists(output_final_report):
    print(f"The '{output_final_report}' exists. Reading this file to check it completed successfully.")
    final_report_df = pd.read_excel(f"{output_final_report}", header=None)
    print("Here is what the file looks like:")
    print(final_report_df)
else:
    print(f"The path '{output_final_report}' does not exist.")