import argparse
import json
import os
import pathlib
import sys
import xlrd

from datetime import datetime


def extract_data(xl_sheet, expected_columns):
    # Check that the columns I expect are present in the sheet (any order and mixed with others)
    # Just a verification that the user filled the correct template
    sheet_columns = {}
    for sh_col in range(xl_sheet.ncols):
        if xl_sheet.cell(0, sh_col).value in expected_columns:
            if xl_sheet.cell(0, sh_col).value in sheet_columns.keys():
                sys.exit("Duplicated columns")
            else:
                sheet_columns[xl_sheet.cell(0, sh_col).value] = sh_col
    for col in range(len(expected_columns)):
        assert expected_columns[col] in sheet_columns.keys(), "Expected column %s not found" %expected_columns[col]

    # fetch rows in a dict
    data_dict = {}
    # the first of the expected columns will be the index
    index_col = sheet_columns[expected_columns[0]]
    ## skip first 2 rows: column names + comments rows
    for row_id in range(2,xl_sheet.nrows):
        row_dict = {}
        for col in range(1,len(expected_columns)):
            # row_dict[expected_columns[col]] = xl_sheet.cell(row_id,col).value
            sheet_col_index = sheet_columns[expected_columns[col]]
            row_dict[expected_columns[col]] = xl_sheet.cell(row_id,sheet_col_index).value
        # should I check for duplicate alias/ids?
        data_dict[xl_sheet.cell(row_id, index_col).value] = row_dict
    return data_dict

parser = argparse.ArgumentParser()
parser.add_argument('--form',dest='xlsx_path', required=True)
parser.add_argument('--out_dir',dest='out_path', required=True)
parser.add_argument('--vir',dest='viral_submission',required=False,action='store_true')
args = parser.parse_args()

xl_workbook = xlrd.open_workbook(args.xlsx_path)


## PARSE STUDIES
#################
xl_sheet = xl_workbook.sheet_by_name('ENA_study')
if(xl_sheet.nrows < 3):
    raise ValueError('No entries found in studies sheet')

studies_dict = {}
# Assert column names
studies_col = ['alias','title','study_type','study_abstract']
studies_dict = extract_data(xl_sheet, studies_col)


## PARSE SAMPLES
xl_sheet = xl_workbook.sheet_by_name('ENA_sample')
if(xl_sheet.nrows < 3):
    raise ValueError('No entries found in samples')
if args.viral_submission:
    samples_cols = ['alias','title','scientific_name','sample_description','geographic location (country and/or sea)', 'host common name', 'host health state', 'host sex', 'host scientific name', 'collector name', 'collection date','collecting institution', 'isolate']
else:
    samples_cols = ['alias','title','scientific_name','sample_description']
samples_dict = extract_data(xl_sheet, samples_cols)



## PARSE EXPERIMENTS
#################
xl_sheet = xl_workbook.sheet_by_name('ENA_experiment')
if(xl_sheet.nrows < 3):
    raise ValueError('No experiments found in experiments sheet')

exp_columns = ['alias','title','study_alias','sample_alias','design_description','library_name','library_strategy','library_source','library_selection','library_layout','insert_size','library_construction_protocol','platform','instrument_model']

experiments_dict = extract_data(xl_sheet, exp_columns)


## PARSE RUNS SHEET
#################
xl_sheet = xl_workbook.sheet_by_name('ENA_run')
if(xl_sheet.nrows < 3):
    raise ValueError('No entries found in runs sheet')

#Assert column names
row_idx = 0
run_cols = ['alias','experiment_alias','file_name','file_format']

runs_dict = extract_data(xl_sheet, run_cols)


## WRITE  DICTIONARIES TO TABLE FILES
studies_table = open(pathlib.Path(args.out_path) / 'studies.tsv', 'w')
studies_table.write('\t'.join(['alias','status','accession','title','study_type','study_abstract','pubmed_id','submission_date']) + '\n')

samples_table = open(pathlib.Path(args.out_path) / 'samples.tsv', 'w')
if args.viral_submission:
    samples_table.write('\t'.join(['alias','status','accession','title','scientific_name','taxon_id','sample_description','collection date','geographic_location','host_common_name','host_subject_id','host_health_state','host_sex','host_scientific_name','collector_name','collecting_institution','isolate','submission_date']) + '\n')
