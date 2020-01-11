# GENERAL IMPORTS
import csv
import json
import os

# Classes

class result_obj:
    def __init__(self,domain_name):

        self.protected = 0
        self.unprotected = 0
        self.error = 0
        self.domain_name = domain_name

# Helper functions

def write_results_to_disk(result_dict,input):

    base_dir        = os.path.dirname(input)
    file            = os.path.splitext(os.path.basename(input))
    file_name       = file[0]
    file_extension  = file[1]

    output = file_name+'_results.json'

    os.system('touch {}'.format(output)) # Create file

    #Write to the output file
    with open(output,'w') as new_file:
        json.dump(result_dict,new_file,indent=4)

# Start function

def generate_report(settings):

    # Get input files

    input = settings.input
    reference = settings.reference

    # Open files

    input_dict  =   {}
    ref_dict    =   {}
    result_dict =   {}


    #CSV to json
    os.system('csvtojson {} > {}.json'.format(input,input))
    os.system('csvtojson {} > {}.json'.format(reference,reference))

    #Open file
    with open(input+'.json') as tmp_file:
       input_dict = json.load(tmp_file)

    with open(reference+'.json') as tmp_file:
       ref_dict = json.load(tmp_file)

    # Cross reference

    for line in input_dict:
        if line['response_name'] not in result_dict:
            result_dict['response_name'] = result_obj(line['response_name'])

        for cross in ref_dict:
            if (line['ns_address'] == cross['ns_address']):
                if( cross['valid_roa'] == 'valid' ):
                    result_dict['response_name'].protected   += 1
                else:
                    result_dict['response_name'].unprotected += 1

                continue # We are done exit for loop

    # Generate results

    protected           =   0
    partial_protected   =   0
    unprotected         =   0
    error               =   0

    for domain in result_dict:
        if (domain.protected == 0 and domain.unprotected == 0): # Strange behaviour -> error
            error+=1
        elif (domain.protected == 0):   # Complete unprotected
            unprotected+=1
        elif (domain.unprotected == 0): # Complete protected
            protected+=1
        else:                           # Partially protected
            partial_protected+=1

    # Add results to dictionary

    results = {}
    results['protected']            =   protected
    results['partial_protected']    =   partial_protected
    results['unprotected']          =   unprotected
    results['error']                =   error

    # Write results to the disk

    write_results_to_disk(results,input)
