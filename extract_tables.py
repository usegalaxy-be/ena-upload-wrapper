import argparse
import json
import os
import pathlib

parser = argparse.ArgumentParser()
parser.add_argument('--studies',dest='studies_json_path', required=True)
parser.add_argument('--out_dir',dest='out_path', required=True)
args = parser.parse_args()


with open(args.studies_json_path,'r') as studies_json_file:
    studies_dict = json.load(studies_json_file)

studies_table = open(pathlib.Path(args.out_path) / 'studies.tsv', 'w')
studies_table.write('\t'.join(['alias','status','accession','title','study_type','study_abstract','pubmed_id','submission_date']) + '\n')

samples_table = open(pathlib.Path(args.out_path) / 'samples.tsv', 'w')
samples_table.write('\t'.join(['alias','status','accession','title','scientific_name','taxon_id','sample_description','submission_date']) + '\n')

experiments_table = open(pathlib.Path(args.out_path) / 'experiments.tsv', 'w')
experiments_table.write('\t'.join(['alias','status','accession','title','study_alias','sample_alias','design_description','library_name','library_strategy','library_source','library_selection','library_layout','insert_size','library_construction_protocol','platform','instrument_model','submission_date'])+ '\n')

runs_table = open(pathlib.Path(args.out_path) / 'runs.tsv', 'w')
runs_table.write('\t'.join(['alias','status','accession','experiment_alias','file_name','file_format','file_checksum','submission_date'])+ '\n')

action = 'add'
viral_submission = False
for study_index, study in enumerate(studies_dict):
    study_alias = 'study_'+str(study_index)
    studies_table.write('\t'.join([study_alias,action,'ENA_accession',study['title'], study['type'],study['abstract'],study['pubmed_id'],'ENA_submission_data']))
    for sample_index,sample in enumerate(study['samples']):
        sample_alias = 'sample_'+str(sample_index)
        if "geo_location" in sample.keys():  # sample belongs to a 
            samples_table.write('\t'.join([sample_alias,action,'ena_accession',sample['title'],sample['tax_name'], sample['tax_id'],sample['description'],'ENA_submission_date'])+ '\n')
        else:
            samples_table.write('\t'.join([sample_alias,action,'ena_accession',sample['title'],sample['tax_name'], sample['tax_id'],sample['description'],'ENA_submission_date'])+ '\n')
        for exp_index,exp in enumerate(sample['experiments']):
            exp_alias = 'experiment_'+str(exp_index)+'_'+str(sample_index)
            lib_alias = 'library_'+str(exp_index)+'_'+str(sample_index)
            experiments_table.write('\t'.join([exp_alias,action,'accession_ena',exp['title'],study_alias,sample_alias,exp['experiment_design'],lib_alias,exp['library_strategy'],exp['library_source'],exp['library_selection'],exp['library_layout'].lower(),exp['insert_size'],exp['library_construction_protocol'],exp['platform'],exp['instrument_model'],'submission_date_ENA']) + '\n')
            run_index = 0
            # exp['runs'] is a list of lists
            for run in exp['runs']:
                run_index += 1
                run_alias = '_'.join(['run',str(exp_index),str(sample_index),str(run_index)])
                for file_entry in run:
                    file_format = 'fastq'
                    runs_table.write('\t'.join([run_alias,action,'ena_run_accession',exp_alias,file_entry,file_format,'file_checksum','submission_date_ENA']) + '\n')

studies_table.close()
samples_table.close()
experiments_table.close()
runs_table.close()