else:
    samples_table.write('\t'.join(['alias','status','accession','title','scientific_name','taxon_id','sample_description','submission_date'])+ '\n')

experiments_table = open(pathlib.Path(args.out_path) / 'experiments.tsv', 'w')
experiments_table.write('\t'.join(['alias','status','accession','title','study_alias','sample_alias','design_description','library_name','library_strategy','library_source','library_selection','library_layout','insert_size','library_construction_protocol','platform','instrument_model','submission_date'])+ '\n')

runs_table = open(pathlib.Path(args.out_path) / 'runs.tsv', 'w')
runs_table.write('\t'.join(['alias','status','accession','experiment_alias','file_name','file_format','file_checksum','submission_date'])+ '\n')

action = 'add'

dt_oobj = datetime.now(tz=None)
timestamp = dt_oobj.strftime("%Y%m%d_%H:%M:%S")
for study_alias, study in studies_dict.items():
    # study_alias = 'study_'+str(study_index)+'_'+timestamp
    # study_alias = study_index #'study_'+str(study_index)+'_'+timestamp
    # studies_col = ['alias','title','study_type','study_abstract']
    studies_table.write('\t'.join([study_alias,action,'ENA_accession',study['title'], study['study_type'],study['study_abstract'],'','ENA_submission_data'])+ '\n')  ## assuming no pubmed_id
for sample_alias, sample in samples_dict.items():
    # if "geo_location" in study['samples'][0].keys(): # sample belongs to a viral sample
    # sample_alias = 'sample_'+str(sample_index)+'_'+timestamp
    if sample['collector name'] == '':
        sample['collector name'] = 'unknown'
    if args.viral_submission:
        samples_table.write('\t'.join([sample_alias,action,'ena_accession',sample['title'],sample['scientific_name'], 'tax_id_updated_by_ENA',sample['sample_description'],sample['collection date'],sample['geographic location (country and/or sea)'],sample['host common name'],'host subject id',sample['host health state'],sample['host sex'],sample['host scientific name'],sample['collector name'],sample['collecting institution'],sample['isolate'],'ENA_submission_date'])+ '\n')
    else:
        samples_table.write('\t'.join([sample_alias,action,'ena_accession',sample['title'],sample['scientific_name'],'tax_id_updated_by_ENA',sample['sample_description']])+ '\n')
    # process the experiments from this sample
    for exp_alias, exp in experiments_dict.items():
        # maybe i should check here if any experiment has a study or sample alias that is incorrect? (not listed in the samples or study dict)
        # process the experiments for this sample
        if exp['sample_alias'] == sample_alias:
            # exp_alias = ' +'_'+timestamp
            # is this ok as a lib alias?
            lib_alias = 'library_'+exp_alias +'_'+ exp['sample_alias']    #+str(exp_index)+'_'+str(sample_index)
            experiments_table.write('\t'.join([exp_alias,action,'accession_ena',exp['title'],study_alias,sample_alias,exp['design_description'],lib_alias,exp['library_strategy'],exp['library_source'],exp['library_selection'],exp['library_layout'].lower(),str(exp['insert_size']),exp['library_construction_protocol'],exp['platform'],exp['instrument_model'],'submission_date_ENA']) + '\n')
            for run_alias, run in runs_dict.items():
                if run['experiment_alias'] == exp_alias:
                    file_format = 'fastq'
                    runs_table.write('\t'.join([run_alias,action,'ena_run_accession',exp_alias,run['file_name'],file_format,'file_checksum','submission_date_ENA']) + '\n')
                    # run_index = 0
                    # exp['runs'] is a list of lists
                    # for run in exp['runs']:
                        # run_index += 1
                        # run_alias = '.'.join(['run_'+str(run_index),str(exp_index),str(sample_index)]) + '_' +timestamp
                        # for file_entry in run:
                            # file_format = 'fastq'
                            # runs_table.write('\t'.join([run_alias,action,'ena_run_accession',exp_alias,file_entry,file_format,'file_checksum','submission_date_ENA']) + '\n')


studies_table.close()
samples_table.close()
experiments_table.close()
runs_table.close()

